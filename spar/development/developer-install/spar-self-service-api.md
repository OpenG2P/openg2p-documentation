---
description: >-
  This page provides comprehensive documentation for the installation of
  spar-self-service-api, a  service designed for data mapping within the Social
  Payments Account and Registry (SPAR) system.
---

# SPAR Self Service API Installation

## Installation

### Prerequisites

* Any machine running Linux (e.g., Ubuntu), macOS, or Windows
* Python3.10 or later
* Git
* PostgreSQL
* virtualenv
* **eSignet:** Ensure that eSignet is properly configured. Refer to the [eSignet Deployment Guide](../../../deployment/common-components/esignet.md) for setup instructions.
*   **SPAR Mapper API Configuration:** Ensure that the SPAR Mapper API is properly configured according to the [SPAR Mapper API Installation](spar-mapper-api.md).



#### Python Dependencies

The following dependencies are managed in the installation steps below.

```sh
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
openg2p-fastapi-auth==1.0.0
openg2p-g2pconnect-common-lib==1.0.0
openg2p-g2pconnect-mapper-lib==1.0.0
openg2p-spar-g2pconnect-mapper-connector-lib==1.0.0
openg2p-spar-mapper-interface-lib==1.0.0
-e git+https://github.com/OpenG2P/openg2p-spar-self-service@8e33f41ca0b2447860e8e8e8f901cc3afcc5707c#egg=openg2p_spar_self_service_api&subdirectory=openg2p-spar-self-service-api
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

### Steps to Install

#### Install from source

* Clone the repository

```sh
git clone https://github.com/OpenG2P/openg2p-spar-self-service
```

* Navigate to the project root

```sh
cd openg2p-spar-self-service
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
pip install openg2p-spar-g2pconnect-mapper-connector-lib &&
pip install greenlet && 
pip install -e .
```

* Configure database credentials and other environment variables in the \`.env\` file
  * [See Configuration section below](spar-self-service-api.md#configuration)
* &#x20;Run migrations to set up the database:

```sh
python main.py migrate
```

### Seeding the database (Optional)

This will seed the database with default values. Make sure to update the eSignet configuration in the db as per your installation.

#### PostgreSQL DB Setup:

Create a new role/user called "sparuser" and create a new database called "spardb", with "sparuser" as the owner.No need to run this step if Postgres was installed through openg2p's deployment script.

```plsql
CREATE ROLE sparuser WITH LOGIN NOSUPERUSER CREATEDB CREATEROLE INHERIT REPLICATION CONNECTION LIMIT -1 PASSWORD 'xxxxxx';
CREATE DATABASE spardb WITH OWNER = sparuser CONNECTION LIMIT = -1;  
```

#### Then run:

```sh
cd db_scripts &&
DB_HOST="openg2p.sandbox.net" \
DB_USER_PASSWORD="xxxxxx" \
./deploy.sh && cd ..
```

#### The following optional Env vars can also be passed:

```
- `VERSION="1.0.0"` Do not set this if you want latest version.
- `DB_PORT="5432"` Default is 5432.
- `DB_NAME="mydb"` Default is spardb.
- `DB_USER="myuser"` Default is sparuser.
- `DEPLOY_DML="false"` Default is true. If false, will not run DML scripts.
- `LOG_DB_QUERY="true"` Default is false. Logs all Db queries.
```

### Quick Start

* Start the development server

```sh
python main.py run
```

* Access Swagger API Documentation
  * [http://localhost:8000/docs](http://localhost:8000/docs)

### Configuration

#### Environment Variables

Set the following environment variables to configure the \`spar-mapper-api\`:

```markup
# Database credentials for spar-mapper-api (Update these values as per your installation/setup)
SPAR_SELFSERVICE_DB_DBNAME=openg2p_spar_db
SPAR_SELFSERVIC_DB_HOSTNAME='localhost'
SPAR_SELFSERVIC_DB_USERNAME='sparuser'

# Auth (Update these values as per your installation/setup)
SPAR_SELFSERVICE_AUTH_DEFAULT_ISSUERS=[ "https://esignet.dev.sandbox.net/v1/esignet", "https://keycloak.dev.sandbox.net/realms/sandbox" ]
SPAR_SELFSERVICE_AUTH_DEFAULT_JWKS_URLS=[ "https://esignet.dev.sandbox.net/v1/esignet/oauth/.well-known/jwks.json", "https://keycloak.dev.sandbox.net/realms/sandbox/protocol/openid-connect/certs" ]

# SPAR Mapper API Endpoints (change only if required)
SPAR_SELFSERVICE_MAPPER_API_URL="http://localhost:8007/sync"
SPAR_SELFSERVICE_MAPPER_LINK_PATH="/link"
SPAR_SELFSERVICE_MAPPER_UNLINK_PATH="/unlink"
SPAR_SELFSERVICE_MAPPER_RESOLVE_PATH="/resolve"
SPAR_SELFSERVICE_MAPPER_UPDATE_PATH="/update"
```

#### Authentication

The `spar-self-service-api` supports authentication via eSignet. Refer to the deployment documentation for eSignet [here](../../../deployment/common-components/esignet.md) for setup instructions.

### Testing

To run unit tests with `pytest`:

```sh
pytest -s
```

### Contributing

Contribution guidelines are available [here](https://github.com/OpenG2P/openg2p-spar-mapper-api/blob/develop/CONTRIBUTING.md).

\


\
\


\
\


\
\


\
\
\
\


\
\


\
\
\
\
\


\
\
\
\
\
\
\
&#x20;