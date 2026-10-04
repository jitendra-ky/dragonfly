# AWS Showcase Deployment

`zcommand.sh` deploys the current Dragonfly checkout to a low-cost AWS
showcase environment. It creates one EC2 instance in the default VPC and runs
the Django ASGI application and PostgreSQL with Docker Compose.

This deployment is intended for demonstrations and recruiter reviews. It is
not designed for production users or important data.

## Architecture and cost choices

The script creates or reuses:

- One `t3.micro` EC2 instance
- One security group
- One EC2 key pair
- One 16 GiB gp3 root volume
- One Docker PostgreSQL volume on the EC2 instance

The default region is `ap-south-1` (Mumbai). The deployment does not create
RDS, ECS, an Application Load Balancer, Route 53 records, ACM certificates,
autoscaling, or backups.

The application is served over HTTP at the instance's public IP. Daphne is
used so Django WebSocket routes continue to work.

## Prerequisites

Run the script from Git Bash on Windows, or from a Linux/macOS shell. Install
and verify:

- AWS CLI
- An authenticated AWS CLI default profile
- Bash
- OpenSSH (`ssh` and `scp`)
- GNU tar

Check AWS access before deploying:

```bash
aws sts get-caller-identity
```

The AWS identity needs permissions for EC2 image lookup and the described
key-pair, security-group, instance, and tagging operations. The
script uses the default AWS CLI profile. It does not accept credentials in the
deployment environment file.

## Configure deployment variables

Create a private deployment environment file:

```bash
cp .env.aws.example .env.aws
```

Edit `.env.aws` and replace every placeholder:

```dotenv
DJANGO_ENV=production
SECRET_KEY=generate-a-long-random-value
CORS_ALLOWED_ORIGINS=https://your-vercel-project.vercel.app
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback
BACKEND_HOSTNAME=dragonfly-backend.jitendra.xyz
ALLOWED_HOSTS=your-vercel-project.vercel.app

POSTGRES_USER=dragonfly
POSTGRES_PASSWORD=generate-a-random-password
POSTGRES_DB=dragonfly
```

The script requires these values:

- `SECRET_KEY`
- `CORS_ALLOWED_ORIGINS`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_REDIRECT_URI`
- `POSTGRES_PASSWORD`
- `BACKEND_HOSTNAME` is optional; set it to the Cloudflare hostname when using
  the custom domain.

`.env.aws` is ignored by Git. Do not commit it or paste its contents into
logs, issues, or pull requests.

For this deployment, use letters and numbers in `POSTGRES_PASSWORD` so the
generated PostgreSQL URL does not require URL escaping.

## Deploy

From the repository root:

```bash
bash ./zcommand.sh deploy
```

Running the script without an action is equivalent:

```bash
bash ./zcommand.sh
```

The script will:

1. Validate local tools, environment variables, and AWS credentials.
2. Create or reuse the EC2 key pair.
3. Find the default VPC and a default public subnet.
4. Create or reuse the tagged security group.
5. Ensure HTTP port 80 and SSH port 22 are open.
6. Create or reuse the tagged EC2 instance.
7. Save resource identifiers locally.
8. Wait for SSH to become available.
9. Package the current checkout without local secrets, virtual environments,
   node modules, or deployment state.
10. Install Docker on EC2.
11. Upload the application and environment file.
12. Build and start Django/Daphne and PostgreSQL.
13. Run migrations and the showcase seed data.
14. Collect static files and start Django/Daphne.

At completion, it prints the application URL, health-check URL, SSH command,
and EC2 instance ID.

Example output:

```text
Backend URL:  https://dragonfly-backend.jitendra.xyz/
Health check: https://dragonfly-backend.jitendra.xyz/api/health/
SSH command:  ssh -i ".../dragonfly-showcase.pem" ubuntu@203.0.113.10
Instance ID:  i-0123456789abcdef0
```

## Optional deployment options

Use a different region:

```bash
bash ./zcommand.sh deploy --region ap-south-1
```

Use a larger instance:

```bash
bash ./zcommand.sh deploy --instance-type t3.small
```

Use a different environment file:

```bash
bash ./zcommand.sh deploy --env-file .env.showcase
```

Use a custom key-pair name and local private-key path:

```bash
bash ./zcommand.sh deploy \
  --key-name dragonfly-demo \
  --key-path "$HOME/.ssh/dragonfly-demo.pem"
```

Use a custom state-file path:

```bash
bash ./zcommand.sh deploy \
  --state-file "$HOME/.dragonfly/showcase.state"
```

## Persistent deployment state

The default state file is:

```text
.aws/dragonfly-showcase/state.env
```

It contains resource identifiers and configuration, including:

- AWS region
- EC2 instance ID
- Security-group ID
- VPC and subnet IDs
- EC2 key-pair name
- Local private-key path
- Deployment ownership markers

It does not contain application secrets. The file is created with mode `600`
and `.aws/` is ignored by Git.

Keep this state file if you plan to run `status` or `destroy`. If it is
deleted, the script cannot safely perform those actions by exact resource ID.

## Check status

```bash
bash ./zcommand.sh status
```

This reads the state file and reports the instance status, instance ID,
security-group ID, and key-pair name. It does not create or modify AWS
resources.

## Retry after a failure

The deployment is designed to be rerun after an interrupted operation:

```bash
bash ./zcommand.sh deploy
```

The script uses ownership tags:

```text
Project=dragonfly
ManagedBy=dragonfly-zcommand
DeploymentId=dragonfly-showcase
Name=dragonfly-showcase
```

It uses these tags to find the exact managed instance and security group. If
multiple matching resources are found, it stops instead of choosing one
arbitrarily.

Typical recovery actions:

```bash
# Inspect the last known deployment
bash ./zcommand.sh status

# Retry the deployment
bash ./zcommand.sh deploy
```

If AWS created a key pair but the local private key was lost, the script stops
and asks you to choose a new key-pair name. AWS does not allow the private key
material to be downloaded again.

Do not run two deploy commands concurrently for the same state file.

## Destroy the showcase

To remove the exact deployment recorded in the state file:

```bash
bash ./zcommand.sh destroy
```

The destroy action:

1. Loads the saved resource IDs.
2. Verifies the instance ownership tags.
3. Terminates the recorded EC2 instance.
4. Waits for termination.
5. Verifies and deletes the recorded security group.
6. Deletes the recorded EC2 key pair.
7. Deletes the local state file.
8. Keeps the local private key by default.

To also delete the local private key:

```bash
bash ./zcommand.sh destroy --delete-key
```

The default behavior is to keep the private key:

```bash
bash ./zcommand.sh destroy --keep-key
```

The script does not delete resources merely because they have a similar name.
It requires the saved state file and ownership checks. Do not use a shared EC2
key pair name for this showcase because `destroy` removes the recorded AWS key
pair.

## SSH and logs

Connect to the instance using the command printed by the deployment:

```bash
ssh -i "$HOME/.ssh/dragonfly-showcase.pem" ubuntu@PUBLIC_IP
```

Inspect the containers:

```bash
cd /opt/dragonfly
sudo docker compose --project-name dragonfly --env-file app/.env -f app/tools/docker-compose.aws.yml ps
sudo docker compose --project-name dragonfly --env-file app/.env -f app/tools/docker-compose.aws.yml logs --tail=100 web
sudo docker compose --project-name dragonfly --env-file app/.env -f app/tools/docker-compose.aws.yml logs --tail=100 db
```

Restart the stack without reprovisioning EC2:

```bash
cd /opt/dragonfly
sudo docker compose --project-name dragonfly --env-file app/.env -f app/tools/docker-compose.aws.yml up -d
```

The application environment files are stored on the instance with restrictive
permissions because Docker needs them. If the remote deployment fails before
cleanup completes, `/opt/dragonfly/.env.source` may remain and should be
removed manually after confirming that `/opt/dragonfly/app/.env` is present.

## Seed data

Each deployment runs [seed.py](../seed.py) in a one-shot Docker Compose
service after PostgreSQL becomes healthy. It creates the showcase users and
recreates the seeded messages:

```text
alice, bob, carol, dave, eve
```

All seeded users use the password:

```text
password123
```

The seeder uses `get_or_create` for users and removes/recreates messages
between the seeded users, so rerunning deployment does not duplicate the
showcase messages. It is intended only for this demo deployment. Do not use
this seed data or password for a real environment.

## Security and data warnings

This showcase configuration intentionally has important limitations:

- SSH port 22 is open to `0.0.0.0/0`.
- HTTP is used instead of HTTPS.
- PostgreSQL runs on the same EC2 instance as the application.
- PostgreSQL is not exposed directly to the internet.
- No automated database backups are created.
- No high availability or autoscaling is configured.
- Environment secrets are stored on the EC2 instance in plaintext files with
  mode `600`.
- Terminating the EC2 instance destroys the PostgreSQL data volume because
  the root volume is configured for deletion on termination.

Do not use this setup for real users or important data.
