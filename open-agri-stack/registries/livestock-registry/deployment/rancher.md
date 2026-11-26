---
description: >-
  Installing the Livestock Registry from the OpenG2P catalogue in Rancher:
  prerequisites, the choices to make, sample data, checks after install, and
  uninstall.
---

# Deploying on Rancher

This page lists the steps and choices. What the registry is: [Livestock Registry](../README.md). Install order and the install Jobs: [Deployment](README.md).

## Prerequisites

1. A Kubernetes cluster, with admin rights to it and to Rancher.
2. **commons-base** and **commons-services** installed and healthy in the namespace. See the [Commons Helm Chart](../../../../deployment/openg2p-commons-helm-chart.md). The registry uses, from commons-services:

   | Service | Needed for | Setting in the commons-services form |
   | --- | --- | --- |
   | **Master Data** | Every coded field (the `LIVESTOCK_*` lists), the geography, and the sample people the sample animals belong to | **Country Pack** (e.g. `ETH`), **Dataset Themes** `agriculture`, **Load Datasets** on; for sample data also **Load Sample People** |
   | **AWE** | Animal and vet registrations and changes | **Install AWE?** on |
   | **Partner Management** | Signature checks on the partner API, and partners' scope policies | On (the default) |
   | **Consent Manager** | Partners' searches, with the farmer's consent | On (the default) |
   | **Superset** | The [dashboards](../README.md#dashboards). Optional: without it the import is skipped | **Install Superset?** on, if dashboards are wanted |

3. The OpenG2P catalogue added in Rancher (**Apps → Repositories**).

{% hint style="warning" %}
Without the **agriculture** domain in Master Data, the install succeeds but the forms' dropdowns are empty and every event is rejected. Master Data must also hold the `LIVESTOCK_*` lists: a Master Data seeded from an openg2p-data older than the Livestock Registry lacks most of them, and needs its country pack loaded again.
{% endhint %}

## Install

1. In Rancher, select the cluster and the namespace.
2. Under **Apps → Charts**, refresh the repositories and select **OpenG2P Livestock Registry**.
3. Choose the version. Tick **Show pre-release versions** to see `0.0.0-develop.N` versions.
4. Name the release, e.g. `lsr`. The release name is part of the hostnames and the database name.
5. Tick **Customize Helm options before install**, then **Next**.
6. Make the choices below, then **Install**.

The form is the platform chart's form plus a **Livestock Registry** group. In a values file, platform settings sit under `registry.*` and shared settings under `global.*`.

## Choices

The defaults suit a production-like install. Change only these.

| Field | Choose | Why |
| --- | --- | --- |
| **Base Domain** | Your environment's domain | Every hostname derives from it. Default `<namespace>.openg2p.org`; the staff portal is then at `<release>.<Base Domain>` |
| **Load Sample Data** | On for a demo only | Loads the sample vets and animals, the sample approval policies and the demo staff users they name. See [Sample data](#sample-data) |
| **Load sample events** | On for a demo only | Shown when Load Sample Data is on. See [Sample data](#sample-data) |
| **AWE Approver User Password** | Your own | The initial password of the demo staff users, among them the approvers `alex.carter` and `nina.patel` (default `pass`, changed at first login). Only with Load Sample Data ([details](../../../../products/registry/registry/deployment-and-extension/country-data-and-seeding.md#approval-policies-and-demo-staff)) |

**Leave as they are:**

* **Install ID Generator?** and **Enable DB Seed** on: the ID generator issues Animal and Vet IDs, and the seed is the registry's configuration.
* **Install Staff Portal API?**, **Install Staff Portal UI?** and **Install Partner API?** on: staff keep the animals in the portal, and partners search and vets' systems send events through the partner API.
* **Use AWE for Approvals** on: new animals and vets, and changes to them, are approved in AWE ([Adding an animal and approving it](#adding-an-animal-and-approving-it)).
* **Verify Partner Signature**, **Enforce Consent** and **Allow Unsigned Read of Data Scope Catalogue** on: partners read animals only with the farmer's consent, and see the catalogue of what can be shared.
* **Install Beneficiary Portal API?** and the Agent Portal off: farmers do not use this registry directly, and it issues no credentials.
* **Install Registry Connector?** off, unless a vet's or an animal identification system pushes its records that way; then set its hostname and **Partner API Service** to `<release>-partner-api`.
* **Sanity - Run Full E2E** off: the platform's e2e tier seeds and searches a reference-registry record this registry does not have.
* **Load Sample Images** and **Optional Seeds**: this registry ships none.

The IDs' lengths and the DCI search fields are YAML settings ([Customisation](../customisation.md)).

### Production

* Keep **Load Sample Data** and **Load sample events** off.
* Set up the approval policies in AWE's admin portal, with the country's approvers: without sample data none are loaded, and a new animal or vet is refused until they exist ([Customisation](../customisation.md#approvals)).
* Write the scope policies for the partners (or the Composite) that may read the registry, in Partner Management.

{% hint style="danger" %}
**Never promote a demo namespace to production.** Sample animals and events are recorded as real records and cannot be separated cleanly afterwards. Install fresh.
{% endhint %}

## Sample data

Sample data is off by default. For a demo, turn on both switches:

| Switch | Loads | Needs |
| --- | --- | --- |
| **Load Sample Data** | The country pack's sample vets and animals (`packs/<country>/samples/veterinarians.json` and `animals.json` in [openg2p-data](https://github.com/OpenG2P/openg2p-data)), the animals owned by Master Data's sample people, as approved records | Master Data, for the geography and the sample people |
| **Load sample events** | Births, vaccinations, treatments, a sale and a death for the sample animals | The sample animals and vets |

* **Which pack:** db-seed picks the pack whose sample vets' areas Master Data knows, so the samples match the country Master Data was installed with. There is no fallback: if no pack's sample vets are in areas Master Data knows (e.g. Master Data holds `XKM`, which has no samples), the pack has no `animals.json`, an animal's owner is not one of Master Data's sample people, Master Data has no sample people, or it is not reachable, db-seed stops with the reason and the release fails. Then keep **Load Sample Data** off.
* **The sample vets:** two per sample woreda, of every cadre (veterinarian, technician, assistant, CAHW).
* **The sample animals:** the pack's `animals.json`: every adult sample person has one to three, kept in the person's woreda: cattle, goats, sheep, chickens, donkeys. The Farmer Registry reads the same file for its sample herds, so a farmer's herd there counts the animals here. Sample person `ETH-IND-0007` is farmer `FR-0007`, with the person's national ID, as in the Farmer and Crop Sown Registries. Animal IDs are fixed, so a reinstall gives the same records: `9`, the person's number in seven digits and a sequence (`9000000701`). A person's last animal, when they have more than one, is a young one born in the herd, its mother the first.
* **The sample events:** each young animal's birth; every animal vaccinated against its species' main disease by a vet of its woreda (every fifth by a vet known only to another system), most verified; every second head of cattle also against anthrax; every third animal dewormed; one animal sold to another sample farmer (its change of owner is left to a change request, for a demo) and one dead. One vaccination is corrected.

{% hint style="info" %}
The db-seed image fetches openg2p-data when it is built, so it carries the sample vets and animals of that day's openg2p-data. Samples added to a pack later reach an install with the next registry build.
{% endhint %}

{% hint style="warning" %}
The `<release>-activity-samples` Job **fails the release** if the events cannot be loaded, e.g. no sample animals. Its log gives the reason.
{% endhint %}

## Verify

A healthy install ends with the Jobs complete and the pods running:

```bash
kubectl -n <ns> get jobs
kubectl -n <ns> get pods
kubectl -n <ns> logs job/<release>-db-seed
```

| Job | Expect |
| --- | --- |
| `<release>-db-seed` | Complete. With sample data, its log counts the vets and animals inserted |
| `<release>-activity-samples` | Complete, with counts. Only when sample events are on |
| `<release>-sanity` | Complete: the partner API is up |
| iam-register | Complete |
| `<release>-dashboards` | Complete. Its log says the dashboards were imported, or that Superset was not reachable and the import was skipped (upgrade the release once Superset is up) |

The release serves these hostnames, named the way every registry's are ([Hostnames](../../../../products/registry/registry/deployment-and-extension/packaging-and-reference-registry.md#hostnames)). With the release `lsr` and Base Domain `trial.openg2p.org`:

| Hostname | Serves | Who uses it |
| --- | --- | --- |
| `lsr.trial.openg2p.org` | The staff portal | Staff, in the browser |
| `lsr-staff-api.trial.openg2p.org` | The staff portal's API | AWE, which posts approval decisions to it (`/awe/webhooks/decision`); IAM. The staff portal calls the API inside the cluster |
| `lsr-partner-api.trial.openg2p.org` | The partner API | Partners searching animals with consent (or the Composite); vets' systems sending events |
| `lsr-idgenerator-api.trial.openg2p.org` | The ID generator | Administrators. The registry calls it inside the cluster, for Animal and Vet IDs |

Then open the staff portal at `https://<Registry Hostname>`:

* **Animals** lists the animals (the sample animals, if loaded). An animal's record has the tabs Animal, Owner and location, and Documents; its dropdowns show the country's lists.
* **Veterinarians** lists the vets.
* The **Livestock events** register shows the five event types under **Record**, and with sample data the events, each animal's current state and the indicators.
* In Superset, searching the dashboard list for the release name shows its three dashboards (`lsr · Livestock Overview`, …); with sample data they have figures.

## Staff access

The install onboards the registry on IAM and Keycloak itself. There is no manual step.

* **IAM:** the `iam-register` Job registers the application `<release>-staff-portal` (the tile **Livestock Registry**), its roles, and the permissions each role grants.
* **Keycloak:** the keycloak-init Job creates the client `<release>-staff-portal` in the `staff` realm with the registry's roles. The demo staff users (`alex.carter`, `nina.patel`, …) are created by db-seed, only with **Load Sample Data**.
* **A new staff user:** in Keycloak, realm `staff` → **Users** → the user → **Role mapping**, assign roles of the client `<release>-staff-portal`.

## Adding an animal and approving it

An animal is not added from the **Animals** list. It is added through intake:

1. On the staff portal's home page, open **Form Submissions** and choose **Animal**.
2. **Add New** (top right) → **New animal**, fill in the form (the owner's Farmer ID and national ID among it) and submit.
3. The submission goes to AWE for approval. With sample data, db-seed sets up two policies per register (**Animal Intake Form**, **Animal Change Request**, and the same for veterinarians). Each has two stages, approved in order: stage 1 by `alex.carter`, stage 2 by `nina.patel`.
4. Each approver signs in to the staff portal (password: **AWE Approver User Password** from the install) and approves under **Tasks**.
5. On the second approval AWE calls the staff API back; the rest runs in the background (Celery): the animal is created, with a temporary `TEMP-…` ID, then the ID generator gives it its Animal ID.

A change to an existing animal (a new owner after a sale, for example) raises a change request that follows the same two stages. A vet is added the same way, under **Veterinarian**.

## Uninstall

`helm uninstall` leaves the database, PVCs and IAM rows behind. Use the repository's script, with `--dry-run` first:

```bash
./scripts/uninstall-registry.sh --namespace <ns> --release lsr --dry-run
./scripts/uninstall-registry.sh --namespace <ns> --release lsr
```

It first removes the release's dashboards, charts, datasets and connection from Superset (they live in commons-services, so `helm uninstall` leaves them), then the release, leftover Jobs, labelled Secrets and ConfigMaps, the registry's database and role in `commons-postgresql`, its IAM rows, and its PVCs and PVs. Options: `--keep-iam`, `--keep-dashboards`, `--keep-pvs`, `--force`, `--yes`; `--superset-release` and `--superset-namespace` when Superset is not `commons-services` in the same namespace. It leaves shared services alone: the Keycloak client, the approval policies in the shared AWE database, and Master Data.
