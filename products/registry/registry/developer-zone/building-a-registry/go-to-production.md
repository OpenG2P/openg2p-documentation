---
description: >-
  Phase 3 — install your registry empty, with the real country pack and every
  demo switch off.
---

# Phase 3 — Go to production

A production registry is **the same artifacts as your sandbox, installed empty**.
You do not build anything different. You install with every demo switch off, a
real country pack, and pinned versions.

{% hint style="danger" %}
**Never promote a sandbox namespace to production.** Demo records and sanity
fixtures cannot be cleanly separated from real registrants afterwards — sanity
fixtures in particular are deliberately never deleted. Install fresh.
{% endhint %}

## 1. Pin a frozen version

Sandboxes may track `0.0.0-develop.N`. Production must not: those are moving
builds with no release notes.

Use a **frozen three-part version** (`1.2.0`) for your registry chart, and pin the
platform deliberately:

```bash
./scripts/bump-rp-version.sh -n            # preview the latest safe platform version
./scripts/bump-rp-version.sh <version>     # pin it in Dockerfiles + chart together
```

Then release your own registry version, and record both. Which platform version
you shipped on is the first question any later investigation asks.

Rules: [Helm & Docker versioning and CI](https://docs.openg2p.org/operations/deployment/helm-docker-versioning-and-ci)

## 2. Load the real country pack

Same mechanism as the sandbox, different content — the real administrative
hierarchy, and **no sample people**:

```yaml
geoSeed:
  load:
    hierarchy: true      # the real hierarchy
    samples: false       # no demo people in production
```

{% hint style="warning" %}
Load the hierarchy **before** the registry. Records reference administrative
units; if the hierarchy arrives later, existing records point at nothing and maps
stay empty.
{% endhint %}

## 3. Turn every demo switch off

The single most important step on this page.

```yaml
registry:
  dbSeed:
    enabled: true            # KEEP: metadata seeding is required
    loadSampleData: false    # no demo records
    loadImages: false        # no demo photos
    loadGeoData: false       # geography comes from the real pack
    loadTemplates: true      # KEEP: DCI templates must be in MinIO
  sanity:
    enabled: false           # or true with runE2e:false for a smoke check
    runE2e: false            # NEVER true in production
analytics:
  bulkSample:
    enabled: false           # no invented records
  reportingViews:
    enabled: true            # KEEP: dashboards read these
```

{% hint style="danger" %}
Two switches are load-bearing and must stay **on**:

* **`dbSeed.enabled`** — without the metadata SQL you have tables but no
  registers, screens or code lists. It creates no registrant data.
* **`loadTemplates`** — without the DCI templates in MinIO every record fails to
  render, and a DCI search returns an empty `200` rather than an error.
{% endhint %}

## 4. Keep the enforcement gates on

They default to on. Turning either off silently opens real PII egress — the only
outward signal is a field in the DCI response header.

| Setting | Keep | What off means |
|---|---|---|
| `global.partnerSignatureValidationEnabled` | `true` | The `signature` field is required but never inspected — any string passes |
| `global.consentEnforcementEnabled` | `true` | Consent Manager is never called; records return **unclamped**, every field to any caller |

Detail: [Partner APIs](../../design/partner-apis.md)

## 5. Point at the production commons

The registry reaches every shared service by URL. Set these to your production
instances — not the sandbox's:

```yaml
global:
  registryHostname: <your production host>
  postgresqlHost: ...
  keycloakBaseUrl: ...
  partnerManagementApiUrl: ...
  consentManagerUrl: ...
  aweBaseUrl: ...
  auditManagerUrl: ...
  minioSecret: ...
```

{% hint style="warning" %}
Confirm the commons release is at a version compatible with your platform pin.
A registry that references a secret key its commons has not yet created fails
with `CreateContainerConfigError` at pod start — upgrade commons first.
{% endhint %}

## 6. Install and verify

```bash
helm dependency update ./helm/openg2p-<domain>
helm install <release> ./helm/openg2p-<domain> \
  --namespace <namespace> --create-namespace \
  --version <frozen-version> \
  -f production-values.yaml
```

Then verify **emptiness as well as function**:

| Check | Expected |
|---|---|
| Registers, tabs and sections render | Metadata seeded |
| Record search returns **nothing** | No demo data — this is the point |
| No `SANITY-*` record exists | Sanity fixtures never ran |
| Staff sign-in works, demo passwords rotated | Keycloak |
| Dashboards render (empty until real data) | Reporting views exist |
| A DCI search without consent is **rejected** | Enforcement gates on |

## 7. Before you hand over

* [ ] **Rotate every default credential** — `keycloak-init` demo users, Superset
      service account, any generated secret you did not supply.
* [ ] **Back-ups configured and a restore rehearsed** —
      [Backups](https://docs.openg2p.org/operations/deployment/backups/README.md).
      An untested restore is not a back-up.
* [ ] **Record the version pair** — your registry version *and* the platform
      version it was built on.
* [ ] **Know how you will upgrade.** Seeding is re-runnable, so a chart upgrade
      re-applies metadata; `loadSampleData` must stay off.
* [ ] **Decide who owns the country pack.** Administrative hierarchies change;
      someone must own updating MDS.

## Sandbox and production, side by side

| | Sandbox | Production |
|---|---|---|
| Version | `0.0.0-develop.N` | Frozen `N.N.N` |
| Country pack | Sample pack, samples on | Real hierarchy, samples off |
| Sample data | On | **Off** |
| Bulk data | On | **Off** |
| Sanity e2e | On | **Off** |
| Metadata seeding | On | **On** |
| DCI templates | On | **On** |
| Enforcement gates | On | **On** |
| Credentials | Defaults fine | **All rotated** |
| Back-ups | Not needed | **Required and rehearsed** |
