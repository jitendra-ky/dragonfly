#!/usr/bin/env bash

# Deploy the current checkout to a low-cost, single-instance AWS showcase.
# Requirements: Git Bash/WSL, AWS CLI, ssh, scp, and tar.

# Make the script stop on errors instead of continuing with a half-configured
# server. `-u` catches misspelled or missing variables, and `pipefail` makes a
# pipeline fail when any command inside it fails.
set -Eeuo pipefail

# Stable names and paths make repeated deployments discoverable and recoverable.
readonly SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_NAME="dragonfly"
readonly DEFAULT_REGION="ap-south-1"
readonly DEFAULT_INSTANCE_TYPE="t3.micro"
readonly DEFAULT_ENV_FILE="${SCRIPT_DIR}/.env.aws"
readonly DEFAULT_KEY_NAME="dragonfly-showcase"
readonly DEFAULT_KEY_PATH="${HOME}/.ssh/${DEFAULT_KEY_NAME}.pem"
readonly DEFAULT_STATE_FILE="${SCRIPT_DIR}/.aws/dragonfly-showcase/state.env"
readonly EXPECTED_MANAGED_BY="dragonfly-zcommand"

# These values can be overridden with command-line options or environment
# variables. Keeping defaults here lets a beginner run the script without
# memorizing a long command.
ACTION="deploy"
REGION="${AWS_REGION:-${DEFAULT_REGION}}"
INSTANCE_TYPE="${INSTANCE_TYPE:-${DEFAULT_INSTANCE_TYPE}}"
ENV_FILE="${DEPLOY_ENV_FILE:-${DEFAULT_ENV_FILE}}"
KEY_NAME="${EC2_KEY_NAME:-${DEFAULT_KEY_NAME}}"
KEY_PATH="${EC2_KEY_PATH:-${DEFAULT_KEY_PATH}}"
INSTANCE_NAME="${INSTANCE_NAME:-${PROJECT_NAME}-showcase}"
STATE_FILE="${DEPLOY_STATE_FILE:-${DEFAULT_STATE_FILE}}"
SSH_USER="ubuntu"
DELETE_LOCAL_KEY=0

# CLI help and small utility functions.
# Print the command reference when the user runs --help.
usage() {
    cat <<'EOF'
Usage: ./zcommand.sh [deploy|status|destroy] [options]

Deploy the current checkout to one low-cost EC2 instance in the default VPC.
Use `status` to inspect the recorded deployment and `destroy` to remove it.

Options:
  --env-file PATH       Deployment environment file (default: .env.aws)
  --region REGION       AWS region (default: ap-south-1)
  --instance-type TYPE  EC2 type (default: t3.micro)
  --key-name NAME       EC2 key-pair name (default: dragonfly-showcase)
  --key-path PATH       Local private-key path
  --state-file PATH     Persistent resource state file
  --delete-key          Delete the local private key during destroy
  --keep-key            Keep the local private key during destroy (default)
  --help                Show this help

The AWS CLI default profile is used. The environment file must contain:
  SECRET_KEY, CORS_ALLOWED_ORIGINS, GOOGLE_CLIENT_ID,
  GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI, POSTGRES_PASSWORD

Optional:
  BACKEND_HOSTNAME  Public hostname, for example
                    dragonfly-backend.jitendra.xyz
EOF
}

# Add a consistent prefix to normal progress messages.
log() {
    printf '[dragonfly] %s\n' "$*"
}

# Print an error and stop immediately. Continuing after an error could create
# resources that are difficult to identify or clean up.
fail() {
    printf '[dragonfly] ERROR: %s\n' "$*" >&2
    exit 1
}

# Delete only the temporary local archive created during this run.
cleanup() {
    if [[ -n "${WORK_DIR:-}" && -d "${WORK_DIR}" ]]; then
        rm -rf -- "${WORK_DIR}"
    fi
}
# Run cleanup whether the script succeeds, fails, or is interrupted.
trap cleanup EXIT

# Save only resource identifiers and deployment metadata locally. Secrets are
# intentionally excluded from this file.
# Save the AWS IDs needed to retry, inspect, or destroy this deployment later.
# The file contains identifiers only; application passwords are never written.
write_state() {
    local state_dir
    state_dir="$(dirname -- "${STATE_FILE}")"
    mkdir -p -- "${state_dir}"
    umask 077
    cat >"${STATE_FILE}" <<EOF
AWS_REGION=${REGION}
STATE_PROJECT_NAME=${PROJECT_NAME}
STATE_MANAGED_BY=${EXPECTED_MANAGED_BY}
DEPLOYMENT_ID=${INSTANCE_NAME}
INSTANCE_NAME=${INSTANCE_NAME}
KEY_NAME=${KEY_NAME}
KEY_PATH=${KEY_PATH}
VPC_ID=${vpc_id:-}
SUBNET_ID=${subnet_id:-}
SECURITY_GROUP_ID=${security_group_id:-}
INSTANCE_ID=${instance_id:-}
EOF
    chmod 600 "${STATE_FILE}"
}

# Load and validate the saved deployment IDs for status and destroy commands.
load_state() {
    [[ -f "${STATE_FILE}" ]] || fail "State file not found: ${STATE_FILE}"
    # This file is generated locally by this script and contains identifiers only.
    set -a
    # shellcheck source=/dev/null
    . "${STATE_FILE}"
    set +a
    [[ "${STATE_MANAGED_BY:-}" == "${EXPECTED_MANAGED_BY}" ]] || fail "State file ownership marker is invalid"
    [[ "${STATE_PROJECT_NAME:-}" == "${PROJECT_NAME}" ]] || fail "State file project marker is invalid"
    [[ -n "${INSTANCE_ID:-}" && -n "${SECURITY_GROUP_ID:-}" && -n "${KEY_NAME:-}" ]] || \
        fail "State file is incomplete"
}

# Apply ownership tags so this script can distinguish its resources from
# unrelated resources in the same AWS account.
# These tags identify resources owned by this script. They are also used to
# recover from a failure when the state file was not updated yet.
aws_resource_tags() {
    printf 'Project=%s\nManagedBy=%s\nDeploymentId=%s\n' \
        "${PROJECT_NAME}" "${EXPECTED_MANAGED_BY}" "${INSTANCE_NAME}"
}

# Add ownership tags to an AWS resource such as a security group or instance.
tag_resource() {
    local resource_id="$1"
    "${aws_cli[@]}" ec2 create-tags --resources "${resource_id}" --tags \
        "Key=Project,Value=${PROJECT_NAME}" \
        "Key=ManagedBy,Value=${EXPECTED_MANAGED_BY}" \
        "Key=DeploymentId,Value=${INSTANCE_NAME}" \
        "Key=Name,Value=${INSTANCE_NAME}"
}

# AWS CLI returns the text "None" when a queried resource is not found.
resource_exists() {
    [[ "$1" != "None" && -n "$1" ]]
}

# Fail early with a readable message when a local tool is unavailable.
require_command() {
    command -v "$1" >/dev/null 2>&1 || fail "Required command is missing: $1"
}

# The default action is deploy; status and destroy use the same saved state.
if [[ $# -gt 0 && "$1" != -* ]]; then
    ACTION="$1"
    shift
fi

case "${ACTION}" in
    deploy|status|destroy) ;;
    *) fail "Unknown action: ${ACTION}" ;;
esac

# Read optional command-line settings such as --region or --key-path.
while [[ $# -gt 0 ]]; do
    case "$1" in
        --env-file)
            [[ $# -ge 2 ]] || fail "--env-file requires a path"
            ENV_FILE="$2"
            shift 2
            ;;
        --region)
            [[ $# -ge 2 ]] || fail "--region requires a value"
            REGION="$2"
            shift 2
            ;;
        --instance-type)
            [[ $# -ge 2 ]] || fail "--instance-type requires a value"
            INSTANCE_TYPE="$2"
            shift 2
            ;;
        --key-name)
            [[ $# -ge 2 ]] || fail "--key-name requires a value"
            KEY_NAME="$2"
            shift 2
            ;;
        --key-path)
            [[ $# -ge 2 ]] || fail "--key-path requires a path"
            KEY_PATH="$2"
            shift 2
            ;;
        --state-file)
            [[ $# -ge 2 ]] || fail "--state-file requires a path"
            STATE_FILE="$2"
            shift 2
            ;;
        --keep-key)
            DELETE_LOCAL_KEY=0
            shift
            ;;
        --delete-key)
            DELETE_LOCAL_KEY=1
            shift
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        *)
            fail "Unknown option: $1 (use --help for usage)"
            ;;
    esac
done

# AWS CLI setup is shared by all actions.
require_command aws
# `aws_cli` is an array so the region and command arguments stay safely
# separated even when values contain shell-special characters.
aws_cli=(aws --region "${REGION}")
# These SSH options avoid an interactive host-key prompt on the first
# connection while still rejecting connections that time out.
ssh_options=(-o StrictHostKeyChecking=accept-new -o ConnectTimeout=10)

# A harmless identity request verifies that the AWS CLI is authenticated before
# the script starts creating resources.
log "Checking AWS credentials"
"${aws_cli[@]}" sts get-caller-identity >/dev/null

if [[ "${ACTION}" == "status" || "${ACTION}" == "destroy" ]]; then
    # Status and destroy must use the exact region and IDs from the previous
    # deployment, not whatever defaults happen to be supplied today.
    load_state
    REGION="${AWS_REGION}"
    KEY_NAME="${KEY_NAME}"
    KEY_PATH="${KEY_PATH}"
    INSTANCE_NAME="${INSTANCE_NAME}"
    aws_cli=(aws --region "${REGION}")
fi

# Read-only inspection of the saved deployment.
if [[ "${ACTION}" == "status" ]]; then
    # Status never creates or changes resources. If AWS cannot describe the
    # instance, show an empty result rather than hiding the state-file details.
    instance_state="$("${aws_cli[@]}" ec2 describe-instances --instance-ids "${INSTANCE_ID}" \
        --query 'Reservations[0].Instances[0].[State.Name,PublicIpAddress]' --output text 2>/dev/null || true)"
    printf 'State file:       %s\n' "${STATE_FILE}"
    printf 'Instance ID:      %s\n' "${INSTANCE_ID}"
    printf 'Instance status:  %s\n' "${instance_state}"
    printf 'Security group:   %s\n' "${SECURITY_GROUP_ID}"
    printf 'Key pair:         %s\n' "${KEY_NAME}"
    exit 0
fi

# Destruction is deliberately driven by saved IDs and ownership checks rather
# than broad name-based searches.
if [[ "${ACTION}" == "destroy" ]]; then
    # Destroy is intentionally conservative: it checks ownership tags before
    # deleting anything, so a changed or incorrect state file cannot easily
    # remove an unrelated AWS resource.
    log "Verifying recorded resources before destruction"
    actual_owner="$("${aws_cli[@]}" ec2 describe-instances --instance-ids "${INSTANCE_ID}" \
        --query "Reservations[0].Instances[0].Tags[?Key=='ManagedBy'].Value | [0]" \
        --output text 2>/dev/null || true)"
    if [[ -n "${actual_owner}" && "${actual_owner}" != "None" ]]; then
        [[ "${actual_owner}" == "${EXPECTED_MANAGED_BY}" ]] || \
            fail "Recorded instance does not have the expected ownership tag"
        actual_deployment="$("${aws_cli[@]}" ec2 describe-instances --instance-ids "${INSTANCE_ID}" \
            --query "Reservations[0].Instances[0].Tags[?Key=='DeploymentId'].Value | [0]" \
            --output text)"
        [[ "${actual_deployment}" == "${INSTANCE_NAME}" ]] || \
            fail "Recorded instance does not have the expected deployment tag"
        log "Terminating instance ${INSTANCE_ID}"
        # Wait until termination finishes before deleting the security group;
        # AWS will reject deletion while the instance still uses it.
        "${aws_cli[@]}" ec2 terminate-instances --instance-ids "${INSTANCE_ID}" >/dev/null
        "${aws_cli[@]}" ec2 wait instance-terminated --instance-ids "${INSTANCE_ID}"
    else
        log "Instance ${INSTANCE_ID} is already absent"
    fi
    if "${aws_cli[@]}" ec2 describe-security-groups --group-ids "${SECURITY_GROUP_ID}" >/dev/null 2>&1; then
        group_owner="$("${aws_cli[@]}" ec2 describe-security-groups --group-ids "${SECURITY_GROUP_ID}" \
            --query "SecurityGroups[0].Tags[?Key=='ManagedBy'].Value | [0]" --output text)"
        [[ "${group_owner}" == "${EXPECTED_MANAGED_BY}" ]] || \
            fail "Recorded security group does not have the expected ownership tag"
        log "Deleting security group ${SECURITY_GROUP_ID}"
        for attempt in $(seq 1 12); do
            if "${aws_cli[@]}" ec2 delete-security-group --group-id "${SECURITY_GROUP_ID}" 2>/dev/null; then
                break
            fi
            [[ "${attempt}" -lt 12 ]] || fail "Could not delete security group ${SECURITY_GROUP_ID}"
            sleep 5
        done
    else
        log "Security group ${SECURITY_GROUP_ID} is already absent"
    fi
    # Deleting an EC2 key pair does not delete the local .pem file unless the
    # caller explicitly supplies --delete-key.
    log "Deleting key pair ${KEY_NAME}"
    "${aws_cli[@]}" ec2 delete-key-pair --key-name "${KEY_NAME}" 2>/dev/null || true
    if [[ "${DELETE_LOCAL_KEY}" -eq 1 ]]; then
        rm -f -- "${KEY_PATH}"
    fi
    rm -f -- "${STATE_FILE}"
    log "Destroy complete"
    exit 0
fi

# **************************************************************************************************************************
# **************************************************************************************************************************
# **************************************************************************************************************************
# **************************************************************************************************************************
# **************************************************************************************************************************
# Everything below this point is used only by deploy.
# Check local tools and the secrets/configuration file before creating AWS
# resources, so an invalid deployment fails as early as possible.
require_command ssh
require_command scp
require_command tar
[[ -f "${ENV_FILE}" ]] || fail "Environment file not found: ${ENV_FILE}"
[[ -f "${SCRIPT_DIR}/manage.py" ]] || fail "Run this script from the project checkout"

required_env=(
    SECRET_KEY
    CORS_ALLOWED_ORIGINS
    GOOGLE_CLIENT_ID
    GOOGLE_CLIENT_SECRET
    GOOGLE_REDIRECT_URI
    POSTGRES_PASSWORD
)
for variable in "${required_env[@]}"; do
    # Do not send a deployment to AWS when a required setting is blank.
    if ! grep -Eq "^${variable}=[^[:space:]]" "${ENV_FILE}"; then
        fail "${variable} must be set in ${ENV_FILE}"
    fi
done

# The EC2 private key is created atomically. An existing AWS key without its local
# private key cannot be recovered, so fail instead of creating a replacement.
mkdir -p -- "$(dirname -- "${KEY_PATH}")"
if [[ ! -f "${KEY_PATH}" ]]; then
    # AWS returns the private key only once. Refuse to create a same-named key
    # when its local copy is missing, because that would make SSH impossible.
    key_exists="$("${aws_cli[@]}" ec2 describe-key-pairs --key-names "${KEY_NAME}" \
        --query 'KeyPairs[0].KeyName' --output text 2>/dev/null || true)"
    resource_exists "${key_exists}" && \
        fail "AWS key pair ${KEY_NAME} exists but ${KEY_PATH} is missing"
    log "Creating EC2 key pair ${KEY_NAME}"
    key_tmp="$(mktemp "${KEY_PATH}.XXXXXX")"
    "${aws_cli[@]}" ec2 create-key-pair \
        --key-name "${KEY_NAME}" \
        --query KeyMaterial \
        --output text >"${key_tmp}"
    chmod 600 "${key_tmp}"
    mv -- "${key_tmp}" "${KEY_PATH}"
else
    # A zero-byte key usually means a previous download was interrupted.
    [[ -s "${KEY_PATH}" ]] || fail "Private key is empty: ${KEY_PATH}"
    key_exists="$("${aws_cli[@]}" ec2 describe-key-pairs --key-names "${KEY_NAME}" \
        --query 'KeyPairs[0].KeyName' --output text 2>/dev/null || true)"
    resource_exists "${key_exists}" || fail "AWS key pair ${KEY_NAME} does not exist"
    log "Using existing private key ${KEY_PATH}"
fi

# Use the account's default VPC and one default public subnet to keep the
# showcase deployment inexpensive.
vpc_id="$("${aws_cli[@]}" ec2 describe-vpcs \
    --filters Name=isDefault,Values=true \
    --query 'Vpcs[0].VpcId' --output text)"
[[ "${vpc_id}" != "None" && -n "${vpc_id}" ]] || fail "No default VPC exists in ${REGION}"

# Select one default public subnet so the instance receives an internet route
# without creating a new VPC or paid networking components.
subnet_id="$("${aws_cli[@]}" ec2 describe-subnets \
    --filters "Name=vpc-id,Values=${vpc_id}" Name=default-for-az,Values=true \
    --query 'Subnets[0].SubnetId' --output text)"
[[ "${subnet_id}" != "None" && -n "${subnet_id}" ]] || fail "No default subnet exists in ${REGION}"

security_group_matches="$("${aws_cli[@]}" ec2 describe-security-groups \
    --filters "Name=vpc-id,Values=${vpc_id}" \
              "Name=tag:ManagedBy,Values=${EXPECTED_MANAGED_BY}" \
              "Name=tag:DeploymentId,Values=${INSTANCE_NAME}" \
    --query 'SecurityGroups[].GroupId' --output text)"
if [[ "$(wc -w <<<"${security_group_matches}")" -gt 1 ]]; then
    # Ambiguity is safer than silently deploying to the wrong security group.
    fail "More than one managed security group matches deployment ${INSTANCE_NAME}"
fi
security_group_id="${security_group_matches}"
if [[ "${security_group_id}" == "None" || -z "${security_group_id}" ]]; then
    # This compatibility lookup adopts resources made by an older version of
    # the script, then tags them so future runs can identify them safely.
    old_security_group_id="$("${aws_cli[@]}" ec2 describe-security-groups \
        --filters "Name=vpc-id,Values=${vpc_id}" "Name=group-name,Values=${PROJECT_NAME}-showcase" \
        --query 'SecurityGroups[0].GroupId' --output text)"
    if resource_exists "${old_security_group_id}"; then
        security_group_id="${old_security_group_id}"
        tag_resource "${security_group_id}"
    fi
fi
if [[ "${security_group_id}" == "None" || -z "${security_group_id}" ]]; then
    # The group starts with no access rules; ensure_ingress adds only the two
    # ports required by this showcase.
    log "Creating security group"
    security_group_id="$("${aws_cli[@]}" ec2 create-security-group \
        --group-name "${PROJECT_NAME}-showcase" \
        --description "Dragonfly showcase HTTP and SSH access" \
        --vpc-id "${vpc_id}" \
        --query GroupId --output text)"
    tag_resource "${security_group_id}"
fi
write_state

# Ensure the public HTTP and SSH rules exist. The helper also tolerates a
# duplicate-rule race between its read and authorize operations.
ensure_ingress() {
    # Check the existing CIDR first so a normal rerun does not request a
    # duplicate rule from AWS.
    local port="$1"
    local existing
    existing="$("${aws_cli[@]}" ec2 describe-security-groups \
        --group-ids "${security_group_id}" \
        --query "SecurityGroups[0].IpPermissions[?FromPort==\`${port}\` && ToPort==\`${port}\` && IpProtocol=='tcp'].IpRanges[].CidrIp" \
        --output text)"
    if grep -Fxq "0.0.0.0/0" <<<"${existing}"; then
        log "Security-group rule tcp/${port} from 0.0.0.0/0 already exists"
        return 0
    fi

    if ! output="$("${aws_cli[@]}" ec2 authorize-security-group-ingress \
        --group-id "${security_group_id}" --protocol tcp --port "${port}" --cidr 0.0.0.0/0 2>&1)"; then
        # Two script processes could pass the check at the same time. AWS may
        # reject one as a duplicate; that result is safe to continue past.
        if grep -Fq "InvalidPermission.Duplicate" <<<"${output}"; then
            log "Security-group rule tcp/${port} was added concurrently; continuing"
            return 0
        fi
        printf '%s\n' "${output}" >&2
        return 1
    fi
}

ensure_ingress 80
ensure_ingress 22

# Find the managed instance, adopt a legacy named instance if necessary, or
# launch a new Ubuntu instance.
instance_id="$("${aws_cli[@]}" ec2 describe-instances \
    --filters "Name=tag:ManagedBy,Values=${EXPECTED_MANAGED_BY}" \
              "Name=tag:DeploymentId,Values=${INSTANCE_NAME}" \
              "Name=instance-state-name,Values=pending,running,stopping,stopped" \
    --query 'Reservations[].Instances[].InstanceId' --output text)"

if [[ "$(wc -w <<<"${instance_id}")" -gt 1 ]]; then
    # Never guess when more than one managed instance matches this deployment.
    fail "More than one managed instance matches deployment ${INSTANCE_NAME}"
fi

if [[ "${instance_id}" == "None" || -z "${instance_id}" ]]; then
    # Try the old Name-only lookup once so an instance created by the previous
    # script version can be adopted instead of duplicated.
    old_instance_id="$("${aws_cli[@]}" ec2 describe-instances \
        --filters "Name=tag:Name,Values=${INSTANCE_NAME}" \
                  "Name=instance-state-name,Values=pending,running,stopping,stopped" \
        --query 'Reservations[].Instances[].InstanceId' --output text)"
    if [[ "$(wc -w <<<"${old_instance_id}")" -gt 1 ]]; then
        fail "More than one instance matches legacy name ${INSTANCE_NAME}"
    fi
    if resource_exists "${old_instance_id}"; then
        instance_id="${old_instance_id}"
        tag_resource "${instance_id}"
    fi
fi

if [[ "${instance_id}" == "None" || -z "${instance_id}" ]]; then
    # Find the newest official Ubuntu 24.04 x86_64 AMI in this region. The
    # owner ID belongs to Canonical, not to this project.
    ami_id="$("${aws_cli[@]}" ec2 describe-images \
        --owners 099720109477 \
        --filters \
            Name=name,Values='ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*' \
            Name=state,Values=available \
            Name=root-device-type,Values=ebs \
            Name=virtualization-type,Values=hvm \
            Name=architecture,Values=x86_64 \
        --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' \
        --output text)"
    [[ "${ami_id}" != "None" && -n "${ami_id}" ]] || \
        fail "No Ubuntu 24.04 x86_64 AMI was found in ${REGION}"
    log "Launching ${INSTANCE_TYPE} instance"
    # Git Bash rewrites POSIX-looking arguments such as /dev/sda1 into Windows
    # paths unless path conversion is disabled for this AWS CLI invocation.
    # Git Bash path conversion is disabled because /dev/sda1 is a Linux device
    # name. Without this, Git Bash changes it into a Windows path.
    instance_id="$(MSYS_NO_PATHCONV=1 "${aws_cli[@]}" ec2 run-instances \
        --image-id "${ami_id}" \
        --instance-type "${INSTANCE_TYPE}" \
        --key-name "${KEY_NAME}" \
        --security-group-ids "${security_group_id}" \
        --subnet-id "${subnet_id}" \
        --block-device-mappings 'DeviceName=/dev/sda1,Ebs={VolumeSize=16,VolumeType=gp3,DeleteOnTermination=true}' \
        --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=${INSTANCE_NAME}},{Key=Project,Value=${PROJECT_NAME}},{Key=ManagedBy,Value=${EXPECTED_MANAGED_BY}},{Key=DeploymentId,Value=${INSTANCE_NAME}}]" \
        --query 'Instances[0].InstanceId' --output text)"
else
    # A stopped instance can be reused; this avoids paying for a second server
    # and preserves the PostgreSQL Docker volume.
    state="$("${aws_cli[@]}" ec2 describe-instances --instance-ids "${instance_id}" \
        --query 'Reservations[0].Instances[0].State.Name' --output text)"
    if [[ "${state}" == "stopped" ]]; then
        log "Starting existing instance ${instance_id}"
        "${aws_cli[@]}" ec2 start-instances --instance-ids "${instance_id}" >/dev/null
    fi
fi
write_state

# Wait for the instance and SSH service before transferring the application.
# The public IP is ephemeral because this low-cost deployment does not reserve
# an Elastic IP address.
"${aws_cli[@]}" ec2 wait instance-running --instance-ids "${instance_id}"
public_ip="$("${aws_cli[@]}" ec2 describe-instances --instance-ids "${instance_id}" \
    --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)"
[[ "${public_ip}" != "None" && -n "${public_ip}" ]] || fail "Instance has no public IP"

log "Waiting for SSH on ${public_ip}"
# A running EC2 instance may still need a few minutes before cloud-init and
# sshd are ready to accept connections.
for attempt in $(seq 1 60); do
    if ssh "${ssh_options[@]}" -i "${KEY_PATH}" "${SSH_USER}@${public_ip}" true 2>/dev/null; then
        break
    fi
    [[ "${attempt}" -lt 60 ]] || fail "SSH did not become available"
    sleep 5
done

WORK_DIR="$(mktemp -d)"
archive="${WORK_DIR}/dragonfly.tar.gz"
remote_dir="/opt/${PROJECT_NAME}"
log "Packaging current checkout"
# Exclude local credentials, generated state, and development dependencies.
# This archive is uploaded to EC2; excluding these files prevents local secrets
# and unnecessary development files from entering the server image.
tar -czf "${archive}" \
    --exclude='./.git' \
    --exclude='./.venv' \
    --exclude='./frontend/node_modules' \
    --exclude='./node_modules' \
    --exclude='./.env' \
    --exclude='./.env.aws' \
    --exclude='./.env.*' \
    --exclude='./*.deploy.env' \
    --exclude='./.aws' \
    --exclude='./db.sqlite3' \
    -C "${SCRIPT_DIR}" .

log "Installing Docker and uploading application"
# Docker is installed on EC2; it is not required on the developer machine.
# The environment file is uploaded separately because it is intentionally
# excluded from the source archive.
ssh "${ssh_options[@]}" -i "${KEY_PATH}" "${SSH_USER}@${public_ip}" \
    "sudo apt-get update -qq && sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq docker.io docker-compose-v2 && sudo systemctl enable --now docker && sudo mkdir -p '${remote_dir}' && sudo chown '${SSH_USER}:${SSH_USER}' '${remote_dir}'"
scp "${ssh_options[@]}" -i "${KEY_PATH}" "${archive}" "${SSH_USER}@${public_ip}:/tmp/dragonfly.tar.gz"
scp "${ssh_options[@]}" -i "${KEY_PATH}" "${ENV_FILE}" "${SSH_USER}@${public_ip}:${remote_dir}/.env.source"

ssh "${ssh_options[@]}" -i "${KEY_PATH}" "${SSH_USER}@${public_ip}" "REMOTE_DIR='${remote_dir}' PUBLIC_IP='${public_ip}' bash -s" <<'REMOTE_SCRIPT'
set -Eeuo pipefail
cd "${REMOTE_DIR}"
# The following block runs on the Ubuntu EC2 machine, not on the developer's
# Windows computer.

# Extract into a staging directory so a failed archive transfer does not
# replace the current application with a partial checkout.
rm -rf app.new
mkdir app.new
tar -xzf /tmp/dragonfly.tar.gz -C app.new
rm -rf app
mv app.new app
cp .env.source app/.env
cp app/.env .env
chmod 600 .env app/.env
rm -f .env.source
# Git Bash uploads Windows CRLF files; remove carriage returns before sourcing.
sed -i 's/\r$//' .env app/.env
set -a
# The deployment env is a local, operator-controlled file supplied to this script.
# Loading it makes its values available to Docker Compose interpolation.
. app/.env
set +a
# The custom hostname is preferred for browser traffic. The EC2 IP is also
# retained so direct HTTP testing continues to work.
backend_hostname="${BACKEND_HOSTNAME:-${PUBLIC_IP}}"
allowed_hosts="${ALLOWED_HOSTS:-},${backend_hostname},${PUBLIC_IP}"
{
    grep -vE '^(DJANGO_ENV|WEBSITE_HOSTNAME|ALLOWED_HOSTS|DATABASE_URL)=' app/.env || true
    printf 'DJANGO_ENV=production\n'
    printf 'WEBSITE_HOSTNAME=%s\n' "${backend_hostname}"
    printf 'ALLOWED_HOSTS=%s\n' "${allowed_hosts}"
    printf 'DATABASE_URL=postgresql://${POSTGRES_USER:-dragonfly}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB:-dragonfly}?sslmode=disable\n'
} > app/.env.generated
mv app/.env.generated app/.env
chmod 600 app/.env

# Rebuild the web/seed image and recreate the stack while retaining the
# postgres_data volume.
# `down` removes containers, not the named database volume, so existing demo
# data survives a normal redeployment.
# The Compose file lives under app/tools, whose directory name would otherwise
# become the project name and leave the previous dragonfly stack running.
sudo docker compose --project-name tools --env-file app/.env -f app/tools/docker-compose.aws.yml down --remove-orphans || true
sudo docker compose --project-name dragonfly --env-file app/.env -f app/tools/docker-compose.aws.yml down --remove-orphans || true
sudo docker compose --project-name dragonfly --env-file app/.env -f app/tools/docker-compose.aws.yml up -d --build
# The source archive is no longer needed after Docker has built the images.
rm -f /tmp/dragonfly.tar.gz
REMOTE_SCRIPT

# These URLs are printed for quick testing after deployment.
log "Deployment complete"
printf 'HTTP URL:     http://%s/\n' "${public_ip}"
if grep -Eq '^BACKEND_HOSTNAME=[^[:space:]]' "${ENV_FILE}"; then
    backend_hostname="$(grep '^BACKEND_HOSTNAME=' "${ENV_FILE}" | tail -n 1 | cut -d '=' -f 2- | tr -d '\r')"
    printf 'Backend URL:  https://%s/\n' "${backend_hostname}"
    printf 'Health check: https://%s/api/health/\n' "${backend_hostname}"
else
    printf 'Health check: http://%s/api/health/\n' "${public_ip}"
fi
printf 'SSH command:  ssh -i "%s" %s@%s\n' "${KEY_PATH}" "${SSH_USER}" "${public_ip}"
printf 'Instance ID:  %s\n' "${instance_id}"
