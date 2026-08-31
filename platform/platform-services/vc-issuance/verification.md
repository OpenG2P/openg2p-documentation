---
description: >-
  How a printed credential's QR is checked, and why OpenG2P runs only Inji Verify's verify-service — no config-server, no PostgreSQL, no stock UI.
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

> The issuing half of this repo is deployed; the **Agent Portal verification
> screen described below is not built yet**. The chart is.

## What is actually being verified

The printed card carries a **claim-169 QR**: CBOR → COSE_Sign1 → CWT, zlib
compressed, Base45 encoded, signed with the issuer's **ES256** key. On paper
that QR signature is the only one anyone checks — the credential's Ed25519
proof covers different bytes and says nothing about the QR.

Verification is therefore:

```
Base45 decode → zlib inflate → CBOR → tag 61 (CWT) → tag 18 (COSE_Sign1)
              → verify ES256 against the issuer's public key
```

Claim-169 verification does **not** resolve DIDs, so the verifier must already
hold the issuer's ES256 key as a **trust anchor**, taken from
`https://<certify-host>/v1/certify/.well-known/jwks.json`.

## Why we run `verify-service` and not the Inji Verify stack

MOSIP's deployment guide for Inji Verify describes a sandbox topology: Istio,
PostgreSQL, a **MOSIP config-server**, an `inji-stack-config` ConfigMap, and two
services (`verify-service` + `verify-ui`), installed by their `install-all.sh`.

Almost none of that is a requirement of the service itself. The repo also ships
a plain `docker-compose.yml` in which `verify-service` runs from environment
variables alone — no config-server anywhere. That is the shape we use, exactly
as we run stock Inji **Certify** with a properties ConfigMap rather than MOSIP's
config-server.

**Verified locally** (`injistack/inji-verify-service:0.18.2`, `active_profile_env=local`,
no database, no config-server): `/v1/verify/actuator/health` → `{"status":"UP"}`,
and `POST /v1/verify/vc-verification` returns a structured verdict.

### No PostgreSQL

`verify-service` ships two Spring profiles:

| profile | datasource |
|---|---|
| `default` | external PostgreSQL — every `DATABASE_*` variable required |
| `local` | bundled **in-memory HSQLDB**, schema created at boot |

The database exists for **OpenID4VP presentation transactions** — `vp-request`,
`vp-result`, session state. We use none of them: the Agent Portal will POST a QR
payload to `/vc-verification`, which is one stateless call in and a verdict out.

So the chart defaults to `stateless: true`. The consequence, stated plainly: an
OpenID4VP flow would not survive a restart. `stateless: false` plus `database.*`
switches to the external-PostgreSQL profile without a chart change.

### No `verify-ui`

The stock React portal is not deployed. The Agent Portal gets its own
upload-and-check screen instead — the agent who just printed a card can confirm
it verifies without leaving the portal or a second product being installed.

## A separate chart, deliberately

`openg2p-inji-verify` is its own chart, not part of `openg2p-inji-certify`,
because the two sit on **opposite sides of a trust boundary**:

* **Certify is issuer-side** — run by the issuing authority, one per
  environment, never publicly exposed for issuance.
* **Verify is verifier-side** — run by a **relying party**, potentially a
  different organisation in a different cluster.

Nothing verifies a credential until a relying party stands one up. Packaging
them together would encode the claim that they deploy as a pair, which is the
wrong mental model — a ministry verifying farmer credentials should not have to
install an issuer to do it.

Environments that want both install both, as sibling subcharts of
commons-services — where `openg2p-inji-certify` already sits.

## The API

`verify-service` dispatches on `Content-Type`:

| Content-Type | Format |
|---|---|
| `application/vc+cwt` | **CWT_VC** — our claim-169 QR payload |
| `application/vc+sd-jwt`, `application/dc+sd-jwt` | VC_SD_JWT |
| anything else | LDP_VC — a JSON-LD credential |

```
POST /v1/verify/vc-verification
Content-Type: application/vc+cwt

<Base45 QR payload>
→ {"verificationStatus": "..."}
```

PixelPass is a dependency of the **service** (`pixelpass-jar`), not only of the
React UI — and at the same `0.8.0` line Certify generates with. So the decode
and the signature check both happen behind that one call: **our UI never has to
implement CBOR or COSE**.

## The Agent Portal verification screen (not built)

A second card on the Agent Portal landing page — upload a PDF or an image of the
QR, get a verdict.

* The QR is read client-side (any JS QR reader) and the payload POSTed to the
  Agent Portal API, which calls `verify-service` in-cluster. The browser never
  talks to `verify-service` directly, consistent with every other call the
  portal makes.
* Gated by its own permission, so "may issue" and "may verify" are separable.

### Auditing

**Verification attempts must be audited through the OpenG2P Audit Manager**, the
same as issuance. A verification is a real event about a real person — someone
presented a credential and a decision was made about it — and it is exactly the
kind of thing an operator needs explained later ("who checked this card, when,
and what did it say?").

The Agent Portal API already emits audit events for issuance via
`AuditMiddleware`; the verification routes are covered by the same middleware
rather than a parallel mechanism. The event must record the outcome
(valid/invalid) and the agent, and must **not** record the credential payload
itself — the point is who checked what and when, not a second copy of the
citizen's data.

## Still open

* **How the issuer trust anchor is configured.** The compose environment
  configures Inji's *own* DID (`INJI_DID_VERIFY_*`) for OpenID4VP, not how it
  trusts *our* ES256 key. Unresolved, and the one thing that must work.
* **A VALID verdict on a real claim-169 QR has not been demonstrated.** The
  endpoint accepts the format and returns structured verdicts; proving a
  genuine issuance verifies needs a live Certify and a freshly issued card.
* The samples in `examples/` predate claim-169 and carry no QR payload — worth
  regenerating.
