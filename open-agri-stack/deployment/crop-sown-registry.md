---
description: >-
  Installing the Crop Sown Registry for Agri Stack: its commons with the
  Consent Manager in the department role, then the Crop Sown Registry chart;
  what it shares, the Farmer ID and national ID in consent checks, the
  Composite as a partner.
---

# Crop Sown Registry

The [Crop Sown Registry](../../products/registry/crop-sown-registry/README.md) (CSR) is the crop department's registry of crop seasons: what each farmer plans, prepares, sows, observes and harvests, plot by plot and season by season. It is an [activity register](../../products/registry/registry/features/activity-register.md) on the registry platform, plus a Cluster register. Its activities, outputs, data scopes and generic install are documented there. This page says what to install and set for Agri Stack. On these pages it runs in the namespace `dept1`, in the Crops Department's cluster ([topology](README.md#topology)). It needs no other registry to run.

## What to install

From **Apps → Charts** in Rancher, in the `dept1` namespace, in this order:

| # | Chart (Rancher name) | Release |
| --- | --- | --- |
| 1 | **OpenG2P Commons Base** (`openg2p-commons-base`) | `commons` (fixed) |
| 2 | **OpenG2P Commons Services** (`openg2p-commons-services`) | `commons-services` (fixed) |
| 3 | **OpenG2P Crop Sown Registry** (`openg2p-crop-sown-registry`) | `csr` |

The generic steps, every form field, ODK Central and the checks: [Crop Sown Registry → Deploying on Rancher](../../products/registry/crop-sown-registry/deployment/rancher.md). Commons: [Commons Helm chart](../../deployment/openg2p-commons-helm-chart.md).

## Form fields to choose

The defaults work for a demo. Change only these.

| Chart | Field | Value | Why |
| --- | --- | --- | --- |
| Commons Services | Exchange Role (Consent Manager) | **department** | The CM trusts consent tokens from the Exchange CM, presented by the Composite, with the public key at `https://consent-manager-partner.agrix.<parent domain>/…/.well-known/jwks.json` |
| Crop Sown Registry | Release name | `csr` | The partner API is then `https://partner-csr.<domain>`, the URL the Composite is given |
| Crop Sown Registry | Load Sample Data | **On**, for a demo only | The two sample clusters |
| Crop Sown Registry | Load sample crop seasons | `true`, for a demo only | Crop seasons for the same farmers and plots as the Farmer Registry's samples ([sample data](#sample-data)) |

Keep the commons-services defaults otherwise: the registry needs Master Data with the `agriculture` dataset theme (every coded field is checked against it), AWE (cluster registrations and changes), Partner Management and the Consent Manager.

Right by default, and not to change: **Verify Partner Signature** and **Enforce Consent** on; the consent data controller `crop-sown-registry`; the PM and CM URLs. **Pull submissions from ODK Central** stays off unless sowings are collected with ODK: turning it on needs an XLSForm you build, a credentials Secret and a mapping ([ODK Central](../../products/registry/crop-sown-registry/deployment/rancher.md#collecting-sowings-with-odk-central)).

The sanity Job's end-to-end check stays off. `scripts/e2e_smoke.py` in the Crop Sown Registry repository does not sign its requests or carry a consent, so it cannot run against an Agri Stack install. Use the [partner test](testing.md#partner-test-public-apis) instead.

## For production

| Field | Value | Why |
| --- | --- | --- |
| Base Domain (both commons charts, and the registry) | The department's own domain | Every hostname sits under it |
| Exchange Domain (Consent Manager) | The Exchange's domain, e.g. `agrix.example.org` | Only when it is not `agrix.<parent of this domain>`. On a separate cluster it usually is not ([Separate Clusters](separate-clusters.md)) |
| Signing Key, Signing Key Secret, Signing Key ID (Consent Manager) | **existing**, the department's own `.p12` | The demo key is public |
| Load Sample Data, Load sample crop seasons, Load Sample People | **Off** | Never promote a demo namespace to production: sample crop seasons cannot be separated cleanly afterwards |

The rest: [Production](../../products/registry/crop-sown-registry/deployment/rancher.md#production).

## What it does in Agri Stack

### How it relates to the Farmer Registry

The two registries share identifiers, not code or databases. In Agri Stack they run in different departments, so the Crop Sown Registry never looks anything up in the Farmer Registry.

* **The farmer** is the Farmer Registry's Farmer ID (`FR-…`). The national ID (Fayda FAN in the shipped Ethiopia example) is recorded alongside on each activity.
* **The plot** is a Farmer Registry land record ID (`LAND-…`).
* **Entities first:** farmers and plots are registered in the Farmer Registry before crop activities are recorded. The Crop Sown Registry checks their IDs by format only.
* **The district is entered** on the plan and the sowing, since the registry cannot read the plot's location.

See [How it relates to the Farmer Registry](../../products/registry/crop-sown-registry/README.md#how-it-relates-to-the-farmer-registry).

### Farmer ID and national ID in consent checks

The register's subject is the farmer by Farmer ID (`subject_type: FARMER_ID`). Its configuration file (`meta_data/activity-config/CropSown.json`) also names `fayda_fan` in `subject_id_fields`. A consent whose subject is the farmer's national ID therefore passes the subject check when the search is by Farmer ID, as long as the registry's own activities record that Farmer ID with that FAN. This is how one consent, given for the national ID, covers both registries. See [sharing through partner search](../../products/registry/registry/design/activity-register.md#sharing-through-partner-search).

### What Agri Stack reads

The `loan-profile` use case searches the `CropSown` register by Farmer ID, read from the Farmer Registry's record (or the subject itself when the partner sends a `FARMER_ID`). Both sources are optional: if the Crop Sown Registry is down or denies, the loan profile still comes back, with that source marked.

| Source | `reg_record_type` | Query |
| --- | --- | --- |
| `season_summaries` | `spdci-extensions-agri:ActivityAggregate` | `subject_id`, `aggregate_type: FARMER_SEASON_SUMMARY`, and the partner's `crop_year` and `season` if given |
| `crop_seasons` | `spdci-extensions-agri:CropSeason` | `subject_id`, and the partner's `crop_year` and `season` if given |

Activities (`spdci-extensions-agri:CropActivity`) and the Cluster register are not read by Agri Stack today.

**Data scopes** in the use case's grant for `crop-sown-registry`:

| Scope | Required or optional |
| --- | --- |
| `crop-sown-registry.farmer_reference` | Required |
| `crop-sown-registry.crop_season` | Required |
| `crop-sown-registry.measures` | Required |
| `crop-sown-registry.location` | Optional |

What each scope covers: [Crop Sown Registry](../../products/registry/crop-sown-registry/README.md#data-scopes).

**Final figures.** A season summary is final (`is_final`) once an administrator locks the season's period in the register's **Settings**. A lender or subsidy programme that must rely on a season's figures should read final summaries. Plans are often made before the season's window, so lock from the planning start, or a late change to a plan makes the summary provisional again.

### The Composite as a partner

As for the [Farmer Registry](farmer-registry.md#the-composite-as-a-partner), the registry sees only the Composite, which names the partner in `header.meta.on_behalf_of`.

| Where (in `dept1`) | What | Set by |
| --- | --- | --- |
| Partner Management | `PARTNER_AGRI_COMPOSITE`, with the Composite's public key and `kid` | [Exchange setup](after-install.md#exchange-setup) |
| Consent Manager, role | **Exchange Role** `department` (trusts `agri-stack-exchange-cm` consent tokens presented by `agri-composite`) | Commons Services form |
| Consent Manager, binding | Audience `agri-composite`, controller `crop-sown-registry` | [Exchange setup](after-install.md#exchange-setup) |
| Consent Manager, standing policy | Allowed scopes: every `crop-sown-registry` scope the Composite's use cases name (for `loan-profile`, the four above); purposes `credit-assessment`; subject ID types `FAYDA_FAN`, `FARMER_ID`; maximum validity `P90D`; fetch type `oneshot` | [Exchange setup](after-install.md#exchange-setup) |

### Searches across farmers

A programme system can read season summaries for many farmers at once (e.g. every final summary for one season for a subsidy run) without a per-farmer consent, only if the registry operator lists it in `REGISTRY_PARTNER_API_DCI_BULK_AGGREGATE_PARTNERS`. Agri Stack's Composite does not use this, and no partner is listed by default. See [Settings only in YAML](../../products/registry/crop-sown-registry/deployment/rancher.md#settings-only-in-yaml).

### Sample data

For a demo, **Load Sample Data** loads two sample clusters and **Load sample crop seasons** records crop seasons for the catalogue's sample people through the post-install Job `<release>-activity-samples`. The farmers and plots match the Farmer Registry's sample data (`FR-0007`, `LAND-0007-1`), so a demo of the `loan-profile` use case returns crop seasons for the same farmer. See [Sample data](../../products/registry/crop-sown-registry/deployment/rancher.md#sample-data).

## Check

```bash
helm -n dept1 list
kubectl -n dept1 get jobs
```

The releases `deployed` and the Jobs complete ([Verify](../../products/registry/crop-sown-registry/deployment/rancher.md#verify)). The partner API answers at `https://partner-csr.dept1.openg2p.org`.
