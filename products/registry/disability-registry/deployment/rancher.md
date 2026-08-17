---
description: Installing the Disability Registry from the OpenG2P catalogue in Rancher.
---

# Deploying on Rancher

## Prerequisites

1. A Kubernetes cluster, and admin rights to it and to the Rancher UI.
2. **commons-services** deployed and healthy in the environment. The registry
   bundles none of the shared services — Keycloak, Master Data, Consent Manager,
   Partner Management, the Approval Workflow Engine (AWE), Audit Manager and
   Superset all come from commons-services and are reached through `global.*`
   URLs.
3. A **country pack** loaded into the Master Data Service, if you want geography
   and national code lists. Seeded by the `openg2p-master-data` chart
   (`geoSeed.countryPack`), not by this registry.

{% hint style="warning" %}
Confirm commons-services is healthy **first**. The db-seed Job waits for AWE; if
AWE is down, db-seed blocks, the install times out and the release fails before
the sanity Job is ever created.
{% endhint %}

## Install

1. Log in to the Rancher console and select the cluster and namespace.
2. Under **Apps → Repositories**, ensure the OpenG2P catalogue repository is
   added.
3. Under **Apps → Charts**, refresh repositories and select **OpenG2P Disability
   Registry**.
4. Choose the version. Three-part versions (`1.2.0`) are frozen; `-develop`
   versions are moving — tick **Show pre-release versions** to see
   `0.0.0-develop.N`.
5. Give the installation a name. The release name is free and scopes the
   resources, so more than one registry can share a namespace.
6. Tick **Customize Helm options before install**, then **Next**.
7. Review the values and **Install**.

The configuration form shows the **same questions as the platform chart** — they
are inherited from the pinned `openg2p-registry` dependency at packaging time
rather than duplicated, so they cannot drift. Platform settings appear under the
`registry` key; `global.*` settings are unchanged. Four questions are this
chart's own, under **Analytics**: reporting views, the refresh schedule,
dashboards, and maps content.

## What to set

At minimum, the ingress host:

```yaml
global:
  registryHostname: dr.example.org
```

For a **sandbox**, the defaults are already right — demo data on, sanity suite
on, analytics on.

For **production**, turn the demo switches off but leave the two that are not
optional:

```yaml
registry:
  dbSeed:
    enabled: true          # REQUIRED — the metadata IS the registry
    loadTemplates: true    # REQUIRED — without the DCI templates every partner
                           #            search returns an empty 200
    loadSampleData: false
    loadImages: false
    loadAttributes: true   # take the country's code lists from Master Data
    syncGeoWidgets: true
  sanity:
    enabled: false
    runE2e: false          # never true in production
global:
  partnerSignatureValidationEnabled: true
  consentEnforcementEnabled: true
```

{% hint style="danger" %}
**Never promote a sandbox namespace to production.** Demo records cannot be
cleanly separated afterwards. Install fresh.
{% endhint %}

### Functional-ID pool

This registry mints functional IDs for one register only:

```yaml
registry:
  idgenerator:
    idGenerator:
      appConfig:
        idTypes:
          personwithdisability:
            idLength: 12
```

You will see **more pools than you declared** — Helm merges maps and a parent
chart cannot delete a subchart default, so the platform's and the ID generator's
own defaults come along too. An unused pool is an empty table that allocates
nothing. Check only that `personwithdisability` is present.

## Verify

A healthy install ends with every Job `Complete`:

```bash
kubectl -n <namespace> get jobs
```

| Job | Expect |
|---|---|
| `<release>-db-seed` | Complete |
| `<release>-iam-register` | Complete |
| `<release>-sanity` | Complete — `12 passed` in the log |
| `<release>-dr-reporting-views` | Complete — "created N view(s)", "no withheld column reached any generated view" |
| `<release>-dr-dashboards` | Complete — "embedding enabled on 7 dashboard(s)" |

and the workload pods `1/1 Running`:

```bash
kubectl -n <namespace> get pods
kubectl -n <namespace> logs job/<release>-sanity
```

Then open the staff portal at your `registryHostname` and search — a sandbox
install with `loadSampleData: true` has records to find.

{% hint style="info" %}
`<release>-dr-reporting-views-refresh` is a **CronJob**, not a Job. It runs
hourly on the hour, so immediately after install it shows `LAST SCHEDULE: <none>`
and has no pods. That is expected — the views themselves were built by the
install-time Job.
{% endhint %}

## Uninstall

`helm uninstall` leaves the PVCs, the database, the MinIO buckets and the
Keycloak clients behind, so a reinstall into the same namespace inherits stale
state. Use the repository's teardown script for a clean removal:

```bash
./scripts/uninstall-registry.sh
```
