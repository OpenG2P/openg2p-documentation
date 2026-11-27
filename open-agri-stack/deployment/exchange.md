---
description: Installing the Exchange.
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

**Use cases from the Composite in Partner Management.** Set Partner Management's catalogue source to the Composite's use cases (YAML below: `partner-management.staffPortalApi.catalogueSources`; not in the Rancher form). The **Use case** field of a policy is then a list of the Composite's published use cases, and Partner Management refuses a name the Composite does not publish. Left empty, the field is free text and only its form (`name@major`) is checked. The source can be set before the Composite is installed: until it answers, a use case is accepted with a warning for the approver.

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
partner-management:
  staffPortalApi:
    catalogueSources:
      - kind: use_cases
        url: http://composite-api/composite/v1/use-cases
        label: Agri Stack Composite
```

</details>

## Composite

Chart **Agri Stack Composite** (`openg2p-agri-composite`). Set or check these fields; keep every other field at its default. The registries are installed by now (step 1); if one is not, the Composite still installs, and that registry's source answers `unavailable` (or `error`, when the gateway answers 404 for its hostname) until it is.

| Group | Field | Value | Notes |
| --- | --- | --- | --- |
| — | Namespace | `agrix` | The Exchange's namespace |
| — | Release name | `composite` | Keep it: the Exchange CM reads consent templates from `http://composite-api` (otherwise set `global.agriStackExchange.consentTemplateSourceUrl` in Commons Services, **Edit YAML**). The public hostnames and the partner ID stay `agri-composite` (below); only the in-cluster Services (`composite-api`, `composite-console`) take the release name |
| General | Base Domain | Empty: `agrix.openg2p.org` | `<namespace>.openg2p.org` by default; set it if your domain differs |
| General | Composite Hostname | Empty: `agri-composite.agrix.openg2p.org` | The departments' Partner Management read the Composite's keys here |
| Integration | Composite Partner ID | `agri-composite` | The default. Must match in every install ([settings that must agree](README.md#settings-that-must-agree-across-installs)) |
| Integration | Farmer Registry Search URL | `https://fr-partner-api.trial.openg2p.org/dci/registry/sync/search` | Required ([Farmer Registry](farmer-registry.md#check)) |
| Integration | Crop Sown Registry Search URL | `https://csr-partner-api.dept1.openg2p.org/dci/registry/sync/search` | Required ([Crop Sown Registry](crop-sown-registry.md#check)) |
| Integration | Livestock Registry Search URL | `https://lsr-partner-api.dept1.openg2p.org/dci/registry/sync/search` | Optional. Empty: `loan-profile` answers without the farmer's animals (its `livestock` source reports `error`) ([Livestock Registry](livestock-registry.md#check)) |
| Agri Stack exchange | Consent Mode | `exchange` | The default |
| Signing key | Generate Signing Key | On | The default: creates Secret `agri-composite-signing` once and keeps it |
| Console | Enable Console | On | The default: the staff console at `agri-composite-console.agrix.openg2p.org` |

Registry URLs are each registry's public partner API host, `<release>-partner-api.<department domain>`, never an in-cluster service name. Production: [Production](production.md#composite). Every option: [Composite Chart Settings](composite-chart-settings.md).

## Check

```bash
helm -n agrix list
curl -s https://consent-manager-partner.agrix.openg2p.org/api/consent-manager-partner/.well-known/jwks.json
curl -s https://agri-composite.agrix.openg2p.org/composite/v1/use-cases
curl -s https://agri-composite.agrix.openg2p.org/.well-known/jwks.json
curl -s -o /dev/null -w '%{http_code}\n' 'https://agri-composite.agrix.openg2p.org/composite/v1/internal/consent-templates?partner=bank-a'
curl -s https://partner-management-partner-api.agrix.openg2p.org/keys/PARTNER_AGRI_COMPOSITE
```

| Expect | If not |
| --- | --- |
| Three releases `deployed` | `kubectl -n agrix get pods`; a hook Job waiting for a service of a release not yet installed |
| The CM's public keys | The Consent Manager's pod and log |
| `loan-profile` listed | The Composite API's log |
| The Composite's public key | Secret `agri-composite-signing` and the Composite API's log |
| `404` for the internal path | Another code: an older Composite chart, or Istio older than 1.15 ([internal API](composite-chart-settings.md#hostnames-and-ingress)) |
| Partner Management serving the same `kid` | **Exchange Role** not `exchange`; the PM staff API log ("Bootstrap") |

The partner portal opens at `https://consent-partner-portal.agrix.openg2p.org`. Next: step 3 of the [install steps](README.md#install-steps).
