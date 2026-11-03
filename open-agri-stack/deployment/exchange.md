---
description: >-
  Installing the Agri Stack Exchange in its own namespace: Commons Base,
  Commons Services, then the Composite, with the Rancher form fields to set
  and the checks.
---

# Exchange

Step 2 of the [install steps](README.md#install-steps), in the namespace `agrix`, before or after the registries. What the Exchange is made of: [The Exchange](../architecture/README.md#the-exchange).

In Rancher, **Apps → Charts**, namespace `agrix`, install in this order: [Commons Base](#commons-base), [Commons Services](#commons-services), [Composite](#composite). Start each once the one before is `deployed` with all its pods running.

## Commons Base

Chart **OpenG2P Commons Base** (`openg2p-commons-base`), release `commons`. Keep the defaults, except:

| Field | Value |
| --- | --- |
| Install Novu? | **No** |
| Install Kafka UI? | **No** (keep **Install Kafka?** on) |

## Commons Services

Chart **OpenG2P Commons Services** (`openg2p-commons-services`), release `commons-services`. For production, first create the Consent Manager's signing key Secret ([Production](production.md#exchange-consent-manager-signing-key)).

| Group | Field | Value |
| --- | --- | --- |
| Consent Manager | Exchange Role | **exchange** |
| Consent Manager | Partner Portal? | **Yes** |
| AWE | Install AWE? | **No** |
| Staff Portal | Install Staff Portal UI? | **No** |
| ODK | Install ODK Central? | **No** |
| Superset | Install Superset? | **No** |
| Verifiable Credentials | Install Inji Certify?, Install Inji Verify? | **No** |
| WebSub | Install WebSub? | **No** |

Keep the rest at the defaults: Master Data (with the same country pack as the registries), Partner Management, Consent Manager, eSignet and the Mock Identity System on; Keymanager off. Other Consent Manager fields: [CM deployment](../../consent-management/deployment/README.md#exchange-optional).

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

## Composite

Chart **Agri Stack Composite** (`openg2p-agri-composite`), release e.g. `agri-composite`. Set each registry's partner search URL, with its public hostname (never an in-cluster service name). The registries need not be installed yet:

| Group | Field | Value |
| --- | --- | --- |
| Integration | Farmer Registry Search URL | `https://partner-fr.trial.openg2p.org/dci/registry/sync/search` ([Farmer Registry](farmer-registry.md#check)) |
| Integration | Crop Sown Registry Search URL | `https://partner-csr.dept1.openg2p.org/dci/registry/sync/search` ([Crop Sown Registry](crop-sown-registry.md#check)) |

Keep the rest at the defaults (**Generate Signing Key** on). Production: [Production](production.md#composite). All options: [Composite chart settings](../composite/chart-settings.md).

## Check

```bash
helm -n agrix list
curl -s https://consent-manager-partner.agrix.openg2p.org/api/consent-manager-partner/.well-known/jwks.json
curl -s https://agri-composite.agrix.openg2p.org/composite/v1/use-cases
curl -s https://agri-composite.agrix.openg2p.org/.well-known/jwks.json
curl -s https://partner-management-partner-api.agrix.openg2p.org/keys/PARTNER_AGRI_COMPOSITE
```

| Expect | If not |
| --- | --- |
| Three releases `deployed` | `kubectl -n agrix get pods`; a hook Job waiting for a service of a release not yet installed |
| The CM's public keys | The Consent Manager's pod and log |
| `loan-profile` listed | The Composite API's log |
| The Composite's public key | Secret `agri-composite-signing` and the Composite API's log |
| Partner Management serving the same `kid` | **Exchange Role** not `exchange`; the PM staff API log ("Bootstrap") |

The partner portal opens at `https://consent-partner-portal.agrix.openg2p.org`. Next: step 3 of the [install steps](README.md#install-steps).
