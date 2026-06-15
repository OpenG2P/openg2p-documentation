# Commons Helm Chart

The OpenG2P Commons Helm charts ([source code](https://github.com/OpenG2P/openg2p-commons-deployment)) install the shared infrastructure and application services that every OpenG2P environment depends on.

## Versions

| Chart                                          | Version                                                                         | Last Modified | Comments                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| ---------------------------------------------- | ------------------------------------------------------------------------------- | ------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| openg2p-commons-base, openg2p-commons-services | 0.0.0                                                                           | 02-Jun-2026   | **OpenSearch removed from commons** — pod logging is now handled cluster-wide by OpenTelemetry + Grafana Loki at the infrastructure layer (no per-service Fluentd Flow/Output in the charts). External-PostgreSQL configuration matured. This is the line the production automation installs by default. |
| openg2p-commons-base, openg2p-commons-services | [2.0.1](https://github.com/OpenG2P/openg2p-commons-deployment/tree/v2.0.1)      | 08-May-2026   | Substantial additions - dashboards, external postgres configurations.                                                                                                                                                                                                                                                                                                                                                                         |
| openg2p-commons-base, openg2p-commons-services | [2.0.0](https://github.com/OpenG2P/openg2p-commons-deployment/tree/v2.0.0)      | 21-Apr-2026 | Stable version. Two charts (base + services). Per-environment Keycloak. NOT COMPATIBLE WITH 1.x VERSIONS.                                                                                                                                                                                                                                                                                                                                     |
| openg2p-commons-base, openg2p-commons-services | [2.0.0-develop](https://github.com/OpenG2P/openg2p-commons-deployment/tree/2.0) | In progress | Default logs saved search added in OpenSearch (with ERROR filter toggle and pod-name substring search). Audit Manager service added to commons-services. Each chart now owns its own Keycloak clients (no cross-chart hostname duplication). Simplified DB names (e.g. `iam`, `audit_manager`, `master_data` — no release-name prefix). MinIO split into two VirtualServices (`minio.<domain>` for Console, `minio-api.<domain>` for S3 API). |

## Chart structure

The commons deployment is split into **two Helm charts**:

1. **`openg2p-commons-base`** - Infrastructure layer (installed first)
2. **`openg2p-commons-services`** - Application services layer (depends on base)

{% hint style="warning" %}
**Release names are deliberately fixed:** `openg2p-commons-base` must be installed as `commons` and `openg2p-commons-services` as `commons-services`. Cross-chart references (PostgreSQL host, Keycloak admin secret, IAM internal service URL, etc.) hardcode these names. Rancher's `catalog.cattle.io/release-name` annotation pre-fills and locks the field; the CLI install scripts reject any other name.
{% endhint %}

### openg2p-commons-base

Installs all infrastructure components:

| Component               | Description                                                         |
| ----------------------- | ------------------------------------------------------------------- |
| **Keycloak**            | Per-environment identity provider (OIDC/OAuth2)                     |
| **Keycloak Init**       | Creates realms, clients, and themes in Keycloak                     |
| **PostgreSQL**          | Shared database server                                              |
| **Postgres Init**       | Creates databases and users for all services                        |
| **Redis**               | Cache (without auth)                                                |
| **Redis Auth**          | Cache with authentication (for eSignet)                             |
| **Kafka**               | Message broker                                                      |
| **Kafka UI**            | Kafka management dashboard                                          |
| **MinIO**               | Object storage                                                      |
| **SoftHSM**             | Software HSM for key management                                     |
| **Mail**                | SMTP relay server (optional)                                        |
| **Client Secrets Sync** | Fetches OIDC client secrets from Keycloak and stores in K8s secrets |

### openg2p-commons-services

Installs application services:

| Component                 | Description                                                                        |
| ------------------------- | ---------------------------------------------------------------------------------- |
| **Superset**              | Data visualization and dashboards                                                  |
| **eSignet**               | Digital signature service                                                          |
| **Mock Identity System**  | Mock identity provider for testing                                                 |
| **Keymanager**            | Cryptographic key management                                                       |
| **ODK Central**           | Data collection                                                                    |
| **OpenG2P Master Data**   | Master data service                                                                |
| **Artifactory**           | Artifact repository                                                                |
| **OpenG2P IAM Service**   | Identity and access management API                                                 |
| **OpenG2P Audit Manager** | Centralized audit event collector (Kafka-backed, stores audit trail in PostgreSQL) |

## Configuration & behaviour

### Per-environment Keycloak

Each environment gets its own Keycloak instance (installed as part of `openg2p-commons-base`). This eliminates the need for a shared Keycloak server and simplifies credential management - the Keycloak admin user is used directly for client initialization.

* **External URL:** `https://keycloak.<baseDomain>` (browser-facing, used for OAuth redirects)
* **Internal URL:** `http://<release>-keycloak:80` (pod-to-pod, used by backend services for token validation, OIDC discovery)
* Admin credentials are auto-generated and stored in K8s secret `<release>-keycloak`
* Keycloak image tag is configurable (default: `24.0.5-debian-12-r1-g2p1`)
* OIDC clients are created automatically by `keycloak-init`
* Client secrets are synced to K8s secrets by `client-secrets-sync`
* Keycloak shares the commons PostgreSQL instance (dedicated `keycloak` database)

### Keycloak Realms and Clients

The `keycloak-init` job creates:

* **`master` realm** - with `openg2p-admin` login and admin themes
* **`staff` realm** - with `staff-portal` login and admin themes, containing OIDC clients (each chart owns its own — base creates `openg2p-kafka`, `openg2p-minio`; services creates `openg2p-superset`, `openg2p-odk`, `staff-portal`):
  * `openg2p-kafka`, `openg2p-minio`, `openg2p-superset`, `openg2p-odk`, `staff-portal`

### Keycloak Themes

Themes are specified per realm in the `keycloak-init` configuration:

```yaml
keycloak-init:
  realms:
    master:
      themes:
        loginTheme: openg2p-admin
        adminTheme: openg2p-admin
      clients: []
    staff:
      themes:
        loginTheme: staff-portal
        adminTheme: staff-portal
      clients:
        - clientId: staff-portal
          name: Staff Portal
          redirectUris: ["*"]
```

### Shared PostgreSQL

All services (including Keycloak) share the same PostgreSQL instance. The `postgres-init` job creates dedicated databases and users for each service. For production deployments, an external PostgreSQL server can be used — see the [External PostgreSQL](openg2p-commons-helm-chart.md#external-postgresql) section below for the full setup steps.

### MinIO Console vs S3 API

MinIO exposes two ports on a single Kubernetes Service: **9001 (Console UI)** and **9000 (S3 API)**. To route browser traffic to the console and S3-client traffic to the API without manual port juggling, the chart creates **two Istio VirtualServices**:

* `minio.<baseDomain>` → port 9001 (Console UI)
* `minio-api.<baseDomain>` → port 9000 (S3 API)

Pod-to-pod S3 calls (e.g., from ODK Central) use the internal cluster service `http://commons-minio:9000` — they don't go through Istio. Both hostnames work out of the box on a fresh install; no manual VirtualService edits required.

### Internal vs External URLs

The charts maintain two Keycloak URL paths:

* `global.keycloakInternalUrl` — used by backend pods (OIDC discovery, token validation, JWK fetching). Points to the in-cluster Keycloak service via HTTP.
* `global.keycloakBaseUrl` / `global.keycloakExternalIssuerUrl` — used for browser-facing OAuth redirects. Points to the external HTTPS URL.

This separation ensures backend services work without external DNS, while browsers are correctly redirected to the public Keycloak URL.

### Logging

The commons charts **do not handle logging**. Pod logs are collected cluster-wide at the **infrastructure layer** by the OpenTelemetry + Grafana Loki stack (an OTel agent DaemonSet tails every pod automatically and ships to Loki, queried via Grafana). The per-service Fluentd `Flow`/`Output` resources that earlier versions used to ship logs to OpenSearch have been removed — there is no app-level logging configuration in these charts anymore.

{% hint style="info" %}
This change retired the OpenSearch + OpenSearch Dashboards components and the Fluent Operator from commons. For the cluster-wide logging pipeline (OTel agent → gateway → Loki, with LogQL alert rules), see the [production infrastructure automation](../operations/deployment/infrastructure-setup/production-automation/).
{% endhint %}

### Resource Limits (Sandbox vs Production)

All components are configured with **sandbox-friendly resource limits** by default — designed for development and testing environments where Keycloak and Kafka see minimal load. This prevents components like Keycloak from consuming 3GB+ of RAM on idle clusters.

**Default sandbox limits:**

| Component                   | Memory Limit | JVM Heap | Notes                                                           |
| --------------------------- | ------------ | -------- | --------------------------------------------------------------- |
| Keycloak                    | 1Gi          | 512m     | Increase to 2Gi / 1g for production                             |
| PostgreSQL                  | 1Gi          | N/A      | Increase to 2-4Gi for production                                |
| Kafka (controller + broker) | 1Gi each     | 512m     | Increase to 2Gi / 1g for production                             |
| MinIO                       | 512Mi        | N/A      | Increase to 1-2Gi for heavy S3 usage                            |
| Redis (x2)                  | 128Mi each   | N/A      | Sufficient for most workloads                                   |
| Kafka UI                    | 512Mi        | 256m     | Sufficient for most workloads                                   |
| SoftHSM                     | 128Mi        | N/A      | Sufficient                                                      |
| Artifactory                 | 512Mi        | N/A      | Sufficient                                                      |

To scale up for production, override the relevant values:

```bash
# Example: scale Keycloak for production
--set keycloak.resources.limits.memory=2Gi \
--set keycloak.extraEnvVars[2].value="-Xms512m -Xmx1g"
```

**How to detect resource constraints:**

* **OOMKilled** restarts — check `kubectl get pods` for high restart counts
* **CPU throttling** — check `kubectl top pods` for CPU at limit
* **Application-specific** — Kafka consumer lag increasing, Keycloak login latency

Enable Rancher Monitoring (Prometheus + Grafana) to get dashboards and alerts for memory/CPU pressure across all pods.

## External PostgreSQL

By default, **commons-base** installs an embedded PostgreSQL (Bitnami chart) inside the cluster. For production deployments, you typically want to use an external PostgreSQL server — a managed service (AWS RDS, Cloud SQL) or a dedicated VM. The charts support this with a few configuration overrides.

### What gets created in PostgreSQL

The `postgres-init` job (running as a regular Kubernetes Job) connects to PostgreSQL using the **superuser** credentials and creates:

* Databases (one per service): `superset`, `odkdb`, `mosip_keymgr`, `mosip_mockidentitysystem`, `mosip_esignet`, `keycloak`, plus `<release>_iam` and `<release>_auditmanager` from the services chart
* One database user per database, with a randomly generated password
* Per-user secrets in Kubernetes (`superset-db-user`, `odk-db-user`, `keymgr-db-user`, `keycloak-db-user`, `commons-services-iam`, `commons-services-auditmanager`, etc.) — services read these for their own connections

So your **external PostgreSQL user must have `CREATE DATABASE` and `CREATE ROLE` privileges**. A managed-service master user (e.g. RDS master) typically works.

### Configuration overrides

Three globals control PostgreSQL connectivity. They are wired identically in both `openg2p-commons-base` and `openg2p-commons-services`:

| Global                       | Purpose                                           | Default (embedded)     | Set for external                             |
| ---------------------------- | ------------------------------------------------- | ---------------------- | -------------------------------------------- |
| `global.postgresqlHost`      | Hostname or IP of the PostgreSQL server           | `<release>-postgresql` | External hostname or IP                      |
| `global.postgresqlSecret`    | Name of K8s secret holding the superuser password | `<release>-postgresql` | Your pre-created secret name                 |
| `global.postgresqlSecretKey` | Key inside the secret                             | `postgres-password`    | Override if your secret uses a different key |

### Why pre-creation of the secret is required

Multiple subcharts reference the superuser secret at template render time (postgres-init, Keycloak's externalDatabase, keymanager's postgresInit, eSignet, mock-identity-system, IAM service, audit-manager). Helm cannot create a secret on the fly that other resources within the same release reference — chicken-and-egg. So the secret must exist **before** `helm install` runs.

### Steps to install with external PostgreSQL

**1. Pre-create the K8s secret** with the PostgreSQL superuser password:

```bash
kubectl create namespace <namespace> 2>/dev/null || true

kubectl create secret generic commons-postgresql \
  -n <namespace> \
  --from-literal=postgres-password='<superuser-password>'
```

**2. Install commons-base** with external PG overrides:

```bash
./install-base.sh <namespace> commons <base-domain> \
  --set postgresql.enabled=false \
  --set global.postgresqlHost=<external-pg-host-or-ip> \
  --set global.postgresqlSecret=commons-postgresql
```

The `install-base.sh` script verifies the secret exists in the namespace before proceeding (fails fast with the exact `kubectl create` command if missing).

**3. Install commons-services** with the same overrides:

```bash
./install.sh <namespace> commons-services commons <base-domain> \
  --set global.postgresqlHost=<external-pg-host-or-ip> \
  --set global.postgresqlSecret=commons-postgresql
```

### From the Rancher UI

The same three globals are exposed in `questions.yaml` for both charts under the **Postgres** / **Infrastructure** group. Set them through the UI and the chart behaves identically. Remember to pre-create the secret in the target namespace using `kubectl` first — Rancher's installer doesn't have a pre-flight check for it, so a missing secret will surface as `CreateContainerConfigError` on the postgres-init pods.

### Notes

* If your external secret uses a different key than `postgres-password`, also set `global.postgresqlSecretKey=<your-key>`.
* The connection assumes standard PostgreSQL port `5432`. Override `postgres-init.postgresql.port` if your service exposes a different port.
* TLS is not configured by default. If your provider requires SSL, you'd need to extend the postgres-init job (out of scope for the standard chart).
* For embedded PostgreSQL (default), no manual secret creation is needed — the Bitnami PostgreSQL chart auto-creates `<release>-postgresql` with key `postgres-password`, which the charts reference by default.

## How to deploy

Refer to the instructions [here](../../operations/deployment/_archive/deployment-instructions/environment-installation.md).

## Tear down

Use the provided uninstall scripts:

```bash
# Uninstall services first
./uninstall.sh <namespace> <services-release-name>

# Then uninstall base
./uninstall-base.sh <namespace> <base-release-name>
```

The uninstall scripts handle cleanup of secrets (including those with `helm.sh/resource-policy: keep`), PVCs, and released PVs.

## Previous versions

Previous version of Helm chart (1.x) was a single Helm chart that deployed all modules. These are available in [https://github.com/OpenG2P/openg2p-commons-deployment](https://github.com/OpenG2P/openg2p-commons-deployment) the repective branches.

| Version       | Last Modified | Comments                                            |
| ------------- | ------------- | --------------------------------------------------- |
| 1.0.0         | 21-Jan-2026   | Frozen stable version (single chart).               |
| 1.1.0-develop | 13-Feb-2026   | Several major changes. Works well with internal DB. |
| 1.2.0-develop | 24-Mar-2026   | Works via CLI but not Rancher.                      |
