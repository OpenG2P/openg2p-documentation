---
description: >-
  This page provides comprehensive documentation for the installation of Openg2p
  IAM Service
---

# Developer Install

### Prerequisites

* Any machine running Linux (e.g., Ubuntu), macOS, or Windows
* Python3.10 or later
* Git
* PostgreSQL
* virtualenv

### Steps to install

#### Install from source

* Install dependencies

```sh
sudo apt install -y python3-pip python3-dev build-essential libpq-dev
```

* Create a Portal folder.

```sh
mkdir staff-portal
```

* Navigate to the  Portal folder.

```sh
cd staff-portal
```

* Clone the repository.

```sh
git clone https://github.com/OpenG2P/openg2p-fastapi-common.git
git clone https://github.com/OpenG2P/iam-service.git
```

* Create a virtual environment with Python 3.10

```sh
python3.10 -m venv .venv
```

* Activate the virtual environment.

```sh
source .venv/bin/activate
```

Checkout `1.1` branch for openg2p-fastapi-common

```
cd openg2p-fastapi-common
git checkout 1.1
cd ..
```

* Install the necessary dependencies.

```sh
pip install -e openg2p-fastapi-common/openg2p-fastapi-common
pip install -e iam-service/iam-core
pip install -e iam-service/iam-staff-portal-api
```

* Create a `.env` file in the `iam-service/iam-staff-portal-api` directory.

```
cd iam-service/iam-staff-portal-api
touch .env
```

```
iam_staff_db_username=odoo_user
iam_staff_db_password=admin
iam_staff_db_hostname=localhost
iam_staff_db_port=5432
iam_staff_db_dbname=db_staff_portal

iam_staff_port=8000

iam_staff_login_providers_table_enabled=true
iam_staff_login_providers_table_name="login_providers"
iam_staff_auth_enabled=true

iam_staff_auth_default_issuers=["https://keycloak2.openg2p.org/realms/master"]
iam_staff_auth_default_jwks_urls=["https://keycloak2.openg2p.org/realms/master/protocol/openid-connect/certs"]

iam_staff_auth_cookie_httponly=true
iam_staff_auth_cookie_secure=false
iam_staff_auth_cookie_path=/
iam_staff_auth_cookie_domain=".openg2p.my"
iam_staff_auth_cookie_max_age=1800
iam_staff_auth_cookie_set_expires=true

iam_staff_openapi_root_path= "/"
```

* Run migrations to set up the database.

```
cd iam-service/iam-staff-portal-api
python3 -m iam_staff_portal_api.main migrate
```

### Seeding the database (optional)

Import the CSV file below into the `login_providers` table.

{% file src="../.gitbook/assets/login_providers.csv" %}

* **Nginx Configuration**: Configure Nginx to act as a reverse proxy for Openg2p IAM Service

```
# Install Nginx if not already installed
sudo apt-get update
sudo apt-get install nginx -y

# Create a new configuration file for Openg2p Registry Staff Portal UI
sudo nano /etc/nginx/sites-available/staff-portal.conf
```

* &#x20;Below is a sample Nginx configuration (`/etc/nginx/sites-available/staff-portal.conf`).

```
server {
    listen 80;
    server_name iam.openg2p.my;

    proxy_buffer_size 256k;
    proxy_buffers 8 512k;
    proxy_busy_buffers_size 512k;
    large_client_header_buffers 8 256k;

    location / {
        proxy_pass                      http://localhost:8000;
        proxy_http_version              1.1;
        proxy_set_header                Upgrade $http_upgrade;
        proxy_set_header                Connection "upgrade";
        proxy_set_header                Host $host;
        proxy_set_header                Referer $http_referer;
        proxy_set_header                X-Real-IP $remote_addr;
        proxy_set_header                X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header                X-Forwarded-Proto $scheme;
        proxy_pass_request_headers      on;
    }
}
```

* **Enable Configuration**: Enable the Nginx configuration by creating a symbolic link to `sites-enabled`

```
sudo ln -sf /etc/nginx/sites-available/staff-portal.conf /etc/nginx/sites-enabled/
```

* **Adding domain to Hosts**: Add the domain to the hosts for the system to recognize the domain.

```
sudo nano /etc/hosts
127.0.0.1 iam.openg2p.my
```

* **Restart Nginx**: Restart the Nginx service to apply the changes:

```
sudo service nginx restart
```

### _Quick_ start

* Start the development server.

```sh
cd iam-service/iam-staff-portal-api
uvicorn iam_staff_portal_api.main:app --reload
```

* Access Swagger API Documentation.
  * [http://localhost:8000/docs](http://localhost:8000/docs) or [http://iam.openg2p.my/docs](http://selfservice17.openg2p.my/v1/selfservice/docs)
