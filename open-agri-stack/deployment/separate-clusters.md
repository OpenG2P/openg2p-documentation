---
description: >-
  Installing Agri Stack with departments on their own clusters: what changes
  from the one-cluster reference install, and adding a department.
---

# Separate Clusters

Each namespace in the [reference topology](README.md#topology) is already installed as a separate organisation, so the same charts and choices work when each department, and the Exchange, run on their own clusters.

<figure><img src="../../.gitbook/assets/open-agri-stack-separate-clusters.svg" alt="Departments on separate clusters: the Agriculture Department's cluster with the Farmer Registry (trial), the Crops Department's cluster with the Crop Sown Registry (dept1), and the Exchange (agrix) in its own cluster or sharing one with a department. Each cluster has its own ingress and domain. The Composite calls each registry's partner API by public hostname; each department's Consent Manager reads the Exchange Consent Manager's public keys from its public JWKS URL."><figcaption><p>Departments on separate clusters</p></figcaption></figure>

## What changes

| Step | On separate clusters |
| --- | --- |
| [Registries](farmer-registry.md) | Set **Exchange Domain** (Commons Services, Consent Manager group) to the Exchange's domain when it is not `agrix.<parent of this domain>`; or **Composite JWKS URL** when the Composite's hostname differs |
| [Exchange](exchange.md) | The registries' search URLs are their public hostnames, as on one cluster |
| [Testing](testing.md) | Each credential in the test's configuration as an environment variable (`env`), since one `kubectl` context does not reach every cluster |

Across clusters, these must be reachable with public DNS names and trusted TLS:

| From | To |
| --- | --- |
| The Exchange (Composite) | Each registry's partner API |
| Each department (Consent Manager) | The Exchange CM's public keys: `https://consent-manager-partner.<Exchange domain>/api/consent-manager-partner/.well-known/jwks.json` |
| Each department (Partner Management) | The Composite's public keys: `https://agri-composite.<Exchange domain>/.well-known/jwks.json` |

Each department upgrades on its own schedule; after any upgrade, run the [test](testing.md) to check the whole path.

## Adding a department

1. Install its registry as on the [registry pages](farmer-registry.md), with **Exchange Role** `department`.
2. Add the registry to the Composite (`composite.registries` in **Edit YAML**) and to the use cases that read it ([adding a data source](../composite/adding-a-data-source.md)).
3. The department releases its registry's data: [Releasing Data to the Exchange](../administration/releasing-data-to-the-exchange.md).
4. Add the registry to the test's configuration (`registries`) and run the [test](testing.md).
