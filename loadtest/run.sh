#!/bin/sh
set -eu

COMPOSE="docker compose -f docker-compose.loadtest.yml"
mkdir -p loadtest/results

cleanup() {
  $COMPOSE down
}
trap cleanup EXIT

$COMPOSE up -d --build --wait db redis

seed_attempt=1
until $COMPOSE run --rm seed; do
  if [ "$seed_attempt" -ge 5 ]; then
    echo "Seed failed after ${seed_attempt} attempts." >&2
    exit 1
  fi
  seed_attempt=$((seed_attempt + 1))
  sleep 3
done

$COMPOSE up -d web

until curl --fail --silent http://localhost:8000/api/health/ >/dev/null; do
  sleep 2
done

$COMPOSE run --rm k6 run \
  --summary-export=/results/smoke.json /scripts/smoke.js

set +e
$COMPOSE run --rm k6 run \
  --summary-export=/results/load.json /scripts/load.js
load_status=$?
set -e

$COMPOSE ps
$COMPOSE stats --no-stream --format \
  'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}' \
  > loadtest/results/docker-stats.txt

exit "$load_status"
