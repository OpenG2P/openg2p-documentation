---
description: >-
  Document on how to setup and install external database for OpenG2P
  environments
---

# Configuring  External Database to OpenG2P Environment

## Prerequisites <a href="#prerequisites" id="prerequisites"></a>

1. Make sure the hardware requirement to setup the external database.

## Installation and configuration

1. Login to the external database node&#x20;
2.  Install PostgreSQL using below commands

    <pre class="language-bash"><code class="lang-bash"><strong>sudo apt update
    </strong><strong>sudo apt install postgresql
    </strong></code></pre>
3.  After installation of postgresql check the status by using below command

    <pre class="language-bash"><code class="lang-bash"><strong>service postgresql status
    </strong></code></pre>
4.  Once done with the installation login to the default database  `postgres` with  default user `postgres`  follow the below command to login to default database.

    <pre class="language-bash"><code class="lang-bash"><strong>sudo -u postgres psql
    </strong></code></pre>
5. After logged in you can check the connection to the database and list of databases and users and tables information using below commands.\
   `\conninfo` - To check the connection\
   `\l` -  list databases\
   `\du` - list users\
   `\d` - list tables - press q to exit\
   `\q -`  exit from the database
6. Since the default “postgres” user does not have a password, you should set it yourself using below command.\
   `\password postgres` - to set the password it will ask for the password give random password like this - `xwfJhfI9tK`\
   Note : It won't allow @ or # or - in the passwords.
7. Once you setup the password for postgres user exit from the database and you have to do some configurations on the server level. Follow the below steps for the same.
   1.  Open postgresql.conf file, find the below parameter uncomment it and set it to listen on all IP addresses and increase the connections:

       ```bash
       vim /etc/postgresql/14/main/postgresql.conf
       listen_addresses = '*'
       max_connections = 500
       ```
   2.  Open pg\_hba.conf file and allow TCP/IP connections (host) to all databases (all) for all users (all) with any IPv4 address (0.0.0.0/0) using an scram-sha-256 encrypted password for authentication and save the file.

       ```bash
       vim /etc/postgresql/14/main/pg_hba.conf
       ```

       <figure><img src="../../.gitbook/assets/postgres1 (2).png" alt=""><figcaption></figcaption></figure>
   3.  Restart PostgreSQL service to load configuration changes.

       ```bash
       sudo systemctl restart postgresql
       ```
   4.  And make sure your system is listening to the 5432 port that is reserved for PostgreSQL.

       ```bash
       ss -nlt | grep 5432
       ```
8.  Now login back to the postgresdb using the command below. Provide the password that you have configured for postgres db.

    ```bash
    psql -U postgres -h localhost
    ```
9.  Creat the databases for socialregistry and odk using below commands and put a random password in the command.

    <pre class="language-bash"><code class="lang-bash"><strong>CREATE ROLE socialregistryuser WITH LOGIN NOSUPERUSER CREATEDB CREATEROLE INHERIT REPLICATION CONNECTION LIMIT -1 PASSWORD '&#x3C;**provide password**>';
    </strong><strong>CREATE DATABASE socialregistrydb WITH OWNER = socialregistryuser TEMPLATE = template0 ENCODING = 'UTF8' TABLESPACE = pg_default CONNECTION LIMIT = -1;
    </strong><strong>
    </strong><strong>CREATE ROLE odkuser WITH LOGIN NOSUPERUSER CREATEDB CREATEROLE INHERIT REPLICATION CONNECTION LIMIT -1 PASSWORD '&#x3C;**provide password**>';
    </strong><strong>CREATE DATABASE odkdb WITH OWNER = odkuser TEMPLATE = template0 ENCODING = 'UTF8' TABLESPACE = pg_default CONNECTION LIMIT = -1;
    </strong></code></pre>
10. Try to connect to both the databases and verify.

    <pre class="language-bash"><code class="lang-bash"><strong>psql -U socialregistryuser -h localhost -d socialregistrydb
    </strong><strong>psql -U odkuser -h localhost -d odkdb
    </strong></code></pre>

## Configure external databases in the social registry deployment from the rancher-ui

1. Go to the rancher-ui and start installing socialregistry and update the below parametes as shown below in the **Edit YAML** and install the services.
   1. Make the default postgresql **enabled** equals to **false.**
   2. Add the below parameters in the last section of postgresql.\
      `externalDatabase:` \
      &#x20;   `create: false` \
      &#x20;   `database: socialregistrydb` \
      &#x20;   `host: <IP address of External DB>`\
      &#x20;   `password: <password for SR DB>`\
      &#x20;   `port: 5432` \
      &#x20;   `user: socialregistryuser`
   3. Add the below parameters in the last section of ODK.\
      `odk-central:` \
      &#x20;  `backend:` \
      &#x20;    `envVars:`\
      &#x20;      `DB_HOST: <IP address of External DB>`\
      &#x20;      `DB_NAME: odkdb`\
      &#x20;      `DB_USER: odkuser`\
      &#x20;      `envVarsFrom:` \
      &#x20;      `DB_PASSWORD: <password for ODK DB>`\
      &#x20; `postgresql:` \
      &#x20;    `enabled: false`
   4. Add the below parameters in the last section of reportingInit.\
      envVars: \
      &#x20;     DB\_NAME: socialregistrydb \
      &#x20;     DB\_HOST: `<IP address of External DB>` \
      &#x20;     DB\_USER: socialregistryuser\
      envVarsFrom: \
      &#x20;      DB\_PASS: `<password for SR DB>`\

2. Make sure the SR and ODK connected to the external databases and verify the tables by logging into the external database.
