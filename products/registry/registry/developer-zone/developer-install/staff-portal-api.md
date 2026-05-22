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
REGISTRY_STAFF_PORTAL_API_DB_DBNAME='registrydb'
REGISTRY_STAFF_PORTAL_API_DB_HOSTNAME='localhost'
REGISTRY_STAFF_PORTAL_API_DB_PORT='5432'
REGISTRY_STAFF_PORTAL_API_DB_USERNAME='registryuser'
REGISTRY_STAFF_PORTAL_API_DB_PASSWORD='password'
REGISTRY_STAFF_PORTAL_API_HOST='0.0.0.0'
REGISTRY_STAFF_PORTAL_API_PORT='8002'

# IAM (Keycloak) authentication – leave blank for local dev without auth
REGISTRY_STAFF_PORTAL_API_AUTH_PROVIDER_API_URL=''
REGISTRY_STAFF_PORTAL_API_KEYCLOAK_CLIENT_ID=''

# Audit Manager integration (disabled by default)
REGISTRY_STAFF_PORTAL_API_AUDIT_ENABLED='false'
REGISTRY_STAFF_PORTAL_API_AUDIT_MANAGER_URL=''
REGISTRY_STAFF_PORTAL_API_AUDIT_TIMEOUT_SECONDS='2.0'
REGISTRY_STAFF_PORTAL_API_AUDIT_SOURCE='/openg2p/registry-staff-portal-api'
REGISTRY_STAFF_PORTAL_API_AUDIT_MODULE='registry-staff-portal-api'
REGISTRY_STAFF_PORTAL_API_AUDIT_ANONYMOUS_FAILURES='true'
```

* Run the API server:

```bash
gunicorn "main:app" --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 127.0.0.1:8002
```

### Verifying the Installation

Open the OpenAPI docs in your browser at `http://127.0.0.1:8002/docs`.
