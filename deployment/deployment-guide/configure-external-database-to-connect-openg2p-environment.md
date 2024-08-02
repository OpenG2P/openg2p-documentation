---
layout:
  title:
    visible: true
  description:
    visible: false
  tableOfContents:
    visible: true
  outline:
    visible: true
  pagination:
    visible: true
---

# Configure External Database to Connect OpenG2P Environment

This document provides instructions to setup and install external database for OpenG2P environments.

## Prerequisites <a href="#prerequisites" id="prerequisites"></a>

* Make sure you have the hardware required for the external database setup.

## Installation and configuration

1. Log in to the external database node.&#x20;
2.  Install PostgreSQL using below commands.

    <pre class="language-bash"><code class="lang-bash"><strong>sudo apt update
    </strong><strong>sudo apt install postgresql
    </strong></code></pre>
3.  After the installation of postgreSQL, use the below command to check the status.

    <pre class="language-bash"><code class="lang-bash"><strong>service postgresql status
    </strong></code></pre>
4.  Use the command below to log into the default postgres database using the default user, postgres, following a successful installation.&#x20;

    <pre class="language-bash"><code class="lang-bash"><strong>sudo -u postgres psql
    </strong></code></pre>
5. After you logged in, use the command below to confirm the database connection and details on the list of databases, users, and tables.\
   `\conninfo` - To check the connection\
   `\l` -  list databases\
   `\du` - list users\
   `\d` - list tables - press q to exit\
   `\q -`  exit from the database
6. You should use the command below to set one for yourself, as the default _**postgres**_ user does not have a password.\
   `\password postgres` - to set the password, the password must have the combination of lowercase, uppercase, number. For example, `xwfJhfI9tK`\
   Note :  The password must not have the special characters @, #, or -.
7. After setting up the postgres password, the user must exit from the database and run the command below to perform some server-level configurations.
   1.  Access the postgresql.conf file, locate the parameter below, uncomment it, set it to listen on all IP addresses, and configure it to increase the number of connections.

       ```bash
       vim /etc/postgresql/14/main/postgresql.conf
       listen_addresses = '*'
       max_connections = 500
       ```
   2.  Acess pg\_hba.conf file and allow TCP/IP connections (host) to all databases (all) for all users (all) with any IPv4 address (0.0.0.0/0) using an scram-sha-256 encrypted password for authentication and save the file.

       ```bash
       vim /etc/postgresql/14/main/pg_hba.conf
       ```

       <figure><img src="../../.gitbook/assets/postgres1 (2).png" alt=""><figcaption></figcaption></figure>
   3.  Restart PostgreSQL service to load configuration changes.

       ```bash
       sudo systemctl restart postgresql
       ```
   4.  Make sure your system is listening to the 5432 port that is reserved for PostgreSQL.

       ```bash
       ss -nlt | grep 5432
       ```
8.  Use the command below to log back into postgresdb now. Provide the postgres database, the password that you have configured.

    ```bash
    psql -U postgres -h localhost
    ```
9.  Use the command below to create the socialregistry and ODK databases, use a random password in each command.

    <pre class="language-bash"><code class="lang-bash"><strong>CREATE ROLE socialregistryuser WITH LOGIN NOSUPERUSER CREATEDB CREATEROLE INHERIT REPLICATION CONNECTION LIMIT -1 PASSWORD '&#x3C;**provide password**>';
    </strong><strong>CREATE DATABASE socialregistrydb WITH OWNER = socialregistryuser TEMPLATE = template0 ENCODING = 'UTF8' TABLESPACE = pg_default CONNECTION LIMIT = -1;
    </strong><strong>
    </strong><strong>CREATE ROLE odkuser WITH LOGIN NOSUPERUSER CREATEDB CREATEROLE INHERIT REPLICATION CONNECTION LIMIT -1 PASSWORD '&#x3C;**provide password**>';
    </strong><strong>CREATE DATABASE odkdb WITH OWNER = odkuser TEMPLATE = template0 ENCODING = 'UTF8' TABLESPACE = pg_default CONNECTION LIMIT = -1;
    </strong></code></pre>
10. Try onnecting to both the databases and verify.

    <pre class="language-bash"><code class="lang-bash"><strong>psql -U socialregistryuser -h localhost -d socialregistrydb
    </strong><strong>psql -U odkuser -h localhost -d odkdb
    </strong></code></pre>

## Configure external databases in the social registry deployment from the rancher-ui

1. Access the rancher-ui to start installing the socialregistry and update the below parametes as shown below in the **Edit YAML** and install the services.
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
