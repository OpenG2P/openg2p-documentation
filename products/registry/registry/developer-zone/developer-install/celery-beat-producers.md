---
description: >-
  Developers can set up and run the OpenG2P Registry Celery Beat Producers on
  their local machines. The Beat Producers schedule periodic registry jobs and
  enqueue them onto the Celery worker queue.
---

# Celery Beat Producers

### Prerequisites

* Python3
* Git
* PostgreSQL
* Redis
* Celery

### Installation of Celery Beat Producers

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

#### 6. Install Python Libraries and Run Celery Beat

* Create a new Python virtual environment:

```bash
cd openg2p-registry-gen2-celery/openg2p-registry-celery-beat-producers
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
    openg2p-registry-celery-beat-producers \
    celery \
    redis \
    psycopg2
```

* Create a `.env` file:

```
REGISTRY_CELERY_BEAT_DB_DRIVER='postgresql'
REGISTRY_CELERY_BEAT_DB_DBNAME='registrydb'
REGISTRY_CELERY_BEAT_DB_HOSTNAME='localhost'
REGISTRY_CELERY_BEAT_DB_PORT='5432'
REGISTRY_CELERY_BEAT_DB_USERNAME='registryuser'
REGISTRY_CELERY_BEAT_DB_PASSWORD='password'

REGISTRY_CELERY_BEAT_CELERY_BROKER_URL='redis://127.0.0.1:6379/0'
REGISTRY_CELERY_BEAT_CELERY_BACKEND_URL='redis://127.0.0.1:6379/0'
REGISTRY_CELERY_BEAT_WORKER_QUEUE='registry_worker_queue'

REGISTRY_CELERY_BEAT_BATCH_SIZE=2000
REGISTRY_CELERY_BEAT_NO_OF_TASKS_TO_PROCESS=4
REGISTRY_CELERY_BEAT_DEFAULT_BEAT_PRODUCER_FREQUENCY=20

# Per-pipeline beat frequencies (seconds). Set only those you want active;
# leave the rest unset to fall back to the default frequency.
REGISTRY_CELERY_BEAT_DATA_TRANSFORMATION_BEAT_PRODUCER_FREQUENCY=60
REGISTRY_CELERY_BEAT_INGEST_DATA_BEAT_PRODUCER_FREQUENCY=60
REGISTRY_CELERY_BEAT_INGEST_DATA_CLASSIFICATION_BEAT_PRODUCER_FREQUENCY=60
REGISTRY_CELERY_BEAT_OUTGEST_DATA_PUBLISH_BEAT_PRODUCER_FREQUENCY=60
REGISTRY_CELERY_BEAT_OUTGEST_TOPIC_REGISTER_BEAT_PRODUCER_FREQUENCY=60
REGISTRY_CELERY_BEAT_DEDUPLICATION_BEAT_PRODUCER_FREQUENCY=60
REGISTRY_CELERY_BEAT_INTAKE_FORM_REGISTER_INGEST_BEAT_PRODUCER_FREQUENCY=60
REGISTRY_CELERY_BEAT_FUNCTIONAL_ID_ALLOCATION_BEAT_PRODUCER_FREQUENCY=60
REGISTRY_CELERY_BEAT_FUNCTIONAL_ID_UPDATION_BEAT_PRODUCER_FREQUENCY=60
REGISTRY_CELERY_BEAT_SCORE_COMPUTE_BEAT_PRODUCER_FREQUENCY=60
REGISTRY_CELERY_BEAT_COMPLETION_SCORE_BEAT_PRODUCER_FREQUENCY=60
```

* Start Redis server (if not already running):

```bash
sudo systemctl start redis
```

* Run Celery Beat:

```bash
celery -A main.celery_app worker --beat --loglevel=info
```

### Verifying the Installation

The terminal logs should show the beat scheduler ticking at the configured frequencies and tasks being dispatched onto the `registry_worker_queue` queue.
