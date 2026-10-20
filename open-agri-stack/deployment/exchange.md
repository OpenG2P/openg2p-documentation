---
description: >-
  Installing the Agri Stack Exchange (agrix): Commons Base and Commons Services
  with the Consent Manager in the Exchange role, the partner portal, eSignet
  and the mock identity system: what to install and which fields to choose.
---

# Exchange

Installing the [Exchange](../architecture/exchange.md): where partners onboard once and use one farmer consent across registries. On these pages it is the namespace `agrix` ([topology](README.md#topology)). The Composite also runs here; it has its own page: [Composite](composite.md).

## What to install

From **Apps → Charts** in Rancher, in the `agrix` namespace, in this order:

| # | Chart (Rancher name) | Release |
| --- | --- | --- |
| 1 | For production only: the CM signing key Secret ([below](#for-production)) | — |
| 2 | **OpenG2P Commons Base** (`openg2p-commons-base`) | `commons` (fixed) |
| 3 | **OpenG2P Commons Services** (`openg2p-commons-services`) | `commons-services` (fixed) |

Then the [Composite](composite.md) and the [after-install steps](after-install.md). The commons charts themselves: [Commons Helm chart](../../deployment/openg2p-commons-helm-chart.md).

## Form fields to choose

The defaults work for a demo. Change only these.

**Commons Base.** Keep PostgreSQL, Keycloak, Redis, Kafka and Garage: all are needed (the Audit Manager and eSignet need Kafka; the consent evidence goes to Garage).

| Field | Value | Why |
| --- | --- | --- |
| Install Novu? | **No** | Notifications: needed only once the Exchange sends farmers notifications (e.g. an SMS after a digital consent) |
| Install Kafka UI? | **No** | Operations only. Not to be confused with **Install Kafka?**, which stays on |

**Commons Services.** Everything is chosen in the form.

| Field | Value | Why |
| --- | --- | --- |
| Install AWE? | **No** | Only needed if approvals in the CM or Master Data are switched on (both off by default) |
| Install Staff Portal UI? | **No** | The registry staff home page; no registry here |
| Install ODK Central? | **No** | Registry data collection |
| Install Superset? | **No** | Registry dashboards |
| Install Inji Certify? | **No** | Issues credentials to beneficiaries |
| Install Inji Verify? | **No** | Checks credentials; nothing in the Exchange does |
| Install WebSub? | **No** | Nothing in the Exchange uses it yet |
| Exchange Role (Consent Manager) | **exchange** | The CM issues a consent token per registry to the Composite |
| Partner Portal? (Consent Manager) | **Yes** | Partner users (e.g. bank staff) raise consent requests for farmers |

Left at their defaults, and needed: **Install Master Data?** (the catalogue), **Install Partner Management?**, **Install Consent Manager?**, **Install eSignet?** (the farmer's national-ID login in the partner portal), **Install Mock Identity System?** (the identities eSignet checks, for testing). Artifactory, which eSignet and the mock identity system use, is always installed. **Install Keymanager?** stays off: Agri Stack does not use it. The IAM service, the Audit Manager and keycloak-init have no form field and are on.

With **Exchange Role** `exchange`, the other Consent Manager fields can stay empty: their defaults are the reference values ([below](#consent-manager)).

<details>

<summary>The same choices as YAML (command-line installs, or a commons-services version without the Consent Manager form fields)</summary>

```yaml
openg2p-awe:
  enabled: false
openg2p-inji-verify:
  enabled: false
openg2p-consent-manager:
  global:
    aweEnabled: false
    agriStackExchange:
      role: exchange
  partnerPortal:
    enabled: true
```

For production, add the signing key under `openg2p-consent-manager`: `global.consentSigningKid: agrix-cm-2026-01` and `consentManagerApi.signingKey: {mode: existing, secretName: agrix-cm-signing, passwordSecretName: agrix-cm-signing}` (`passwordSecretName` is needed on CM charts develop.74 and earlier).

</details>

## For production

| Field | Value | Why |
| --- | --- | --- |
| Base Domain (both commons charts) | The Exchange's own domain, the same in both | Every hostname sits under it. The departments find the Exchange CM under `agrix.<parent domain>`; with another name, each department sets **Exchange Domain** |
| Signing Key (Consent Manager) | **existing** | The demo key is public: anyone could sign consent tokens the departments accept |
| Signing Key Secret | `agrix-cm-signing` | Created before Commons Services, with keys `cm_signing.p12` and `password` (command below) |
| Signing Key ID | e.g. `agrix-cm-2026-01` | Published with the public key and stamped on each consent token. Keep it while the key is in use; change it on rotation |
| Install Mock Identity System? | **No** | eSignet is connected to the real national ID system instead |
| Load Sample People | **Off** | Sample data is for demos |
| Token Issuer ID, Token Presenters | Only to differ from `agri-stack-exchange-cm`, `agri-composite` | Every department must then be given the same values |
| Required Subject Identifiers, Composite URL | Only to differ from `FARMER_ID`, `https://agri-composite.<this domain>` | |

```bash
kubectl -n agrix create secret generic agrix-cm-signing \
  --from-file=cm_signing.p12=./cm_signing.p12 --from-literal=password='<p12 password>'
```

Replacing the demo key, step by step: [CM deployment](../../consent-management/deployment/README.md#replacing-the-demo-key-for-production-rancher-step-by-step).

## What the exchange role sets

**Exchange Role** `exchange` alone sets these. Why the Exchange works this way: [The Exchange](../architecture/exchange.md).

### Consent Manager

| Setting | Value | Why |
| --- | --- | --- |
| Token issuer | `agri-stack-exchange-cm` | Stamped as `iss` on every consent token; the department CMs trust this ID |
| Token presenters | `agri-composite` | Only the Composite may ask for consent tokens (`/validate` with `issue_receipts: true`) |
| Token lifetime | 900 seconds, capped by the consent's expiry | A consent token is used for one query |
| Signing key | The CM's signing key (same `kid`, same public JWKS) | The department CMs fetch the public key from `https://consent-manager-partner.agrix.<parent domain>/api/consent-manager-partner/.well-known/jwks.json` |
| AWE approval of policies | Off | Policies take effect when the CM administrator saves them |

Every CM setting: [CM deployment](../../consent-management/deployment/README.md#exchange-optional).

### Partner portal

| Setting | Value | Why |
| --- | --- | --- |
| National-ID login | Always on | Only subject ID types `FAYDA_FAN`, `NATIONAL_ID`, `national_id` can log in |
| Required subject identifiers | `FARMER_ID` | CM staff check the Farmer ID before approving a consent |
| Composite URL | `https://agri-composite.<this domain>` | The portal fills a request's grants from the Composite's published use cases. The Composite allows the portal's origin by default ([CORS](composite.md#cors)) |
| Evidence storage | Garage, bucket `consent-evidence` (created by Commons Base) | The form the farmer signed |

A Job registers the CM's client in eSignet once eSignet is up ([national ID authentication](../../consent-management/deployment/README.md#national-id-authentication-of-the-subject-esignet)). Partner users log in through the CM's `partner` realm in Keycloak; they are created after install ([After Install](after-install.md#partner-portal-realm-and-users)).

Partners themselves (their PM entry, and a binding and policy per registry) are added by administrators after install: [partner guide](../partner-guide.md#step-2-get-onboarded-in-partner-management); the [partner test](testing.md#partner-test-public-apis) adds a test partner. The Composite's PM entry is added by the [Exchange setup](after-install.md#exchange-setup).

## Check

```bash
helm -n agrix list
kubectl -n agrix get pods
```

Both releases `deployed`, every pod running. The CM's public keys answer at `https://consent-manager-partner.<this domain>/api/consent-manager-partner/.well-known/jwks.json`, and the partner portal opens at `https://consent-partner-portal.<this domain>`.
