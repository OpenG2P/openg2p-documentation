---
description: >-
  Phase 2 — install your registry into a namespace with demo data, dashboards
  and maps, and prove it works.
---

# Phase 2 — Run it in a sandbox

A sandbox is a **throwaway namespace with demo data in it** — for showing the
registry, exercising it, and catching mistakes before they matter. Everything
here is the opposite of what you want in production, which is
[Phase 3](go-to-production.md).

## 1. Check the environment first

Your registry brings none of the shared services. They come from
**commons-services**, and the install fails in confusing ways when they are
missing.

| Service | Used for |
|---|---|
| PostgreSQL | The registry, Master Data and AWE databases |
| Keycloak | Staff and beneficiary sign-in |
| **Master Data (MDS)** | Geography and the country pack — **required**, see step 2 |
| AWE | Change-request approvals |
| Consent Manager, Partner Management | Consent-aware data sharing |
| Audit Manager | The audit trail |
| MinIO | Documents, photos, templates |
| Superset | Dashboards, if you want them |

```bash
kubectl -n <namespace> get pods | grep commons
```

{% hint style="danger" %}
**Fix commons before installing.** The db-seed job waits for AWE to be healthy.
If AWE is down, db-seed blocks, Helm's timeout expires, and the release is marked
failed **before the sanity job is ever created** — so you get no test output to
diagnose from.
{% endhint %}

## 2. Load a country pack into Master Data

Do this **before** installing the registry. A country pack gives the deployment
its administrative hierarchy and, optionally, sample people who live at real
addresses in it.

Enable both on the Master Data chart:

```yaml
geoSeed:
  load:
    hierarchy: true     # administrative units — required
    samples: true       # sample individuals and households
```

{% hint style="warning" %}
**Without a hierarchy in MDS, bulk generation refuses to run and maps break.**
Every generated record must point at a real administrative unit.

**Without samples in MDS**, the sample loader falls back to a demography CSV baked
into the image. That CSV describes one fixed country, so you get people whose
addresses do not match your pack.
{% endhint %}

Concepts: [Country Data Architecture](../../../../../platform/country-data-architecture.md)
· [Master Data Service](../../../../../platform/platform-services/master-data-service/README.md)

## 3. Install

**From Rancher** (recommended — the form is generated from your chart):

1. **Apps → Repositories** — add the OpenG2P catalogue if it is not there.
2. **Apps → Charts** — pick your registry. Tick **Show pre-release versions** for
   `0.0.0-develop.N` builds.
3. Name the release, tick **Customize Helm options before install**.
4. Set the ingress hostname; leave the rest at defaults for a sandbox.

**From the CLI:**

```bash
helm dependency update ./helm/openg2p-<domain>
helm install <release> ./helm/openg2p-<domain> \
  --namespace <namespace> --create-namespace \
  --set global.registryHostname=<host>
```

The release name scopes Keycloak clients, MinIO buckets and secrets, so several
registries can share a namespace.

## 4. Turn on the demo data

Three **independent** kinds of data, for three different purposes. This is the
part most often misunderstood:

<table>
  <thead><tr><th width="130">Kind</th><th>What it is</th><th width="230">Switch</th></tr></thead>
  <tbody>
    <tr>
      <td><strong>Sample</strong></td>
      <td>A few dozen realistic records a human reads in the portal. Comes from the country pack's sample people, augmented with your domain fields.</td>
      <td><code>registry.dbSeed.loadSampleData</code><br><code>registry.dbSeed.loadImages</code></td>
    </tr>
    <tr>
      <td><strong>Bulk</strong></td>
      <td>Tens or hundreds of thousands of invented records, so dashboards and maps have volume. Nobody reads an individual row.</td>
      <td><code>analytics.bulkSample.enabled</code></td>
    </tr>
    <tr>
      <td><strong>Sanity</strong></td>
      <td>A handful of fixtures the e2e suite creates to test itself. Off by default.</td>
      <td><code>registry.sanity.runE2e</code></td>
    </tr>
  </tbody>
</table>

For a sandbox, sample and bulk on:

```yaml
registry:
  dbSeed:
    loadSampleData: true
    loadImages: true
analytics:
  bulkSample:
    enabled: true
```

{% hint style="info" %}
`analytics.*` is **your chart's** key, not the platform's, so it may not appear in
the generated Rancher form unless you declared it in `questions.own.yaml`. Set it
in the YAML editor alongside the form.
{% endhint %}

Details: [Country data & seeding](../../deployment-and-extension/country-data-and-seeding.md)

## 5. Turn on reporting

Dashboards and maps never read your register tables. They read **reporting
views** — one per entity, carrying geography and workflow columns with personal
data withheld. Most are generated at install from your schema; you hand-write
only the ones that pair entities or derive bands.

```yaml
analytics:
  reportingViews:
    enabled: true
    generate: true
    refreshSchedule: "0 * * * *"
  dashboards:
    enabled: true
mapsContent:
  enabled: true
```

Concepts: [Reporting views](../../../../../platform/platform-services/reporting-and-analytics/reporting-views.md)
· [Dashboards](../../../../../platform/platform-services/reporting-and-analytics/dashboards.md)
· [Map drill-down](../../../../../platform/platform-services/reporting-and-analytics/map-drill-down.md)
· [Setting up reporting](../../../../../platform/platform-services/reporting-and-analytics/setting-up-reporting.md)

## 6. Run the sanity suite

Off by default because it seeds persistent fixtures. In a sandbox, turn it on —
it is the fastest way to know the whole chain works:

```yaml
registry:
  sanity:
    enabled: true
    runE2e: true
```

It exercises the signed DCI path with consent enforcement, and a change request
through AWE approval to applied change, history row and audit trail.

```bash
kubectl -n <namespace> logs job/<release>-sanity
```

Details: [Testing & the sanity suite](../../deployment-and-extension/testing-and-sanity-suite.md)

## 7. Verify

Work down this list; each failure points somewhere specific.

| Check | If it fails |
|---|---|
| All jobs completed: `kubectl -n <ns> get jobs` | Jobs are ordered — the **first** failure blocks the rest. Fix that one |
| `<release>.<domain>` shows the Keycloak login | Ingress / hostname |
| You can sign in with a `keycloak-init` demo user | Change the temporary password when prompted |
| Your registers appear, with their tabs and sections | `meta_data/register-metadata` — most likely a section/ORM field-name mismatch |
| A sample record opens and shows data | Sample data did not load, or the fields disagree |
| Dashboards show numbers | Reporting views, or bulk data missing |
| The map drills down | MDS hierarchy missing or geo columns absent from the views |
| The sanity job passed | Read its log — it narrates each step |

Once all of these pass, your registry works. Now install it properly:

---

**Next:** [Phase 3 — Go to production](go-to-production.md)
