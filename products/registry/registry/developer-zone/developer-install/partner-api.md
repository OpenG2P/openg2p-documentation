---
description: >-
  Developers can set up and run the OpenG2P Registry Partner API on their local
  machines. This guide outlines the steps to install it on a Linux-based laptop
  or desktop.
---

# Partner API

### Prerequisites

* Python3
* Git
* PostgreSQL

### Installation of Partner API

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
git clone https://gitlab.com/openg2p/registry/registry-platform/-/tree/develop/apis
```

#### 5. Install Python Libraries and Run the API

* Create a new Python virtual environment:

```bash
cd registry-platform/apis/openg2p-registry-partner-api
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
    openg2p-registry-partner-api \
    jsonpath_ng \
    asyncpg \
    psycopg2
```

* Create a `.env` file:

```
REGISTRY_PARTNER_API_DB_DBNAME='registrydb'
REGISTRY_PARTNER_API_DB_HOSTNAME='localhost'
REGISTRY_PARTNER_API_DB_PORT='5432'
REGISTRY_PARTNER_API_DB_USERNAME='registryuser'
REGISTRY_PARTNER_API_DB_PASSWORD='password'
REGISTRY_PARTNER_API_HOST='0.0.0.0'
REGISTRY_PARTNER_API_PORT='8001'

# Keymanager (leave disabled for local dev)
REGISTRY_PARTNER_API_KEYMANAGER_AUTH_ENABLED='false'
REGISTRY_PARTNER_API_KEYMANAGER_API_BASE_URL=''
REGISTRY_PARTNER_API_KEYMANAGER_AUTH_URL=''
REGISTRY_PARTNER_API_KEYMANAGER_AUTH_CLIENT_ID='openg2p-registry-partner'
REGISTRY_PARTNER_API_KEYMANAGER_AUTH_CLIENT_SECRET=''
REGISTRY_PARTNER_API_KEYMANAGER_SIGN_APP_ID='REGISTRY'
REGISTRY_PARTNER_API_KEYMANAGER_SIGN_REF_ID=''
```

* Run the API server:

```bash
gunicorn "main:app" --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 127.0.0.1:8001
```

### Verifying the Installation

Open the OpenAPI docs in your browser at `http://127.0.0.1:8001/docs`.
