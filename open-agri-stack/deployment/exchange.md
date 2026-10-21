---
description: >-
  Installing the Agri Stack Exchange (agrix): Commons Base and Commons Services
  with the Consent Manager in the Exchange role, the partner portal, eSignet
  and the mock identity system: what to install, which fields to choose, the
  Composite's key and access (by script or by hand), and what production needs.
---

# Exchange

Installing the [Exchange](../architecture/exchange.md): where partners onboard once and use one farmer consent across registries. On these pages it is the namespace `agrix` ([topology](README.md#topology)). The Composite also runs here; it has its own page: [Composite](composite.md).

## What to install

From **Apps → Charts** in Rancher, in the `agrix` namespace, in this order:

| # | Chart (Rancher name) | Release |
| --- | --- | --- |
| 1 | For production only: the CM signing key Secret ([below](#form-fields)) | — |
| 2 | **OpenG2P Commons Base** (`openg2p-commons-base`) | `commons` (fixed) |
| 3 | **OpenG2P Commons Services** (`openg2p-commons-services`) | `commons-services` (fixed) |

Then the [Composite](composite.md), the [after-install steps](after-install.md) and [the Composite's key and access](#the-composites-key-and-access). The commons charts themselves: [Commons Helm chart](../../deployment/openg2p-commons-helm-chart.md).

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
| Install AWE? | **No** | Only needed if approvals in Master Data are switched on (off by default). Partner and policy changes are approved in Partner Management |
| Install Staff Portal UI? | **No** | The registry staff home page; no registry here |
| Install ODK Central? | **No** | Registry data collection |
| Install Superset? | **No** | Registry dashboards |
| Install Inji Certify? | **No** | Issues credentials to beneficiaries |
| Install Inji Verify? | **No** | Checks credentials; nothing in the Exchange does |
| Install WebSub? | **No** | Nothing in the Exchange uses it yet |
| Exchange Role (Consent Manager) | **exchange** | The CM issues a consent token per registry to the Composite |
| Partner Portal? (Consent Manager) | **Yes** | Partner users (e.g. bank staff) raise consent requests for farmers |

Left at their defaults, and needed: **Install Master Data?** (the catalogue), **Install Partner Management?**, **Install Consent Manager?**, **Install eSignet?** (the farmer's national-ID login in the partner portal), **Install Mock Identity System?** (the identities eSignet checks, for testing). Artifactory, which eSignet and the mock identity system use, is always installed. **Install Keymanager?** stays off: Agri Stack does not use it. The IAM service, the Audit Manager and keycloak-init have no form field and are on.

With **Exchange Role** `exchange`, the other Consent Manager fields can stay empty: their defaults are the reference values ([CM deployment](../../consent-management/deployment/README.md#exchange-optional)).

<details>

<summary>The same choices as YAML (command-line installs, or a commons-services version without the Consent Manager form fields)</summary>

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

For production, add the signing key under `openg2p-consent-manager`: `global.consentSigningKid: agrix-cm-2026-01` and `consentManagerApi.signingKey: {mode: existing, secretName: agrix-cm-signing, passwordSecretName: agrix-cm-signing}` (`passwordSecretName` is needed on CM charts develop.74 and earlier).

</details>

**Exchange Role** `exchange` sets the rest: the CM issues consent tokens as `agri-stack-exchange-cm` to the Composite only, and the partner portal makes consents for a granted use case, with national-ID login and the Farmer ID required. Every value and how to change it: [CM deployment](../../consent-management/deployment/README.md#exchange-optional); why the Exchange works this way: [The Exchange](../architecture/exchange.md) and [Exchange consent tokens](../../consent-management/design/exchange-receipts.md). Partners themselves are onboarded in the Exchange's Partner Management after install ([partner guide](../partner-guide.md#step-2-get-onboarded-in-partner-management)); partner-portal users are created in [After Install](after-install.md#partner-portal-realm-and-users).

## Check

```bash
helm -n agrix list
kubectl -n agrix get pods
```

Both releases `deployed`, every pod running. The CM's public keys answer at `https://consent-manager-partner.<this domain>/api/consent-manager-partner/.well-known/jwks.json`, and the partner portal opens at `https://consent-partner-portal.<this domain>`.

## The Composite's key and access

After the Composite is installed, it needs its signing key, and a place in the Exchange's and each department's Partner Management, before it can call any registry (until then the console shows the registries unreachable and queries fail with `signing_unavailable`). The [Exchange setup script](after-install.md#exchange-setup) does all of it when one `kubectl` context reaches every namespace. Otherwise, or when each organisation does its own part, do these steps in order; each says who does it.

| # | Who | What |
| --- | --- | --- |
| 1 | Exchange | Create the Composite's signing key |
| 2 | Exchange | Onboard the Composite in the Exchange PM |
| 3 | Each department | Onboard the Composite in the department PM, with its scope policy |
| 4 | Exchange and each department | Check the consent-token trust between the CMs |
| 5 | Exchange | Create the signing key Secret and restart the Composite |
| 6 | Exchange | Check that it works |

### 1. Signing key

An EC P-256 key with a self-signed certificate, in a password-protected `.p12`, and a `kid` you choose (it names the key in every PM):

```bash
openssl ecparam -name prime256v1 -genkey -noout -out composite.key
openssl req -new -x509 -key composite.key -subj "/CN=agri-composite" -days 365 -out composite.crt
openssl pkcs12 -export -inkey composite.key -in composite.crt -name agri-composite -out composite.p12
openssl ec -in composite.key -pubout -out composite.pub.pem     # the public key for each PM
```

Keep `composite.p12` and its password where your organisation keeps secrets ([for production](#for-production)), and delete `composite.key` once the `.p12` is made.

### 2. The Exchange PM

In the Exchange's Partner Management portal (`https://partner-management.<base domain>`), **Onboard partner**: partner ID `PARTNER_AGRI_COMPOSITE`, the public key from `composite.pub.pem`, the `kid`, algorithm `ES256`, and no policy (the Composite is not granted anything at the Exchange; partners are). Approve the request. Partners verify the Composite's answers with this key.

### 3. Each department PM

In each department's Partner Management portal, **Onboard partner** `PARTNER_AGRI_COMPOSITE` with the same public key and `kid`, and a **scope policy** for each registry that department serves (the Composite's ceiling there):

| Field | Value |
| --- | --- |
| Data controller | The registry's controller ID (e.g. `farmer-registry`) |
| Data scopes | Every scope, required and optional, that the Composite's published use cases read from this registry: `consent_scopes` in `GET /composite/v1/use-cases` |
| Purposes | Those use cases' purposes |
| Subject ID types | The ID types partners' consents name (e.g. `FAYDA_FAN`, `FARMER_ID`) |
| Signing algorithms | `ES256` |
| Maximum validity | e.g. `P90D` |
| Fetch type | `oneshot` |

Approve the request. If the Composite is already onboarded, raise a **Change policy** request instead. Steps in the portal: [Creating and Changing Policies](../../platform/platform-services/partner-management/creating-and-changing-policies.md). Why the department holds this policy: [the Composite as a partner](../architecture/registries.md#the-composite-as-a-partner); the fields: [access policies](../../platform/platform-services/partner-management/functional-specifications.md#access-policies).

### 4. Consent-token trust

Form settings, chosen at install:

* The Exchange's commons: **Exchange Role** `exchange` (its CM issues consent tokens to the Composite).
* Each department's commons: **Exchange Role** `department`, trusting the Exchange CM's tokens presented by the Composite. The default trusted issuer and its JWKS URL derive from the Exchange's domain ([Exchange](exchange.md)).

A department whose CM does not trust the Exchange's tokens denies every Composite call to its registry.

### 5. Secret and restart

```bash
kubectl -n agrix create secret generic agri-composite-signing \
  --from-file=composite.p12=./composite.p12 --from-literal=password='<p12 password>' \
  --from-literal=kid=<kid> --from-literal=algorithm=auto
kubectl -n agrix rollout restart deploy/agri-composite-api
```

The `kid` must be the one registered in the PMs. Other Secret names and keys: [Composite: signing key](composite.md#signing-key).

### 6. Check

* Composite console, **Registries**: each registry reachable, the Composite's key served.
* Each department's PM partner API (from inside its cluster): `GET /keys/PARTNER_AGRI_COMPOSITE` serves the `kid`, and `GET /policies/PARTNER_AGRI_COMPOSITE?data_controller=<controller>` the scope policy.
* A test partner's query: [Testing](testing.md).

### When use cases change

A new use case, or one that reads more scopes or another registry, needs the departments' ceilings widened first: each department raises a **Change policy** request for `PARTNER_AGRI_COMPOSITE` with the new scopes and purposes (step 3), or the operator reruns the script. Until then the registry denies what the ceiling does not cover. Narrowing a ceiling is always done by hand: the script never narrows.

## For production

What a demo install can leave as it is, and a production install cannot.

### Form fields

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



### The Composite's key

* **Custody.** Generate the key where your organisation generates keys, and keep the `.p12` and its password in its secrets store. The script's local copy (`~/.agri-stack-setup/<ns>/`) is for demos: in production, set the key up by hand or point `--state-dir` at protected storage and remove the copy afterwards.
* **Access to the Secret.** Only the Composite and its operators may read `agri-composite-signing`: restrict who can read Secrets in the Exchange namespace.
* **Rotation.** The certificate lasts as long as you made it (a year above). To rotate without downtime:
  1. Create the new key and `kid`.
  2. Add it with a **key-update** request in the Exchange PM and in every department PM, and approve; both keys are now served.
  3. Replace the Secret and restart the Composite; it now signs with the new key.
  4. After the caches have expired (the registries keep a partner's keys for up to 5 minutes, and the last known keys for longer during a PM outage), revoke the old `kid` with a key-update request in every PM.
* **A compromised key:** revoke its `kid` in every PM at once and rotate; registries refuse the Composite until the new key is served.

### Approvals

* **Separate the roles by process.** Partner Management lets the person who raises a request approve it. In production, have one person raise and another approve every onboarding, key and policy request, at the Exchange and in each department.
* **Departments own their ceilings.** A department approves the Composite's scope policy for its own registry; the Exchange operator should not hold PM admin rights in a department.
* **Review widenings.** A new use case reaches a department's data only after that department widens its ceiling (above): review the scopes and purposes before approving.

### Services that must stay internal

* PM's partner API (`/keys`, `/policies`) and the CMs' partner APIs have **no login**. They must be reachable only inside the cluster (the charts put them on the internal gateway); check that no public route exposes them.
* The Composite's partner API is the only public entry for partners.

### Revocation takes effect after the caches

The Composite and the CMs keep a partner's policy for up to 60 s, and the last known answer for up to 6 h while PM is unreachable. A revoked policy or disabled partner is therefore refused within a minute normally, but not during a PM outage. Lower the hard TTL (`PARTNER_POLICY_HARD_TTL_SECONDS` in the [Composite](composite.md) and the CM) if that window is too long for you.

### Demo leftovers

Remove what a demo install creates before going live:

* Test partners in the Exchange PM (e.g. `PARTNER_BANK_A` from the partner test) and their partner-portal users: disable them in PM and remove the users from the `partner` realm.
* The registries' sanity partner (`PARTNER_CM_SANITY`) and its policy, if the sanity tests ran.
* Sample data in the registries.
* Any locally kept test keys (`~/.agri-partner-test/`, `~/.agri-stack-setup/`).

### Keep

* The Audit Manager on in every install: it records PM approvals, consent decisions and the Composite's calls.
* Backups of each PM's and CM's database: partners, keys, policies and consents live there.
