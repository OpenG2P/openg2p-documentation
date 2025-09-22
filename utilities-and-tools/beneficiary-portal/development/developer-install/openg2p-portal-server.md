---
description: >-
  This page provides comprehensive documentation for the installation of Openg2p
  Portal Server
---

# Openg2p Portal Server

## Installation

### Prerequisites

* Any machine running Linux (e.g., Ubuntu), macOS, or Windows
* Python3.10 or later
* Git
* PostgreSQL
* virtualenv

#### Python dependencies

The following dependencies are managed in the installation steps below.

```
fastapi ~=0.103.1
uvicorn[standard] >=0.12.0
gunicorn ~=22.0.0
asyncio ~=3.4.3
pydantic-settings ~=2.0.0
pydantic-extra-types ~=2.0.0
python-multipart >=0.0.5
httpx >=0.23.0
sqlalchemy ~=2.0.20
json-logging ~=1.3.0
orjson ~=3.9.7
cryptography ~=41.0.4
python-jose ~=3.3.0
python-slugify>=8.0.0
psycopg2
asyncpg
SQLAlchemy
email-validator
openg2p-fastapi-common
openg2p-fastapi-auth
```

### Steps to install

#### Install from source

* Install dependencies

```sh
sudo apt install -y python3-pip python3-dev build-essential libpq-dev
```

* Create a Portal folder.

```sh
mkdir PORTAL
```

* Navigate to the  Portal folder.

```sh
cd PORTAL
```

* Clone the repository.

<pre class="language-sh"><code class="lang-sh"><strong>git clone https://github.com/OpenG2P/openg2p-fastapi-common.git
</strong><strong>git clone https://github.com/OpenG2P/openg2p-portal-server.git
</strong></code></pre>

* Create a virtual environment with Python 3.10

```sh
python3.10 -m venv .venv
```

* Activate the virtual environment.

```sh
source .venv/bin/activate
```

* Install the necessary dependencies.

```sh
pip install -e openg2p-fastapi-common/openg2p-fastapi-common
pip install -e openg2p-fastapi-common/openg2p-fastapi-auth
pip install -e openg2p-portal-server
```

* Create a '.env' file

```
PORTAL_PORT=8001
PORTAL_DB_USERNAME="portal_user"
PORTAL_DB_PASSWORD="pass"
PORTAL_DB_HOSTNAME="localhost"
PORTAL_DB_PORT="5432"
PORTAL_DB_DBNAME="db_portal"
PORTAL_AUTH_COOKIE_SECURE="false"
PORTAL_OPENAPI_ROOT_PATH= "/v1/selfservice"
PORTAL_AUTH_DEFAULT_ISSUERS="[\"https://keycloak.openg2p.org/realms/master\",\"https://esignet.openg2p.org\"]"
PORTAL_AUTH_DEFAULT_JWKS_URLS="[\"https://keycloak.openg2p.org/realms/master/protocol/openid-connect/certs\",\"https://esignet.openg2p.org/.well-known/jwks.json\"]"
```

* &#x20;Run migrations to set up the database.

```sh
python3 main.py migrate
```

### Seeding the database (optional)

This will seed the database with default values.

```sh
# Connect to the PostgreSQL database
psql -U portal_user -d db_portal -h localhost -p 5432
```

```sql
-- Insert a new OAuth provider with the provided details
INSERT INTO public.auth_oauth_provider (
    id, name, flow, body, image_icon_url, client_id, 
    client_authentication_method, client_secret, 
    auth_endpoint, validation_endpoint, token_endpoint, jwks_uri, 
    scope, enable_pkce, code_verifier, 
    date_format, token_map, extra_authorize_params, 
    g2p_portal_oauth_callback_url, g2p_id_type
) 
VALUES
(
    1,
    'Benficiary Portal',
    'oidc_auth_code',
    'LOGIN WITH NATIONAL ID',
    'https://esignet.openg2p.org/logo.png',
    'openg2p-beneficiary-esignet',
    'private_key_jwt',
    'secret_value',
    'https://esignet.openg2p.org/authorize',
    'https://esignet.openg2p.org/v1/esignet/oidc/userinfo',
    'https://esignet.openg2p.org/v1/esignet/oauth/v2/token',
    'https://esignet.openg2p.org/.well-known/jwks.json',
    'openid profile email',
    true,
    'code_verifier',
    '%Y/%m/%d',
    'sub:user_id name:name email:email phone_number:phone birthdate:birthdate gender:gender address:address picture:picture individual_id:provider_unique_id',
    '{
       "acr_values": "mosip:idp:acr:generated-code mosip:idp:acr:biometrics mosip:idp:acr:linked-wallet", 
       "claims": "{\"userinfo\":{\"name\":{\"essential\":true},\"phone_number\":{\"essential\":false},\"email\":{\"essential\":false},\"gender\":{\"essential\":true},\"birthdate\":{\"essential\":true},\"address\":{\"essential\":false},\"picture\":{\"essential\":false},\"individual_id\":{\"essential\":false}},\"id_token\":{}}"
     }',
    'http://selfservice17.openg2p.my/v1/selfservice/oauth2/callback',
    'NATIONAL ID'
);
```

<pre class="language-sh"><code class="lang-sh"># Encode the private key file into Base64 format and save it to a temporary file
<strong>base64 -w0 /home/Downloads/beneficiary.priv.pem > /tmp/key.b64
</strong>
# Connect to the PostgreSQL database
psql -U portal_user -d db_portal -h localhost -p 5432
</code></pre>

```sql
--Set the content of the private key by reading it from a file
\set content `cat /tmp/key.b64`

--Update the client private key for OAuth provider with id = 1
UPDATE public.auth_oauth_provider
SET client_private_key = :'content'
WHERE id = 1;

--Verify the updated private key
SELECT 
    id, 
    LENGTH(client_private_key) AS key_length,
    LEFT(client_private_key::text, 30) AS key_start,
    RIGHT(client_private_key::text, 30) AS key_end
FROM public.auth_oauth_provider
WHERE id = 1;
```

### Quick start

* Start the development server.

```sh
python3 main.py run
```

* Access Swagger API Documentation.
  * [http://localhost:8001/docs](http://localhost:8000/docs) or [http://selfservice17.openg2p.my/v1/selfservice/docs](http://selfservice17.openg2p.my/v1/selfservice/docs)

