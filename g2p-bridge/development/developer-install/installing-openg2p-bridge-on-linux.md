---
description: Installation of G2P Bridge on a developer machine
---

# G2P Bridge

Developers can set up and run the G2P Bridge on their local machines. This guide outlines the steps to install G2P Bridge on a <mark style="color:purple;">**Linux-based**</mark> laptop or desktop.

## Prerequisites

* Python3
* Git
* PostgreSQL
* Redis
* Celery

## Installation of G2P Bridge

#### 1. Update system packages

* Log in to your Linux server using SSH and update the package list and upgrade the existing packages:

```bash
sudo apt update
sudo apt upgrade -y
```

#### 2. Install dependencies

```bash
sudo apt install -y python3-pip python3-dev build-essential libpq-dev
```

3\. Install and configure PostgreSQL

*   G2P Bridge requires PostgreSQL as the database engine. Install PostgreSQL (if not already installed) and create a new database user for G2P Bridge.

    ```bash
    sudo apt install -y postgresql
    sudo su - postgres
    psql 
    CREATE ROLE bridgeuser WITH LOGIN NOSUPERUSER CREATEDB CREATEROLE INHERIT REPLICATION CONNECTION LIMIT -1 PASSWORD 'password';
    CREATE DATABASE bridgedb WITH OWNER = bridgeuser CONNECTION LIMIT = -1;
    exit
    exit
    ```

4\. Clone the G2P Bridge Repository

*   Clone the `openg2p-g2p-bridge` repository to your local machine.

    ```bash
    git clone https://github.com/OpenG2P/openg2p-g2p-bridge
    ```

#### 5. Install Python Libraries and G2P Bridge Components <a href="#docs-internal-guid-f8d8e15e-7fff-3872-8a9f-bfbb05735977" id="docs-internal-guid-f8d8e15e-7fff-3872-8a9f-bfbb05735977"></a>

{% tabs %}
{% tab title="Bridge API" %}
### Setting up the Bridge API

*   Make a new Python virtual environment.

    ```bash
    cd openg2p-g2p-bridge/openg2p-g2p-bridge-api
    python3 -m venv venv
    ```
*   Activate the virtual environment.

    ```bash
    source venv/bin/activate
    ```
*   Use `pip` to install the required Python packages, including the core libraries for the G2P Bridge.

    ```bash
    python3 -m pip install \
        openg2p-fastapi-common==1.1.2 \
        openg2p-fastapi-auth==1.1.2 \
        openg2p-g2pconnect-common-lib==1.1.0 \
        openg2p-g2p-bridge-models==1.1.0 \
        openg2p-g2p-bridge-api==1.1.0
    ```
*   Create a .env file&#x20;

    ```
    G2P_BRIDGE_DB_DBNAME='bridgedb'
    G2P_BRIDGE_DB_HOSTNAME='localhost'
    G2P_BRIDGE_DB_PASSWORD='password'
    G2P_BRIDGE_DB_PORT='5432'
    G2P_BRIDGE_DB_USERNAME='bridgeuser'
    G2P_BRIDGE_WORKER_TYPE='gunicorn'
    G2P_BRIDGE_HOST='0.0.0.0'
    G2P_BRIDGE_PORT='8000'
    G2P_BRIDGE_NO_OF_WORKERS=1
    ```
*   Migrate the database schema

    ```
    python3 main.py migrate; 
    ```
*   Run the API server on `127.0.0.1:8000`

    ```
    gunicorn "main:app" --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000
    ```
{% endtab %}

{% tab title="Bridge Celery Beat" %}
### Setting up the Bridge Celery Beat

*   Make a new Python virtual environment.

    ```bash
    cd openg2p-g2p-bridge/openg2p-g2p-bridge-celery-beat-producers
    python3 -m venv venv
    ```
*   Activate the virtual environment.

    ```bash
    source venv/bin/activate
    ```
*   Use `pip` to install the required Python packages, including the core libraries for the G2P Bridge.

    ```bash
    python3 -m pip install \
        openg2p-fastapi-common==1.1.2 \
        openg2p-fastapi-auth==1.1.2 \
        openg2p-g2pconnect-common-lib==1.1.0 \
        openg2p-g2p-bridge-models==1.1.0 \
        openg2p-g2p-bridge-bank-connectors==1.1.0 \
        openg2p-g2p-bridge-celery-beat-producers==1.1.0    
    ```
*   Create a .env file

    ```
    G2P_BRIDGE_CELERY_BEAT_MAPPER_RESOLVE_API_URL='http://spar-mapper-api/sync/resolve' # Update the Spar Mapper Resolve URL
    G2P_BRIDGE_CELERY_BEAT_DB_HOSTNAME='localhost'
    G2P_BRIDGE_CELERY_BEAT_DB_PASSWORD='password'
    G2P_BRIDGE_CELERY_BEAT_CELERY_BROKER_URL='redis://127.0.0.1:6379/0'
    G2P_BRIDGE_CELERY_BEAT_CELERY_BACKEND_URL='redis://127.0.0.1:6379/0'
    G2P_BRIDGE_CELERY_BEAT_MAPPER_RESOLVE_FREQUENCY=60
    G2P_BRIDGE_CELERY_BEAT_FUNDS_AVAILABLE_CHECK_FREQUENCY=60
    G2P_BRIDGE_CELERY_BEAT_FUNDS_BLOCKED_FREQUENCY=60
    G2P_BRIDGE_CELERY_BEAT_FUNDS_DISBURSEMENT_FREQUENCY=60
    G2P_BRIDGE_CELERY_BEAT_MT940_PROCESSOR_FREQUENCY=60
    G2P_BRIDGE_CELERY_BEAT_PROCESS_FUTURE_DISBURSEMENT_SCHEDULES=true
    ```
*   Run redis-server

    ```bash
    sudo systemctl start redis
    ```
*   Run the celery beat

    ```bash
    celery -A main.celery_app worker --beat --loglevel=info
    ```
{% endtab %}

{% tab title="Bridge Celery Worker" %}
### Setting up the Bridge Celery Worker

*   Make a new Python virtual environment.

    ```bash
    cd openg2p-g2p-bridge/openg2p-g2p-bridge-celery-workers
    python3 -m venv venv
    ```
*   Activate the virtual environment.

    ```bash
    source venv/bin/activate
    ```
*   Use `pip` to install the required Python packages, including the core libraries for the G2P Bridge.

    ```bash
    python3 -m pip install \
        openg2p-fastapi-common==1.1.2 \
        openg2p-fastapi-auth==1.1.2 \
        openg2p-g2pconnect-common-lib==1.1.0 \
        openg2p-g2p-bridge-models==1.1.0 \
        openg2p-g2p-bridge-bank-connectors==1.1.0 \
        openg2p-g2p-bridge-celery-workers==1.1.0    
    ```
*   Create a .env file

    ```
    G2P_BRIDGE_CELERY_WORKERS_MAPPER_RESOLVE_API_URL='http://mapper/sync/resolve'
    G2P_BRIDGE_CELERY_WORKERS_MAPPER_RESOLVE_RETRY_DELAY=5
    G2P_BRIDGE_CELERY_WORKERS_DB_DBNAME='bridgedb'
    G2P_BRIDGE_CELERY_WORKERS_DB_USERNAME='bridgeuser'
    G2P_BRIDGE_CELERY_WORKERS_DB_PASSWORD='password'
    G2P_BRIDGE_CELERY_WORKERS_DB_HOSTNAME='localhost'
    G2P_BRIDGE_CELERY_BEAT_BANK_FA_DECONSTRUCT_STRATEGY='^account_number:(?P<account_number>.*)\.branch_code:(?P<branch_code>.*)\.bank_code:(?P<bank_code>.*)\.mobile_number:(?P<mobile_number>.*)\.email_address:(?P<email_address>.*)\.fa_type:(?P<fa_type>.*)$'
    G2P_BRIDGE_CELERY_BEAT_MOBILE_WALLET_DECONSTRUCT_STRATEGY='^mobile_number:(?P<mobile_number>.*)\.wallet_provider_name:(?P<wallet_provider_name>.*)\.wallet_provider_code:(?P<wallet_provider_code>.*)\.fa_type:(?P<fa_type>.*)$'
    G2P_BRIDGE_CELERY_BEAT_EMAIL_WALLET_DECONSTRUCT_STRATEGY='^email_address:(?P<email_address>.*)\.wallet_provider_name:(?P<wallet_provider_name>.*)\.wallet_provider_code:(?P<wallet_provider_code>.*)\.fa_type:(?P<fa_type>.*)$'
    G2P_BRIDGE_CELERY_PRODUCERS_FUNDS_AVAILABLE_CHECK_URL_EXAMPLE_BANK='http://127.0.0.1:8003/check_funds'
    G2P_BRIDGE_CELERY_PRODUCERS_FUNDS_BLOCK_URL_EXAMPLE_BANK='http://127.0.0.1:8003/block_funds'
    G2P_BRIDGE_CELERY_PRODUCERS_FUNDS_DISBURSEMENT_URL_EXAMPLE_BANK='http://127.0.0.1:8003/initiate_payment'
    G2P_BRIDGE_CELERY_WORKERS_CELERY_BROKER_URL='redis://127.0.0.1:6379/0'
    G2P_BRIDGE_CELERY_WORKERS_CELERY_BACKEND_URL='redis://127.0.0.1:6379/0'
    ```
*   Run redis-server (if not already started)

    ```bash
    sudo systemctl start redis
    ```
*   Run the celery beat

    ```bash
    celery -A main.celery_app worker -Q g2p_bridge_celery_worker_tasks --loglevel=info
    ```
{% endtab %}
{% endtabs %}
