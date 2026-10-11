# Dragonfly load test

This setup runs the production settings with Daphne, PostgreSQL, Redis-backed
Channels, and the seeded application data. It only targets local Docker
containers and publishes the app at `http://localhost:8000`.

## Run end to end

From the repository root:

```sh
sh loadtest/run.sh
```

The command builds the app image, migrates and seeds 250 users plus 6,250
messages, runs the 30-second smoke test first, then the staged load test
(ramping to 30 VUs, holding for two minutes, and ramping down). Results are
written to `loadtest/results/smoke.json`, `loadtest/results/load.json`, and
`loadtest/results/docker-stats.txt`.

The seeded login is `loadtest-0000@example.com` /
`LoadtestPassword123!`. To rerun from a clean database:

```sh
docker compose -f docker-compose.loadtest.yml down -v
sh loadtest/run.sh
```

The k6 thresholds are p95 request duration below 500 ms, HTTP error rate below
1%, and check success above 99%.
