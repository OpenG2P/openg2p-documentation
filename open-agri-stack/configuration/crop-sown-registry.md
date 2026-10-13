---
description: >-
  What is configured in the Crop Sown Registry install for Agri Stack: the data
  it shares, the Farmer ID and national ID link for consent checks, the composite
  as a partner, and the department Consent Manager with its standing policy.
---

# Crop Sown Registry

The [Crop Sown Registry](../../products/registry/crop-sown-registry/README.md) (CSR) is the crop department's registry of crop seasons: what each farmer plans, prepares, sows, observes and harvests, plot by plot and season by season. It is an [activity register](../../products/registry/registry/features/activity-register.md) on the registry platform ([design](../../products/registry/registry/design/activity-register.md)), plus a Cluster register. Its activities, outputs, data scopes and installation are documented there. This page says what is set for Agri Stack.

In the three-namespace setup it runs in the department namespace `dept1`, release `csr`, with its own commons. It needs no other registry to run. See [deploying on a cluster](../guides/deployment.md#crop-sown-registry).

## Registry settings

| Setting | Value for Agri Stack | Default? |
| --- | --- | --- |
| **Verify Partner Signature** | On | Yes |
| **Enforce Consent** | On | Yes |
| Consent data controller | `crop-sown-registry` | Yes (the registry variant) |
| **Load Sample Data**, **Load sample crop seasons** | On for a demo only | Off |
| **Pull submissions from ODK Central** | Off, unless sowings are collected with ODK | Off |

Master Data in `dept1` needs the **agriculture** dataset theme (the default): every coded field is checked against it. Settings, ODK and sample data are explained in [Deploying on Rancher](../../products/registry/crop-sown-registry/deployment/rancher.md).

## How it relates to the Farmer Registry

The two registries share identifiers, not code or databases. In Agri Stack they run in different departments, so the Crop Sown Registry never looks anything up in the Farmer Registry.

* **The farmer** is the Farmer Registry's Farmer ID (`FR-…`). The national ID (Fayda FAN in the reference setup) is recorded alongside on each activity.
* **The plot** is a Farmer Registry land record ID (`LAND-…`).
* **Entities first:** farmers and plots are registered in the Farmer Registry before crop activities are recorded. The Crop Sown Registry checks their IDs by format only.
* **The district is entered** on the plan and the sowing, since the registry cannot read the plot's location.

See [How it relates to the Farmer Registry](../../products/registry/crop-sown-registry/README.md#how-it-relates-to-the-farmer-registry).

### Farmer ID and national ID in consent checks

The register's subject is the farmer by Farmer ID (`subject_type: FARMER_ID`). Its configuration file (`meta_data/activity-config/CropSown.json`) also names `fayda_fan` in `subject_id_fields`. A consent whose subject is the farmer's national ID therefore passes the subject check when the search is by Farmer ID, as long as the registry's own activities record that Farmer ID with that FAN. This is how one consent, given for the national ID, covers both registries. See [sharing through partner search](../../products/registry/registry/design/activity-register.md#sharing-through-partner-search).

## What Agri Stack reads

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

What each scope covers is on the [Crop Sown Registry](../../products/registry/crop-sown-registry/README.md#data-scopes) page.

**Final figures.** A season summary is final (`is_final`) once an administrator locks the season's period in the register's **Settings**. A lender or subsidy programme that must rely on a season's figures should read final summaries. Plans are often made before the season's window, so lock from the planning start, or a late change to a plan makes the summary provisional again.

## The composite as a partner

As for the [Farmer Registry](farmer-registry.md#the-composite-as-a-partner), the registry sees only the composite, which names the partner in `header.meta.on_behalf_of`.

| Where (in `dept1`) | What | Set by |
| --- | --- | --- |
| Partner Management | `PARTNER_AGRI_COMPOSITE`, with the composite's public key and `kid` | [Exchange setup](../guides/exchange-setup.md) |
| Consent Manager, role | **Agri Stack Exchange Role** `department` (trusts `agri-stack-exchange-cm` tokens presented by `agri-composite`) | commons-services form |
| Consent Manager, binding | Audience `agri-composite`, controller `crop-sown-registry` | [Exchange setup](../guides/exchange-setup.md) |
| Consent Manager, standing policy | Allowed scopes: every `crop-sown-registry` scope the composite's use cases name (for `loan-profile`, the four above); purposes `credit-assessment`; subject ID types `FAYDA_FAN`, `FARMER_ID`; maximum validity `P90D`; fetch type `oneshot` | [Exchange setup](../guides/exchange-setup.md) |

## Searches across farmers

A programme system can read season summaries for many farmers at once (e.g. every final summary for one season for a subsidy run) without a per-farmer consent, only if the registry operator lists it in `REGISTRY_PARTNER_API_DCI_BULK_AGGREGATE_PARTNERS`. Agri Stack's composite does not use this, and no partner is listed by default. See [Settings only in YAML](../../products/registry/crop-sown-registry/deployment/rancher.md#settings-only-in-yaml).

## Sample data

For a demo, **Load Sample Data** loads two sample clusters and **Load sample crop seasons** records crop seasons for Master Data's sample people through the post-install Job `<release>-activity-samples`. The farmers and plots match the Farmer Registry's sample data (`FR-0007`, `LAND-0007-1`), so a demo of the `loan-profile` use case returns crop seasons for the same farmer. See [Sample data](../../products/registry/crop-sown-registry/deployment/rancher.md#sample-data).
