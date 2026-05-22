---
description: >-
  Developers can set up and run the OpenG2P Registry Celery Workers on their
  local machines. The Workers execute the tasks enqueued by the Celery Beat
  Producers.
---

# Celery Workers

### Prerequisites

* Python3
* Git
* PostgreSQL
* Redis
* Celery

### Installation of Celery Workers

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

#### 4. Install and configure Redis

Redis is used as the Celery broker and result backend.

```bash
sudo apt install -y redis
sudo systemctl enable --now redis
```

#### 5. Clone the Registry Celery Repository

```bash
git clone https://github.com/OpenG2P/openg2p-registry-gen2-celery
```

#### 6. Install Python Libraries and Run Celery Workers

* Create a new Python virtual environment:

```bash
cd openg2p-registry-gen2-celery/openg2p-registry-celery-workers
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
    openg2p-fastapi-auth \
    openg2p-registry-extensions \
    openg2p-registry-celery-workers \
    celery \
    redis \
    requests \
    python-jose \
    fastnanoid \
    psycopg2 \
    asyncpg
```

* Create a `.env` file:

```
REGISTRY_CELERY_WORKERS_DB_DBNAME='registrydb'
REGISTRY_CELERY_WORKERS_DB_HOSTNAME='localhost'
REGISTRY_CELERY_WORKERS_DB_PORT='5432'
REGISTRY_CELERY_WORKERS_DB_USERNAME='registryuser'
REGISTRY_CELERY_WORKERS_DB_PASSWORD='password'

REGISTRY_CELERY_WORKERS_CELERY_BROKER_URL='redis://127.0.0.1:6379/0'
REGISTRY_CELERY_WORKERS_CELERY_BACKEND_URL='redis://127.0.0.1:6379/0'
REGISTRY_CELERY_WORKERS_WORKER_QUEUE='celery_jobs_worker_queue'

REGISTRY_CELERY_WORKERS_BATCH_SIZE=2000
REGISTRY_CELERY_WORKERS_WORKER_MAX_ATTEMPTS=5

# Functional-ID generation service (point to your local/dev instance)
REGISTRY_CELERY_WORKERS_FUNCTIONAL_ID_GENERATION_URL='http://localhost:8080/v1'
REGISTRY_CELERY_WORKERS_ID_GENERATION_ALLOCATION_PATH='/idgenerator/{id_type}/id'
REGISTRY_CELERY_WORKERS_ID_GENERATION_UPDATION_PATH=''
```

* Start Redis server (if not already running):

```bash
sudo systemctl start redis
```

* Run Celery Worker:

```bash
celery -A main.celery_app worker -Q celery_jobs_worker_queue --loglevel=info
```

### Verifying the Installation

The terminal logs should show the worker connecting to the broker and picking up tasks from the `celery_jobs_worker_queue` queue as the Beat Producers dispatch them.
