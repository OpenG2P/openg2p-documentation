---
description: >-
  Turning on the Farmer Registry's sample, bulk and sanity data, the reporting
  views and the dashboards, and the install Jobs in the order they run.
---

# Data seeding

This page lists the steps and choices. What each kind of data is: [Data the registry can create](../README.md#data-the-registry-can-create) and, for all registries, [Country data & seeding](../../registry/deployment-and-extension/country-data-and-seeding.md). What the reporting views and dashboards are: [Reporting and dashboards](../README.md#reporting-and-dashboards).

The registry's own configuration (registers, screens, DCI templates, the binding of change requests to AWE policy keys) is always seeded by the db-seed Job. Everything below is optional, and off by default. Which data is configuration and which is sample, across Master Data and the registries: [every switch](../../registry/deployment-and-extension/country-data-and-seeding.md#configuration-or-sample-every-switch).

## Before you install

On the **commons-services** form:

* **Dataset Themes** includes `agriculture` (the default) and **Load Datasets** is on. Without them the coded dropdowns are empty.
* **Load Sample People** is on, if you want sample data.

The Farmer Registry's Jobs read Master Data through its API, with the `<release>-staff-portal` Keycloak client. That client needs read access to Master Data's `/catalogue` and `/samples`.

## Sample data

1. On the Farmer Registry form, turn on **Load Sample Data**. Turn on **Load Sample Images** too for profile photos.
2. Install or upgrade.
3. Check: the staff portal lists farmers numbered like the sample people, e.g. `FR-0007`, with lands `LAND-0007-1`.

**Load Sample Data** loads:

* **Sample farmers:** every one of Master Data's sample people, with the farmer fields of the registry's own overlay (lands, farm inputs, household members, memberships, scores).
* **Livestock:** the country pack's sample animals (`packs/<country>/samples/animals.json` in [openg2p-data](https://github.com/OpenG2P/openg2p-data), taken when the image is built), as herds: per owner, one for each species, breed and livestock system, with the animals' count, on the owner's first land (`LIVESTOCK-0007-1` on `LAND-0007-1`). The Livestock Registry loads the same animals one by one, so the two agree on every sample farmer's livestock. The codes are Master Data's (`LSTK_CATTLE`, `BREED_LOCAL`). A pack without the file gives no herds. An install loaded before this change keeps its old sample herds (unrelated to the Livestock Registry's) until reinstalled.
* **The sample approval policies** for change requests, and the **demo staff users** they name (`alex.carter`, `nina.patel`…), with the initial password **AWE Approver User Password** ([Approval policies and demo staff](../../registry/deployment-and-extension/country-data-and-seeding.md#approval-policies-and-demo-staff)).

{% hint style="warning" %}
**The sample farmers are Master Data's sample people, with no fallback.** If Master Data is not reachable, or holds no geography or no sample people (**Load Sample People** off on commons-services, or a pack without samples such as `XKM`), db-seed stops with the reason in its log and the release fails. Turn on **Load Sample People** and upgrade commons-services, or turn **Load Sample Data** off.
{% endhint %}

## Bulk data

1. On the form, under **Analytics**, turn on **Generate bulk demo data**.
2. Set **Bulk demo farmers** if 100,000 is not the size you want.
3. Optional, in YAML: set `analytics.bulkSample.expectedCountry` (e.g. `ETH`) so the Job fails if Master Data holds another country.
4. Install or upgrade. Check the `<release>-fr-bulk-sample` Job completed.

Bulk generation needs Master Data's geography; the Job fails if it is not there.

## Sanity data

Sanity data is created only with **Sanity - Run Full E2E** on. It needs **Load Sample Data**: its test user is added as an approver to the sample approval policies. Its fixtures are never deleted, so use it only on a test environment. Steps: [Sanity testing](sanity-testing.md).

## Reporting views

On by default (**Build reporting views**). Choose the refresh interval in **Reporting data refresh** (cron, hourly by default; empty means never). Between refreshes, new farmers are not in reports.

Check the `<release>-fr-reporting-views` Job completed, and the CronJob `<release>-fr-reporting-views-refresh` exists.

## Dashboards

The dashboards are imported into the environment's Superset at install. To load them:

1. Install Superset with commons-services (**Install Superset?**).
2. Install or upgrade the Farmer Registry.
3. Check the `<release>-dashboards` Job's log says the dashboards were imported.

In Superset, the dashboards are titled `<release> · <title>` (e.g. `fr · Land & Tenure`), on a connection named after the release. So several Farmer Registries can share the namespace's Superset, each with its own copy: [Several installs in one Superset](../../../../platform/platform-services/reporting-and-analytics/dashboards.md#several-installs-in-one-superset).

If Superset was not reachable, the Job skips the import and says so. Upgrade the registry once Superset is up. To fail the install instead, set `registry.dashboards.superset.required: true` in YAML.

Bringing reporting up for a country: [Setting up reporting](../../../../platform/platform-services/reporting-and-analytics/setting-up-reporting.md).

## Install sequence

The install Jobs run as Helm post-install and post-upgrade hooks, in hook-weight order. Helm waits for each to succeed before the next, so **a failure blocks every Job after it**.

| Weight | Job | Does | Runs when |
| --- | --- | --- | --- |
| — | the `iam-register` Job | Registers the registry's roles and permissions in IAM. A regular Job, started with the pods; a failure does not fail the release | always |
| 10 | `<release>-db-seed` | Registry configuration, sample data, images, templates. Waits for AWE and for Master Data's geography | **Enable DB Seed** (on) |
| 11 | `<release>-sanity-pm-seed` | Registers the test partner in Partner Management, with its key and its scope policy for this registry (allowing the consents it signs itself) | **Sanity - Run Full E2E** |
| 13 | `<release>-sanity-data-seed` | The sanity farmer, Keycloak user and approver rule | **Sanity - Run Full E2E** |
| 15 | `<release>-registrant-auth-bootstrap` | Sets up the eSignet login farmers use before a credential is issued | credentials on |
| 16 | `<release>-agent-vc-register` | Registers the Farmer Credential with Inji Certify | credentials on |
| 25 | `<release>-sanity` | Runs the sanity suite | **Run Sanity Tests** (on) |
| 40 | `<release>-fr-bulk-sample` | Generates the bulk farmers | **Generate bulk demo data** |
| 45 | `<release>-fr-reporting-views` | Builds the reporting views | **Build reporting views** (on) |
| 50 | `<release>-dashboards` | Imports the dashboards into Superset, named after the release | `registry.dashboards.enabled` (on) |

Two dependencies are on other releases, which Helm cannot order:

* **Master Data** must be seeded before db-seed (weight 10) and bulk generation (weight 40). Both wait for it, then fail with a clear message.
* **Superset** must be reachable for the dashboard import (weight 50). The Job waits, then skips.

{% hint style="warning" %}
If Superset has no dashboards after an install, check the **earlier** Jobs first. A failed bulk Job (weight 40) stops the reporting views and the dashboard import from running.
{% endhint %}

## For production

Keep sample data, sample images, bulk data and the full e2e off. Keep **Enable DB Seed** on: it also uploads the templates (on Registry Platform `0.0.0-develop.847` or older, keep **Load Templates to Object Store** on too). Details: [An empty install](../../registry/deployment-and-extension/country-data-and-seeding.md#an-empty-install-for-production).
