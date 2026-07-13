---
description: >-
  Developers can set up and run the OpenG2P Registry Staff Portal API on their
  local machines. This guide outlines the steps to install it on a Linux-based
  laptop or desktop.
---

# Staff Portal API

### Prerequisites

* Python3
* Git
* PostgreSQL

### Installation of Staff Portal API

#### 1. Update system packages

Log in to your Linux server using SSH and update the package list and upgrade the existing packages:

```bash
sudo apt update
sudo apt upgrade -y
```

#### 2. Install dependencies

```bash
sudo apt install -y python3-pip python3-dev python3-venv build-essential libpq-dev
```

#### 3. Install and configure PostgreSQL

The Registry uses PostgreSQL as the database engine. Install PostgreSQL (if not already installed) and create a new database user and database.

```bash
sudo apt install -y postgresql
sudo su - postgres
psql
CREATE ROLE registryuser WITH LOGIN NOSUPERUSER CREATEDB CREATEROLE INHERIT REPLICATION CONNECTION LIMIT -1 PASSWORD 'password';
CREATE DATABASE registrydb WITH OWNER = registryuser CONNECTION LIMIT = -1;
exit
exit
```

#### 4. Clone the Registry APIs Repository

```bash
git clone https://github.com/OpenG2P/openg2p-registry-gen2-apis
```

#### 5. Install Python Libraries and Run the API

* Create a new Python virtual environment:

```bash
cd openg2p-registry-gen2-apis/openg2p-registry-staff-portal-api
python3 -m venv venv
```

* Activate the virtual environment:

```bash
source venv/bin/activate
```

* Install required Python packages:

```bash
python3 -m pip install \
    openg2p-fastapi-common \
    openg2p-registry-core \
    openg2p-registry-extensions \
    openg2p-registry-staff-portal-api \
    asyncpg \
    psycopg2
```

* Create a `.env` file:

```
# MASTER DATA DB
REGISTRY_STAFF_PORTAL_API_MASTER_DATA_DB_DBNAME=commons_services_master_data
REGISTRY_STAFF_PORTAL_API_MASTER_DATA_DB_DRIVER=postgresql+asyncpg
REGISTRY_STAFF_PORTAL_API_MASTER_DATA_DB_HOSTNAME=localhost
REGISTRY_STAFF_PORTAL_API_MASTER_DATA_DB_PORT=5432
REGISTRY_STAFF_PORTAL_API_MASTER_DATA_DB_USERNAME=postgres
REGISTRY_STAFF_PORTAL_API_MASTER_DATA_DB_PASSWORD=admin

# MAIN DB
REGISTRY_STAFF_PORTAL_API_DB_DBNAME=registry
REGISTRY_STAFF_PORTAL_API_DB_HOSTNAME=localhost
REGISTRY_STAFF_PORTAL_API_DB_PORT=5434
REGISTRY_STAFF_PORTAL_API_DB_USERNAME=postgres
REGISTRY_STAFF_PORTAL_API_DB_PASSWORD=admin

# AUTH
REGISTRY_STAFF_PORTAL_API_AUTH_PROVIDER_API_URL=http://iam.dev.openg2p.org
REGISTRY_STAFF_PORTAL_API_AUTH_REDIS_URL=redis://localhost:6379/0
REGISTRY_STAFF_PORTAL_API_AUTH_TRANSACTION_STORE_BACKEND=redis
REGISTRY_STAFF_PORTAL_API_AUTH_REFRESH_TOKEN_ENABLED=true
REGISTRY_STAFF_PORTAL_API_AUTH_COOKIE_HTTPONLY=true
REGISTRY_STAFF_PORTAL_API_AUTH_COOKIE_SECURE=false
REGISTRY_STAFF_PORTAL_API_AUTH_COOKIE_PATH=/
REGISTRY_STAFF_PORTAL_API_AUTH_COOKIE_DOMAIN=.openg2p.my
REGISTRY_STAFF_PORTAL_API_AUTH_COOKIE_MAX_AGE=1800
REGISTRY_STAFF_PORTAL_API_AUTH_COOKIE_SET_EXPIRES=true

# KEYCLOAK
REGISTRY_STAFF_PORTAL_API_KEYCLOAK_CLIENT_ID=registry-staff-portal

# MINIO
REGISTRY_STAFF_PORTAL_API_MINIO_ACCESS_KEY=minioadmin
REGISTRY_STAFF_PORTAL_API_MINIO_SECRET_KEY=minioadmin
REGISTRY_STAFF_PORTAL_API_MINIO_ENDPOINT=localhost:9000
REGISTRY_STAFF_PORTAL_API_MINIO_BUCKET_NAME=default
REGISTRY_STAFF_PORTAL_API_TEMPLATE_BUCKET_NAME=template
REGISTRY_STAFF_PORTAL_API_MINIO_SECURE=false

# APP
REGISTRY_STAFF_PORTAL_API_OPENAPI_ROOT_PATH=/

REGISTRY_STAFF_PORTAL_API_AWE_CALLBACK_HMAC_SECRET=111111
REGISTRY_STAFF_PORTAL_API_AWE_WEBHOOK_TIMESTAMP_TOLERANCE_SECONDS=300
REGISTRY_STAFF_PORTAL_API_AWE_ENABLED=true
REGISTRY_STAFF_PORTAL_API_AWE_DEFAULT_CALLBACK_URL="https://staff-ofr.dev.openg2p.org/awe/webhooks/decision"
REGISTRY_STAFF_PORTAL_API_AWE_CALLBACK_SECRET_ID=ofr
REGISTRY_STAFF_PORTAL_API_AWE_BASE_URL="https://awe-ofr.dev.openg2p.org"
```

* Run the API server:

```bash
gunicorn "main:app" --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 127.0.0.1:8002
```

### Verifying the Installation

Open the OpenAPI docs in your browser at `http://127.0.0.1:8002/docs`.
