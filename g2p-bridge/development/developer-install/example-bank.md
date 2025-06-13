---
description: Installation of Example Bank Simulator on a developer machine
---

# Example Bank

Developers can set up and run the G2P Bridge Example Bank Simulator on their local machines. This guide outlines the steps to install the same on a <mark style="color:purple;">**Linux-based**</mark> laptop or desktop.

## Prerequisites

* Python3
* Git
* PostgreSQL
* Redis
* Celery

## Installation of Example Bank Simulator

#### 1. Update system packages

* Log in to your Linux server using SSH and update the package list and upgrade the existing packages:

```bash
sudo apt update
sudo apt upgrade -y
```

#### 2. Install dependencies

```bash
sudo apt install -y python3-pip python3-dev build-essential
```

3\. Install and configure PostgreSQL

*   G2P Bridge requires PostgreSQL as the database engine. Install PostgreSQL (if not already installed) and create a new database user for G2P Bridge.

    ```bash
    sudo apt install -y postgresql
    sudo su - postgres
    CREATE ROLE bankuser WITH LOGIN NOSUPERUSER CREATEDB CREATEROLE INHERIT REPLICATION CONNECTION LIMIT -1 PASSWORD 'password';
    CREATE DATABASE bankdb WITH OWNER = bankuser CONNECTION LIMIT = -1;
    exit
    ```

4\. Clone the G2P Bridge Repository

*   Clone the `openg2p-g2p-bridge` repository to your local machine.

    ```bash
    git clone https://github.com/OpenG2P/openg2p-g2p-bridge-example-bank
    ```

#### 5. Install Python Libraries and G2P Bridge Components <a href="#docs-internal-guid-f8d8e15e-7fff-3872-8a9f-bfbb05735977" id="docs-internal-guid-f8d8e15e-7fff-3872-8a9f-bfbb05735977"></a>

{% tabs %}
{% tab title="Example Bank API" %}
### Setting up the Bridge API

*   Make a new Python virtual environment.

    ```bash
    cd openg2p-g2p-bridge/openg2p-g2p-bridge-example-bank-api
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
        openg2p-g2p-bridge-example-bank-models==1.0.0 \
        openg2p-g2p-bridge-example-bank-api==1.0.0
    ```
*   Create a .env file

    ```
    EXAMPLE_BANK_DB_HOSTNAME='localhost'
    EXAMPLE_BANK_DB_DBNAME='bankdb'
    EXAMPLE_BANK_DB_USERNAME='bankuser'
    EXAMPLE_BANK_DB_PASSWORD='password'
    EXAMPLE_BANK_CELERY_BROKER_URL='redis://127.0.0.1:6379/0'
    EXAMPLE_BANK_CELERY_BACKEND_URL='redis://127.0.0.1:6379/0'
    ```
*   Migrate the database schema

    ```bash
    python3 main.py migrate; 
    ```
*   Run the API server on `127.0.0.1:8000`

    ```bash
    gunicorn "main:app" --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000
    ```
{% endtab %}

{% tab title="Example Bank Celery" %}
### Setting up the Example Bank Celery&#x20;

*   Make a new Python virtual environment.

    ```bash
    cd openg2p-g2p-bridge/openg2p-g2p-bridge-example-bank-celery
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
        openg2p-g2p-bridge-example-bank-models==1.0.0 \
        openg2p-g2p-bridge-example-bank-celery==1.0.0
    ```
*   Run redis-server (if not already started)

    ```
    bash sudo systemctl start redis
    ```
*   Create a .env file

    ```
    EXAMPLE_BANK_CELERY_DB_HOSTNAME='localhost'
    EXAMPLE_BANK_CELERY_DB_DBNAME='bankdb'
    EXAMPLE_BANK_CELERY_DB_USERNAME='bankuser'
    EXAMPLE_BANK_CELERY_DB_PASSWORD='password'
    EXAMPLE_BANK_CELERY_CELERY_BROKER_URL='redis://127.0.0.1:6379/0'
    EXAMPLE_BANK_CELERY_CELERY_BACKEND_URL='redis://127.0.0.1:6379/0'
    EXAMPLE_BANK_CELERY_MT940_STATEMENT_CALLBACK_URL='http://openg2p-g2p-bridge-api/upload_mt940'
    ```
*   Run the celery beat and worker

    ```bash
    celery -A main.celery_app worker --loglevel=info --beat & \
        celery -A main.celery_app worker --loglevel=info -Q g2p_bridge_celery_worker_tasks
    ```
{% endtab %}
{% endtabs %}
