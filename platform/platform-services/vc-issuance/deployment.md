---
description: >-
  Deploying VC issuance and verification with Helm — the charts, their
  parameters, the jobs they run, and how to test the result.
---

# Deployment

Everything here is installed with **Helm** (directly, or through **Rancher**, which reads the same
charts' `questions.yaml`). There is no manual install path.

**Assumption: `commons-services` is already installed.** It brings PostgreSQL, Keycloak, IAM and
eSignet, and it is also where Inji Certify and Inji Verify come from — they are subcharts of it, not
separate installs.

---

# Part A — Concepts

Read once; skip to Part B to deploy. Full detail lives in
[Phase 1 — Paper Credential](phase-1-paper-credential.md) and
[Signatures, Keys and the QR](signatures-keys-and-the-qr.md).

**Who does what.** The **Agent Portal API** (Registry Platform) resolves the record and *pushes* the
claims to **Inji Certify**, which signs the credential and returns it; the API renders the PDF. Certify
never reads the registry. **Inji Verify**'s `verify-service` checks a presented QR. The UI never talks
to Certify or verify-service.

**Two authentications, not one.** The **agent** logs in against Keycloak's `agent` realm; the
**beneficiary** authenticates against **eSignet** to authorise each issuance. Agents are distinct from
registry *staff* — separate realm, separate API, separate portal.

**Two signing keys, stored differently.** This is the one concept that changes what you must back up:

| Signs | Key alias | Private key lives in |
|---|---|---|
| the JSON-LD credential (Ed25519) | `CERTIFY_VC_SIGN_ED25519` | **PostgreSQL** `certify.key_store`, encrypted |
| the printed claim-169 QR (ES256) | `CERTIFY_VC_SIGN_EC_R1` | **the `.p12` keystore** |

The master key that decrypts the database row is itself inside the `.p12`. So `.p12` + the Certify
database + the keystore password are **one backup set** — restoring one without the other loses the
issuer identity, and every credential already issued becomes unverifiable.

**Where verifiers get the public key.** `https://<certify-host>/.well-known/jwks.json` carries **all**
keys including the ES256 QR key; `/.well-known/did.json` carries the **Ed25519 key only**. Paper
verification uses the QR, so **the JWKS is the trust anchor** — both paths exist only because the
Certify chart rewrites them.

**One Certify per environment.** It is a generic signing service; every module (Registry, PBMS, …)
pushes to the same instance and selects its own `credential_configuration_id`. Credential *types* are
owned by the consuming module, not by Certify.

---

# Part B — Deployment

## 1. Charts required

| Chart | Where it comes from | Purpose |
|---|---|---|
| `openg2p-inji-certify` | subchart of **commons-services** (`openg2p-inji-certify.enabled`, default on) | Issues and signs credentials |
| `openg2p-inji-verify` | subchart of **commons-services** (`openg2p-inji-verify.enabled`, default on) | `verify-service` — checks a presented QR |
| `openg2p-registry` | the **registry** chart (Farmer Registry, NSR, …) | Agent Portal API + UI, the VC definitions, and the registration jobs |

So there are only **two installs**: commons-services (which brings Certify and Verify together), and
the registry. Both charts are published from the `verifiable-credentials` repo and share one version
line, so they always pin to the same `0.0.0-develop.N`.

## 2. Versions

Chart and image versions for every component are published in the OpenG2P catalogue:

**https://openg2p.github.io/versions/index.html**

Pin explicitly. Do not install from a floating tag.

## 3. Install parameters

Only the values that matter for VC issuance and verification are listed. Everything else keeps its
chart default.

### 3.1 Inji Certify (via commons-services)

| Parameter | Description | Default |
|---|---|---|
| `openg2p-inji-certify.enabled` | Deploy Certify | `true` |
| `global.baseDomain` | Domain every hostname derives from | `<namespace>.openg2p.org` |
| `global.certifyHostname` | Public host | `certify.<baseDomain>` |
| `global.vcIssuerDid` | **Issuer identity** stamped on every credential | `did:web:<certifyHostname>` |
| `global.postgresqlHost` | Cluster PostgreSQL | `commons-postgresql` |
| `global.certifyDB` / `certifyDBUser` | Dedicated database and role | `inji_certify` / `inji_certify_user` |
| `certify.appConfig.issuerDisplay` | Human-readable issuing authority; **Certify will not start without it** | — |
| `certify.p12.enabled` | Generate the keystore on first boot | `true` |
| `certify.p12.persistence.enabled` | Keep the keystore on a PVC (`helm.sh/resource-policy: keep`) | `true` |
| `certify.p12.existingSecret` | Restore a backed-up keystore instead; takes precedence over the PVC | `""` |
| `certify.p12.backupToSecret.enabled` | Copy the keystore into a Secret so namespace backups capture it | `true` |

{% hint style="warning" %}
`global.vcIssuerDid` must be given to the **registry** too, as `global.vcIssuer.did`. If they differ,
credentials are signed under an issuer nobody can resolve. The registry chart refuses to install with
it empty rather than signing with a blank issuer.
{% endhint %}

### 3.2 Inji Verify (via commons-services)

| Parameter | Description | Default |
|---|---|---|
| `openg2p-inji-verify.enabled` | Deploy `verify-service` | `true` |
| `global.verifyHostname` | Public host | `verify.<baseDomain>` |
| `verifyService.stateless` | Use the image's bundled in-memory database | `true` |
| `verifyService.contextPath` | Base path | `/v1/verify` |
| `verifyService.database.*` | External PostgreSQL — **only** required when `stateless: false` | — |

Nothing else needs configuring: the issuer's public key is **not** a parameter. `verify-service`
resolves it at verification time from the credential's `kid` and the issuer it names.

### 3.3 Registry (any manifestation)

These are the parameters in **any** registry chart that this feature depends on — the same set for
Farmer Registry, NSR or a customer registry, because they all build on the Registry Platform.

| Parameter | Description | Default |
|---|---|---|
| `agentPortalApi.enabled` | Deploy the Agent Portal API and its route | `false` |
| `agentPortalApi.vcIssuance.enabled` | Mount the **issuance** endpoints | `false` |
| `agentPortalApi.vcVerification.enabled` | Mount the **verification** endpoint (the Verify VC card) | varies |
| `agentPortalApi.vcVerification.serviceUrl` | In-cluster verify-service | `http://commons-services-inji-verify-service/v1/verify` |
| `agentPortalApi.certifyBaseUrl` | In-cluster Certify | `http://commons-services-inji-certify/v1/certify` |
| `global.vcIssuer.did` | **Must equal** Certify's `global.vcIssuerDid` | `""` (install fails if empty) |
| `agentPortalApi.vcDefinitions[]` | The credential types this registry issues — view, claim columns, Certify config, SVG, `qr_data_label` | supplied by the manifestation |
| `agentPortalApi.vcIssuance.registerId` | Register credentials are issued from | — |
| `agentPortalApi.vcIssuance.authWindowSeconds` | How long a beneficiary authentication stays valid | `300` |
| `global.agentPortalHostname` | Public host of the Agent Portal UI | `<release>-agent.<baseDomain>` |
| `global.agentKeycloakClientId` | Must equal IAM's `IAM_AGENT_KEYCLOAK_CLIENT_ID` | `agent-portal` |

{% hint style="danger" %}
**Set `global.agentPortalHostname` to the same value on the commons-services install.** The registry
derives it from its own release name (`fr-agent.<baseDomain>`); commons-services defaults to
`agent-portal.<baseDomain>` and cannot know the registry's release name. A mismatch **breaks sign-out
only** — login keeps working — so it surfaces long after install. commons-services now rejects the
install rather than letting the two diverge.
{% endhint %}

With both `agentPortalApi.*` switches off, the chart renders exactly what it did before the capability
existed. The only always-present addition is the issuance event-log table, created by an additive
migration; it stays empty and is referenced by nothing.

### 3.4 Keys — what you must decide

There is one decision: **how the Certify keystore is held.**

* **New environment** — take the defaults. Keymanager generates the keypairs on first boot onto a PVC
  marked `resource-policy: keep`, and `p12.backupToSecret` copies it into a Secret.
* **Redeploying an existing issuer** — set `certify.p12.existingSecret` to the backed-up keystore
  **and** restore the matching Certify database. Both, from the same moment.

Nothing else about keys is configured: the DID is derived from the hostname, and verifiers fetch
public keys from the JWKS endpoint.

## 4. Jobs that run on the cluster

| Job | Chart | When | What it does |
|---|---|---|---|
| `<release>-postgres-init-<name>` | certify | pre-install | Creates the Certify database and role on the cluster PostgreSQL |
| `<release>-inji-certify-db-schema-init` | certify | pre-install | Seeds keymanager tables and key policies. **No** `credential_config` — modules register those |
| `<release>-db-seed` | registry | post-install/upgrade, w=10 | Registry schema and seed data; must precede everything that references a register |
| `<release>-registrant-auth-bootstrap` | registry | post-install/upgrade, w=15 | Creates the **eSignet OIDC client**, the registry's provider row and its keypair, and sets `requires_registrant_authentication` on the register. Reuses the key from its Secret rather than rotating it |
| `<release>-agent-vc-register` | registry | post-install/upgrade, w=16 | Registers each `vcDefinitions[].certifyConfig` with Certify (`credential_config`). Certify can only issue a type it already knows |
| `<release>-iam-register` | registry | post-install/upgrade, w=20 | Publishes the registry's applications, permissions and roles to IAM — including `register:issue_credential` and `register:verify_credential` |
| `<release>-sanity` | registry | post-install/upgrade, w=25 | Smoke and contract checks; fails the install if the wiring is broken |
| `<release>-keycloak-init` | commons/registry | pre-install | Creates the `agent` realm, the `agent-portal` client and its roles |

Weights matter: the register job runs **after** `db-seed` because it needs the register to exist, and
**before** `iam-register` and `sanity`.

Jobs with `hook-delete-policy: hook-succeeded` remove themselves on success, so a completed
`registrant-auth-bootstrap` or `agent-vc-register` will **not** appear in `kubectl get jobs`. Use
`helm get hooks <release>` to see them.

## 5. Testing the deployment

**Automatic.** The registry's `sanity` job runs as an install hook and fails the install if the wiring
is wrong — `/ping`, OpenAPI, the issuance routes present only when enabled, protected endpoints
rejecting anonymous calls. No data is created. An opt-in `runE2e` mode walks the real chain
(agent token → lookup → beneficiary authentication → issuance → PDF); **turn it off in production.**

**Manual, in order — each step proves the one before it:**

1. **Certify is up and knows its types**

   ```bash
   curl -s https://<certify-host>/v1/certify/.well-known/openid-credential-issuer | jq '.credential_configurations_supported | keys'
   ```
   Empty means `agent-vc-register` did not run.

2. **Both public keys are published** — the QR cannot be verified without the P-256 key

   ```bash
   curl -s https://<certify-host>/.well-known/jwks.json | jq '.keys[] | {kid, crv}'
   ```
   Expect an `Ed25519` entry **and** a `P-256` entry. A 404 here means the chart's well-known rewrite
   is missing.

3. **verify-service answers**

   ```bash
   curl -s -o /dev/null -w '%{http_code}\n' -X POST https://<verify-host>/v1/verify/vc-verification \
     -H 'Content-Type: application/vc+cwt' --data 'aa'
   ```

4. **Issue a credential** from the Agent Portal and print it.

5. **Verify it** — upload the PDF or a photo to the portal's **Verify VC** card. Expect `SUCCESS` and
   the credential's contents.

6. **Prove verification is real** — flip one character in the QR payload and confirm the verdict
   becomes `INVALID`. A verifier that accepts everything is worse than none.

---

# Part C — Troubleshooting

## Beneficiary authentication fails

**eSignet must release `individual_id`.** Its discovery document advertises
`subject_types_supported: ["pairwise"]`, so `sub` is a per-client pseudonym, never the national ID. The
adapter falls back to `sub` when `individual_id` is absent, and the binding check then compares a
pseudonym against `foundational_id` and fails every time. Request it explicitly via the provider's
`extra_authorize_params.claims.userinfo.individual_id`.

**The registrant-auth session store must be shared.** The eSignet transaction is created when
authentication *starts* (agent portal) and read back at the *callback* (staff API) — two services, each
with several workers. With the default in-process store the callback has never seen the state. Point
`registry_core_registrant_auth_session_store_backend=redis` and `registry_core_registrant_auth_redis_url`
at one Redis for both; the registry chart does this by default.

## The eSignet client key — why a reinstall must not rotate it

The registry authenticates to eSignet with **`private_key_jwt`**: every token
exchange is signed with a private key whose public half eSignet holds in
`esignet.client_detail`. The `registrant-auth-bootstrap` Job creates both halves
on install.

**The key must survive a reinstall.** It originally lived only in
`g2p_registrant_authentication_providers.client_private_key`, and the registry
schema is rebuilt by a reinstall — so the row disappeared, the Job saw no key,
and minted a new one. That rotates a live credential as a side effect of
reinstalling, and the failure it produces is deeply unhelpful:

```
eSignet: Failed to verify client assertion
         BadJWSException: Signed JWT rejected: Invalid signature
returned to the portal as: invalid_assertion
```

Nothing in that says a key moved. Both databases look *consistent* afterwards,
because the Job updates eSignet's `client_detail` with the new public half too —
so comparing the two moduli shows a match while authentication still fails.

The chart therefore also keeps the keypair in a Secret
(`agentPortalApi.vcIssuance.bootstrap.persistKeyToSecret`, on by default, named
`<release>-registrant-auth-client-key`). The Job restores from it when present
and generates only when it is absent. The Secret is deliberately **not** owned by
the release, so `helm uninstall` leaves it and the key survives an
uninstall/reinstall cycle.

To rotate deliberately: delete that Secret, reinstall, **then clear eSignet's
client cache** (see below).

{% hint style="danger" %}
**eSignet caches the client in REDIS, not in memory. Restarting eSignet does not
clear it.**

The cached entry is `clientdetails::<client_id>` in the Redis that
`spring_redis_host` points at (`commons-redis-auth` in a standard OpenG2P
install). It holds the client's **public key** as it was when first read.

So after any key rotation, eSignet keeps verifying against the *old* public key
while the registry signs with the new private key — and every authentication
fails with `invalid_assertion` until the cache entry is deleted or expires.
Restarting the eSignet pod achieves nothing, because the cache outlives it.

```bash
kubectl -n <ns> exec <redis-pod> -- \
  sh -c 'REDISCLI_AUTH=<pw> redis-cli DEL "clientdetails::<client_id>"'
```

This is why a reinstall that rotates the key breaks authentication in a way that
looks like a misconfiguration: both databases agree, the assertion is correctly
signed, and eSignet still rejects it.
{% endhint %}

### Diagnosing `invalid_assertion`

The portal reports:

```
Authentication Failed — invalid_assertion: invalid_assertion
```

and eSignet logs `BadJWSException: Signed JWT rejected: Invalid signature` from
`TokenServiceImpl.verifyClientAssertionToken`.

Work through it in this order — the first two are cheap and settle most cases:

**1. Are the two halves of the keypair actually a pair?** Read the private key
from `g2p_registrant_authentication_providers.client_private_key`, derive its
public modulus, and compare with `esignet.client_detail.public_key`.`n`. If they
differ, the registry and eSignet were written at different times.

**2. Is eSignet's Redis cache stale?** Fetch `clientdetails::<client_id>` and
check whether the CURRENT modulus appears in it. If it does not, that is the
fault — delete the key. **This is the common case after any reinstall.**

**3. Is the assertion itself well-formed?** Capture what the registry actually
sends (point `token_endpoint` at a logging proxy) and verify its signature
locally against the stored private key.

{% hint style="warning" %}
**Do not test an assertion with a dummy `code`.** eSignet validates the
transaction *before* the client assertion, so an invalid code returns
`invalid_transaction` having never looked at the assertion. Reading that as "the
assertion was accepted" is wrong and will send you down a blind alley — only a
real authorization code exercises assertion verification.
{% endhint %}

## Sign-out returns a 404

`global.agentPortalHostname` on commons-services does not match the registry's agent UI host. See
[Agent Portal → Signing out](../../../products/registry/registry/features/agent-portal.md).

## Uninstalling

`helm uninstall` does **not** remove the Certify database and role (created by `postgres-init`, not
owned by the release) or the keystore PVC (`helm.sh/resource-policy: keep`). That is deliberate — both
are the issuer identity. Remove them by hand only when you intend to retire the issuer, and understand
that every credential it signed becomes unverifiable.
