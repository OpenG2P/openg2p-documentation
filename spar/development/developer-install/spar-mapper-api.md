---
description: >-
  This page provides comprehensive documentation for the installation of
  spar-mapper-api, a FastAPI-based service designed for data mapping within the
  Social Payments Account and Registry (SPAR) system.
---

# SPAR Mapper API

## Installation

### Prerequisites

* Any machine running Linux (e.g., Ubuntu), macOS, or Windows
* Python 3.11 or later
* Git
* PostgreSQL
* virtualenv

#### Python Dependencies

The following dependencies are managed in the installation steps below.

```
annotated-types==0.6.0
anyio==3.7.1
asyncio==3.4.3
asyncpg==0.28.0
certifi==2024.2.2
cffi==1.16.0
click==8.1.7
coverage==7.5.1
cryptography==41.0.7
ecdsa==0.19.0
fastapi==0.103.2
greenlet==3.0.3
h11==0.14.0
hiredis==2.2.3
httpcore==1.0.5
httptools==0.6.1
httpx==0.27.0
idna==3.7
iniconfig==2.0.0
Jinja2==3.1.4
json-logging==1.3.0
MarkupSafe==2.1.5
openg2p-g2pconnect-common-lib==1.0.0
openg2p-g2pconnect-mapper-lib==1.0.0
-e ./core/mapper-partner-api   # openg2p-spar-mapper-partner-api (local, from the openg2p-spar repo)
openg2p_fastapi_common==1.0.0
orjson==3.9.15
packaging==24.0
parse==1.20.1
pluggy==1.5.0
psycopg2==2.9.9
pyasn1==0.6.0
pycparser==2.22
pydantic==2.7.1
pydantic-extra-types==2.0.0
pydantic-settings==2.0.3
pydantic_core==2.18.2
pytest==8.2.0
pytest-asyncio==0.23.6
pytest-cov==5.0.0
python-dotenv==1.0.1
python-jose==3.3.0
python-multipart==0.0.9
PyYAML==6.0.1
redis==5.0.4
rsa==4.9
six==1.16.0
sniffio==1.3.1
SQLAlchemy==2.0.30
starlette==0.27.0
typing_extensions==4.11.0
uvicorn==0.29.0
uvloop==0.19.0
watchfiles==0.21.0
websockets==12.0
```

### Steps to install

* Install dependencies

```bash
sudo apt install -y python3-pip python3-dev build-essential libpq-dev
```

* Clone the consolidated repository&#x20;

```sh
git clone https://github.com/OpenG2P/openg2p-spar.git
```

* Switch to the branch of interest (e.g. `develop`) and navigate to the mapper partner API project

```sh
cd openg2p-spar && git checkout develop
cd core/mapper-partner-api
```

* Create a virtual environment with Python 3

```sh
virtualenv venv --python=python3
```

* Activate the virtual environment

```sh
source venv/bin/activate
```

* Install the necessary dependencies

```sh
pip install -r ../test-requirements.txt &&
pip install greenlet &&
pip install -e ../models -e ../mapper-core -e .
```

* Create a '.env' file and configure database
  *   Set the following environment variables to configure the \`spar-mapper-api\`:

      ```xml
      # Application Port
      SPAR_MAPPER_PARTNER_API_PORT='8000'

      # Database credentials
      SPAR_MAPPER_PARTNER_API_DB_HOSTNAME='localhost'
      SPAR_MAPPER_PARTNER_API_DB_USERNAME='sparuser'
      SPAR_MAPPER_PARTNER_API_DB_PASSWORD='password'
      SPAR_MAPPER_PARTNER_API_DB_DBNAME='spardb'
      ```
  *   Database setup

      ```sql
      CREATE ROLE sparuser WITH LOGIN NOSUPERUSER CREATEDB CREATEROLE INHERIT REPLICATION CONNECTION LIMIT -1 PASSWORD 'password';
      CREATE DATABASE spardb WITH OWNER = sparuser CONNECTION LIMIT = -1;
      ```


* &#x20;Run migrations to set up the database:

```sh
python main.py migrate
```

### Quick start

* Start the development server

```sh
python main.py run
```

* Access Swagger API Documentation
  * [http://localhost:8000/docs](http://localhost:8000/docs)

### Testing

To run unit tests with `pytest`:

```sh
pytest -s
```

### Contributing

Contribution guidelines are available [here](https://github.com/OpenG2P/openg2p-spar/blob/develop/CONTRIBUTING.md).
