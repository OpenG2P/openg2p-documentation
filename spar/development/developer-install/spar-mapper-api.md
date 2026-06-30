---
description: >-
  This guide walks through setting up the SPAR Mapper Partner API for local
  development. It covers the full stack: shared libraries, database, application
  server, and optional Docker-based setup.
---

# SPAR Mapper Partner API

### Overview

The SPAR (Social Protection Account Registry) Mapper Partner API is a FastAPI service that implements the G2P Connect Mapper specification. It enables linking and resolving a beneficiary's ID (e.g., national ID) to a Financial Address (e.g., mobile wallet or bank account number).

**Core capabilities:**

* Link an ID to a Financial Address
* Resolve an ID to its linked Financial Address
* Update an existing ID–FA mapping
* Unlink an ID from a Financial Address

All endpoints require a signed JWT from a trusted issuer (e.g., Keycloak).

***

### Architecture

This is a monorepo with four Python packages under `core/`:

| Package                           | Path                       | Role                                          |
| --------------------------------- | -------------------------- | --------------------------------------------- |
| `openg2p-spar-models`             | `core/models/`             | Shared SQLAlchemy models and Pydantic schemas |
| `openg2p-spar-mapper-core`        | `core/mapper-core/`        | Mapper business logic, services, helpers      |
| `openg2p-spar-mapper-partner-api` | `core/mapper-partner-api/` | FastAPI app exposing the Mapper endpoints     |
| `openg2p-spar-bene-portal-api`    | `core/bene-portal-api/`    | Beneficiary portal API (separate service)     |

The packages have this dependency chain:

```
openg2p-fastapi-common (external)
        ↓
openg2p-spar-models
        ↓
openg2p-spar-mapper-core
        ↓
openg2p-spar-mapper-partner-api
```

Install them in that order.

***

### Prerequisites

| Requirement | Version | Notes                                             |
| ----------- | ------- | ------------------------------------------------- |
| Python      | 3.11+   | 3.11 is tested in CI                              |
| PostgreSQL  | 15+     | Tested with pg 15 in CI                           |
| Git         | any     | Required for installing external deps from GitHub |
| pip         | 23+     | `pip install --upgrade pip` before starting       |
| virtualenv  | any     | Or use `python -m venv`                           |

**System packages (Debian/Ubuntu):**

```bash
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-dev python3-pip python3-venv \
    build-essential libpq-dev git postgresql postgresql-contrib
```

**macOS (Homebrew):**

```bash
brew install python@3.11 postgresql@15 git
brew services start postgresql@15
```

***

### Repository Setup

```bash
git clone https://github.com/OpenG2P/spar.git
cd spar
git checkout develop
```

The working directory for all commands below is the repo root (`spar/`) unless stated otherwise.

***

### Python Environment

Create and activate a virtual environment at the repo root:

```bash
python3.11 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

Upgrade pip and build tools before installing packages:

```bash
pip install --upgrade pip setuptools wheel
```

***

### Install Dependencies

Dependencies must be installed in the correct order because each package depends on the one before it.

#### External OpenG2P FastAPI Common Libraries

These are hosted in a separate GitHub repository. Pin to the same ref used in the Dockerfile (`v1.1.5`):

```bash
FASTAPI_COMMON_REF=v1.1.5

pip install \
  "git+https://github.com/openg2p/openg2p-fastapi-common@${FASTAPI_COMMON_REF}#subdirectory=openg2p-fastapi-auth-models" \
  "git+https://github.com/openg2p/openg2p-fastapi-common@${FASTAPI_COMMON_REF}#subdirectory=openg2p-fastapi-auth" \
  "git+https://github.com/openg2p/openg2p-fastapi-common@${FASTAPI_COMMON_REF}#subdirectory=openg2p-fastapi-partner-auth" \
  "git+https://github.com/openg2p/openg2p-fastapi-common@${FASTAPI_COMMON_REF}#subdirectory=openg2p-fastapi-common"
```

> **Note:** Installing `openg2p-fastapi-partner-auth` is required even though it is not listed in `pyproject.toml` directly — it is a runtime dependency for JWT validation.

#### Local SPAR Packages (editable installs)

Install in dependency order:

```bash
pip install -e core/models
pip install -e core/mapper-core
pip install -e core/mapper-partner-api
```

Editable installs (`-e`) mean any local code changes are immediately reflected without reinstalling.

#### Test Dependencies (optional, for running tests)

```bash
pip install -r core/test-requirements.txt
```

***

### Database Setup

#### Create Database and User

Connect to PostgreSQL and run:

```sql
-- Create a dedicated role
CREATE ROLE spar_user WITH LOGIN PASSWORD 'spar_password';

-- Create the database
CREATE DATABASE spardb OWNER spar_user;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE spardb TO spar_user;
```

Or as a one-liner using `psql`:

```bash
psql -U postgres -c "CREATE ROLE spar_user WITH LOGIN PASSWORD 'spar_password';"
psql -U postgres -c "CREATE DATABASE spardb OWNER spar_user;"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE spardb TO spar_user;"
```

#### Verify Connection

```bash
psql -U spar_user -d spardb -c "SELECT version();"
```

***

### Environment Configuration

The application reads configuration from environment variables (or a `.env` file in the working directory). All variables use the prefix `SPAR_MAPPER_PARTNER_API_`.

Create a `.env` file inside `core/mapper-partner-api/`:

```bash
cp core/mapper-partner-api/.env.example core/mapper-partner-api/.env
```

Edit the file with your local values:

```dotenv
# Server
SPAR_MAPPER_PARTNER_API_HOST=0.0.0.0
SPAR_MAPPER_PARTNER_API_PORT=8000
SPAR_MAPPER_PARTNER_API_NO_OF_WORKERS=1
SPAR_MAPPER_PARTNER_API_WORKER_TYPE=gunicorn

# API path prefix (used when behind a reverse proxy)
SPAR_MAPPER_PARTNER_API_OPENAPI_ROOT_PATH=/api/mapper

# Database
SPAR_MAPPER_PARTNER_API_DB_HOSTNAME=localhost
SPAR_MAPPER_PARTNER_API_DB_PORT=5432
SPAR_MAPPER_PARTNER_API_DB_USERNAME=spar_user
SPAR_MAPPER_PARTNER_API_DB_PASSWORD=spar_password
SPAR_MAPPER_PARTNER_API_DB_DBNAME=spardb

# JWT Authentication
# Replace with your Keycloak realm URL(s)
SPAR_MAPPER_PARTNER_API_DEFAULT_ISSUERS=["http://localhost:8080/realms/openg2p-beneficiary"]
SPAR_MAPPER_PARTNER_API_DEFAULT_JWKS_URLS=["http://localhost:8080/realms/openg2p-beneficiary/protocol/openid-connect/certs"]

# Partner signature verification (openg2p-fastapi-common). SPAR only VERIFIES —
# it never signs — so no signing key is configured.
SPAR_MAPPER_PARTNER_API_JWT_AUTH_ENABLED=true
SPAR_MAPPER_PARTNER_API_CRYPTO_BACKEND=local           # local | keymanager
SPAR_MAPPER_PARTNER_API_CRYPTO_ALLOWED_ALGORITHMS=RS256
# Seed-based onboarding: JSON list of partner public certs upserted into the
# partner_keys table at migrate-time (referenceId = PARTNER_<MNEMONIC>).
SPAR_MAPPER_PARTNER_API_CRYPTO_PARTNER_CERTS=[{"reference_id":"PARTNER_G2P_BRIDGE","public_key":"-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----\n"}]

# KeyManager — only used when CRYPTO_BACKEND=keymanager.
SPAR_MAPPER_PARTNER_API_KEYMANAGER_SIGN_APP_ID=SPAR
```

#### Configuration Reference

| Variable                                         | Default       | Description                       |
| ------------------------------------------------ | ------------- | --------------------------------- |
| `SPAR_MAPPER_PARTNER_API_HOST`                   | `0.0.0.0`     | Bind address                      |
| `SPAR_MAPPER_PARTNER_API_PORT`                   | `8000`        | Listen port                       |
| `SPAR_MAPPER_PARTNER_API_NO_OF_WORKERS`          | `1`           | Gunicorn worker count             |
| `SPAR_MAPPER_PARTNER_API_WORKER_TYPE`            | `gunicorn`    | Server type                       |
| `SPAR_MAPPER_PARTNER_API_OPENAPI_ROOT_PATH`      | `/api/mapper` | OpenAPI root path                 |
| `SPAR_MAPPER_PARTNER_API_DB_HOSTNAME`            | `localhost`   | PostgreSQL host                   |
| `SPAR_MAPPER_PARTNER_API_DB_PORT`                | `5432`        | PostgreSQL port                   |
| `SPAR_MAPPER_PARTNER_API_DB_USERNAME`            | `postgres`    | Database user                     |
| `SPAR_MAPPER_PARTNER_API_DB_PASSWORD`            | `password`    | Database password                 |
| `SPAR_MAPPER_PARTNER_API_DB_DBNAME`              | `spardb`      | Database name                     |
| `SPAR_MAPPER_PARTNER_API_DEFAULT_ISSUERS`        | —             | JSON array of trusted JWT issuers |
| `SPAR_MAPPER_PARTNER_API_DEFAULT_JWKS_URLS`      | —             | JSON array of JWKS endpoint URLs  |
| `SPAR_MAPPER_PARTNER_API_JWT_AUTH_ENABLED`       | `false`       | Verify the partner JWS signature on every request |
| `SPAR_MAPPER_PARTNER_API_CRYPTO_BACKEND`         | `keymanager`  | Verify backend: `local` (in-process PyJWT, partner_keys DB) or `keymanager` |
| `SPAR_MAPPER_PARTNER_API_CRYPTO_ALLOWED_ALGORITHMS` | `RS256`    | Allowed JWS algorithms (RS256 only; `none`/HMAC rejected) |
| `SPAR_MAPPER_PARTNER_API_CRYPTO_PARTNER_CERTS`   | `[]`          | Seed-based onboarding: JSON list of `{reference_id, public_key}` partner certs (local backend) |
| `SPAR_MAPPER_PARTNER_API_KEYMANAGER_SIGN_APP_ID` | `SPAR`        | App ID for KeyManager (only when backend=`keymanager`) |

> **Local dev tip:** For development without Keycloak, you can configure the JWT validation to accept a self-signed token by pointing `DEFAULT_JWKS_URLS` at a local mock JWKS endpoint.

***

### Run Migrations

The application manages its own schema through an in-app migration command. Run this once after creating the database, and again after pulling changes that modify models.

```bash
cd core/mapper-partner-api
python main.py migrate
```

This creates (or updates) the `id_fa_mapping` and `strategy` tables in the configured database.

***

### Start the Server

From the `core/mapper-partner-api/` directory:

**Development mode (uvicorn with auto-reload):**

```bash
cd core/mapper-partner-api
python main.py run
```

**Production-like mode (gunicorn + uvicorn workers):**

```bash
cd core/mapper-partner-api
gunicorn main:app \
  --workers 1 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --log-level info \
  --access-logfile - \
  --error-logfile -
```

Once running, the API is available at:

| URL                                  | Description                       |
| ------------------------------------ | --------------------------------- |
| `http://localhost:8000/docs`         | Swagger UI (interactive API docs) |
| `http://localhost:8000/redoc`        | ReDoc API documentation           |
| `http://localhost:8000/openapi.json` | Raw OpenAPI schema                |
| `http://localhost:8000/ping`         | Health check endpoint             |

***

### API Endpoints

All mapper endpoints are under the `/mapper` prefix and require a valid JWT in the `Authorization: Bearer <token>` header.

| Method | Path              | Description                            |
| ------ | ----------------- | -------------------------------------- |
| `POST` | `/mapper/link`    | Link an ID to a Financial Address      |
| `POST` | `/mapper/resolve` | Resolve an ID to its Financial Address |
| `POST` | `/mapper/update`  | Update an existing ID–FA mapping       |
| `POST` | `/mapper/unlink`  | Remove an ID–FA mapping                |

All requests and responses follow the G2P Connect Mapper API specification.

#### Example: Link Request

```bash
curl -X POST http://localhost:8000/mapper/link \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -d '{
    "signature": "<jws-detached-signature>",
    "header": {
      "version": "1.0.0",
      "message_id": "msg-001",
      "message_ts": "2024-01-01T00:00:00Z",
      "action": "link",
      "sender_id": "snd-001",
      "total_count": 1
    },
    "message": {
      "transaction_id": "txn-001",
      "link_request": [
        {
          "reference_id": "ref-001",
          "timestamp": "2024-01-01T00:00:00Z",
          "id": "national-id-12345",
          "fa": {
            "strategy_id": "default",
            "value": "wallet://provider/account123"
          }
        }
      ]
    }
  }'
```

***

### Running Tests

Install test dependencies if you haven't already:

```bash
pip install -r core/test-requirements.txt
```

A running PostgreSQL instance is required for integration tests. Set the test database connection via environment variables before running:

```bash
export SPAR_MAPPER_PARTNER_API_DB_HOSTNAME=localhost
export SPAR_MAPPER_PARTNER_API_DB_USERNAME=spar_user
export SPAR_MAPPER_PARTNER_API_DB_PASSWORD=spar_password
export SPAR_MAPPER_PARTNER_API_DB_DBNAME=spardb
```

Run tests from the relevant module directory:

```bash
# Mapper core tests
cd core/mapper-core
pytest -s -v

# Mapper partner API tests
cd core/mapper-partner-api
pytest -s -v

# All tests with coverage
cd core/mapper-partner-api
pytest -s -v --cov=src --cov-report=term-missing
```

***

### Code Quality

The project uses pre-commit hooks to enforce code style.

#### Install Pre-commit Hooks

```bash
pip install pre-commit
cd core
pre-commit install
```

#### Run Manually

```bash
cd core
pre-commit run --all-files
```

#### Tools Used

| Tool                                               | Purpose                               |
| -------------------------------------------------- | ------------------------------------- |
| [Black](https://black.readthedocs.io/)             | Code formatting                       |
| [Ruff](https://docs.astral.sh/ruff/)               | Fast linting (replaces flake8, isort) |
| [pyupgrade](https://github.com/asottile/pyupgrade) | Modernise Python syntax               |

Ruff config: core/.ruff.toml — line length 110, checks: `E`, `W`, `F`, `I`, `C`, `B`.

***

### Docker Build & Run

#### Build the Image

The Docker build context must be the **repo root** (not the api subdirectory), as the Dockerfile copies multiple packages:

```bash
docker build \
  -f docker/spar-apis/mapper-partner-api/Dockerfile \
  -t spar-mapper-partner-api:local \
  .
```

To pin a specific version of the external FastAPI common library:

```bash
docker build \
  -f docker/spar-apis/mapper-partner-api/Dockerfile \
  --build-arg FASTAPI_COMMON_REF=v1.1.5 \
  -t spar-mapper-partner-api:local \
  .
```

#### Run the Container

```bash
docker run -d \
  --name spar-mapper-api \
  -p 8000:8000 \
  -e SPAR_MAPPER_PARTNER_API_DB_HOSTNAME=host.docker.internal \
  -e SPAR_MAPPER_PARTNER_API_DB_PORT=5432 \
  -e SPAR_MAPPER_PARTNER_API_DB_USERNAME=spar_user \
  -e SPAR_MAPPER_PARTNER_API_DB_PASSWORD=spar_password \
  -e SPAR_MAPPER_PARTNER_API_DB_DBNAME=spardb \
  -e SPAR_MAPPER_PARTNER_API_DEFAULT_ISSUERS='["http://host.docker.internal:8080/realms/openg2p-beneficiary"]' \
  -e SPAR_MAPPER_PARTNER_API_DEFAULT_JWKS_URLS='["http://host.docker.internal:8080/realms/openg2p-beneficiary/protocol/openid-connect/certs"]' \
  spar-mapper-partner-api:local
```

> On Linux, replace `host.docker.internal` with `172.17.0.1` (the default Docker bridge gateway) or use `--network host`.

The container automatically runs `python main.py migrate` on startup before launching gunicorn.

#### Container Environment Variables

All `SPAR_MAPPER_PARTNER_API_*` variables from the Configuration Reference section work as container environment variables.

| Variable                                | Container Default |
| --------------------------------------- | ----------------- |
| `SPAR_MAPPER_PARTNER_API_HOST`          | `0.0.0.0`         |
| `SPAR_MAPPER_PARTNER_API_PORT`          | `8000`            |
| `SPAR_MAPPER_PARTNER_API_NO_OF_WORKERS` | `4`               |

***

### Troubleshooting

#### `ModuleNotFoundError: No module named 'openg2p_fastapi_partner_auth'`

The partner-auth library is not installed automatically via `pyproject.toml`. Install it explicitly:

```bash
pip install "git+https://github.com/openg2p/openg2p-fastapi-common@v1.1.5#subdirectory=openg2p-fastapi-partner-auth"
```

#### `asyncpg.exceptions.InvalidCatalogNameError: database "spardb" does not exist`

The database has not been created yet. Follow Section 7 to create it.

#### `FATAL: password authentication failed for user "spar_user"`

Check that:

1. The `SPAR_MAPPER_PARTNER_API_DB_PASSWORD` env var matches the password set during database creation.
2. PostgreSQL `pg_hba.conf` allows password-based authentication for local connections (use `md5` or `scram-sha-256`).

#### `sqlalchemy.exc.ProgrammingError: relation "id_fa_mapping" does not exist`

Migrations have not been run. Execute:

```bash
cd core/mapper-partner-api
python main.py migrate
```

#### JWT Validation Errors (`401 Unauthorized`)

* Verify `SPAR_MAPPER_PARTNER_API_DEFAULT_ISSUERS` matches the `iss` claim in your JWT.
* Verify `SPAR_MAPPER_PARTNER_API_DEFAULT_JWKS_URLS` points to a reachable JWKS endpoint.
* For local dev without Keycloak, check the G2P FastAPI Auth library docs for configuring a bypass or test mode.

#### Pre-commit Hooks Failing on `black` or `ruff`

Run formatting and linting manually, then re-stage:

```bash
cd core
black .
ruff check --fix .
git add -u
git commit
```

###
