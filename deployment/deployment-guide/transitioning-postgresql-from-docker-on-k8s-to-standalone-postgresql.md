---
description: >-
  This document describes how to migrate from Docker PostgreSQL to standalone
  PostgreSQL with existing data.
---

# Transitioning PostgreSQL From Docker on K8s to Standalone PostgreSQL

Migrating PostgreSQL from a Kubernetes cluster (running in Docker containers with NFS storage) to an external standalone instance is a strategic move for improving scalability, performance, and manageability in production. Below is a step-by-step guide to performing this transition with minimal disruption.

### Steps for migrating postgresql to an external instance:

1.  **Pre-Migration Planning**:

    * **Downtime Requirements**: Decide if you need minimal downtime (consider replication if necessary).
    * **Networking**: Verify that the new PostgreSQL instance is accessible, and configure firewalls or security groups.
    * **Scaling**: Ensure the new instance has enough CPU, memory, and storage for future needs.


2.  **Set Up the Standalone PostgreSQL Instance**.

    * For setting up **Standalone PostgreSQL Instance** Follow the guide up to 10th point given [here](https://docs.openg2p.org/deployment/deployment-guide/configure-external-database-to-connect-openg2p-environment).
    * In case a DB cluster needs to be created for high availability, follow the documentation [here](https://www.servermania.com/kb/articles/setup-postgresql-cluster).


3.  **Create a Backup of the Current Database.**

    * Follow the document here to [Access a Database from Outside the Cluster](https://docs.openg2p.org/deployment/deployment-guide/access-a-database-from-outside-the-cluster).
    *   To back up a PostgreSQL database using `pg_dump`, you can use the following command structure:

        ```bash
        pg_dump -c --if-exists -h <hostname> -p <port> -U <dbuser> -d "<dbname>" -f <backupfilename.dump>
        ```

        **Example:**

        ```bash
        pg_dump -c --if-exists -h localhost -p 5432 -U pbmsuser -d "pbmsdb" -f pbmsdb.dump
        ```

        This command connects to a PostgreSQL database and creates a dump of the specified database, saving it to a file.&#x20;


4.  **Restore the Backup to the External Instance**.

    *   Copy the `db.dump` file into your newly created PostgreSQL instance, and run the following command to restore the backup data into the empty database created in step 2. Ensure that the database is created before running the restore command.

        To restore a database from a dump file, use the following `psql` command:

        ```bash
        psql -U dbuser -h localhost -d dbname -f backupfile.dump
        ```

        Example for a specific user and database:

        ```bash
        psql -U pbmsuser -h localhost -d pbmsdb -f pbmsdb.dump
        ```
    * Then verify whether all the tables were created successfully after the restore.


5. **Update Application to Use the External Instance**.
   *   Go to the Rancher UI, select **Apps -> Installed Apps**, and choose the service you want to edit or upgrade. Edit the YAML file and update the following parameters to connect to the new external database.

       ```yaml
       #Make the default postgresql enabled equals to false.
       postgresql:
         auth:
           database: pbmsdb
           username: pbmsuser
         enabled: false
       ```

       ```yaml
       #Add the below parameters in the last section of default postgresql.
       externalDatabase:
         create: false
         database: socialregistrydb/pbmsdb
         host: <IP address of External DB>
         password: <password for DB>
         port: 5432
         user: socialregistryuser/pbmsuser
       ```
   *   Once you are done with the edit/upgrade, the Odoo service might fail to connect to the externally configured database and display an error message indicating that it is **unable to connect to the database**. This occurs because the service will attempt to connect to the previous database host. This happens due to the `post-init-openg2p.sh` script, which creates the `odoo.conf` file only once during deployment.

       To resolve this issue, you can exec into the pod and run the following command to update the `odoo.conf` file with the external database details:

       ```bash
       /post-init-openg2p.sh
       ```
   *   After running this command, restart the Odoo service. Once it is up and running, exec into the pod again and verify whether the external database details have been updated in the `odoo.conf` file located in the directory `/bitnami/odoo/conf/odoo.conf`.\
       \


       <figure><img src="../../.gitbook/assets/image (3).png" alt=""><figcaption><p>odoo-conf.png</p></figcaption></figure>


6. **Ensure Data Consistency** **after the migration.**
   * **Data Verification**: Use tools such as `pg_dump` or custom SQL queries to compare the data in the old and new databases. Ensure that no data was missed during the migration.
   * **Check Application Performance**: Monitor how the application performs with the new PostgreSQL instance. Ensure that query performance is optimal, and database latency is within acceptable limits.
