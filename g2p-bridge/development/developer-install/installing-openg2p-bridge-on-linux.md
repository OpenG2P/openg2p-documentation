---
icon: laptop-code
description: Installation of G2P Bridge on developer machine
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
sudo apt install -y python3-pip python3-dev build-essential

```

3\. Install and configure PostgreSQL

*   G2P Bridge requires PostgreSQL as the database engine. Install PostgreSQL and create a new database user for G2P Bridge.

    ```bash
    sudo apt install -y postgresql
    sudo su - postgres
    createuser --createdb --username postgres --no-createrole --no-superuser --pwprompt g2p_bridge_user
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

    ```
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
        openg2p-fastapi-common==1.1.0 \
        openg2p-fastapi-auth==1.1.0 \
        openg2p-g2pconnect-common-lib==1.1.0 \
        openg2p-g2p-bridge-models==1.0.0 \
        openg2p-g2p-bridge-api==1.0.0
        
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

    ```
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
        openg2p-fastapi-common==1.1.0 \
        openg2p-fastapi-auth==1.1.0 \
        openg2p-g2pconnect-common-lib==1.1.0 \
        openg2p-g2p-bridge-models==1.0.0 \
        openg2p-g2p-bridge-bank-connectors==1.0.0 \
        openg2p-g2p-bridge-celery-beat-producers==1.0.0    
    ```
*   Run redis-server

    ```
    bash sudo systemctl start redis
    ```
*   Run the celery beat

    ```bash
    celery -A main.celery_app worker --beat --loglevel=info
    ```
{% endtab %}

{% tab title="Bridge Celery Worker" %}
### Setting up the Bridge Celery Worker

*   Make a new Python virtual environment.

    ```
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
        openg2p-fastapi-common==1.1.0 \
        openg2p-fastapi-auth==1.1.0 \
        openg2p-g2pconnect-common-lib==1.1.0 \
        openg2p-g2p-bridge-models==1.0.0 \
        openg2p-g2p-bridge-bank-connectors==1.0.0 \
        openg2p-g2p-bridge-celery-workers==1.0.0    
    ```
*   Run redis-server

    ```
    bash sudo systemctl start redis
    ```
*   Run the celery beat

    ```bash
    celery -A main.celery_app worker -Q g2p_bridge_celery_worker_tasks --loglevel=info
    ```
{% endtab %}
{% endtabs %}
