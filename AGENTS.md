# Project Overview

OrderFlow is a teaching e-commerce platform: registration, catalog browsing,
orders, simulated payments, and payment-event analytics. This repository alone
is the source of project context; source code takes precedence over these docs.

# Technology Stack

- Backend: Python **3.14** (`python:3.14-slim`), FastAPI, Pydantic settings, pip.
- Dependencies: each service's `requirements.txt`; some pins, no Python lockfile.
- Persistence: PostgreSQL 16, SQLAlchemy 2; psycopg2 in auth/catalog/orders,
  asyncpg in payments. Analytics uses async PyMongo and MongoDB 8.
- Messaging: aio-pika / RabbitMQ 3.13, aiokafka / Kafka 4.3.1 (KRaft).
- Frontend: React, TypeScript, Vite, oxlint, npm lockfile, Node 22 Docker build.
- Deployment: Docker Compose and Nginx 1.27.

# Repository Structure

- `auth-service/`, `catalog-service/`, `order-service/`, `payment-service/`,
  `api-gateway/`, `analytic-service/`: independent `app/` packages, Dockerfiles,
  and requirements. Run Python imports from the relevant service directory;
  do not combine their identically named `app` packages on one import path.
- `frontend/`: UI, `package.json`, `package-lock.json`, TypeScript/Vite config.
- `infra/`: core and analytics Compose files, env examples, Nginx routing.
- `README.md`: local setup, operations, and API routes.
- `create_product_script.txt`: Bash demo-product creation against running catalog.
- `server_install_utils.txt`: host provisioning commands, not a test/setup runner.
- No shared Python library, tests directory, CI, or migration tooling is present.

# Services

| Directory | Responsibility |
| --- | --- |
| `api-gateway` | `/api` routing, JWT validation, order ownership check |
| `auth-service` | Users, Argon2 passwords, JWT registration/login |
| `catalog-service` | Products and prices |
| `order-service` | Order/items persistence, catalog/payment HTTP calls, payment-result consumer |
| `payment-service` | Simulated payment, RabbitMQ and Kafka event publication |
| `analytic-service` | Kafka payment events to MongoDB and `/events` |
| `frontend` | Shop, authentication, cart, order-status polling |

# Development Rules

1. Read this file first; read `ARCHITECTURE.md` only when relevant.
2. Inspect recent commits, the affected service/files, and related tests before
   edits. Expand only if the map is outdated or insufficient. Do not rediscover
   the entire repository every scheduled run.
3. Preserve service boundaries, API responses, auth/ownership checks, money
   representation, transaction boundaries, and message contracts.
4. Use pip with the affected service's existing requirements in a separate venv.
   Do not migrate managers, upgrade dependencies, or add unrelated tooling.
5. Do not load local/production env files for automation. Use fresh cloud-only
   test configuration derived from `infra/.env.*.example`; never print secrets.
6. Setup does not authorize running a daily maintenance task immediately.

# Testing

There are currently **no unit/integration suites, pytest configuration, Python
lint/format/type-check commands, or CI workflows**. Do not claim they passed or
install pytest/ruff/mypy/black merely to satisfy an automation checklist.

Existing frontend commands (from `frontend/`):

```bash
npm ci
npm run lint
npm run build
npm run dev
```

`build` runs `tsc -b && vite build`; `lint` runs oxlint. Neither is a backend test.

Dependency installation per service, using Python 3.14:

```bash
python3.14 -m venv <venv-outside-repository>
<venv-outside-repository>/bin/python -m pip install -r <service>/requirements.txt
<venv-outside-repository>/bin/python -m pip check
```

Safe supplemental syntax check from the repository root (does not import apps,
connect to services, or prove runtime correctness):

```bash
python3.14 -c "import ast, pathlib; dirs=['auth-service','catalog-service','order-service','payment-service','api-gateway','analytic-service']; files=[p for d in dirs for p in pathlib.Path(d, 'app').rglob('*.py')]; [ast.parse(p.read_text(encoding='utf-8'), filename=str(p)) for p in files]; print(f'Parsed {len(files)} Python files')"
```

Existing Compose validation, from `infra/`, using disposable test env files:

```bash
docker compose --env-file .env.core -f docker-compose.core.yml config --quiet
docker compose --env-file .env.analytic -f docker-compose.analytic.yml config --quiet
```

Compose validation does not start containers or prove integration behavior.
The README's `up -d --build`, `ps`, `logs`, and `down` commands are development
operations, not an automated integration suite. There is no dedicated test
Compose file, testcontainers, or fixture infrastructure. Only run the development
stack in an isolated disposable cloud Docker environment with synthetic data;
both Compose files share project name `orderflow` and its default network.
Never use production endpoints/credentials/data or remove existing volumes.

Before a maintenance commit, demonstrate the affected behavior with an isolated
regression check and run applicable existing checks. If adequate validation needs
unavailable services or tooling, choose another safe task or make no change.
Syntax/Compose checks alone are insufficient to validate a behavior change.

# Database Rules

- One PostgreSQL database and independent declarative metadata per auth,
  catalog, order, and payment service. No cross-service SQL joins or sessions.
- Tables are created by lifespan `Base.metadata.create_all`; no Alembic/history.
- Auth/catalog/order sessions are synchronous and closed by `get_db` finally.
  Payment sessions are async with `expire_on_commit=False`, `autoflush=False`.
- Preserve commit/flush/rollback, session/connection ownership, relationships,
  and query behavior. No destructive DDL, significant schema changes, unrelated
  migrations, production writes, or new N+1 queries in unattended maintenance.

# Kafka Rules

- Payments publish JSON bytes to `payment-events` with `send_and_wait`.
- Analytics consumes that topic into MongoDB; no explicit consumer group,
  record key, application offset commit, deduplication, or retry policy is set.
- Preserve topic/config names, event fields, serialization, ordering and current
  semantics. Do not invent stronger delivery guarantees or casually change them.

# RabbitMQ Rules

- Exchange `payment.events`, queue `payment.results`, key `payment.succeeded`.
- Payment publishes JSON; order uses `message.process()` and commits status
  `paid` within that context. Declarations use aio-pika defaults, without explicit
  durability, persistent messages, retry/DLQ, or deduplication configuration.
- Preserve bindings, schema and ack/reject behavior; avoid loss, duplicates,
  infinite retries, and unrequested delivery-guarantee changes.

# Git Rules

- Repository: `https://github.com/gitchady/orderflow-platform.git`.
- Default branch verified during setup: `main`; recheck remote HEAD each run.
- Each scheduled run starts from the latest fetched default branch in an
  isolated cloud checkout. Stop if unexpected dirty files are present.
- Exactly one useful, small, low-risk task per run (normally 1-3 production files
  plus related checks/docs). Prefer no change to churn; no empty commit.
- Tests/checks and full diff review before one commit. Stage explicit paths only.
- Fetch again before pushing; integrate straightforward remote changes and
  revalidate, or stop on conflict. Never overwrite concurrent work.
- Push directly to the default branch; **no PR, no force push, no protection
  bypass**. Stop and report the exact rejection if GitHub blocks direct push.
- Verify the remote SHA after publication and report problem, change, safety,
  paths, checks/results, docs update, commit message/SHA, and push outcome.
- Do not commit env files, credentials, logs, databases, caches, build output,
  IDE state, or unrelated user work. Respect human reverts and recent history.

# Documentation Maintenance

If a code change makes information in `AGENTS.md` or `ARCHITECTURE.md` outdated,
update the relevant documentation in the **same commit**. This includes changed
services, responsibilities, paths, databases, message contracts/topology,
dependency management, test/setup commands, or architectural conventions.
Do not update docs for minor implementation changes that leave them accurate.
