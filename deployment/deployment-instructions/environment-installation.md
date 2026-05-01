# Environment Installation

The instructions here pertain to the deployment of [common components](../concepts/openg2p-commons-helm-chart.md) for an environment on the Kubernetes cluster. All components are installed in the same namespace using two Helm charts: **openg2p-commons-base** (infrastructure) and **openg2p-commons-services** (applications).

## Prerequisites

Before you deploy, make sure the following are in place:

* [Infrastructure setup](infrastructure-setup.md) is completed
* Domain name with wildcard SSL certificate for `*.<environment>.<domain>` (e.g., `*.trial.openg2p.org`)
* **Project Owner access** on the target namespace
* `kubectl`, `helm`, `jq` installed on your machine

## Installation using the command line

### Step 1: Install base infrastructure

```bash
cd charts/openg2p-commons-base

./install-base.sh <namespace> <release-name> <base-domain> [extra-helm-args...]
```

**Example:**

```bash
./install-base.sh trial commons trial.openg2p.org
```

This installs PostgreSQL, Keycloak, Redis, Kafka, OpenSearch, MinIO, and all init jobs. Keycloak will be available at `https://keycloak.<base-domain>`.

The script waits for all infrastructure to be ready before returning.

### Step 2: Install application services

```bash
cd charts/openg2p-commons-services

./install.sh <namespace> <release-name> <base-release-name> <base-domain> [extra-helm-args...]
```

**Example:**

```bash
./install.sh trial commons-services commons trial.openg2p.org
```

Parameters:

* `namespace` - must match the base chart namespace
* `release-name` - Helm release name for services (e.g., `commons-services`)
* `base-release-name` - release name used for base chart (e.g., `commons`)
* `base-domain` - same domain used for base chart

### Re-running

Both scripts use `helm upgrade --install`, so they can be safely re-run to apply changes.

## Installation using Rancher UI

1. Log in to Rancher admin console.
2. Select your cluster.
3. Under **Apps -> Repositories** click on Create to add a repository.
4. Provide Name as `openg2p` and target HTTPS Index URL as `https://openg2p.github.io/openg2p-helm/rancher` and click Create.
5. To display prerelease versions, click on your user avatar in the upper right corner, then click on `Include Prerelease Versions` under Preferences.
6. Select the namespace from the namespace filter on the top-right.
7. Navigate to **Apps -> Charts**. You should see **OpenG2P Commons Base** and **OpenG2P Commons Services** listed.
8. **Install OpenG2P Commons Base first:**
   * Select the latest version and click Install.
   * Set the installation name to **`commons`**.
   * Configure the **Base Domain** (e.g., `trial.openg2p.org`).
   * Keycloak is enabled by default and will be installed in this namespace.
   * Keycloak image tag can be customized (default: `24.0.5-debian-12-r1-g2p1`).
   * Disable the **Wait** checkbox under Helm Options.
   * Click Install.
9. **Wait for base infrastructure to be ready** (all pods in Running state).
10. **Install OpenG2P Commons Services:**
    * Select the latest version and click Install.
    * Set the installation name to **`commons-services`**.
    * Configure the **Base Domain** (must match the base chart).
    * Disable the **Wait** checkbox under Helm Options.
    * Click Install.

## What gets created

### Keycloak (auto-configured)

Keycloak is installed per-environment with:

* **URL:** `https://keycloak.<base-domain>`
* **Admin user:** `admin` (password auto-generated, stored in K8s secret `<release>-keycloak`)
* **Realms:** `master` and `staff`
* **Themes:** `openg2p-admin` (master realm), `staff-portal` (staff realm)
* **OIDC Clients** (in `staff` realm): `openg2p-superset`, `openg2p-opensearch`, `openg2p-kafka`, `openg2p-minio`, `openg2p-odk`, `staff-portal`

To retrieve the Keycloak admin password:

```bash
kubectl get secret commons-keycloak -n <namespace> -o jsonpath='{.data.admin-password}' | base64 -d
```

### Databases

PostgreSQL databases are created automatically for all services. User passwords are stored in K8s secrets.

## Post Installation

### Assigning roles to users

Create [Keycloak client roles](https://www.keycloak.org/docs/latest/server_admin/#con-client-roles_server_administration_guide) for the following components and assign them to users:

| Component             | Client               | Role name      |
| --------------------- | -------------------- | -------------- |
| OpenSearch Dashboards | `openg2p-opensearch` | `admin`        |
| Kafka UI              | `openg2p-kafka`      | `Admin`        |
| Apache Superset       | `openg2p-superset`   | `Admin`        |
| MinIO Console         | `openg2p-minio`      | `consoleAdmin` |

### Assigning roles to clients

* For Social Registry to access Keymanager APIs, create a realm role `KEYMANAGER_ADMIN` and assign it as a service account role to the Social Registry Keycloak client.

{% hint style="info" %}
By default, the Superset username and password are **admin / admin**. To change this, run the following command inside the superset pod:\
`superset fab reset-password --username admin --password <NEW_PASSWORD>`
{% endhint %}

## External PostgreSQL

For production deployments where PostgreSQL runs outside Kubernetes (a managed service like AWS RDS / Cloud SQL, or a dedicated VM), follow these steps.

### Why pre-create the secret?

Helm cannot create a Kubernetes secret on the fly that subcharts reference at render time. Several components — `postgres-init`, Keycloak's external database config, the per-service `postgresInit` jobs (keymanager, eSignet, mock-identity-system, IAM service, audit-manager) — all read the PostgreSQL **superuser password** from the same Kubernetes secret. So the secret must exist **before** `helm install` runs.

### Step 1: Pre-create the superuser secret

```bash
kubectl create namespace <namespace> 2>/dev/null || true

kubectl create secret generic external-pg-superuser \
  -n <namespace> \
  --from-literal=postgres-password='<your-postgres-superuser-password>'
```

The default key name is `postgres-password`. If your secret uses a different key (e.g. `password` from a managed-service-generated secret), pass `--set global.postgresqlSecretKey=<key-name>` during install.

### Step 2: Install with external PostgreSQL overrides

```bash
./install-base.sh <namespace> commons <base-domain> \
  --set postgresql.enabled=false \
  --set global.postgresqlHost=<external-pg-hostname-or-ip> \
  --set global.postgresqlSecret=external-pg-superuser
```

* **`postgresql.enabled=false`** — disables the embedded Bitnami PostgreSQL chart
* **`global.postgresqlHost`** — fully qualified hostname or IP of your external server (must be reachable from the cluster's pod network)
* **`global.postgresqlSecret`** — name of the secret you created in Step 1

The install script verifies that the secret exists before proceeding.

### Step 3: Install services with the same overrides

```bash
./install.sh <namespace> commons-services commons <base-domain> \
  --set global.postgresqlHost=<external-pg-hostname-or-ip> \
  --set global.postgresqlSecret=external-pg-superuser
```

### What gets created in PostgreSQL

The `postgres-init` job (running as a regular Kubernetes Job) connects to the external server using the superuser credentials and creates:

* Databases: `superset`, `odkdb`, `mosip_keymgr`, `mosip_mockidentitysystem`, `mosip_esignet`, `keycloak`, plus `<release>_iam` and `<release>_auditmanager` from the services chart
* One database user per database with auto-generated passwords
* Per-user secrets stored in Kubernetes (`superset-db-user`, `odk-db-user`, `keymgr-db-user`, etc.)

Your external PostgreSQL user must therefore have **`CREATE DATABASE` and `CREATE ROLE`** privileges. A typical RDS master user works.

### Notes for managed PostgreSQL (RDS / Cloud SQL)

* Some managed services don't allow `CREATE DATABASE` for non-master users — use the master credentials
* The connection must use the standard PostgreSQL port `5432` (override `postgres-init.postgresql.port` if your service exposes a different port)
* TLS connections are not yet configured by default — if your provider requires SSL, you may need to extend the postgres-init job

## Modules

Install the modules and other utility apps individually using their respective instructions:

1. [Registry](../../products/registry/registry/_archive/social-registry/deployment/registry-installation.md)
2. [PBMS](https://docs.openg2p.org/pbms/deployment)
3. [SPAR](https://docs.openg2p.org/spar/deployment)
4. [G2P Bridge](https://docs.openg2p.org/g2p-bridge/deployment#installation-using-rancher-ui)
5. Beneficiary Portal
