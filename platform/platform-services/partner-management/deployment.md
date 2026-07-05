# Deployment

Partner Management ships a single Helm chart (`partner-management`) with three
components — the staff-portal-api, the partner-api, and the staff portal UI —
plus the standard OpenG2P init dependencies.

{% hint style="info" %}
**Installed as part of commons-services.** In an OpenG2P environment, Partner
Management is deployed **as a subchart of `openg2p-commons-services`** (the shared
platform services layer) — not installed separately. There it runs alongside the
IAM staff-portal API, Audit Manager and AWE, and its components are named
`commons-services-pm-staff-portal-api`, `commons-services-pm-partner-api`, and
`commons-services-pm-staff-portal-ui`. The `partner-management` dependency in
commons-services is pinned to a specific published PM version and bumped on each
PM update while both are on `develop`. See
[Commons Helm Chart](../../../deployment/openg2p-commons-helm-chart.md).

The standalone chart below is for local/dev or isolated installs; the sections
that follow describe that standalone chart, which commons-services embeds and
re-wires (component names, DB names, and the Keycloak issuer split).
{% endhint %}

## Images

| Image | Built from |
| --- | --- |
| `openg2p/partner-management-staff-portal-api` | `docker/staff-portal-api/Dockerfile` |
| `openg2p/partner-management-partner-api` | `docker/partner-api/Dockerfile` |
| `openg2p/partner-management-staff-portal-ui` | `docker/staff-portal-ui/Dockerfile` |

All three are built and pushed by the `docker-build` GitHub workflow (matrix;
tag = git ref), which mirrors g2p-bridge's build (OCI labels,
`FASTAPI_COMMON_REF` build-arg). The `helm-publish` workflow derives the chart
version from the branch (`develop` → `0.0.0-develop.<run>`), matching g2p-bridge.

## Helm chart

`deployment/charts/partner-management`. Dependencies (from
`https://openg2p.github.io/openg2p-helm`):

| Dependency | Role |
| --- | --- |
| `common` | Shared Bitnami-style template helpers. |
| `postgres-init` | Creates the service database + user secret. |
| `keycloak-init` | Registers the `<release>-staff-portal` client + `partner_manager` role in the **staff** realm (same shape as g2p-bridge / national-social-registry). |

A `db-password-sync` pre-install/pre-upgrade hook re-syncs the DB role password
to its Secret before the app pods start (persistent commons Postgres), matching
g2p-bridge.

### Install

```bash
helm repo add openg2p https://openg2p.github.io/openg2p-helm
helm dep up deployment/charts/partner-management
helm install partner-management openg2p/partner-management \
  --namespace <ns> --create-namespace
```

### Key values

| Value | Default | Notes |
| --- | --- | --- |
| `global.postgresqlHost` | `commons-postgresql` | Shared Postgres. |
| `global.keycloakRealm` | `staff` | Staff realm for admin auth. |
| `global.authAdminRole` | `partner_manager` | Role required on the staff-portal-api. |
| `global.authClientId` | `<release>-staff-portal` | Keycloak client the role lives under. |
| `global.iamServiceUrl` | `http://commons-services-iam-staff-portal-api` | Shared IAM the UI logs in against. |
| `global.auditEnabled` | `true` | Ship admin API calls to the central Audit Manager (non-blocking). |
| `global.auditManagerUrl` | `http://commons-services-auditmanager:80` | Shared Audit Manager (commons-services release). |
| `staffPortalApi.image.tag` | `develop` | staff-portal-api image tag. |
| `partnerApi.image.tag` | `develop` | partner-api image tag. |
| `staffPortalUi.image.tag` | `develop` | UI image tag. |

### Routing

Each component exposes an Istio `VirtualService` on the **internal** gateway:

* UI — `partner-management.<ns>.openg2p.org`
* staff-portal-api — `partner-management-staff-portal-api.<ns>.openg2p.org`
* partner-api — `partner-management-partner-api.<ns>.openg2p.org`

In-cluster consumers reach the **partner-api** directly via its Service DNS
(`<release>-partner-api`); the key-fetch API is not intended for the public
internet, which is why it needs no caller signature. The UI reaches the
staff-portal-api server-side via `http://<release>-staff-portal-api`.

### Migrations

Each API container runs `... <entrypoint> migrate && gunicorn ...` — a failed
migration crashes the pod rather than serving against an un-migrated schema.
Both entrypoints run the same idempotent `create_migrate()` against the shared DB.

## Uninstall

`helm uninstall` leaves behind the PostgreSQL database and role (they live in the
shared `commons-postgresql`, not the release) and the hook Jobs
(`before-hook-creation` delete policy). Use the full uninstall script — modeled
on g2p-bridge's — to clean everything up:

```bash
# Preview (no changes):
./deployment/scripts/uninstall-partner-management.sh --namespace <ns> --dry-run

# For real (interactive confirmation):
./deployment/scripts/uninstall-partner-management.sh --namespace <ns>

# Non-interactive (CI):
./deployment/scripts/uninstall-partner-management.sh --namespace <ns> --yes
```

It runs `helm uninstall`, deletes leftover Jobs/Pods/Secrets/ConfigMaps by
`app.kubernetes.io/instance` label, drops the `<release-underscored>` database +
`<release-underscored>_user` role inside commons-postgresql, and removes any
PVCs/PVs. It preserves other components' databases, the shared commons IAM, and
the Keycloak client (`<release>-staff-portal`, reused idempotently on reinstall).
Flags: `--release`, `--postgres-release`, `--postgres-namespace`, `--keep-pvs`,
`--dry-run`, `--yes`.

## Configuration reference

The APIs read `PARTNER_MANAGER_*` env vars for their own settings; the
staff-portal-api additionally reads `COMMON_AUTH_*` (consumed by
`openg2p-fastapi-auth`) for staff-realm JWT validation. The UI reads `IAM_URL`
(shared IAM), `STAFF_PORTAL_API_URL` (this release's staff-portal-api),
`LOGIN_PROVIDER_ID`, `COOKIE_DOMAIN`, `REDIRECT_URL`, and `KEYCLOAK_LOGOUT_URL`.
See each component's `.env.example`.
