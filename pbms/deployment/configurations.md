---
description: >-
  The instructions here are related to configuration of base settings for PBMS
  using the Odoo UI
---

# Configurations

Once all the pods are in **Running** state we can start interacting with the Odoo UI and configure some base settings.

## Prerequisites

* [ ] An installed and running instance of keycloak
* [ ] An installed and running instance of minio object store
* [ ] The user must have access to PBMS in OpenG2P systems
* [ ] The user must be an Administrator on the system

## Configure Minio Object Store

1. Navigate to the minio hostname specified during installation. You can find this in your Rancher namespace by navigating to **Istio -> Virtual Services**, and searching for `minio`
2. Login using credentials from Rancher **Storage -> Secrets**, search for `minio`
3. Navigate to the Buckets section in the Minio UI and click **Create Bucket**
4. Choose an appropriate bucket name (example: `documents`) and click on **Create Bucket**

## Configure PBMS Document Settings

1. Navigate to the pbms hostname specified during installation. You can find this in your Rancher namespace by navigating to **Istio -> Virtual Services**, and searching for `pbms`. Login using credentials from Rancher.
2. From the top-left Apps icon, go to **Settings -> Technical -> Storage Backend**
3. Create a new storage backend or update existing ones.
   * Give the record a name (example: Default S3 Document Store)
   * Select Backend type as **Amazon S3**
   * Check the `Is Public` boolean field.
   * Fill the Amazon S3 section using credentials from Rancher and the bucket name created while [configuring minio](configurations.md#configure-minio-object-store) (it is recomended to use internal url on port 9000, example: `http://minio-pbms:9000`).
   * Save the record using the top-left odoo save icon.

## Configure Keycloak

PBMS delegates all staff (operator) authentication to Keycloak. Keycloak is deployed as part of the commons layer in the same namespace as PBMS, and staff log in through the `staff` realm.

The chart derives the Keycloak connection from these `global` keys in `values.yaml`:

| Key | Default | Description |
| --- | --- | --- |
| `global.keycloakBaseUrl` | `https://keycloak.<namespace>.openg2p.org` | Base URL of the per-namespace Keycloak. The `<namespace>` segment is resolved from `global.namespace` (falling back to the install namespace `.Release.Namespace`). Surfaced in the Rancher form as **Keycloak Base URL** under *General Settings*. |
| `global.keycloakRealm` | `staff` | Realm used for staff login. Do not change unless your Keycloak provisions a differently named realm for PBMS operators. |
| `global.keycloakIssuerUrl` | `<keycloakBaseUrl>/realms/<keycloakRealm>` | OIDC issuer URL, templated from the two keys above. Rarely overridden directly. |

Steps:

1. Ensure a Keycloak instance is reachable at `global.keycloakBaseUrl` and contains a realm named per `global.keycloakRealm` (`staff` by default).
2. In that realm, provision the staff/operator users (or federate them from your identity provider) and the OIDC client(s) PBMS uses.
3. If your Keycloak is not on the default `keycloak.<namespace>.openg2p.org` hostname, override **Keycloak Base URL** in the Rancher form during installation.

## Configure PBMS Base Settings

1. Navigate to the pbms hostname specified during installation. You can find this in your Rancher namespace by navigating to **Istio -> Virtual Services**, and searching for `pbms`. Login using credentials from Rancher.
2. From the top-left Apps icon, go to **Settings** and click on **G2P PBMS Settings** tab from the left sidebar.
3. Update the URLs for Background Task API and Bridge API from **Rancher -> Istio -> Virtual Services**.
4. Select the pre-configured Document Store from the dropdown.
5. Configure Keymanager if required (by default Keymanager is toggled off).

## External Commons Prerequisites and Install Order

The `openg2p-pbms` chart does **not** deploy the shared commons infrastructure. It assumes the following services already exist in the target namespace (typically installed as part of the OpenG2P commons/base layer) and only bundles three dependencies of its own — `postgres-init`, `odoo`, and `redis` (see `Chart.yaml`).

External prerequisites the chart connects to:

| Service | Default installation name (`values.yaml` key) | Used for |
| --- | --- | --- |
| PostgreSQL | `commons-postgresql` (`global.postgresqlHost`) | Hosts the PBMS, background-task and registry databases. Its `postgres-password` is read from the `commons-postgresql` secret. |
| Keycloak | `keycloak.<namespace>.openg2p.org` (`global.keycloakBaseUrl`) | Staff authentication (`staff` realm). |
| MinIO | `commons-minio` (`global.minioInstallationName`) | S3 document store, reached in-cluster at `http://<minioInstallationName>:9000`. |
| Keymanager | `commons-keymanager` (`global.keymanagerInstallationName` / `global.keymanagerBaseUrl`) | Digital signing of disbursement requests. |
| Mail | `commons-mail` (`global.mailInstallationName`) | Outbound email. Surfaced in the Rancher form as **Email Service Name**. |
| Social Registry (NSR) | release name `registry` (`global.registryDB` etc.) | Beneficiary/registry data read by PBMS. |

**Install order:** deploy the commons layer (PostgreSQL, Keycloak, MinIO, Keymanager, Mail) and the Social Registry (NSR) release **before** installing `openg2p-pbms`. The chart's `postgres-init` init step needs the PostgreSQL server and its `commons-postgresql` secret to already exist, and the background-task and portal components expect the `registry` NSR database to be present.

**Overriding installation names:** the defaults above assume the standard commons release names. When a dependency was installed under a different release name, override the corresponding `*InstallationName` key (e.g. `global.postgresqlHost`, `global.minioInstallationName`, `global.keymanagerInstallationName`, `global.mailInstallationName`, `global.redisInstallationName`) so the derived in-cluster service names resolve correctly. See the [Two-Database Model](#two-database-model) and [Social Registry (NSR) Connection](#social-registry-nsr-connection) sections for overriding the NSR release name.

## Namespace-Derived Hostnames

All ingress hostnames are derived from a single environment segment controlled by `global.namespace`:

| Key | Default | Description |
| --- | --- | --- |
| `global.namespace` | `""` (empty) | Hostname segment shared by every derived host. When left **empty** (the usual case) it falls back to the install namespace `.Release.Namespace`, so it is **not** asked in the Rancher form. Set it only when the hostname segment must differ from the Kubernetes namespace. |

Hostnames that are templated from this segment:

| Component | Key | Default pattern |
| --- | --- | --- |
| Admin / Odoo UI | `hostname` | `admin-pbms.<namespace>.openg2p.org` |
| Background-task base host | `global.g2pPbmsBgTaskHostname` | `<release>-bg-task.<namespace>.openg2p.org` |
| Staff Portal API | `staffPortalApi.hostname` | `staff-<release>-bg-task.<namespace>.openg2p.org` |
| Bene Portal API | `benePortalApi.hostname` | `bene-<release>-bg-task.<namespace>.openg2p.org` |
| Keycloak | `global.keycloakBaseUrl` | `keycloak.<namespace>.openg2p.org` |

`<release>` is the Helm release name (`.Release.Name`) and `<namespace>` resolves as described above. The admin `hostname` can be overridden directly in the Rancher form (**Hostname** under *General Settings*); the rest are normally left to derive automatically.

## Two-Database Model

PBMS uses **two** PostgreSQL databases, each provisioned with its own user and secret by the bundled `postgres-init` dependency (see the `postgres-init.databases` list in `values.yaml`):

* the **PBMS / Odoo** database — the main application database, and
* the **background-task** database (`<release>_bgtask`) — used by the Celery beat producers, workers and the portal APIs.

Both databases live on the same PostgreSQL server (`global.postgresqlHost`, default `commons-postgresql`) but have **separate** user credentials. The database user secrets are distinct from the PostgreSQL server secret (`commons-postgresql` / key `postgres-password`).

PBMS (Odoo) database:

| Key | Default (templated) | Description |
| --- | --- | --- |
| `global.pbmsDB` | `<release>` | Database name. |
| `global.pbmsDBUser` | `<release>_user` | Database user. |
| `global.pbmsDBSecret` | `<release>` | Kubernetes secret holding the user password. |
| `global.pbmsDBUserPasswordKey` | `<release>-db-user` | Key within that secret. |

Background-task database:

| Key | Default (templated) | Description |
| --- | --- | --- |
| `global.pbmsBgTaskDB` | `<release>_bgtask` | Database name. |
| `global.pbmsBgTaskDBUser` | `<release>_bgtask_user` | Database user. |
| `global.pbmsBgTaskDBSecret` | `<release>-bgtask` | Kubernetes secret holding the user password. Note the **hyphen** — underscores are not valid in Kubernetes secret names. |
| `global.pbmsBgTaskDBUserPasswordKey` | `<release>-bgtask-db-user` | Key within that secret. |

`<release>` is the Helm release name. These defaults are shared consistently across `postgres-init`, `odoo.externalDatabase`, and the background-task/portal components, so change them only if you must reuse pre-existing databases — and change all references together.

## Social Registry (NSR) Connection

The background-task workers, beat producers, and the Staff Portal API read beneficiary data from the Social Registry (NSR) database. The connection is described by these `global` keys:

| Key | Default | Description |
| --- | --- | --- |
| `global.registryDB` | `registry` | NSR database name. |
| `global.registryDBUser` | `registry_user` | NSR database user. |
| `global.registryDBSecret` | `registry` | Kubernetes secret holding the NSR user password. |
| `global.registryDBUserPasswordKey` | `registry-db-user` | Key within that secret. |

The defaults match what the `openg2p-nsr` chart provisions when it is installed with the release name **`registry`** (its DB, user and secret are all derived from that release name). If NSR was installed under a different release name, override all four keys — they are surfaced in the Rancher form under the **Registry** group (**Registry DB**, **Registry DB User**, **Registry DB Secret with User Password**, **Registry DB Secret Key with User Password**).

## Portal APIs

PBMS ships two optional API components, toggled independently:

| Key | Default | Description |
| --- | --- | --- |
| `staffPortalApi.enabled` | `true` | Staff-facing portal API. Backed by the background-task and registry databases. Exposed at `staff-<release>-bg-task.<namespace>.openg2p.org`. |
| `benePortalApi.enabled` | `false` | Beneficiary self-service portal API. **Disabled by default.** Backed by the PBMS and background-task databases. Exposed at `bene-<release>-bg-task.<namespace>.openg2p.org`. |

Both toggles appear in the Rancher form under the **Portal API Settings** group.

The Bene Portal API authenticates beneficiaries via **eSignet** OIDC (rather than the staff Keycloak realm). Its issuer and JWKS defaults point at the per-namespace eSignet instance:

| Key | Default | Description |
| --- | --- | --- |
| `benePortalApi.envVars.COMMON_AUTH_DEFAULT_ISSUERS` | `["https://esignet.<namespace>.openg2p.org"]` | JSON array of accepted OIDC issuers for beneficiary self-service. |
| `benePortalApi.envVars.COMMON_AUTH_DEFAULT_JWKS_URLS` | `["https://esignet.<namespace>.openg2p.org/v1/esignet/oauth/.well-known/jwks.json"]` | JSON array of JWKS URLs used to validate tokens. |

Both are editable in the Rancher form (**Bene Portal API Default Issuers** / **Bene Portal API Default JWKS URLs**) when `benePortalApi.enabled=true`. Override them if your eSignet is on a non-standard hostname.

The background-task host also has an OIDC client used for machine-to-machine calls:

| Key | Default | Description |
| --- | --- | --- |
| `global.g2pPbmsBgTaskClientId` | `openg2p-pbms-bg-task-<namespace>` | OIDC client ID for the background-task/portal host. |
| `global.g2pPbmsBgTaskClientSecret` | `""` (empty) | Client secret — supply it at install time (leave empty only in environments where the client is public/unconfigured). |

## Background-Task Tuning

The `beatProducers` and `celeryWorkers` components drive PBMS background processing (building and dispatching disbursement requests via the G2P Bridge). Their throughput is tuned via `envVars`:

Beat producers (`beatProducers.envVars`):

| Key | Default | Description |
| --- | --- | --- |
| `BG_TASK_CELERY_BEAT_PRODUCER_FREQUENCY` | `20` | How often (seconds) the beat producer scans for work. |
| `BG_TASK_CELERY_BEAT_BATCH_SIZE` | `500` | Number of records fetched per batch. |
| `BG_TASK_CELERY_BEAT_NO_OF_TASKS_TO_PROCESS` | `4` | Number of tasks enqueued per run. |

Celery workers (`celeryWorkers.envVars`):

| Key | Default | Description |
| --- | --- | --- |
| `BG_TASK_CELERY_WORKERS_BATCH_SIZE` | `500` | Number of records a worker processes per batch. |
| `BG_TASK_CELERY_WORKERS_G2P_BRIDGE_BASE_URL` | `http://g2p-bridge-api` | In-cluster URL of the G2P Bridge API. Assumes the bridge was installed with release name `g2p-bridge` in the same namespace (service `g2p-bridge-api:80`, serving `/create_disbursement_envelopes` and `/create_disbursements` at root). Override if the bridge service name or namespace differs. |

The frequency and batch-size knobs are exposed in the Rancher form under the **Background Task Settings** group. Increase batch sizes / task counts for higher throughput on large disbursement runs; lower them to reduce load on PostgreSQL and the Bridge. `BG_TASK_CELERY_WORKERS_G2P_BRIDGE_BASE_URL` must be corrected whenever the Bridge is not reachable at the default in-cluster address.

## Keymanager (Disbursement Signing)

The Celery workers digitally sign disbursement requests through Keymanager. The connection is configured via these `global` keys (consumed by `celeryWorkers` and the portal APIs, which reference `global.keymanagerInstallationName`):

| Key | Default | Description |
| --- | --- | --- |
| `global.keymanagerInstallationName` | `commons-keymanager` | In-cluster service (release) name of Keymanager. Override when installed under a different name. |
| `global.keymanagerBaseUrl` | `http://commons-keymanager` | Base URL the workers call. |
| `global.keymanagerAuthEnabled` | `'false'` | Whether Keymanager requires authentication. Left off by default; set to `'true'` and supply the auth URL/client credentials (`BG_TASK_CELERY_WORKERS_KEYMANAGER_AUTH_*`) when Keymanager is secured. |
| `global.keymanagerG2pPbmsBgTaskAppId` | `OPENG2P_G2P_PBMS_BG_TASK` | Keymanager application ID under which PBMS background-task signing keys are registered. |

By default Keymanager auth is disabled and the workers reach it in-cluster over plain HTTP. Point `keymanagerBaseUrl` / `keymanagerInstallationName` at your Keymanager release, and enable auth in secured environments.

## Odoo Extra Addons

The Odoo core image can pull additional custom addons at container startup:

| Key | Default | Description |
| --- | --- | --- |
| `odoo.extraAddonsUrlsToPull` | `''` (empty) | Comma-separated git URLs of extra Odoo addons to fetch when the container starts, in the form `git://<branch>//<https-repo-url>`. Passed through to the container as `EXTRA_ADDONS_URLS_TO_PULL`. Leave empty for none. |

This is surfaced in the Rancher form as **Odoo Extra Addons URLs to Pull** under *Odoo Settings* (shown when `odoo.enabled=true`). Use it to layer site-specific or additional PBMS modules on top of the base `openg2p-pbms-core` image without rebuilding it.
