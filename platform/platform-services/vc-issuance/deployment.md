---
description: >-
  Deploying the Phase-1 VC-issuance stack — the Agent Portal API + Inji Certify —
  on the OpenG2P Kubernetes cluster, reusing the existing PostgreSQL. Plus Inji
  Verify for offline QR verification.
---

# Deployment (Phase 1)

Phase 1 is intentionally small: an **Agent Portal API** (issuance backend) + **Inji Certify** (issuer)
signing to a **`.p12`** keystore, reusing the cluster **PostgreSQL**, plus **Inji Verify** for the
verification side. The Agent Portal API reads the Registry and **pushes** claims to Certify, so
Certify stays decoupled from the Registry. **No Mimoto, no Inji Web** (those belong to the wallet
options).

Two authentications must be wired, and they are **not** the same thing: the **agent** logs in against
Keycloak's **`agent` realm**, while the **beneficiary** authenticates against **eSignet** (biometric or
OTP) to authorise each issuance. Agents are distinct from registry **staff** — separate realm, separate
API, separate portal.

The Agent Portal API ships **as part of the Registry Platform chart** and is **disabled by default**,
so every registry manifestation inherits the capability without being affected until it opts in.

## Components

| Component | Image / source | Role |
|---|---|---|
| **Agent Portal API** | `agent-portal-api` (FastAPI; built in the **Registry Platform** repo) | Resolves the record, drives the beneficiary's eSignet authentication, **pushes** claims to Certify, renders the PDF/QR, logs the issuance |
| **Agent Portal UI** | reference web client (Registry Platform) | The agent's screen; talks only to the Agent Portal API |
| **Agent login API** | `iam-agent-portal-api` (IAM service) | Authenticates the **agent** against Keycloak's `agent` realm |
| **eSignet** | existing deployment | Authenticates the **beneficiary** (biometric at the counter, or OTP) — issues nothing |
| **Inji Certify** | `injistack/inji-certify-with-plugins` (**stock**, no custom plugin) | Issues + signs the VC (+ QR payload); the built-in `PreAuthDataProviderPlugin` makes the pushed claims the subject |
| **Inji Verify** | `injistack/inji-verify-*` | Verifier side. A **web portal** the verifying organisation hosts (webcam scan or upload), plus an SDK for embedding it. Not a phone app, and not installed by the citizen. |
| **PostgreSQL** | existing cluster instance | Reused: a dedicated DB/schema for Certify; the Agent Portal API reads the registry DB read-only |

All run on the OpenG2P **Kubernetes** cluster.

> **The Certify helm chart alone is NOT enough.** `helm/inji-certify` deploys only the Certify
> service pod — no database, no init SQL, no keystore, no data source. (The upstream `install.sh` also
> assumes the full MOSIP sandbox — config-server, softhsm, esignet-mock, mock-identity — which Phase 1
> does **not** use.) You must additionally provide items 2–10 below.

## Install checklist (Phase 1)

| # | Install / configure | Notes |
|---|---|---|
| 1 | **Inji Certify** (helm service pod) | issuer + signer |
| 2 | **Certify DB/schema** on the cluster PostgreSQL | run Certify's init SQL once (keymanager tables, key policies, caches) — **no** `credential_config` (modules register those) |
| 3 | **`.p12` keystore** on a persistent volume | the issuer identity — persist + back up (no HSM) |
| 4 | **Certify config** | Certify-as-AS (`authn.*` / `oauth.issuer` → itself); `data-provider-plugin=PreAuthDataProviderPlugin`; add `credentialOfferCache`; **issuer DID** (`global.vcIssuerDid`) + signing key. The `credential_config` rows are registered by the **module** (registry/NSR). |
| 5 | **Agent Portal API** (Registry Platform chart) | set `agentPortalApi.enabled=true` **and** `agentPortalApi.vcIssuance.enabled=true`; resolves the record, pushes claims, renders the PDF/QR, logs the issuance |
| 6 | **Agent Portal UI** | talks **only** to the Agent Portal API — never to Certify |
| 7 | **Registry VC view** keyed on `internal_record_id` + least-privilege read-only DB user | supplied by the **manifestation** (NSR, Farmer Registry, …), since the claim fields differ |
| 7a | **`credential_config` registration** | The registry chart's `credential-config-register` Job POSTs (or PUTs, on re-run) each `vcDefinitions[].certifyConfig` to Certify on install/upgrade. Certify can only issue a type it already knows, so without this the first issuance fails on an unknown `credential_configuration_id`. Set **`global.vcIssuer.did`** to the same DID as Certify's — the chart refuses to install with it empty, rather than signing credentials with a blank issuer. The `vcTemplate` is authored as readable JSON (`vcTemplateJson`) and base64-encoded by the Job. |
| 8 | **Keycloak `agent` realm** | Created by **commons-services**' `keycloak-init` (`keycloak-init.realms.agent`), alongside the `staff` realm and for the same reason: the `agent-portal` client is CONFIDENTIAL and `iam-agent-portal-api` is its only consumer, so the client and the Secret holding its secret must come from the release that configures that API. It carries the `register:issue_credential` role, and registers two redirect URIs — the IAM callback (`agentPortalApiHostname`) and the agent portal UI (`agentPortalHostname`). The registry chart adds only the demo `agent` user (`global.agentUserPassword`, change it). **Set `global.agentPortalHostname` on the commons-services install to the registry's real agent UI host** (e.g. `fr-agent.<domain>`): it drives both the redirect URI and `IAM_AGENT_CORS_ALLOW_ORIGINS`, exactly as `staffPortalHostname` does for staff. Note that `keycloak-init` never resets an existing user's password, and the realm lives in the Keycloak DB, which outlives a registry reinstall. |
| 8a | **`iam-agent-portal-api`** (IAM chart) | set `iamAgentPortalApi.enabled=true`. Agent *login*, in the `agent` realm — nothing to do with eSignet. Its `IAM_AGENT_KEYCLOAK_CLIENT_ID` must equal the registry's `global.agentKeycloakClientId` (`agent-portal`), or an agent authorised at login is unauthorised at issuance. |
| 8b | **eSignet provider row** for registrant authentication | `adapter_name = esignet`; eSignet must be configured to **release `individual_id`**, which is matched against the record's `foundational_id` |
| 8c | **eSignet OIDC client** | Register a client (e.g. `openg2p-registry-vc`) whose `redirect_uris` is the **staff** API's `/registrant-auth/callback`, with `private_key_jwt` (the only method eSignet advertises) and `individual_id` among its claims. Store the matching private key on the provider row. |
| 8d | **IAM role → permission** | The agent portal resolves permissions through IAM's `/user-access/get_permissions_for_roles`. An application with the `register:issue_credential` **permission**, a role of the same mnemonic, and the mapping between them must exist, or every issuance call is refused. |
| 8e | **IAM login provider for the `agent` realm** | Token validation looks the issuer up in IAM's `login_providers`. Without a row whose `issuer` is `<keycloak>/realms/agent`, every agent token is rejected as *Unknown Issuer*. |
| 8f | **Enable authentication on the register** | Set `requires_registrant_authentication` on the register definition. Core refuses to start an authentication otherwise. |
| 9 | **Inji Verify** (helm) | verifier side — needed to scan/validate, not to issue |
| 10 | **Trust distribution** | publish issuer cert/DID; push the issuer cert to verifiers' trust list |

Optional infra: **Redis** only if Certify runs multi-replica/HA (the pre-auth offer/claims cache); a
single replica uses the in-memory cache. Ingress/TLS as usual.


### Two settings that silently break the beneficiary authentication

**eSignet must release `individual_id`.** Its discovery document advertises
`subject_types_supported: ["pairwise"]`, so the `sub` in the token is a *pseudonymous,
per-client* identifier — never the national ID. The adapter falls back to `sub` when
`individual_id` is absent, and the binding check then compares a pairwise pseudonym against
the record's `foundational_id` and fails every time. Request it explicitly through the
provider's `extra_authorize_params.claims.userinfo.individual_id`.

**The registrant-auth session store must be shared.** The eSignet transaction (state, nonce,
PKCE verifier and the record context) is created when authentication *starts* and read back at
the *callback*. In the agent flow those are two different services — the agent portal starts it,
the staff API receives the redirect — and each API also runs several gunicorn workers. With the
default in-process store the callback has never seen the state. Point
`registry_core_registrant_auth_session_store_backend=redis` and
`registry_core_registrant_auth_redis_url` at one Redis for both services; the registry chart now
does this by default.

## End-to-end call sequence (who calls whom)
The **UI never touches Certify**; the **Agent Portal API** is the OpenID4VCI client (trusted M2M
caller) and Certify is **not exposed publicly**.

1. Agent logs into the UI against Keycloak's **`agent` realm** (via `iam-agent-portal-api`).
2. Agent enters/scans the beneficiary's **national ID**; the API matches it to the register's
   **`foundational_id`** and requires `record_status = ACTIVE`, resolving the **`internal_record_id`**.
3. API initiates **registrant authentication** with the eSignet provider and returns the authorization
   URL; the **beneficiary** authenticates (biometric at the counter, or OTP). eSignet's own UI performs
   the capture.
4. On callback the API checks the binding (**`individual_id` == `foundational_id`**) and the **VC
   window** (`SUCCESS` and within `authWindowSeconds`, default 300).
5. API reads the claims **by `internal_record_id`**, then → Certify **pre-authorized-code 4-call
   flow**: `POST /pre-authorized-data` (claims) → `GET /credential-offer-data/{id}` →
   `POST /oauth/token` → `POST /issuance/credential` (Bearer + proof JWT) → **signed VC**
   (+ claim-169 QR).
6. API renders the PDF, **streams it to the agent's browser** as a download, and writes the **issuance
   event log** row. The agent prints it and hands it to the citizen.
7. Later: a verifier scans the QR with **Inji Verify** (its hosted web portal, or
   the SDK embedded in their own app) → validates the COSE signature against a
   **pre-loaded trust anchor**. The signature check needs no call back to
   OpenG2P, but the portal itself is a web page, so a browser-based verifier
   still needs the page loaded. A genuinely offline counter needs the SDK
   embedded in an installed application.

Nuances: with no citizen device, the **API generates an ephemeral holder key** for the proof JWT
(`credentialSubject.id` = a throwaway `did:jwk`; trust comes from the issuer signature, not holder
binding). Certify caches the pushed claims only **transiently** for the issuance — it does not persist
citizen data. The pre-auth `tx_code` is set/supplied by the API itself.

## One shared issuance service per environment
Run **one Certify instance per environment** and let **every module** (Registry, PBMS, SPAR, …) use
it. Certify is a **generic signing service**; the push model keeps it decoupled from each module's
data — every module is its own issuance backend that pushes its own claims.

* **Many credential types** — each VC type is one `credential_config` row (its own Velocity template,
  scope, signing key, issuer DID, format, QR settings). An individual can hold several types; a
  **household** credential is just a config whose subject is household attributes. Adding a type =
  adding a row (no Certify rebuild).
* **Multiple issuers** — each `credential_config` carries its own `did_url` + signing key
  (`key_manager_app_id` / `key_manager_ref_id`). **Onboard an issuer** by (1) generating a signing key
  in Certify's keymanager (app-id + key policy), (2) publishing its **DID** (`did:web` at a stable,
  resolvable HTTPS URL), (3) creating the `credential_config` rows that reference that key/DID. Share
  one org-level issuer DID across types, or give each department its own — a policy choice.
* **All modules push to the same instance** — Certify's built-in **`PreAuthDataProviderPlugin`**
  serves them all; each backend selects its `credential_configuration_id` when pushing.

> **Constraint (Certify 0.14.0):** `mosip.certify.integration.data-provider-plugin` is a **single
> global setting** — one active data-provider plugin per instance. `PreAuthDataProviderPlugin` is
> generic (it just returns the pushed claims), so standardise **all** modules on **push**. Mixing
> push for one module and DB-pull for another on the *same* instance isn't supported in 0.14.0 (use a
> separate instance, or a later Certify version).

## Reuse the cluster PostgreSQL
* Create a **dedicated database/schema** for Certify (e.g. `inji_certify`) on the existing
  PostgreSQL; do not co-mingle with `registrydb`.
* Run Certify's init SQL once (keymanager tables, `credential_config`, key policies).
* The **Agent Portal API** connects to the registry DB **read-only** via a least-privilege user
  against the manifestation's dedicated **VC view** (keyed on `internal_record_id`). It also writes the
  **issuance event log**. Certify does **not** connect to the registry in Phase 1
  (the pull connector — see [Registry Data Connector](registry-data-connector.md) — is for the wallet
  flow).

## Helm artifacts (where the charts live)
* **Inji Certify chart** — `vc-issuance/helm/openg2p-inji-certify` (OpenG2P style: `common` +
  `postgres-init` deps; Certify Deployment/Service/Gateway/VirtualService + a properties ConfigMap, a
  `.p12` keystore volume (PVC by default, or a restore Secret), and a **DB-schema-init Job** that seeds the keymanager tables + key policies —
  generic, **no** `credential_config`; modules register those).
  It is packaged into and enabled from **commons-services** (`charts/openg2p-commons-services`, dep
  alias `injiCertify`) — installed **with the commons layer**, reusing the cluster PostgreSQL.
* **Inji Verify chart** — `vc-issuance/helm/openg2p-inji-verify`. Deploys **only**
  `verify-service`: no MOSIP config-server, no PostgreSQL (it runs the image's bundled in-memory
  profile), no stock `verify-ui`. It is a **dependency of commons-services too**
  (`condition: openg2p-inji-verify.enabled`, default **on**), so **installing commons-services
  installs both Certify and Verify** — the issuing and checking halves of the same feature arrive
  together. Both charts are published from the `verifiable-credentials` repo and share a version
  line, so they are pinned to the same `0.0.0-develop.N`.
* **Agent Portal API + UI** — built in the **Registry Platform** repo (`apis/`, `ui/`, `docker/`) and
  shipped in the **`openg2p-registry`** chart under the `agentPortalApi` block, pointed at the commons
  Certify service. Because it lives in the platform chart, **every registry manifestation inherits it**;
  it stays inert until switched on.
* **Agent login API** — `iam-agent-portal-api`, deployed from the **IAM service** chart against the
  Keycloak `agent` realm.

## Configuration highlights
* **Certify** (stock image, no custom plugin): set
  `data-provider-plugin=PreAuthDataProviderPlugin` (a built-in — turns the pushed claims into the VC
  subject); point the resource-server token settings (`authn.issuer-uri` / `jwk-set-uri` /
  `allowed-audiences` / `oauth.issuer`) at Certify itself (pre-authorized-code flow, no eSignet); set
  the **issuer DID** (`global.vcIssuerDid`) + signing key. The `credential_config` (Velocity template,
  type/fields, **`qr_settings` / `qr_signature_algo`**) is **registered by the module**, not here.
* **Required plugin-integration properties** (`certify.appConfig.*` → the Certify ConfigMap). The
  stock image expects these from its config source; the OpenG2P chart sets them explicitly so the app
  starts without a Spring Cloud Config server. The bundled plugins live in
  **`io.mosip.certify.mock.integration`** (inside `inji-certify-with-plugins`):

  | Property | Chart value | Default |
  | --- | --- | --- |
  | `mosip.certify.integration.scan-base-package` | `appConfig.scanBasePackage` | `io.mosip.certify.mock.integration` |
  | `mosip.certify.integration.data-provider-plugin` | `appConfig.dataProviderPlugin` | `PreAuthDataProviderPlugin` |
  | `mosip.certify.integration.audit-plugin` | `appConfig.auditPlugin` | `LoggerAuditService` |
  | `mosip.certify.integration.vci-plugin` | `appConfig.vciPlugin` | `MockVCIssuancePlugin` |
  | `mosip.certify.plugin-mode` | _(fixed)_ | `DataProvider` |

  `scan-base-package` is **mandatory** — Spring resolves it during configuration parsing (for the
  plugin `@ComponentScan`), so an unset value crashes startup *before* any other bean with
  `Could not resolve placeholder 'mosip.certify.integration.scan-base-package'`. If you swap in a
  custom plugin jar (e.g. the Phase-2 `RegistryDataProviderPlugin` in package
  `org.openg2p.certify.registry`), point `scanBasePackage` + `dataProviderPlugin` at it.
* **Agent Portal API**: configure the read-only registry datasource (the manifestation's VC view), the
  Certify base URL + credential-config id, the eSignet provider used for beneficiary authentication, and
  the VC authentication window (`authWindowSeconds`, default 300). It owns the only registry connection.
* **`.p12` keystore (no HSM)** — the Certify chart supports two custody modes (`certify.p12` values):
  * **Generate-on-first-boot onto a PVC** (default, `p12.persistence.enabled=true`): a durable
    `PersistentVolumeClaim` (`<release>-inji-certify-p12`) is created and mounted **writable** at
    `p12.mountPath`; keymanager writes `local.p12` there on first boot. The PVC carries
    `helm.sh/resource-policy: keep` so an uninstall does not destroy the issuer identity (it is **not**
    a substitute for a real backup).
  * **Restore from a Secret** (`p12.existingSecret`): mount a backed-up keystore **read-only** (Secret
    key `local.p12`). When set, this takes precedence over the PVC. Use this to redeploy with an
    existing issuer identity.
  * The connecting role must own the keystore directory; the `.p12` plus the encrypted key rows **are
    the issuer identity** — regenerating them invalidates previously issued credentials.
* **Issuer key / trust anchor**: the signed claim-169 QR is a **COSE/CWT**. Per the MOSIP 169 spec,
  verifiers use **COSE** key-discovery (`x5chain` embedded cert, `x5t` hash, or `x5u` URI) and a
  **pre-distributed trust anchor** — *not* `.well-known`/JWKS/DID resolution. So **distribute the
  issuer's signing cert / root to verifiers** (a trust list). The spec allows embedding `x5chain` in the
  QR for self-contained verification, at a cost in QR space; **OpenG2P does not** — our COSE header
  carries only `alg` and `kid`, so a pre-distributed trust anchor is the ONLY way our QR verifies. (The separate **JSON-LD VC** still uses
  `did:web` → `https://<host>/.well-known/did.json` for `proof.verificationMethod`; publish that too if
  JSON-LD VCs are issued.)
* **Photograph**: if the credential embeds a face in the QR, the **Agent Portal API** must push a
  **~1–2 KB WEBP/AVIF/JPEG thumbnail** (base64) as the `face` claim — a QR holds only ~2.9 KB and
  Certify does not fetch images. See [Phase 1 — Paper Credential](phase-1-paper-credential.md).

## Issuer identity — configuration, keys & verification (key points)
* **One issuer/authority per environment, configured at Certify install.** The issuer **DID**
  (`global.vcIssuerDid`) + signing-key alias/algo are set on the **Certify** chart (surfaced in its
  install **`questions.yaml`**, standalone and under commons-services). Keymanager **generates the
  keypairs on first boot**, and `did.json` is **already served** at
  `https://<certify-host>/.well-known/did.json` — see the key-hosting bullet below.
* **VC definitions are owned by the consuming module — not Certify.** Credential *types, templates,
  fields, views and scopes* come from the **registry/NSR** chart (`vcDefinitions`), which **registers**
  each `credential_config` with Certify (the register Job, `POST /credential-configurations`) and
  **references** the env issuer above. The Certify chart seeds **only** schema + key policies — no
  `credential_config`. See [Registry Data Connector](registry-data-connector.md).
* **Where the two signing keys actually live.** An issuance uses **two** keys (see
  [Signatures, Keys and the QR](signatures-keys-and-the-qr.md)), and they are **not stored the same
  way** — which matters entirely for backup:

  | | Signs | Key alias | Private key stored in |
  |---|---|---|---|
  | **Ed25519** | the JSON-LD credential | `CERTIFY_VC_SIGN_ED25519` / `ED25519_SIGN` | **PostgreSQL**, `inji_certify` → `certify.key_store`, **encrypted** under a master key |
  | **ES256** | the claim-169 QR | `CERTIFY_VC_SIGN_EC_R1` / `EC_SECP256R1_SIGN` | **the `.p12` keystore**, directly |

  The master key that unwraps the Ed25519 row is `CERTIFY_VC_SIGN_ED25519` with **no** `ref_id`, and it
  is a `PrivateKeyEntry` inside the same `.p12`. So the chain for the credential key is:

  ```
  certify.key_store row (encrypted)  ──unwrapped by──►  master key in local.p12
  ```

  Of the nine key aliases keymanager creates, **exactly one — the Ed25519 credential key — is a database
  row**; every other key, the ES256 QR key included, sits in the keystore. PKCS12/JCE handles EC and RSA
  natively but not Ed25519, which is why that one is held as an encrypted blob instead.

  Keystore file: `/home/inji/CERTIFY_PKCS12/local.p12` (`p12.mountPath`), on the PVC. Its password is
  currently the fixed value `local` (`mosip.kernel.keymanager.hsm.keystore-pass`) and is **not yet
  chart-configurable** — treat it as part of the identity regardless.

* **Back the `.p12` and the key rows up together, from the same moment.** The `.p12` is on the critical
  path for **both** signatures — one key is *in* it, the other is *unlocked by* it. Consequently:

  * `.p12` alone → you recover the **QR** key, but the credential key stays undecryptable.
  * database alone → you recover an **encrypted** credential key and nothing to unwrap it with.
  * a `.p12` restored against a **mismatched** database → the QR key keeps working while the Ed25519 row
    fails to decrypt. The failure looks partial and is actually a lost issuer identity.

  Treat `.p12` + `certify.key_store` + the keystore password as **one** backup set, captured together.
  The Certify chart can copy the keystore into a Secret for you (`p12.backupToSecret`, on by default) so
  it lands in whatever backs up the namespace — but that covers the keystore only; the Certify database
  must be in the same backup regime. To redeploy onto an existing identity, restore the keystore via
  `p12.existingSecret` **and** the matching database.

* **Where verifiers get the public keys.**
  * `https://<certify-host>/.well-known/did.json` — the DID document for `did:web:<certify-host>`.
    **Live**, not deferred: the Certify chart rewrites this path to Certify's own
    `/v1/certify/.well-known/did.json` (`istio.virtualservice.exposeDidDocument`). It carries the
    **Ed25519** key only, because Certify builds it from each credential config's `signatureAlgo` and
    never consults `qrSignatureAlgo`.
  * `https://<certify-host>/.well-known/jwks.json` — **all** Certify public keys, including
    the **ES256 QR key**. This is where a verifier obtains the QR key, and it is
    **live** for the same reason as `did.json`: the Certify chart rewrites the well-known path onto
    Certify's own `/v1/certify/.well-known/jwks.json`.

  For Phase 1 the QR is what gets verified, and **claim-169 verification does not resolve DIDs**: the
  COSE header carries only `alg` and `kid`, with **no `x5chain`** embedded. The ES256 public key must
  therefore be **pre-distributed to verifiers as a trust anchor**, taken from the JWKS endpoint above.

## Enabling and disabling the capability

VC issuance ships **off**. Two independent switches in the `openg2p-registry` chart:

| Value | Default | Effect |
|---|---|---|
| `agentPortalApi.enabled` | `false` | Deploys (or removes) the Agent Portal API and its Service/route entirely. |
| `agentPortalApi.vcIssuance.enabled` | `false` | Feature switch **inside** the service — the issuance endpoints are not mounted when off. |
| `global.agentPortalHostname` | `{{ .Release.Name }}-agent.{{ .Release.Namespace }}.openg2p.org` | Public host of the Agent Portal UI — e.g. `fr-agent.trial.openg2p.org`. Also the redirect URI registered on both Keycloak `agent` clients, so changing it changes both. |

With both off, the chart renders **exactly** what it rendered before the capability existed. The only
always-present addition is the issuance event-log table, created by an additive migration; it stays
empty and is referenced by nothing when the feature is off. Nothing else in the registry changes, so
an existing deployment can take the new chart version with no behavioural difference.

Turning it on additionally requires the manifestation's **VC view** and **VC definitions**, the
Keycloak **`agent` realm**, and an **eSignet provider** row — see the install checklist above.

## Sanity and end-to-end tests

The chart runs a **sanity Job** as a `post-install,post-upgrade` hook, so a broken wiring fails the
install rather than surfacing later in the field.

* **Smoke + contract (always on).** `/ping` reachable, OpenAPI served, the issuance routes present
  only when the feature is enabled, and protected endpoints reject unauthenticated calls. **No data is
  created.**
* **End-to-end (opt-in, `runE2e`).** Walks the real chain — agent token → record lookup by
  `foundational_id` → registrant authentication → issuance → PDF — against the deployed components, to
  prove the wiring between the Agent Portal API, the Registry, eSignet and Certify. Any entity it
  creates is tagged with a `TEST_` prefix. **Turn it off for production.**

Gating is `failOnError: true` by default, with a values-only escape hatch.

## Verifier side
**Inji Verify** validates the printed QR by checking the COSE/CWT signature against the issuer's
**ES256** key. Our QR embeds no certificate — only a `kid` — so the key is resolved from the JWKS
Certify publishes at **`https://<certify-host>/.well-known/jwks.json`**.

{% hint style="warning" %}
That well-known path exists only because the **Certify chart's VirtualService rewrites it** onto
Certify's own `/v1/certify/.well-known/jwks.json`. Without the rewrite the URL is a **404** and QR
verification cannot work. The ES256 key is published in the JWKS and **not** in `did.json`, so
resolving the DID is not an alternative — see
[Verification](verification.md#where-the-verification-keys-come-from).
{% endhint %}

### What verify-service needs configured, and where it comes from

Very little, by design — which is the point of running it stateless:

| Setting | Value | Where it comes from |
|---|---|---|
| `active_profile_env` | `local` | Chart default (`verifyService.stateless: true`) — selects the bundled in-memory database instead of PostgreSQL |
| Host / route | `verify.<baseDomain>` | `global.verifyHostname`, derived from `global.baseDomain` in commons-services |
| Context path | `/v1/verify` | Chart default (`verifyService.contextPath`) |
| Issuer's public key | fetched at verification time | **Not configured.** Resolved from the `kid` in the credential and the issuer named in it |
| `DATABASE_*` | unset | Only required if `stateless: false` |

There is deliberately **no trusted-issuer list** to configure — and that is also a limitation: see
[Verification → Still open](verification.md#still-open).

The Agent Portal API reaches it in-cluster at
`http://commons-services-inji-verify-service/v1/verify`, the default already shipped in
`agentPortalApi.vcVerification.serviceUrl`. Switch the screen on with
`agentPortalApi.vcVerification.enabled=true`.

Two qualifications that are easy to miss:

* **Inji Verify is a web portal the verifying organisation hosts** (webcam scan or upload), plus an SDK
  for embedding it — it is not a phone app, and the citizen installs nothing. Inji **Wallet** is the
  phone app and is a *holder* app. See
  [Signatures, Keys and the QR](signatures-keys-and-the-qr.md).
* **"Offline" applies to the signature check**, which needs no call to OpenG2P at scan time. A browser
  still has to load the portal; a genuinely disconnected counter needs the SDK inside an installed
  application.

A claim-169 QR issued by our Certify **verifies against `verify-service`**, confirmed end to end on a
live deployment: a genuine credential returns `SUCCESS`, while a tampered signature and a token
re-signed with a different key both return `INVALID`.

## Teardown / uninstall

`helm uninstall` does **not** fully remove a Certify install: the PostgreSQL **database + role** live
inside `commons-postgresql` (created by the `postgres-init` subchart, not owned by the release), and
both the **`.p12` keystore PVC** and the **DB-password Secret** carry `helm.sh/resource-policy: keep`.
Use the teardown script, which removes all of them in the correct order:

```sh
# Dry run first — prints every action, changes nothing:
vc-issuance/scripts/uninstall-inji-certify.sh --namespace <ns> --release inji-certify --dry-run

# For real (prompts for confirmation):
vc-issuance/scripts/uninstall-inji-certify.sh --namespace <ns> --release inji-certify
```

It runs: `helm uninstall` → delete leftover hook Jobs/Pods → delete the DB-password Secret → sweep
release-labelled Secrets/ConfigMaps → drop the Postgres DB + role (`kubectl exec` into
`commons-postgresql`) → delete the keystore PVC → delete released PVs. Run with no flags to be prompted
for the namespace and release name.

> **⚠️ This destroys the issuer identity.** The `.p12` PVC + the keymanager key rows in the dropped
> database together *are* the issuer signing identity — removing them makes **every credential already
> issued unverifiable**, with no recovery. Only run on throwaway/re-creatable environments, or after a
> verified backup. Pass **`--keep-pvs`** to drop the workloads + DB while **retaining** the keystore
> PVC. If Certify was installed as a subchart of commons-services (release name `commons-services`),
> pass `--release commons-services` so the derived DB/role/Secret names match.

## Security checklist
* **Both parties are authenticated.** The **agent** holds a Keycloak token in the **`agent` realm** and
  the issuance endpoint is permission-gated; the **beneficiary** must have a successful eSignet
  authentication inside the VC window. Neither alone is sufficient.
* **The authentication is bound to the record.** eSignet's `individual_id` is matched against the
  record's `foundational_id`, so one person's authentication cannot be used to issue another person's
  credential. This requires eSignet to release `individual_id`.
* **Issuance is keyed on `internal_record_id`**, never on a value typed by the agent — the typed ID
  only locates the record.
* The **Agent Portal API** calls Certify as a **trusted machine-to-machine** caller; Certify is not
  exposed publicly for issuance.
* The Agent Portal API → Registry connection is **read-only** via a dedicated view and a
  least-privilege user — never raw registry tables. Certify itself has **no** Registry connection in
  Phase 1.
* **KYC claims are not retained.** Whatever eSignet returns is used for the issuance and then purged;
  the registry keeps the issuance *event*, not the credential, its claims or the citizen's KYC data.
* Signing keys never leave Certify; the `.p12` + key tables are persisted, backed up, access-controlled.
* **Revocation is deferred to Phase 2** — paper is verified offline, so short credential validity is
  the compensating control. See [Phase 2 — Device Wallet](phase-2-device-wallet.md).

## Notes (environment)
* The cluster already runs much of the OpenG2P/Inji stack (eSignet, keymanager, mock-identity,
  registry APIs). Phase 1 only needs the **Agent Portal API + Certify** added; the wallet-side
  services are not required.
* Local development can run Certify under Docker/Colima while the Agent Portal API reaches the
  cluster's registry DB via `host.docker.internal` — but Phase-1 production lives on the cluster.
