---
description: >-
  Running Agri Stack's departments on their own clusters: reachable hostnames,
  domains, availability, upgrades and adding a department.
---

# Separate Clusters

The installs on these pages already treat each namespace as a separate organisation, so the same charts and settings work when departments run on their own clusters, as the Crops Department's Crop Sown Registry does in the [topology](README.md#topology). In addition:

| Topic | What to do |
| --- | --- |
| **Hostnames reachable across departments** | From the Exchange: the Composite's API and the Exchange CM's public keys (`/.well-known/jwks.json` on its partner host, the only partner API path published; also the consent token status endpoint when **Expose Token Status Endpoint** is on, needed only if a department switches the status check on). From each department: its registry's partner API. Use public DNS names and trusted TLS for them |
| **Domains** | Each department CM finds the Exchange CM at `agrix.<parent of its own domain>`. On another cluster with another domain, set **Exchange Domain** in the department's Commons Services form (Consent Manager group) |
| **Registry URLs** | The Composite's **Farmer Registry Search URL** and **Crop Sown Registry Search URL** are the departments' public partner API URLs, as on one cluster |
| **Availability** | The Exchange depends on each department's partner API. Partner keys and catalogue reads are cached, and departments verify consent tokens offline with cached keys; only the optional status check (off by default) needs the Exchange CM per query, and then consent fails closed when it is down. Set timeouts and alerts |
| **Upgrades** | The Exchange and each department upgrade on their own schedules. Check the Composite, the CMs and the registries' partner APIs together after an upgrade ([Upgrades and Uninstall](upgrades-and-uninstall.md)) |
| **Exchange setup** | The [Exchange setup](after-install.md#exchange-setup) uses **one** kubectl context for the Exchange and every department, so it reaches only departments in the Exchange's cluster. For a department on another cluster, set up the Composite there by hand (below) |

## The Composite in a department on another cluster

The department's administrators do steps 3 and 4 of the [Composite's key and access](exchange.md#the-composites-key-and-access): the Composite onboarded in their PM with its public key and `kid` (from the Exchange), and its scope policy for their registry; and their CM trusting the Exchange's consent tokens.

{% hint style="info" %}
**To be written:** running the Exchange setup against departments on other clusters (a kubectl context per department).
{% endhint %}

## Adding a department

1. Install its commons with **Exchange Role** `department`, and its registry ([Farmer Registry](farmer-registry.md) and [Crop Sown Registry](crop-sown-registry.md) show the pattern).
2. Add the registry to the Composite (`composite.registries`, in **Edit YAML**) and to the use cases that read it ([adding a data source](../composite/adding-a-data-source.md)).
3. Rerun the [Exchange setup](after-install.md#exchange-setup) with the new `--registry <controller>=<namespace>` (same cluster), or set up the Composite in it by hand (another cluster, above).
