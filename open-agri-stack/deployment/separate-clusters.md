---
description: >-
  Running Agri Stack's departments on their own clusters: reachable hostnames,
  domains, availability, upgrades and adding a department.
---

# Separate Clusters

The installs on these pages already treat each namespace as a separate organisation, so the same charts and settings work when departments run on their own clusters, as the Crops Department's Crop Sown Registry does in the [topology](README.md#topology). In addition:

| Topic | What to do |
| --- | --- |
| **Hostnames reachable across departments** | From the Exchange: the Composite's API and the Exchange CM's partner API (its public keys at `/.well-known/jwks.json` and the consent token status check). From each department: its registry's partner API. Use public DNS names and trusted TLS for them |
| **Domains** | Each department CM finds the Exchange CM at `agrix.<parent of its own domain>`. On another cluster with another domain, set **Exchange Domain** in the department's Commons Services form (Consent Manager group) |
| **Registry URLs** | The Composite's **Farmer Registry Search URL** and **Crop Sown Registry Search URL** are the departments' public partner API URLs, as on one cluster |
| **Availability** | The Exchange depends on each department's partner API. Partner keys and catalogue reads are cached, and consent tokens are verified with cached keys, but the status check needs the Exchange CM: consent fails closed when it is down. Set timeouts and alerts |
| **Upgrades** | The Exchange and each department upgrade on their own schedules. Check the Composite, the CMs and the registries' partner APIs together after an upgrade ([Upgrades and Uninstall](upgrades-and-uninstall.md)) |
| **Exchange setup** | The [Exchange setup](after-install.md#exchange-setup) uses **one** kubectl context for the Exchange and every department, so it reaches only departments in the Exchange's cluster. For a department on another cluster, set up the Composite there by hand (below) |

## The Composite in a department on another cluster

What the Exchange setup does in a department, done by that department's administrators:

1. **PM, key:** onboard `PARTNER_AGRI_COMPOSITE` with the Composite's public key and `kid` (the same as in the Exchange PM; the Exchange setup keeps them in `~/.agri-stack-setup/<ns>/`).
2. **PM, scope policy:** in the same onboarding request (or a policy request, if the Composite is already onboarded), a scope policy for the registry's data controller with the data scopes (required and optional) and purposes of the Composite's published use cases for that registry (`GET /composite/v1/use-cases`, `consent_scopes`), subject ID types `FAYDA_FAN`, `FARMER_ID`, signing algorithm `ES256`, maximum validity `P90D`, fetch type `oneshot`. Approve the request ([access policies](../../platform/platform-services/partner-management/functional-specifications.md#access-policies); why: [the Composite as a partner](../architecture/registries.md#the-composite-as-a-partner)).

{% hint style="info" %}
**To be written:** running the Exchange setup against departments on other clusters (a kubectl context per department).
{% endhint %}

## Adding a department

1. Install its commons with **Exchange Role** `department`, and its registry ([Farmer Registry](farmer-registry.md) and [Crop Sown Registry](crop-sown-registry.md) show the pattern).
2. Add the registry to the Composite (`composite.registries`, in **Edit YAML**) and to the use cases that read it ([adding a data source](../composite/adding-a-data-source.md)).
3. Rerun the [Exchange setup](after-install.md#exchange-setup) with the new `--registry <controller>=<namespace>` (same cluster), or set up the Composite in it by hand (another cluster, above).
