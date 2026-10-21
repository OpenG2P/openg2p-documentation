---
description: >-
  Deploying Agri Stack: the topology assumed on these pages, the
  prerequisites, the install order across namespaces, what each namespace holds
  afterwards and the names that must match across installs.
---

# Deployment

Agri Stack is installed from unchanged OpenG2P Helm charts, through Rancher. These pages say which charts go where and which form fields to change. What each registry does in Agri Stack: [Registries in Agri Stack](../architecture/registries.md). Each product's own install details stay in its own docs, linked from each page.

## Topology

These pages assume one arrangement, used for the reference install:

| Cluster | Namespace (example) | Install | Holds |
| --- | --- | --- | --- |
| Agriculture Department | `agrix` | The **Exchange**: commons (Exchange role) and the **Composite** | Partner Management and Consent Manager for partners, the partner portal, eSignet, the Composite. No registry |
| Agriculture Department | `trial` | The **Farmer Registry**: commons (department role) and the Farmer Registry | Farmers, land, households, declared main crops |
| Crops Department | `dept1` | The **Crop Sown Registry**: commons (department role) and the Crop Sown Registry | Crop seasons, plot by plot and season by season |

Each namespace is installed as if it were a separate organisation, with its own commons (Keycloak, Postgres, Partner Management, Consent Manager, Master Data). Calls between namespaces use **public hostnames** only, never in-cluster service names. A partner (e.g. `bank-a`) onboards and the farmer consents only at the Exchange; each department still decides at its own boundary. Why it is split this way: [across departments](../architecture/README.md#across-departments).

For testing, all three namespaces can run on one cluster; the commands on these pages assume that. With the Crops Department on its own cluster, see [Separate Clusters](separate-clusters.md). Each needs its own domain on its `internal` gateway (e.g. `*.agrix.openg2p.org`, `*.trial.openg2p.org`, `*.dept1.openg2p.org`), with DNS and TLS.

{% hint style="info" %}
**Other arrangements: to be written.** What would change: the hostnames (each install's Base Domain, the registries' search URLs in the Composite, the Exchange Domain in each department); which Consent Manager trusts which (each department CM trusts the Exchange CM's consent tokens); and where the Composite runs (always next to the Exchange CM it asks for consent tokens). Departments on separate clusters: [Separate Clusters](separate-clusters.md).
{% endhint %}

## Prerequisites

| What | Where |
| --- | --- |
| A Kubernetes cluster with Rancher, Istio and the `internal` gateway | [OpenG2P deployment](../../deployment/README.md): [infrastructure setup](../../operations/deployment/infrastructure-setup/README.md) |
| One environment (namespace) per install, with its domain, DNS and TLS | [Environment setup](../../operations/deployment/environment-setup-multi-node.md) |
| The OpenG2P chart repository in Rancher (**Apps → Repositories**) | [Commons Helm chart](../../deployment/openg2p-commons-helm-chart.md) |
| `kubectl` and Python 3 on the operator's machine, for the [after-install scripts](after-install.md) | [agri-stack/scripts](https://github.com/openg2p/agri-stack/tree/develop/scripts) |

**Catalogue in every namespace.** Each namespace's Master Data loads its own catalogue. Load the **same country pack version** everywhere, so codes and geography match across registries. The commons-services defaults are right for Agri Stack: **Country Pack** `ETH` (the shipped example), **Dataset Themes** `agriculture` (the registries' dropdowns and coded fields need it), **Load Datasets** on, **Load Sample People** on for a demo (the registries' sample farmers and the mock identity system's identities are these people). The ETH pack carries a licence obligation (CC BY-IGO, attribution required); see [Country Packs: sources and licence](../../platform/platform-services/master-data-service/country-packs.md#sources-and-licence).

## Install order

Install each step only after the previous one is ready (all pods running, release `deployed`). The departments can be installed in parallel with the Exchange.

| # | Namespace | Install | Page |
| --- | --- | --- | --- |
| 1 | `agrix` | Commons Base, Commons Services (Exchange role) | [Exchange](exchange.md) |
| 2 | `trial` | Commons Base, Commons Services (department role), Farmer Registry `fr` | [Farmer Registry](farmer-registry.md) |
| 3 | `dept1` | Commons Base, Commons Services (department role), Crop Sown Registry `csr` | [Crop Sown Registry](crop-sown-registry.md) |
| 4 | `agrix` | Composite, with the two registries' search URLs | [Composite](composite.md) |
| 5 | `agrix` | Partner portal realm and users; Exchange setup (scripts) | [After Install](after-install.md) |
| 6 | — | Test | [Testing](testing.md) |

## What each namespace holds afterwards

| Where | What |
| --- | --- |
| `agrix` PM | The Composite (`PARTNER_AGRI_COMPOSITE`, its key) and each partner (`PARTNER_BANK_A`, …) with its key and a **use-case policy per use case** it may call (`loan-profile@1`), with purposes and subject ID types. A partner is onboarded **only here** |
| `agrix` CM | The partners' consents; it reads each partner's use-case policies from the `agrix` PM |
| `trial` PM and `dept1` PM | The Composite (`PARTNER_AGRI_COMPOSITE`, same `kid`), so each registry verifies the Composite's signature, and its **scope policy** for the registry's data controller: the ceiling of what the department releases through the Exchange (allowed purposes, data scopes, subject ID types), covering every published use case |
| `trial` CM and `dept1` CM | The Exchange CM as a **trusted token issuer** (issuer `agri-stack-exchange-cm`, its public keys at `https://consent-manager-partner.agrix.openg2p.org/api/consent-manager-partner/.well-known/jwks.json`, presenter `agri-composite`) |

The registries need no change: each keeps calling its own CM, which accepts the Exchange's consent tokens. A department's scope policy for the Composite caps what any partner gets from it (token scopes ∩ the Composite's scope policy); see [Data-Sharing Policies](../architecture/data-sharing-policies.md). A denial from a department shows as that source's `denied` status with the registry's reason.

## Names that must match across installs

The installs only work together if these names match. The defaults match everywhere, so a default install needs none of them set.

| Name | Value | Used by |
| --- | --- | --- |
| Composite partner ID | `agri-composite` | The Composite (**Composite Partner ID**); its PM entry `PARTNER_AGRI_COMPOSITE` in every PM, with its scope policies in the department PMs; the token presenter at the Exchange CM; the trusted presenter at the department CMs |
| Consent token issuer | `agri-stack-exchange-cm` | The Exchange CM (issuer); the department CMs (trusted issuer) |
| Data controllers | `farmer-registry`, `crop-sown-registry` | Each registry (its variant); the grants in a consent; the Composite's registries; the data controller of each PM scope policy |
| Subject ID types | `FAYDA_FAN`, `FARMER_ID` | The use case's input; the PM policies (offered from the Master Data list `SUBJECT_ID_TYPE`); consents. The registries map the DCI type `UIN` to `FAYDA_FAN` (`consentSubjectIdTypes`, the registry charts' default) |
| Purposes | `credit-assessment` | The use case's purpose; the PM policies (offered from the Master Data list `CONSENT_PURPOSE`); consents |
| Exchange domain | `agrix.<parent domain>` | The department CMs find the Exchange CM's public keys there |

## Pages

| Page | Covers |
| --- | --- |
| [Exchange](exchange.md) | Commons Base and Commons Services in `agrix`: Exchange role, partner portal, eSignet, mock identity system |
| [Farmer Registry](farmer-registry.md) | Commons (department role) and the Farmer Registry in `trial` |
| [Crop Sown Registry](crop-sown-registry.md) | Commons (department role) and the Crop Sown Registry in `dept1` |
| [Composite](composite.md) | The Composite chart and all its options |
| [After Install](after-install.md) | Partner portal realm and users; Exchange setup (the Composite's key and its department entries) |
| [Testing](testing.md) | Testing end to end; the partner test |
| [Upgrades and Uninstall](upgrades-and-uninstall.md) | Upgrading charts and images; uninstall scripts |
| [Separate Clusters](separate-clusters.md) | What changes when departments run on their own clusters |

## Repositories

| Repository | What |
| --- | --- |
| [OpenG2P/registry-platform](https://github.com/OpenG2P/registry-platform) | The registry platform, including activity registers |
| [OpenG2P/farmer-registry](https://github.com/OpenG2P/farmer-registry) | The Farmer Registry extension and chart |
| [OpenG2P/crop-sown-registry](https://github.com/OpenG2P/crop-sown-registry) | The Crop Sown Registry extension and chart |
| [OpenG2P/consent-manager](https://github.com/OpenG2P/consent-manager) | The Consent Manager |
| [OpenG2P/commons](https://github.com/OpenG2P/commons) | The commons charts |
| [openg2p/agri-stack](https://github.com/openg2p/agri-stack) | The Composite (`composite/`) and the scripts (`scripts/`) |
