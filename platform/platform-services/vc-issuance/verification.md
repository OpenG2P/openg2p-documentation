---
description: >-
  How a printed credential's QR is checked — the Agent Portal's verification screen, the trust anchor it resolves keys from, and why OpenG2P runs only Inji Verify's verify-service.
layout:
  width: default
  title:
    visible: true
  description:
    visible: true
  tableOfContents:
    visible: true
  outline:
    visible: true
  pagination:
    visible: true
  metadata:
    visible: true
  tags:
    visible: true
---

# Verification — how a printed credential is checked

Web-based verification is **implemented and working**. An agent uploads a PDF or
a photo of a printed card and gets a verdict, checked against the issuer's
published key.

## What is actually being verified

The printed card carries a **claim-169 QR**: CBOR → COSE_Sign1 → CWT, zlib
compressed, Base45 encoded, signed with the issuer's **ES256** key. On paper
that QR signature is the only one anyone checks — the credential's Ed25519
proof covers different bytes and says nothing about the QR.

Verification is therefore:

```
Base45 decode → zlib inflate → hex CWT → tag 61 (CWT) → tag 18 (COSE_Sign1)
              → verify ES256 against the issuer's published public key
```

## Where the verification keys come from

This is the part that has to be right, so it is stated exactly.

`verify-service` resolves the issuer's **ES256 public key** from the JWKS that
Certify publishes:

```
https://<certify-host>/.well-known/jwks.json
```

for example `https://certify.trial.openg2p.org/.well-known/jwks.json`.

Two details matter:

**That path only exists because the Certify chart creates it.** Certify serves
its JWKS at `/v1/certify/.well-known/jwks.json`; the chart's VirtualService adds
a rewrite so the standard well-known path resolves too. Without that rewrite the
URL is a **404** and QR verification cannot work at all.

**The QR key is in the JWKS and *not* in the DID document.** The two are
populated by different code paths in Certify:

| Surface | Contains | Populated from |
|---|---|---|
| `/.well-known/jwks.json` | **all** configured keys — Ed25519 **and** ES256 (P-256) | `mosip.certify.signature-algo.key-alias-mapper` |
| `/.well-known/did.json` | **Ed25519 only** | `credential_config.signature_algo` |

So a verifier that resolves `did:web` finds only the JSON-LD proof key and never
the key that signed the QR. **The JWKS is the trust anchor for paper
credentials.** Both keys being published is verifiable directly:

```bash
curl -s https://<certify-host>/.well-known/jwks.json | jq '.keys[] | {kid, crv}'
```

A correct deployment shows an `Ed25519` entry and a `P-256` entry.

### What a SUCCESS verdict does and does not prove

Demonstrated against a live deployment:

| Input | Verdict |
|---|---|
| A genuine issued credential | `SUCCESS` |
| The same token, one byte of the signature flipped | `INVALID` |
| The same issuer, same `kid`, same payload, re-signed with a different key | `INVALID` |

The third case is the meaningful one: it proves the verifier really does fetch
Certify's published key rather than trusting anything asserted inside the token.

What a `SUCCESS` does **not** cover:

* **Revocation.** There is no status list. A credential is valid until it
  expires (180 days by default) and cannot be cancelled.
* **Anything not in the QR.** The verdict applies to the claim-169 payload
  only — see [Phase 1 — Paper Credential](phase-1-paper-credential.md) for
  exactly which fields that is.
* **Issuer allow-listing.** `verify-service` is not configured with a list of
  trusted issuers, so the honest reading of a verdict is "this signature is
  authentic for the issuer the credential names".

## The Agent Portal verification screen

A **Verify VC** card on the Agent Portal landing page. Upload the printed PDF or
a photo of it; the verdict and the credential's contents come back.

### The image never leaves the device

The QR is read **in the browser** — `pdf.js` to rasterise a PDF page, a JS QR
reader for images, then MOSIP's **PixelPass** to unwrap Base45 → zlib → hex.
Only the resulting hex CWT is sent to the Agent Portal API.

This is a deliberate property, not an accident of implementation: a photo of a
credential is a photo of a person's identity document, often with their name,
date of birth and sometimes their face on it. Uploading it would put that image
in request logs, proxies and any intermediary between the agent's laptop and the
cluster. **The image is never transmitted, never buffered server-side, and never
stored.** What travels is the signed payload the QR already encodes.

### Request path

```
browser (reads QR, unwraps to hex)
   └─> Agent Portal API   POST /agent_portal/vc/verify
          └─> verify-service (in-cluster)  POST /v1/verify/vc-verification
```

The browser never talks to `verify-service` directly — consistent with every
other call the portal makes, and it keeps `verify-service` off the public
network.

{% hint style="warning" %}
`verify-service` expects the **hex-encoded CWT**, not the Base45 string printed
in the QR. Posting the raw QR text returns `ERR_INVALID_HEX`, which reads like a
bad credential rather than a wrongly-framed request. The Agent Portal API
rejects a non-hex payload with `G2P-VC-400` before the call is made.
{% endhint %}

### What the agent sees

The verdict, and then the credential's contents beneath it: issuer, validity
dates, and the claim-169 fields — Full Name, Date of Birth, Gender, and the
Farmer ID.

Showing the contents is the point, not decoration. "Valid" alone tells an agent
the card is genuine without telling them **whose** it is, so it cannot catch a
real credential presented by the wrong person. The contents are decoded from the
signed payload, so what is displayed is exactly what was signed — and they are
displayed **only after** a `SUCCESS`, so a failed token never puts
attacker-chosen text on screen.

`verify-service` returns the verdict alone (`{"verificationStatus": "SUCCESS"}`)
and no payload, so the Agent Portal API decodes the CWT itself for display. That
decode has no bearing on the verdict.

### Permissions

Gated by `register:verify_credential`, separate from
`register:issue_credential`, so "may issue" and "may verify" are independently
grantable. Both are client roles on the `agent-portal` Keycloak client.

{% hint style="info" %}
`keycloak-init` creates a realm and its client only when absent — it does **not**
reconcile roles onto an existing client. On an environment whose Keycloak
predates this feature, `register:verify_credential` will not appear and the
Verify card will not render, even though the chart requests it. The role has to
be added to the existing client.
{% endhint %}

### Auditing

Every call is recorded through the OpenG2P Audit Manager, including refusals.
A verification event carries the agent, their IP and session, the endpoint, the
**verdict**, and the Farmer ID from the QR.

The verdict is recorded as the event's `outcome` rather than the HTTP status: a
credential that fails verification is a *successful* HTTP call carrying bad
news, and filing it as `success` would put forged cards in the same bucket as
genuine ones — defeating the question the trail is most likely to be asked.

The credential payload itself is **not** stored. The point is who checked what
and when, not a second copy of the citizen's data.

## Why we run `verify-service` and not the Inji Verify stack

MOSIP's deployment guide for Inji Verify describes a sandbox topology: Istio,
PostgreSQL, a **MOSIP config-server**, an `inji-stack-config` ConfigMap, and two
services (`verify-service` + `verify-ui`), installed by their `install-all.sh`.

Almost none of that is a requirement of the service itself. The repo also ships
a plain `docker-compose.yml` in which `verify-service` runs from environment
variables alone. That is the shape we use, exactly as we run stock Inji
**Certify** with a properties ConfigMap rather than MOSIP's config-server.

### No PostgreSQL

`verify-service` ships two Spring profiles:

| profile | datasource |
|---|---|
| `default` | external PostgreSQL — every `DATABASE_*` variable required |
| `local` | bundled **in-memory HSQLDB**, schema created at boot |

The database exists for **OpenID4VP presentation transactions** — `vp-request`,
`vp-result`, session state. We use none of them: the Agent Portal POSTs a QR
payload to `/vc-verification`, which is one stateless call in and a verdict out.

So the chart defaults to `stateless: true`. The consequence, stated plainly: an
OpenID4VP flow would not survive a restart. `stateless: false` plus `database.*`
switches to the external-PostgreSQL profile without a chart change.

### No `verify-ui`

The stock React portal is not deployed. The Agent Portal has its own
upload-and-check screen instead — the agent who just printed a card can confirm
it verifies without leaving the portal or a second product being installed.

## The API

`verify-service` dispatches on `Content-Type`:

| Content-Type | Format |
|---|---|
| `application/vc+cwt` | **CWT_VC** — our claim-169 QR payload, hex-encoded |
| `application/vc+sd-jwt`, `application/dc+sd-jwt` | VC_SD_JWT |
| anything else | LDP_VC — a JSON-LD credential |

```
POST /v1/verify/vc-verification
Content-Type: application/vc+cwt

<hex-encoded CWT>
→ {"verificationStatus": "SUCCESS"}
```

PixelPass is a dependency of the **service** (`pixelpass-jar`), not only of the
React UI — and at the same `0.8.0` line Certify generates with.

## A separate chart, deliberately

`openg2p-inji-verify` is its own chart, not part of `openg2p-inji-certify`,
because the two sit on **opposite sides of a trust boundary**:

* **Certify is issuer-side** — run by the issuing authority, one per
  environment, never publicly exposed for issuance.
* **Verify is verifier-side** — run by a **relying party**, potentially a
  different organisation in a different cluster.

Packaging them together would encode the claim that they deploy as a pair, which
is the wrong mental model — a ministry verifying farmer credentials should not
have to install an issuer to do it.

Environments that want both install both, as sibling subcharts of
commons-services. See [Deployment](deployment.md).

## Still open

* **Issuer allow-listing.** `verify-service` has no trusted-issuer list, so it
  validates a signature against whichever issuer the credential names. For a
  single-issuer deployment this is academic; for a relying party accepting
  credentials from several authorities it is not.
* **Revocation.** No status list is issued or checked.
* The samples in `examples/` predate claim-169 and carry no QR payload — worth
  regenerating.
