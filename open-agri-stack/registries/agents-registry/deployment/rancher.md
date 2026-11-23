---
description: >-
  Installing the Agents Registry from the OpenG2P catalogue in Rancher:
  prerequisites, the choices to make, sample data, checks after install, and
  uninstall.
---

# Deploying on Rancher

This page lists the steps and choices. What the registry is: [Agents Registry](../README.md). Install order and the install Jobs: [Deployment](README.md).

## Prerequisites

1. A Kubernetes cluster, with admin rights to it and to Rancher.
2. **commons-base** and **commons-services** installed and healthy in the namespace. See the [Commons Helm Chart](../../../../deployment/openg2p-commons-helm-chart.md). The registry uses, from commons-services:

   | Service | Needed for | Setting in the commons-services form |
   | --- | --- | --- |
   | **Master Data** | Every coded field (the `AGENT_*` lists) and the geography | **Country Pack** (e.g. `ETH`), **Dataset Themes** `agriculture`, **Load Datasets** on |
   | **AWE** | Agent registrations and changes | **Install AWE?** on |
   | **Partner Management** | Signature checks on the partner API (a learning platform's trainings) | On (the default) |

   The Consent Manager is not used.
3. The OpenG2P catalogue added in Rancher (**Apps → Repositories**).

{% hint style="warning" %}
Without the **agriculture** domain in Master Data, the install succeeds but the forms' dropdowns are empty and every training is rejected. Master Data must also hold the `AGENT_*` lists: a Master Data seeded from an openg2p-data older than the Agents Registry lacks them, and needs its country pack loaded again.
{% endhint %}

## Install

1. In Rancher, select the cluster and the namespace.
2. Under **Apps → Charts**, refresh the repositories and select **OpenG2P Agents Registry**.
3. Choose the version. Tick **Show pre-release versions** to see `0.0.0-develop.N` versions.
4. Name the release, e.g. `agents`. The release name is part of the hostnames and the database name.
5. Tick **Customize Helm options before install**, then **Next**.
6. Make the choices below, then **Install**.

The form is the platform chart's form plus an **Agents Registry** group. In a values file, platform settings sit under `registry.*` and shared settings under `global.*`.

## Choices

The defaults suit a production-like install. Change only these.

| Field | Choose | Why |
| --- | --- | --- |
| **Base Domain** | Your environment's domain | Every hostname derives from it. Default `<namespace>.openg2p.org`; the staff portal is then at `<release>.<Base Domain>` |
| **Load Sample Data** | On for a demo only | Loads the country pack's sample agents. See [Sample data](#sample-data) |
| **Load sample trainings** | On for a demo only | Shown when Load Sample Data is on. See [Sample data](#sample-data) |
| **AWE Approver User Password** | Your own | The initial password of the demo approvers `alex.carter` and `nina.patel` |

**Leave as they are:**

* **Install ID Generator?** and **Enable DB Seed** on: the ID generator issues Agent IDs, and the seed is the registry's configuration.
* **Verify Partner Signature** on, **Enforce Consent** off: the registry shares nothing, and its partner API only takes data in, from signed partners.
* **Load Templates to Object Store** off: the registry renders no records for partners.
* **Sanity - Run Full E2E** off: the platform's e2e tier seeds and searches a reference-registry record this registry does not have.
* **Load Sample Images** and **Optional Seeds**: this registry ships none.

The Agent ID's length is a YAML setting ([Customisation](../customisation.md#agent-id)).

### Production

* Keep **Load Sample Data** and **Load sample trainings** off.
* Replace the demo approvers with the country's ([Customisation](../customisation.md#approvals)).

{% hint style="danger" %}
**Never promote a demo namespace to production.** Sample agents and trainings are recorded as real records and cannot be separated cleanly afterwards. Install fresh.
{% endhint %}

## Sample data

Sample data is off by default. For a demo, turn on both switches:

| Switch | Loads | Needs |
| --- | --- | --- |
| **Load Sample Data** | The country pack's sample agents (`packs/<country>/samples/agents.json` in [openg2p-data](https://github.com/OpenG2P/openg2p-data)), as approved Agent records with their specializations and qualifications | Master Data, for the areas' geography |
| **Load sample trainings** | Trainings and certifications for the sample agents | The sample agents |

* **Which pack:** db-seed picks the pack whose sample agents' areas Master Data knows, so the samples match the country Master Data was installed with. A pack without `samples/agents.json` loads none.
* **The ETH pack** has 24 Development Agents in eleven woredas of eight regions, among them the Tigray woredas of the pack's sample farmers: DAs, senior DAs, supervisors, woreda specialists and community animal health workers, with one on leave, one suspended and one retired.
* **Agent IDs** are fixed, so a reinstall gives the same records: a woreda's six P-code digits and a sequence (`01010101` is the first DA of Tahtay Adiyabo, `ET010101`).
* **Trainings:** every sample agent has a course in the topic of their primary specialization; every second one also an online course on digital tools; every third one a certification. One training is corrected.

{% hint style="info" %}
The db-seed image fetches openg2p-data when it is built, so it carries the sample agents of that day's openg2p-data. Sample agents added to a pack later reach an install with the next registry build.
{% endhint %}

{% hint style="warning" %}
The `<release>-activity-samples` Job **fails the release** if the trainings cannot be loaded, e.g. no sample agents. Its log gives the reason.
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
| `<release>-db-seed` | Complete. With sample data, its log counts the agents, specializations and qualifications inserted |
| `<release>-activity-samples` | Complete, with counts. Only when sample trainings are on |
| `<release>-sanity` | Complete: the partner API is up |
| iam-register | Complete |

Then open the staff portal at `https://<Registry Hostname>`:

* **Agent** lists the agents (the sample agents, if loaded). An agent's record has the tabs Profile, Employment and assignment, Specializations and qualifications, and Documents; its dropdowns show the country's lists.
* The **Trainings** activity register shows the two activity types under **Record**, and with sample data the trainings, the per-agent summaries and the indicators.

## Uninstall

`helm uninstall` leaves the database, PVCs and IAM rows behind. Use the repository's script, with `--dry-run` first:

```bash
./scripts/uninstall-registry.sh --namespace <ns> --release agents --dry-run
./scripts/uninstall-registry.sh --namespace <ns> --release agents
```

It removes the release, leftover Jobs, labelled Secrets and ConfigMaps, the registry's database and role in `commons-postgresql`, its IAM rows, and its PVCs and PVs. Options: `--keep-iam`, `--keep-pvs`, `--force`, `--yes`. It leaves shared services alone: the Keycloak client, the approval policies in the shared AWE database, and Master Data.
