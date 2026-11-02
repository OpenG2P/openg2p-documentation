---
description: >-
  Installing the Agri Stack Exchange in its own namespace: its services through
  Commons Base and Commons Services, then the Composite, with the Rancher form
  fields to choose and the checks.
---

# Exchange

Step 2 of the [install steps](README.md#install-steps), in the namespace `agrix`, before or after the registries. What the Exchange is: [The Exchange](../architecture/exchange.md).

## What gets installed

| Service | Role in the Exchange | Installed by |
| --- | --- | --- |
| Partner Management | Partners, their keys and use-case policies; the Composite, onboarded at install | Commons Services |
| Consent Manager, with its partner portal | Farmers' consents, collected by partner staff in the portal; a consent token per registry for the Composite | Commons Services |
| eSignet, and a mock identity system for testing | The farmer's national-ID login in the partner portal | Commons Services |
| Master Data | The catalogue (the same country pack as the registries) | Commons Services |
| Audit Manager, IAM | Audit events; staff login | Commons Services (always on) |
| Keycloak, PostgreSQL, Redis, Kafka, Garage | Login, databases, rate-limit counters, events, consent evidence files | Commons Base |
| **Composite** | The partners' entry point: runs the use cases across the registries | Its own chart ([below](#composite)) |

From **Apps → Charts** in Rancher, in `agrix`, in this order:

| # | Chart (Rancher name) | Release |
| --- | --- | --- |
| 1 | **OpenG2P Commons Base** (`openg2p-commons-base`) | `commons` (fixed) |
| 2 | **OpenG2P Commons Services** (`openg2p-commons-services`) | `commons-services` (fixed) |
| 3 | **Agri Stack Composite** (`openg2p-agri-composite`) | e.g. `agri-composite` |

For production, create the Consent Manager's signing key Secret before step 2 ([Production](production.md#exchange-consent-manager-signing-key)).

## Commons Base

Keep the defaults: PostgreSQL, Keycloak, Redis, Kafka and Garage are all needed. Change only:

| Field | Value | Why |
| --- | --- | --- |
| Install Novu? | **No** | Not used until the Exchange notifies farmers |
| Install Kafka UI? | **No** | Operations only. **Install Kafka?** stays on |

## Commons Services

| Group | Field | Value | Why |
| --- | --- | --- | --- |
| Consent Manager | Exchange Role | **exchange** | The CM issues consent tokens to the Composite; Partner Management onboards the Composite (`PARTNER_AGRI_COMPOSITE`) with its keys read from the Composite in this namespace |
| Consent Manager | Partner Portal? | **Yes** | Partner staff raise consent requests for farmers |
| AWE | Install AWE? | **No** | Partner and policy changes are approved in Partner Management |
| Staff Portal | Install Staff Portal UI? | **No** | No registry here |
| ODK | Install ODK Central? | **No** | Registry data collection |
| Superset | Install Superset? | **No** | Registry dashboards |
| Verifiable Credentials | Install Inji Certify?, Install Inji Verify? | **No** | Nothing in the Exchange issues or checks credentials |
| WebSub | Install WebSub? | **No** | Not used by the Exchange |

Leave on, at their defaults: **Install Master Data?**, **Install Partner Management?**, **Install Consent Manager?**, **Install eSignet?**, **Install Mock Identity System?** (testing only). Leave **Install Keymanager?** off. With **Exchange Role** `exchange`, the other Consent Manager fields can stay empty; their defaults are the reference values ([CM deployment](../../consent-management/deployment/README.md#exchange-optional)).

<details>

<summary>The same choices as YAML (command-line installs)</summary>

```yaml
openg2p-awe:
  enabled: false
openg2p-inji-verify:
  enabled: false
global:
  agriStackExchange:
    role: exchange
openg2p-consent-manager:
  partnerPortal:
    enabled: true
```

</details>

**Check:** both releases `deployed` and every pod running; the CM's public keys answer at `https://consent-manager-partner.agrix.openg2p.org/api/consent-manager-partner/.well-known/jwks.json`, and the partner portal opens at `https://consent-partner-portal.agrix.openg2p.org`.

## Composite

Install **Agri Stack Composite** in `agrix`. Only the registries' search URLs have no default; they follow from each registry's release name and domain, so the registries need not be installed yet:

| Group | Field | Value |
| --- | --- | --- |
| Integration | Farmer Registry Search URL | `https://partner-fr.trial.openg2p.org/dci/registry/sync/search` ([Farmer Registry](farmer-registry.md#check)) |
| Integration | Crop Sown Registry Search URL | `https://partner-csr.dept1.openg2p.org/dci/registry/sync/search` ([Crop Sown Registry](crop-sown-registry.md#check)) |

Use the departments' public hostnames, never in-cluster service names. Keep the other fields at their defaults; **Generate Signing Key** (on) gives the Composite its key. For production see [Production](production.md#composite). Every option of the chart: [Composite chart settings](../composite/chart-settings.md).

**Check:**

```bash
helm -n agrix list
curl -s https://agri-composite.agrix.openg2p.org/composite/v1/use-cases
curl -s https://agri-composite.agrix.openg2p.org/.well-known/jwks.json
curl -s https://partner-management-partner-api.agrix.openg2p.org/keys/PARTNER_AGRI_COMPOSITE
```

The release `deployed`, `loan-profile` listed, the Composite's public key served, and the Exchange's Partner Management serving the same `kid`. Next: [After Install](after-install.md).
