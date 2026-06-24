---
description: >-
  Guide to back up and restore PostgreSQL, MinIO, and Keycloak on an OpenG2P
  single machine deployment.
---

# Single Machine Backup & Restore Guide

## 1. Overview

This document explains how to back up and restore the three critical stateful components running on the OpenG2P single machine deployment: PostgreSQL, MinIO, and Keycloak. It covers what each component is, why it needs a backup, the exact commands to run, and how to verify the restore worked.

### 1.1 What Needs to be backed up

Not everything in the cluster needs a backup. Only components that store persistent data matter. Stateless pods like \<your-app>, \<your-app> frontend, and Redis are automatically restarted by Kubernetes if they crash — no backup needed.

<br>

| Component  | Pod Name                    | What It Stores                                     | Priority |
| ---------- | --------------------------- | -------------------------------------------------- | -------- |
| PostgreSQL | \<postgresql-pod>           | All application databases — application databases  | Critical |
| PostgreSQL | <\<keycloak-pg-secret>-pod> | Keycloak's own database                            | Critical |
| MinIO      | \<minio-pod>                | Uploaded files, form attachments, documents        | High     |
| Keycloak   | \<keycloak-pod>             | Realm config — users, clients, roles, SSO settings | High     |

### 1.2 Restore order

When restoring a fresh system, always follow this order. Keycloak depends on its database existing first.

1. Restore PostgreSQL (\<pg-secret>)
2. Restore PostgreSQL (\<keycloak-pg-secret>)
3. Restore MinIO buckets
4. Restore Keycloak realms
5. Restart all pods

{% hint style="warning" %}
&#x20;Never restore Keycloak realm before PostgreSQL. Keycloak needs its database to be running before the realm import can succeed.
{% endhint %}

## 2. Prerequisites

### 2.1 SSH access to node

All backup commands are run on the node itself. Connect from your laptop using:

```
ssh -i ~/Downloads/your-key.pem <user>@<node-ip>
```

Once connected, switch to root:

```
sudo -i
```

### 2.2 Create backup directories

Run once on the node to create the backup folder structure:

```
mkdir -p /opt/backups/postgres
mkdir -p /opt/backups/minio
mkdir -p /opt/backups/keycloak
```

{% hint style="success" %}
Verify with: ls /opt/backups/ — you should see three folders: postgres, minio, keycloak
{% endhint %}

### 2.3 Install MinIO client (mc)

The mc tool is needed for MinIO backup. Install it once on the node:

```
curl -sL https://dl.min.io/client/mc/release/linux-amd64/mc -o /usr/local/bin/mc && chmod +x /usr/local/bin/mc
```

Verify installation:

```
mc --version
```

### 2.4 Credentials reference

Keep these credentials secure. They are needed for backup and restore commands.

| Component             | Secret Name           | Username | Password                      |
| --------------------- | --------------------- | -------- | ----------------------------- |
| \<pg-secret>          | \<pg-secret>          | postgres | \<postgres-password>          |
| \<keycloak-pg-secret> | \<keycloak-pg-secret> | postgres | \<keycloak-postgres-password> |
| MinIO                 | \<minio-secret>       | admin    | \<minio-secret-key>           |
| Keycloak (commons)    | \<keycloak-secret>    | admin    | \<keycloak-admin-password>    |

To re-fetch any password from the cluster: kubectl get secret \<secret-name> -n \<namespace> -o jsonpath='{.data.\<key>}' | base64 -d && echo

## 3. Taking backups

### 3.1 PostgreSQL backup

PostgreSQL stores all application data. We use pg\_dumpall which exports every database, table, user, and permission into a single compressed SQL file. This file can recreate everything from scratch on a fresh PostgreSQL instance.

#### Backup \<pg-secret> (main databases)

This backs up: \<app-database>, \<app-database>, odkdb, \<app-db>, commons\_services\_iam, commons\_services\_master\_data, \<app-database>.

```
kubectl exec -n <namespace> <postgresql-pod> -- \
    bash -c "PGPASSWORD=<postgres-password> pg_dumpall -U postgres" \
    | gzip > /opt/backups/postgres/commons-postgres-$(date +%Y-%m-%d).sql.gz
```

Verify the file was created:

```
ls -lh /opt/backups/postgres/
```

{% hint style="success" %}
&#x20;Expected output: a .sql.gz file of around 150-200KB. If the file is 0 bytes, the backup failed.
{% endhint %}

#### Backup \<keycloak-pg-secret>

This backs up the Keycloak database separately.

```
kubectl exec -n <namespace> <<keycloak-pg-secret>-pod> -- \
bash -c "PGPASSWORD=<keycloak-postgres-password> pg_dumpall -U postgres" \
  | gzip > /opt/backups/postgres/keycloak-postgres-$(date +%Y-%m-%d).sql.gz
```

Verify:

```
ls -lh /opt/backups/postgres/
```

{% hint style="success" %}
Expected: a file of around 30-50KB.
{% endhint %}

### 3.2 MinIO backup

MinIO stores all uploaded files and attachments. We use the mc mirror command which copies all buckets and their contents to a local folder.

#### Configure mc alias (run once)

```
mc alias set local-minio http://<minio-cluster-ip>:9000 admin <minio-secret-key>
```

#### Run the mirror backup

```
mc mirror --preserve local-minio /opt/backups/minio/
```

Verify:

```
ls -lh /opt/backups/minio/
```

{% hint style="warning" %}
If MinIO has no data yet, the folder will be empty. That is normal — the process is correct and will capture files once users start uploading.
{% endhint %}

### 3.3 Keycloak realm export

Keycloak organises everything into realms. We export each realm as a JSON file using the Keycloak Admin API. The export includes all clients, roles, users, and SSO configurations.

Your cluster has two realms: staff and master.

#### Export staff realm

```
kubectl exec -n <namespace> <keycloak-pod> -- \
  bash -c "TOKEN=\$(curl -s -X POST http://localhost:8080/realms/master/protocol/openid-connect/token \
  -d 'client_id=admin-cli&grant_type=password&username=admin&password=<keycloak-admin-password>' \
  | grep -o '\"access_token\":\"[^\"]*\"' | cut -d'\"' -f4) && \
  curl -s -X POST -H \"Authorization: Bearer \$TOKEN\" \
  'http://localhost:8080/admin/realms/staff/partial-export?exportClients=true&exportGroupsAndRoles=true'" \
  > /opt/backups/keycloak/commons-realm-staff-$(date +%Y-%m-%d).json
```

#### Export master realm

```
kubectl exec -n <namespace> <keycloak-pod> -- \
  bash -c "TOKEN=\$(curl -s -X POST http://localhost:8080/realms/master/protocol/openid-connect/token \
  -d 'client_id=admin-cli&grant_type=password&username=admin&password=<keycloak-admin-password>' \
  | grep -o '\"access_token\":\"[^\"]*\"' | cut -d'\"' -f4) && \
  curl -s -X POST -H \"Authorization: Bearer \$TOKEN\" \
  'http://localhost:8080/admin/realms/master/partial-export?exportClients=true&exportGroupsAndRoles=true'" \
  > /opt/backups/keycloak/commons-realm-master-$(date +%Y-%m-%d).json

```

Verify both files:

```
ls -lh /opt/backups/keycloak/
```

{% hint style="success" %}
Expected: staff realm around 80KB and master realm around 52KB. Files smaller than 1KB mean the export failed.
{% endhint %}

### 3.4 Copy backups to laptop

Run this command on your laptop (not on the node) to pull all backup files locally:

```
scp -i ~/Downloads/your-key.pem -r \
  <user>@<node-ip>:/opt/backups/ \
  ~/backups/
```

Verify on laptop:

```
ls -lh ~/backups/backups/postgres/
ls -lh ~/backups/backups/keycloak/
```

## 4. Automating with cron job

A cron job is a scheduled task on Linux. Instead of running backup commands manually every day, a cron job runs them automatically at a fixed time — in our case, every day at 2 AM.

### 4.1 Create the backup script

On the node, create a single script that runs all backups:

```
cat > /opt/backup-scripts/daily_backup.sh << 'EOF'
#!/bin/bash
set -e
DATE=$(date +%Y-%m-%d)
LOG=/opt/backups/logs/backup_${DATE}.log
mkdir -p /opt/backups/postgres /opt/backups/minio /opt/backups/keycloak /opt/backups/logs


echo "[$(date)] Starting backup..." >> $LOG


# PostgreSQL commons
kubectl exec -n <namespace> <postgresql-pod> -- \
  bash -c "PGPASSWORD=<postgres-password> pg_dumpall -U postgres" \
  | gzip > /opt/backups/postgres/commons-postgres-${DATE}.sql.gz
echo "[$(date)] PostgreSQL commons done" >> $LOG


# PostgreSQL keycloak
kubectl exec -n <namespace> <<keycloak-pg-secret>-pod> -- \
  bash -c "PGPASSWORD=<keycloak-postgres-password> pg_dumpall -U postgres" \
  | gzip > /opt/backups/postgres/keycloak-postgres-${DATE}.sql.gz
echo "[$(date)] PostgreSQL keycloak done" >> $LOG


# MinIO
mc mirror --preserve local-minio /opt/backups/minio/
echo "[$(date)] MinIO done" >> $LOG


# Keycloak realms
TOKEN=$(kubectl exec -n <namespace> <keycloak-pod> -- \
  bash -c "curl -s -X POST http://localhost:8080/realms/master/protocol/openid-connect/token \
  -d 'client_id=admin-cli&grant_type=password&username=admin&password=<keycloak-admin-password>' \
  | grep -o '\"access_token\":\"[^\"]*\"' | cut -d'\"' -f4")


kubectl exec -n <namespace> <keycloak-pod> -- \
  bash -c "curl -s -X POST -H 'Authorization: Bearer ${TOKEN}' \
  'http://localhost:8080/admin/realms/staff/partial-export?exportClients=true&exportGroupsAndRoles=true'" \
  > /opt/backups/keycloak/commons-realm-staff-${DATE}.json
echo "[$(date)] Keycloak realms done" >> $LOG
# Delete backups older than 7 days
find /opt/backups/postgres -mtime +7 -delete
find /opt/backups/keycloak -mtime +7 -delete
echo "[$(date)] Cleanup done. Backup complete." >> $LOG
EOF
```

Make the script executable:

```
chmod +x /opt/backup-scripts/daily_backup.sh
```

### 4.2 Schedule with cron

Open the crontab editor:

```
crontab -e
```

Add this line at the bottom of the file:

```
0 2 * * * /opt/backup-scripts/daily_backup.sh >> /opt/backups/logs/cron.log 2>&1
```

This means: run the backup script every day at 2:00 AM.

Verify the cron job was saved:

```
crontab -l
```

{% hint style="success" %}
To test the script manually without waiting for 2 AM: bash /opt/backup-scripts/daily\_backup.sh
{% endhint %}

## 5. Restore procedures

Use these procedures when the system needs to be recovered. Always restore in the order shown — PostgreSQL first, Keycloak last.

### 5.1 Restore PostgreSQL

This procedure restores all application databases from a backup file. Use this when PostgreSQL data is lost or corrupted.

#### Step 1 — Copy backup file into the pod

```
kubectl cp /opt/backups/postgres/commons-postgres-2026-04-15.sql.gz \
  <namespace>/<postgresql-pod>:/tmp/commons-postgres.sql.gz
```

#### Step 2 — Restore all databases

```
kubectl exec -n <namespace> <postgresql-pod> -- \
  bash -c "gunzip -c /tmp/commons-postgres.sql.gz | PGPASSWORD=<postgres-password> psql -U postgres"
```

{% hint style="warning" %}
You will see errors like 'role already exists' — these are normal and safe to ignore. The data restores correctly despite these messages.
{% endhint %}

#### Step 3 — Verify all databases are back

kubectl exec -n \<namespace> \<postgresql-pod> -- \\

```
  bash -c "PGPASSWORD=<postgres-password> psql -U postgres -c '\\l'"
```

You should see all these databases in the list:

* commons\_services\_iam
* commons\_services\_master\_data
* keycloak
* \<app-database>
* \<app-database>
* \<app-database>
* odkdb
* \<app-db>

#### Restore keycloak postgreSQL

```
# Restore Keycloak PostgreSQL
kubectl cp /opt/backups/postgres/postgres-keycloak-<date>.sql.gz \
  <namespace>/<keycloak-postgresql-pod>:/tmp/keycloak-restore.sql.gz

kubectl exec -n <namespace> <keycloak-postgresql-pod> -- \
  bash -c "gunzip -c /tmp/keycloak-restore.sql.gz | \
  PGPASSWORD=<keycloak-postgres-password> psql -U postgres"
```

### 5.2 Restore MinIO

This procedure restores all MinIO buckets and files from the backup folder.

#### Step 1 — Configure mc alias (if not already done)

```
mc alias set local-minio http://<minio-cluster-ip>:9000 admin <minio-secret-key>
```

#### Step 2 — Mirror backup back to MinIO

```
mc mirror --preserve /opt/backups/minio/ local-minio
```

#### Step 3 — Verify buckets are restored

```
mc ls local-minio
```

✓ All buckets that existed at backup time should now appear in the list.

### 5.3 Restore keycloak realms

This procedure reimports the Keycloak realm configuration — clients, roles, users, and SSO settings — from the JSON backup files.

#### Step 1 — Get auth token

```
TOKEN=$(kubectl exec -n <namespace> <keycloak-pod> -- \
  bash -c "curl -s -X POST http://localhost:8080/realms/master/protocol/openid-connect/token \
  -d 'client_id=admin-cli&grant_type=password&username=admin&password=<keycloak-admin-password>' \
  | grep -o '\"access_token\":\"[^\"]*\"' | cut -d'\"' -f4")
```

#### Step 2 — Copy realm JSON into the pod

```
kubectl cp /opt/backups/keycloak/commons-realm-staff-2026-04-16.json \
  <namespace>/<keycloak-pod>:/tmp/realm-staff.json
```

#### Step 3 — Import the realm

```
kubectl exec -n <namespace> <keycloak-pod> -- \
  bash -c "curl -s -X POST -H 'Authorization: Bearer $TOKEN' \
  -H 'Content-Type: application/json' \
  -d @/tmp/realm-staff.json \
  http://localhost:8080/admin/realms"
```

{% hint style="success" %}
Repeat Step 2 and Step 3 for the master realm using commons-realm-master-2026-04-16.json
{% endhint %}

