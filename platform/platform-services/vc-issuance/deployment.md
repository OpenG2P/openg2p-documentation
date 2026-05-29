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
Certify stays decoupled from the Registry. **No Logto, no Mimoto, no Inji Web** (those belong to the
wallet options).

## Components

| Component | Image / source | Role |
|---|---|---|
| **Agent Portal API** | `agent-portal-api` (FastAPI; built in `openg2p-registry-gen2-apis`) | Reads the Registry view, **pushes** claims to Certify, renders the PDF/QR |
| **Inji Certify** | `injistack/inji-certify-with-plugins` (**stock**, no custom plugin) | Issues + signs the VC (+ QR payload); the built-in `PreAuthDataProviderPlugin` makes the pushed claims the subject |
| **Inji Verify** | `injistack/inji-verify-*` | Scans + validates the QR (offline) — verifier side |
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
| 5 | **Agent Portal API** (docker/helm) | reads `beneficiary_vc_view`, pushes claims, renders PDF/QR; holds the **only** Registry + MINIO connections |
| 6 | **Agent Portal UI** | talks **only** to the Agent Portal API — never to Certify |
| 7 | **Registry** `beneficiary_vc_view` + `certify_ro` user | read-only, least-privilege |
| 8 | **MINIO access** for the Agent Portal API | only if the VC embeds a face thumbnail |
| 9 | **Inji Verify** (helm) | verifier side — needed to scan/validate, not to issue |
| 10 | **Trust distribution** | publish issuer cert/DID; push the issuer cert to verifiers' trust list |

Optional infra: **Redis** only if Certify runs multi-replica/HA (the pre-auth offer/claims cache); a
single replica uses the in-memory cache. Ingress/TLS as usual.

## End-to-end call sequence (who calls whom)
The **UI never touches Certify**; the **Agent Portal API** is the OpenID4VCI client (trusted M2M
caller) and Certify is **not exposed publicly**.

1. Agent logs into the UI and verifies the citizen (LoA1); UI → `POST /agent_portal/issue_vc {phone}`.
2. Agent Portal API reads `beneficiary_vc_view` (and, if used, fetches + compresses the MINIO face).
3. API → Certify **pre-authorized-code 4-call flow**: `POST /pre-authorized-data` (claims) →
   `GET /credential-offer-data/{id}` → `POST /oauth/token` → `POST /issuance/credential` (Bearer +
   proof JWT) → **signed VC** (+ claim-169 QR).
4. API renders the PDF and returns VC + PDF to the UI; the agent prints it for the citizen.
5. Later: a verifier scans the QR with **Inji Verify** → validates the COSE signature **offline**.

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
  against a dedicated `beneficiary_vc_view`. Certify does **not** connect to the registry in Phase 1
  (the pull connector — see [Registry Data Connector](registry-data-connector.md) — is for the wallet
  flow).

## Helm artifacts (where the charts live)
* **Inji Certify chart** — `vc-issuance/helm/openg2p-inji-certify` (OpenG2P style: `common` +
  `postgres-init` deps; Certify Deployment/Service/Gateway/VirtualService + a properties ConfigMap, a
  `.p12` keystore volume (PVC by default, or a restore Secret), and a **DB-schema-init Job** that seeds the keymanager tables + key policies —
  generic, **no** `credential_config`; modules register those).
  It is packaged into and enabled from **commons-services** (`charts/openg2p-commons-services`, dep
  alias `injiCertify`) — installed **with the commons layer**, reusing the cluster PostgreSQL.
* **Agent Portal API image** — built from `openg2p-registry-gen2-apis/agent-portal-api` (Dockerfile +
  `docker-build.yml`), e.g. `openg2p/openg2p-registry-agent-portal-api:<branch>`. Wired into the
  **registry** chart (`openg2p-registry-gen2-deployment`, `agentPortalApi` block) so it installs **with
  the registry**, pointed at the commons Certify service. (The agent portal **UI** follows the same
  pattern once its image exists.)

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
* **Agent Portal API**: configure the read-only registry datasource (`beneficiary_vc_view`), the
  Certify base URL + credential-config id, and the PDF output dir. It owns the only registry connection.
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
  issuer's signing cert / root to verifiers** (a trust list). Optionally embed `x5chain` in the QR for
  self-contained offline verification, trading off QR space. (The separate **JSON-LD VC** still uses
  `did:web` → `https://<host>/.well-known/did.json` for `proof.verificationMethod`; publish that too if
  JSON-LD VCs are issued.)
* **Photograph**: if the credential embeds a face in the QR, the **Agent Portal API** must push a
  **~1–2 KB WEBP/AVIF/JPEG thumbnail** (base64) as the `face` claim — a QR holds only ~2.9 KB and
  Certify does not fetch images. See [Phase 1 — Paper Credential](phase-1-paper-credential.md).

## Issuer identity — configuration, keys & verification (key points)
* **One issuer/authority per environment, configured at Certify install.** The issuer **DID**
  (`global.vcIssuerDid`) + signing-key alias/algo are set on the **Certify** chart (surfaced in its
  install **`questions.yaml`**, standalone and under commons-services). Keymanager **generates the
  keypair on first boot**; (Phase 2 only) you publish `did.json`.
* **VC definitions are owned by the consuming module — not Certify.** Credential *types, templates,
  fields, views and scopes* come from the **registry/NSR** chart (`vcDefinitions`), which **registers**
  each `credential_config` with Certify (the register Job, `POST /credential-configurations`) and
  **references** the env issuer above. The Certify chart seeds **only** schema + key policies — no
  `credential_config`. See [Registry Data Connector](registry-data-connector.md).
* **The issuer identity is a 3-part bundle — back it up together.** The **`.p12`** (master key) + the
  **keymanager key rows in PostgreSQL** (the actual signing keys, encrypted under the master key) + the
  **keystore password** (Secret). All three must be preserved and restored *consistently*; losing or
  changing any of them **invalidates every credential already issued**. By default the chart persists
  `local.p12` on a durable **PVC** (generated on first boot); to redeploy with an existing identity,
  restore it via `p12.existingSecret`. Either way, fold the `.p12` (PVC or Secret) + keystore password
  + Certify DB into the backup system as **one** critical set.
* **Verification key hosting differs by phase:**
  * **Phase 1 (paper / claim-169 QR): no hosted `did.json` needed.** Verification uses a
    **pre-distributed trust anchor** (issuer cert/root loaded into Inji Verify) and/or the cert
    **embedded in the QR** (`x5chain`). Distribute the issuer signing cert to verifiers.
  * **Phase 2 (wallet / JSON-LD VC): a resolvable `did:web` is required** — host `did.json` (built from
    `/.well-known/jwks.json` after first boot) at `https://<issuer-host>/.well-known/did.json`, either
    self-hosted on the cluster under the Certify domain or on an external static host. Deferred to Phase 2.

## Verifier side
**Inji Verify** validates the printed QR by checking the COSE/CWT signature against the issuer's key —
obtained from the QR's COSE header (`x5chain`/`x5t`/`x5u`) and/or a **pre-loaded issuer trust anchor**.
It does not need access to OpenG2P at scan time (offline-verifiable).

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
* The **Agent Portal API** calls Certify as a **trusted machine-to-machine** caller
  (agent-authenticated context); Certify is not exposed publicly for issuance.
* The Agent Portal API → Registry connection is **read-only** via a dedicated view and a
  least-privilege `certify_ro` user — never raw registry tables. Certify itself has **no** Registry
  connection in Phase 1.
* Signing keys never leave Certify; the `.p12` + key tables are persisted, backed up, access-controlled.
* Decide a **revocation/validity** posture for paper (short validity and/or an optional online
  status-list check when the verifier is connected).

## Notes (environment)
* The cluster already runs much of the OpenG2P/Inji stack (eSignet, keymanager, mock-identity,
  registry APIs). Phase 1 only needs the **Agent Portal API + Certify** added; the wallet-side
  services are not required.
* Local development can run Certify under Docker/Colima while the Agent Portal API reaches the
  cluster's registry DB via `host.docker.internal` — but Phase-1 production lives on the cluster.
