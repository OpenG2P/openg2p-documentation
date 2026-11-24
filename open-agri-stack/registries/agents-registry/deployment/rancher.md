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
* **Verify Partner Signature** on; **Enforce Consent** and **Allow Unsigned Read of Data Scope Catalogue** off: the registry shares nothing and has no data scopes, and its partner API only takes data in, from signed partners.
* **Install Beneficiary Portal API?** off: the registry has no beneficiaries; its records are the agents, kept by staff.
* **Install Registry Connector?** off: the platform's ingestion gateway (ODK Central, webhooks, event buses into the partner API). It is of use only if an existing agent system pushes its records that way; then set its hostname and **Partner API Service** (`<release>-partner-api`).
* **Load Templates to Object Store** (versions on Registry Platform `0.0.0-develop.847` or older) off. The templates are Jinja files that convert records between the registry's format and a partner's format (e.g. a farmer record into a DCI search result in the Farmer Registry), uploaded to the object store by db-seed. This registry shares no records and ships none, so turned on there db-seed fails. Later versions have no switch: db-seed uploads the templates an image ships and skips when there are none.
* **Sanity - Run Full E2E** off: the platform's e2e tier seeds and searches a reference-registry record this registry does not have.
* **Load Sample Images** and **Optional Seeds**: this registry ships none.

The Agent ID's length is a YAML setting ([Customisation](../customisation.md#agent-id)).

The form is the platform chart's, so it also shows platform options this registry does not use (the beneficiary portal, the registry connector, consent). Their defaults are already right for it.

### Verifiable credentials

Off by default. To issue agents their credential:

1. The environment needs Inji Certify (commons layer), the Keycloak `agent` realm, and the national ID system's login (eSignet) ([VC Issuance → Deployment](../../../../platform/platform-services/vc-issuance/deployment.md)).
2. In the form's **VC Issuance** group, turn on **Verifiable Credentials (Agent Portal)**, **Agent Portal UI** and **Enable VC Issuance**, and check **Issuer DID**: it must be the DID Certify was installed with (the default is `did:web:` and the Certify hostname).
3. Leave **Register ID** as the chart sets it (the Agent register) and **Set Up Beneficiary Login Automatically** on: here the "beneficiary" is the agent, and the bootstrap Job creates the eSignet client and turns on the Agent register's registrant authentication.

The card design is `files/pdf-templates/agent-card.svg` in the chart, and its title and issuer are `registry.agentPortalApi.pdf.title` and `.issuerName`.

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
* **What a pack's samples hold:** agents of every position, posted in the areas of the pack's sample farmers, with one on leave, one suspended and one retired.
* **Agent IDs** are fixed, so a reinstall gives the same records: the code of the agent's area and a sequence.
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

The release serves these hostnames, named the way every registry's are ([Hostnames](../../../../products/registry/registry/deployment-and-extension/packaging-and-reference-registry.md#hostnames)). With the release `agents` and Base Domain `trial.openg2p.org`:

| Hostname | Serves | Who uses it |
| --- | --- | --- |
| `agents.trial.openg2p.org` | The staff portal | Staff, in the browser |
| `agents-staff-api.trial.openg2p.org` | The staff portal's API | AWE, which posts approval decisions to it (`/awe/webhooks/decision`); IAM. The staff portal calls the API inside the cluster |
| `agents-partner-api.trial.openg2p.org` | The partner API | Signed partners sending data in (a learning platform's trainings) |
| `agents-idgenerator-api.trial.openg2p.org` | The ID generator | Administrators. The registry calls it inside the cluster, for Agent IDs |
| `agents-agent.trial.openg2p.org`, `agents-agent-api.trial.openg2p.org` | The Agent Portal and its API | Only with VC issuance on |

Agents Registry versions on a Registry Platform older than this convention served the APIs as `staff-agents…`, `partner-agents…`, `idgenerator-agents…` and `agent-agents…`.

Then open the staff portal at `https://<Registry Hostname>`:

* **Agent** lists the agents (the sample agents, if loaded). An agent's record has the tabs Profile, Employment and assignment, Specializations and qualifications, and Documents; its dropdowns show the country's lists.
* The **Trainings** activity register shows the two activity types under **Record**, and with sample data the trainings, the per-agent summaries and the indicators.

## Staff access

The install onboards the registry on IAM and Keycloak itself. There is no manual step.

* **IAM:** the `iam-register` Job registers the application `<release>-staff-portal` (the tile **Agents Registry**, with the staff portal and its API's URL), its roles, and the permissions each role grants (the catalogue `files/iam-registration/payload.json` in the platform chart). A user's Keycloak roles are few; what they can do in the portal is the permissions IAM maps to those roles.
* **Keycloak:** the keycloak-init Job creates the client `<release>-staff-portal` in the `staff` realm with the registry's roles (Intake Officer, Data Editor, … Technical Administrator). It gives `admin` the Operations Administrator and Technical Administrator roles, and the demo staff users theirs.
* **A new staff user:** in Keycloak, realm `staff` → **Users** → the user → **Role mapping**, assign roles of the client `<release>-staff-portal`.

## Uninstall

`helm uninstall` leaves the database, PVCs and IAM rows behind. Use the repository's script, with `--dry-run` first:

```bash
./scripts/uninstall-registry.sh --namespace <ns> --release agents --dry-run
./scripts/uninstall-registry.sh --namespace <ns> --release agents
```

It removes the release, leftover Jobs, labelled Secrets and ConfigMaps, the registry's database and role in `commons-postgresql`, its IAM rows, and its PVCs and PVs. Options: `--keep-iam`, `--keep-pvs`, `--force`, `--yes`. It leaves shared services alone: the Keycloak client, the approval policies in the shared AWE database, and Master Data.
