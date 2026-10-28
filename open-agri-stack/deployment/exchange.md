---
description: >-
  Installing the Agri Stack Exchange in its own namespace: its services through
  Commons Base and Commons Services, then the Composite, with the Rancher form
  fields to choose and the checks.
---

# Exchange

Step 2 of the [install order](README.md#install-order), in the namespace `agrix`, once the registries are installed. What the Exchange is: [The Exchange](../architecture/exchange.md).

## What gets installed

| Service | Role in the Exchange | Installed by |
| --- | --- | --- |
| Partner Management | Partners, their keys and use-case policies; the Composite's key | Commons Services |
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
| Consent Manager | Exchange Role | **exchange** | The CM issues consent tokens to the Composite |
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
openg2p-consent-manager:
  global:
    agriStackExchange:
      role: exchange
  partnerPortal:
    enabled: true
```

</details>

**Check:** both releases `deployed` and every pod running; the CM's public keys answer at `https://consent-manager-partner.agrix.openg2p.org/api/consent-manager-partner/.well-known/jwks.json`, and the partner portal opens at `https://consent-partner-portal.agrix.openg2p.org`.

## Composite

Install **Agri Stack Composite** in `agrix`. Only the registries' search URLs have no default:

| Group | Field | Value |
| --- | --- | --- |
| Integration | Farmer Registry Search URL | `https://partner-fr.trial.openg2p.org/dci/registry/sync/search` ([Farmer Registry](farmer-registry.md#check)) |
| Integration | Crop Sown Registry Search URL | `https://partner-csr.dept1.openg2p.org/dci/registry/sync/search` ([Crop Sown Registry](crop-sown-registry.md#check)) |

Use the departments' public hostnames, never in-cluster service names. Keep the other fields at their defaults for a demo; for production see [Production](production.md#composite). Every option of the chart: [Composite chart settings](../composite/chart-settings.md).

**Check:**

```bash
helm -n agrix list
curl -s https://agri-composite.agrix.openg2p.org/composite/v1/use-cases
```

The release `deployed` and `loan-profile` listed. Queries fail with `signing_unavailable` until the Composite has its signing key: the next step, [After Install](after-install.md).
