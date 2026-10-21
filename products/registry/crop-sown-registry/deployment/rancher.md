---
description: >-
  Installing the Crop Sown Registry from the OpenG2P catalogue in Rancher:
  prerequisites, the choices to make, sample data, ODK Central, checks after
  install, and uninstall.
---

# Deploying on Rancher

This page lists the steps and choices. What the registry is and how it is packaged: [Crop Sown Registry](../README.md). Install order and the install Jobs: [Deployment](README.md).

## Prerequisites

1. A Kubernetes cluster, with admin rights to it and to Rancher.
2. **commons-base** and **commons-services** installed and healthy in the namespace. See the [Commons Helm Chart](../../../../deployment/openg2p-commons-helm-chart.md). The registry uses, from commons-services:

   | Service | Needed for | Setting in the commons-services form |
   | --- | --- | --- |
   | **Master Data** | Every coded field, the geography, sample farmers | **Country Pack** `ETH`, **Dataset Themes** `agriculture`, **Load Datasets** on. For a demo, also **Load Sample People** on |
   | **AWE** | Cluster registrations and changes | **Install AWE?** on |
   | **Partner Management** and **Consent Manager** | Partner calls: signature checks and consent | On (defaults) |
   | **ODK Central** | Only if sowings are collected with ODK | **Install ODK Central?** on |

3. The OpenG2P catalogue added in Rancher (**Apps → Repositories**).

The Farmer Registry is **not** needed. See [How it relates to the Farmer Registry](../README.md#how-it-relates-to-the-farmer-registry).

{% hint style="warning" %}
Without the **agriculture** domain in Master Data, the install succeeds but every activity is rejected on its crop code. Check it before you install.
{% endhint %}

## Install

1. In Rancher, select the cluster and the namespace.
2. Under **Apps → Charts**, refresh the repositories and select **OpenG2P Crop Sown Registry**.
3. Choose the version. Tick **Show pre-release versions** to see `0.0.0-develop.N` versions.
4. Name the release, e.g. `csr`. The release name is part of the hostnames and the database name.
5. Tick **Customize Helm options before install**, then **Next**.
6. Make the choices below, then **Install**.

The form is the platform chart's form plus a **Crop Sown Registry** group. Each field is described in the form. In a values file, platform settings sit under `registry.*` and shared settings under `global.*`.

## Choices

The defaults suit a production-like install. Change only these.

| Field | Choose | Why |
| --- | --- | --- |
| **Base Domain** | Your environment's domain | Every hostname derives from it. Default `<namespace>.openg2p.org`. The partner API is then at `partner-<release>.<Base Domain>` |
| **Load Sample Data** | On for a demo only | Loads two sample clusters. See [Sample data](#sample-data) |
| **Load sample crop seasons** | On for a demo only | Shown when Load Sample Data is on. See [Sample data](#sample-data) |
| **Pull submissions from ODK Central** | On only if sowings are collected with ODK | Needs more steps. See [ODK Central](#collecting-sowings-with-odk-central) |
| **Pinned Catalogue Release** | Empty, or a release to freeze the lists for a season | Empty reads the latest lists from Master Data |
| **AWE Approver User Password** | Your own | The initial password of the demo cluster approvers `alex.carter` and `nina.patel` |

**Leave as they are:**

* **Install ID Generator?**, **Enable DB Seed** and **Load Templates to Object Store** on. The ID generator issues Cluster IDs, the seed is the registry's configuration, and without the templates every DCI search fails.
* **Sanity - Run Full E2E** off. The platform's e2e tier seeds an entity record this registry does not have.
* **Load Sample Images** and **Optional Seeds**: this registry ships none.
* The ID generator's unused platform pools (`individual`, `household`, `farmer`) are harmless.

{% hint style="warning" %}
**Verify Partner Signature** and **Enforce Consent** are on by default. Turning either off returns data to partners unchecked or not cut down to their consent ([Consent-aware data sharing](../../registry/features/consent-aware-data-sharing.md#configuration)).
{% endhint %}

### Settings only in YAML

Set these in **Edit YAML**:

```yaml
registry:
  partnerApi:
    envVars:
      # Partners allowed to search season summaries across farmers (no farmer ID,
      # no per-farmer consent), with the scopes they get. Off unless listed.
      REGISTRY_PARTNER_API_DCI_BULK_AGGREGATE_PARTNERS: '{"benefits-system": ["crop-sown-registry.crop_season", "crop-sown-registry.measures"]}'
  celeryWorker:
    envVars:
      # ODK Central address (default: the commons-services ODK Central)
      REGISTRY_CELERY_WORKERS_ACTIVITY_ODK_BASE_URL: "http://commons-services-odk-central-backend"
    envVarsFrom:
      # ODK Central login, from a Secret you create (see below)
      REGISTRY_CELERY_WORKERS_ACTIVITY_ODK_USERNAME:
        secretKeyRef: {name: csr-odk-credentials, key: username}
      REGISTRY_CELERY_WORKERS_ACTIVITY_ODK_PASSWORD:
        secretKeyRef: {name: csr-odk-credentials, key: password}
```

### Production

* Keep **Load Sample Data** and **Load sample crop seasons** off, and **Sanity - Run Full E2E** off.
* Keep **Verify Partner Signature** and **Enforce Consent** on.
* **Allow Unsigned Read of Data Scope Catalogue** is on by default: anyone who can reach the partner API can list the scopes (field names, no data). Turn it off to keep them private; Partner Management then takes scopes as free text.
* Replace the demo cluster approvers (see [Customisation](../customisation.md#clusters)).

{% hint style="danger" %}
**Never promote a demo namespace to production.** Sample crop seasons are recorded through the normal write path and cannot be separated cleanly afterwards. Install fresh.
{% endhint %}

## Sample data

Sample data is off by default. For a demo, turn on both switches:

| Switch | Loads | Needs |
| --- | --- | --- |
| **Load Sample Data** | Two sample clusters, approved: `CL-4729318560` (teff, Sheno, Oromia) and `CL-5863027194` (wheat, Tahtay Adiyabo, Tigray) | Master Data, for the clusters' geography |
| **Load sample crop seasons** | Crop seasons for every adult among Master Data's sample people | The sample clusters, and Master Data's **sample people** |

**What the crop seasons cover:**

* **Farmers** are Master Data's sample people: person `ETH-IND-0007` is farmer `FR-0007`, with the person's national ID as the Fayda FAN.
* **Plots** are `LAND-0007-1` for every farmer and `LAND-0007-2` for every third, in the person's district (woreda).
* **Seasons:** Meher 2018 complete (with a pest report for some); Belg 2018 complete for some farmers (with drought damage); Meher 2019 growing, so its harvests are due on the work list.
* **Verification:** most sowings and harvests are verified; every fifth farmer's are pending. One sowing is corrected.
* **Clusters:** farmers in a sample cluster's district join it.

The Farmer Registry numbers its sample farmers and lands the same way. A demo of both shows the same farmers and plots, though neither reads the other.

{% hint style="warning" %}
The `<release>-activity-samples` Job **fails the release** if any sample cannot be loaded, e.g. no sample people in Master Data, no sample clusters, or a code missing from a list. Its log gives the reason.
{% endhint %}

## Collecting sowings with ODK Central

The registry can pull **Sown** activities from an ODK Central form. This is off by default and takes five steps.

1. **The form.** Build and publish an XLSForm with form ID `crop_sowing` in an ODK Central project. The registry ships the field mapping, **not the form**. The form's field paths must match the mapping in `scripts/activity_definitions.py` (`ODK_FORMS`), e.g. `farmer/farmer_id`, `plot/plot_id`, `plot/woreda`, `season/crop_year`, `season/season`, `sowing/crop`, `sowing/area_ha`, `sowing/seed_type`, `sowing/sowing_date_ec`, `sowing/photo`. Coded answers must be Master Data codes.
2. **A login.** Create an ODK Central web user with access to the project, and a Secret holding it:

   ```bash
   kubectl -n <ns> create secret generic csr-odk-credentials \
     --from-literal=username='<odk user email>' --from-literal=password='<password>'
   ```

3. **The YAML.** Add the `envVarsFrom` entries shown in [Settings only in YAML](#settings-only-in-yaml).
4. **The switch.** Set **Pull submissions from ODK Central** to `true` and upgrade.
5. **Activate the mapping.** The seeded mapping is inactive, for project `1`. There is no screen for it yet. In the registry's database:

   ```sql
   UPDATE g2p_activity_odk_forms
      SET is_active = true, odk_project_id = <your ODK project ID>
    WHERE odk_form_id = 'crop_sowing';
   ```

Submissions are then pulled every five minutes. The ODK instance ID makes each pull idempotent. Photos are stored as documents. A submission that fails validation is kept in `g2p_activity_odk_failures` and retried; it does not hold back the others.

{% hint style="info" %}
If you change `odk_project_id`, later db-seed runs log a duplicate-key error for the ODK mapping file and no longer update the mapping. The rest of the seed is not affected.
{% endhint %}

## Verify

A healthy install ends with the Jobs complete and the pods running:

```bash
kubectl -n <ns> get jobs
kubectl -n <ns> get pods
kubectl -n <ns> logs job/<release>-sanity
```

| Job | Expect |
| --- | --- |
| `<release>-db-seed` | Complete |
| `<release>-activity-samples` | Complete, with counts. Only when sample crop seasons are on |
| `<release>-sanity` | Complete: the partner API is up and serves DCI search |
| iam-register | Complete |

Then open the staff portal at `https://<Registry Hostname>`:

* **Activity registers → Crop Sown** shows the activity types under **Record**. With sample data, it also shows activities, crop seasons, summaries and indicators.
* **Cluster** lists the sample clusters, if loaded.

**End-to-end check.** `scripts/e2e_smoke.py` in the repository records one crop season through the partner API (plan to harvest), checks idempotency, a blocked out-of-order activity and a correction, and reads it back with DCI search. It does not sign its requests or carry a consent, so it runs against a registry with **Verify Partner Signature** and **Enforce Consent** off, typically the [hybrid local run](https://github.com/OpenG2P/crop-sown-registry/blob/develop/local/README.md):

```bash
python3 scripts/e2e_smoke.py --partner-url <partner API URL> [--db-url postgresql://…]
```

## Uninstall

`helm uninstall` leaves the database, PVCs and IAM rows behind. Use the repository's script, with `--dry-run` first:

```bash
./scripts/uninstall-registry.sh --namespace <ns> --release csr --dry-run
./scripts/uninstall-registry.sh --namespace <ns> --release csr
```

It removes the release, leftover Jobs, labelled Secrets and ConfigMaps, the registry's database and role in `commons-postgresql`, its IAM rows, and its PVCs and PVs. Options: `--keep-iam`, `--keep-pvs`, `--force`, `--yes`. It leaves shared services alone: the Keycloak client, the templates in the shared object store, Master Data, and any Partner Management or Consent Manager entries.
