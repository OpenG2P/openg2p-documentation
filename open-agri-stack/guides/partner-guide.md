---
description: >-
  How a partner (bank, MFI, agritech) joins Agri Stack and uses it end to
  end: onboarding, keys, CM bindings, the farmer's consent with a grant per
  registry, signing, calling a use case, and reading and verifying the
  response.
---

# Partner Guide

You are a **partner**: a bank, MFI or agritech that needs farmer data held across several registries, for an approved use case such as `loan-profile`. You send **one signed request** with the farmer's identifier and **one consent** to the use-case composite, and get back **one signed response** with a status per registry.

{% hint style="info" %}
This guide covers what is specific to Agri Stack. The consent object, its signing and the Consent Manager's reason codes are documented once, in the Consent Manager's [Partner Integration Guide](../../consent-management/partner-integration-guide.md); onboarding mechanics are in [Partner Management](../../platform/platform-services/partner-management/README.md). This guide links to both rather than repeating them.
{% endhint %}

## How it fits together

The diagram shows the sample use case `loan-profile`, which reads the Farmer Registry and then the Crop Sown Registry; another use case reads its own registries in its own order.

```mermaid
sequenceDiagram
  participant P as You (partner)
  participant C as Composite
  participant FR as Farmer Registry
  participant CSR as Crop Sown Registry
  participant CM as Consent Manager
  participant PM as Partner Management
  Note over P,PM: One-time: onboarding (PM), bindings and policies (CM), allowed for the use case
  P->>P: collect the farmer's consent; sign a consent JWS with a grant per registry
  P->>C: POST /composite/v1/use-cases/loan-profile/query (signed envelope + consent)
  C->>PM: your public key (PARTNER_<ID>)
  C->>FR: DCI search, signed by the composite, your consent unchanged
  FR->>CM: /validate (your consent, data_controller = farmer-registry)
  FR-->>C: farmer record, filtered to your grant ∩ policy
  par after the farmer
    C->>CSR: DCI search (season summaries)
    C->>CSR: DCI search (crop seasons)
  end
  CSR->>CM: /validate (data_controller = crop-sown-registry)
  CSR-->>C: records, filtered
  C-->>P: one signed response, status per source
```

You never call the registries or `/validate` yourself. Each registry asks the Consent Manager about **its own grant** in your consent, and releases only `grant ∩ policy`. The composite only routes, maps and signs; it stores nothing.

## What you need, and who sets it up

| What | Who does it today | Step |
| --- | --- | --- |
| A signing key pair and a `kid` | You | [1](#step-1-generate-your-signing-key) |
| Your partner record and public key in Partner Management | A **PM administrator** (no self-service yet) | [2](#step-2-get-onboarded-in-partner-management) |
| A binding and data-share policy for each registry, in the Consent Manager | The **CM administrator** (each registry's policy may need AWE approval) | [3](#step-3-get-a-binding-and-policy-for-each-registry) |
| Permission to call the use case (`allowed_partners`) | The **Agri Stack operator** | [4](#step-4-get-allowed-for-the-use-case) |
| The composite's URL and its public key | The Agri Stack operator | [5](#step-5-discover-the-use-case) |

## Step 1 — Generate your signing key

You sign two things with the same key: the **consent** and the **request envelope**. Supported algorithms: **EdDSA** (Ed25519), **ES256** (EC P-256) and **RS256** (RSA). Keep the private key in a keystore (a `.p12` is recommended); share only the public key. Choose a stable `kid` (e.g. `bank-a-2026-01`) and put it in every JWS header.

Key generation is shown in the Consent Manager's [Partner Integration Guide, step 1](../../consent-management/partner-integration-guide.md#step-1-generate-and-hold-your-signing-key). The [partner test kit](#test-kit) generates an EC P-256 key (ES256) for testing.

## Step 2 — Get onboarded in Partner Management

Partner Management (PM) is the trust root: the composite, every registry and the Consent Manager fetch your public key from it. In the first version of PM the portal is **admin-run**: a PM administrator files your onboarding request and approves it. There is no partner self-service.

**What you give the PM administrator:**

| Item | Example | Notes |
| --- | --- | --- |
| **Partner ID** | `bank-a` | Your DCI `sender_id`, used in every request, and the consent's `aud`. Lower-case with hyphens is the convention. |
| Name and organisation | Bank A | |
| **Public key(s)** | PEM, X.509 certificate, or JWK; or a `jwks_url` to import from once | With `kid` and `algorithm` (EdDSA, ES256 or RS256) |

**The PM ID.** PM stores you as `PARTNER_<SENDER_ID>`, upper-cased with `-` replaced by `_`: partner `bank-a` is `PARTNER_BANK_A`. The composite and the registries look your key up under that ID. The composite is itself a PM partner: `agri-composite` is `PARTNER_AGRI_COMPOSITE`.

After approval your keys are served at `GET {pm}/keys/PARTNER_BANK_A` (and `/keys/PARTNER_BANK_A/jwks.json`). Ask the administrator to confirm; PM returns `404` for an unknown or disabled partner, which everyone treats as a rejection. Key rotation is a **key-update request**, also filed by the administrator. See the PM [API reference](../../platform/platform-services/partner-management/api-reference.md) and [functional specifications](../../platform/platform-services/partner-management/functional-specifications.md).

## Step 3 — Get a binding and policy for each registry

For **each registry** the use case reads, the Consent Manager needs a **binding** of your partner to that registry (data controller) with a **data-share policy**: the data scopes, purposes, subject identifier types, signing algorithms, validity limit and fetch type you may ever receive. The policy is the ceiling: you get `grant ∩ policy`, never more. The CM administrator creates them; a new or wider policy may wait for AWE approval by the department. See [Partner policy binding & approval](../../consent-management/design/partner-onboarding-and-policy.md).

The registries a use case reads are its sources' `controller`s, listed as `consent_grants_needed` when you [describe the use case](#step-5-discover-the-use-case).

**Binding** (one per registry):

| Field | Meaning | Where the value comes from |
| --- | --- | --- |
| `audience` | Who consents are given to | Your partner ID ([step 2](#step-2-get-onboarded-in-partner-management)); the same for every registry |
| `controller_id` | The registry | The registry's data-controller ID, as the use case's source names it (`sources[].controller`) |
| `partner_mgmt_id` | Your record in Partner Management | `PARTNER_<YOUR_ID>` ([step 2](#step-2-get-onboarded-in-partner-management)) |

**Policy** (one per binding):

| Field | Meaning | Where the value comes from |
| --- | --- | --- |
| `allowed_data_scopes` | The data you may ever receive from this registry | **Scope IDs from the registry's scope catalogue**, `<controller>.<name>`. The registry publishes it at `POST /partner/data_scopes` on its partner API, a signed call like every other (sign `{header, message}` with your key, `message` may be empty; the unsigned `GET` is off by default — ask the registry operator if it is not reachable to you): each scope with a label, a description and the fields it covers. Ask for the scopes the use case's output needs, and no more. |
| `allowed_purposes` | Purpose codes your consents may carry | The use case's `purpose` ([step 5](#step-5-discover-the-use-case)) |
| `allowed_subject_id_types` | Identifier types the consent's subject may use | The use case's `input.subject.id_types` ([step 5](#step-5-discover-the-use-case)) |
| `allowed_signing_algs` | Algorithms your consents may be signed with | Your key's algorithm ([step 1](#step-1-generate-your-signing-key)): `EdDSA`, `ES256` or `RS256` |
| `max_validity_duration` | The longest consent validity accepted | Agreed with the department; an ISO 8601 duration such as `P90D` |
| `fetch_type` | Access pattern | `oneshot` for a use case you call per request |

A data scope is a **named group of the registry's own fields**, not a key of the record you get back: the registry filters each record to the scopes' fields before rendering it. A scope ID the registry does not have grants nothing. See [Data Scopes](../../products/registry/registry/design/data-scopes.md).

**Sources that depend on another.** When a use case queries one registry with a value read from another registry's record (a source with `depends_on`), your scopes for the first registry must include the one that carries that value. Otherwise the dependent sources have nothing to query with.

#### Example: `loan-profile`

Two bindings, for `farmer-registry` and `crop-sown-registry`, both with `audience` = `bank-a` and `partner_mgmt_id` = `PARTNER_BANK_A`:

| Policy field | `farmer-registry` | `crop-sown-registry` |
| --- | --- | --- |
| `allowed_data_scopes` | `farmer-registry.farmer_identifiers`, `farmer-registry.personal_details`, `farmer-registry.household_location`, `farmer-registry.land`, `farmer-registry.land_location`, `farmer-registry.main_crops` | `crop-sown-registry.farmer_reference`, `crop-sown-registry.crop_season`, `crop-sown-registry.measures`, `crop-sown-registry.location` |
| `allowed_purposes` | `credit-assessment` | `credit-assessment` |
| `allowed_subject_id_types` | `FAYDA_FAN`, `FARMER_ID` | `FAYDA_FAN`, `FARMER_ID` |
| `allowed_signing_algs` | `ES256` | `ES256` |
| `max_validity_duration` | `P90D` | `P90D` |
| `fetch_type` | `oneshot` | `oneshot` |

The crop sources query the Crop Sown Registry by farmer ID, read from the farmer record, so the Farmer Registry scopes include `farmer-registry.farmer_identifiers`.

## Step 4 — Get allowed for the use case

Until Partner Management holds policies and partner associations, each use case lists the partners that may call it in `allowed_partners` (for example, the sample `loan-profile` ships with `[bank-a]`). Ask the Agri Stack operator to add your partner ID; otherwise every call is rejected `403 partner_not_allowed`. See [composite configuration](composite-configuration.md#use-case-file-format).

## Step 5 — Discover the use case

The operator gives you the composite's URL, e.g. `https://agri-composite.<namespace>.openg2p.org`, and its public key for verifying responses. The describe endpoints need no signature:

```bash
curl -s https://agri-composite.<ns>.openg2p.org/composite/v1/use-cases              # all published use cases
curl -s https://agri-composite.<ns>.openg2p.org/composite/v1/use-cases/<use_case>   # one use case
```

The description tells you what to set up and send: `purpose` (for the policies and the consent), `input.subject.id_types` and `input.parameters` (for the request), `sources` and `consent_grants_needed` (the registries to get bindings for and to grant in the consent), `consent_scopes` (per registry, the data scopes the consent must grant, `required`, and may grant, `optional`), and `output_fields`.

Example: `loan-profile`.

```json
{
  "use_case": "loan-profile@1",
  "name": "loan-profile",
  "version": "1.0.0",
  "status": "published",
  "title": "Farmer loan profile",
  "description": "Identity, location, land and declared crops from the Farmer Registry, and crop seasons …",
  "policy": "credit-assessment",
  "purpose": "credit-assessment",
  "consent": {"required": true},
  "input": {
    "subject": {"id_types": ["FAYDA_FAN", "FARMER_ID"]},
    "parameters": {
      "crop_year": {"type": "integer", "description": "Crop year, e.g. 2019 (…)", "required": false, "min": 1990.0, "max": 2100.0},
      "season": {"type": "string", "description": "Season code", "required": false,
                 "enum": ["SEASON_MEHER", "SEASON_BELG", "SEASON_IRRIGATION"]}
    },
    "batch": {"max_subjects": 1}
  },
  "sources": [
    {"id": "farmer", "controller": "farmer-registry", "requirement": "mandatory", "depends_on": [],
     "scopes": ["farmer-registry.farmer_identifiers", "farmer-registry.personal_details",
                "farmer-registry.land", "farmer-registry.main_crops"],
     "optional_scopes": ["farmer-registry.household_location", "farmer-registry.land_location"]},
    {"id": "season_summaries", "controller": "crop-sown-registry", "requirement": "optional", "depends_on": ["farmer"],
     "scopes": ["crop-sown-registry.farmer_reference", "crop-sown-registry.crop_season", "crop-sown-registry.measures"],
     "optional_scopes": ["crop-sown-registry.location"]},
    {"id": "crop_seasons", "controller": "crop-sown-registry", "requirement": "optional", "depends_on": ["farmer"],
     "scopes": ["crop-sown-registry.farmer_reference", "crop-sown-registry.crop_season", "crop-sown-registry.measures"],
     "optional_scopes": ["crop-sown-registry.location"]}
  ],
  "consent_grants_needed": ["crop-sown-registry", "farmer-registry"],
  "consent_scopes": {
    "crop-sown-registry": {"required": ["crop-sown-registry.crop_season", "crop-sown-registry.farmer_reference",
                                        "crop-sown-registry.measures"],
                           "optional": ["crop-sown-registry.location"]},
    "farmer-registry": {"required": ["farmer-registry.farmer_identifiers", "farmer-registry.land",
                                     "farmer-registry.main_crops", "farmer-registry.personal_details"],
                        "optional": ["farmer-registry.household_location", "farmer-registry.land_location"]}
  },
  "output_fields": ["crops.season_summaries", "crops.seasons", "crops.total_area_sown_ha", "farmer.birth_date",
                    "farmer.identifiers", "farmer.location", "farmer.main_crops", "farmer.name", "farmer.sex",
                    "land.parcel_count", "land.parcels", "land.total_size"],
  "source_status": true,
  "partial_response": "allowed",
  "rate_per_partner": "60/min"
}
```

`consent_grants_needed` lists the registries your consent needs a grant for, and `consent_scopes` the data scopes of each grant: grant every `required` scope (and the `optional` ones you want). A grant for a **mandatory** source, with its required scopes, is needed or the request fails (`consent_scope_missing`); without them for an **optional** source, that source is reported `denied` and not called. Scopes beyond the use case's are never asked for.

## Step 6 — Collect the farmer's consent

Data is released only against the farmer's consent for the specific purpose and scopes.

{% hint style="warning" %}
**Today you collect the consent yourself and sign it.** A consent collected inside the Consent Manager (the farmer approving in CM with a Fayda OTP) cannot yet be presented at a registry ([open items](../open-items/README.md)). So the consent you send is one **you obtained from the farmer** through your own channel and assert in a consent object signed with your key (the "partner-embedded" flow).
{% endhint %}

What that means for you:

* **Obtain real, informed consent** for the use case's purpose (e.g. `credit-assessment` for `loan-profile`) and for each registry's data, before you sign. Tell the farmer which registries hold the data being shared (e.g. the Farmer Registry and the Crop Sown Registry for `loan-profile`) and what each scope covers (its label and description in the registry's catalogue), as the CM consent screen would.
* **Stay within the policy.** The scopes you grant per registry must be within that registry's policy (step 3), and within what the farmer agreed to.
* **Keep evidence** of how the consent was obtained, for audit and disputes: who consented, when, through which channel and how they were authenticated, for which purpose and which registries' data. The capture method and evidence a department accepts are part of your agreement with it when your binding and policy are set up; follow what it requires.
* **The signed consent and the Consent Manager's receipts are the audit trail.** CM issues a receipt per registry that validated your consent ([Partner Integration Guide, step 9](../../consent-management/partner-integration-guide.md)). Misrepresenting consent is a compliance breach.

## Step 7 — Build and sign the consent

The consent is a **compact JWS** signed with your key, with **one grant per registry**. The claims are defined in the [Partner Integration Guide, step 5](../../consent-management/partner-integration-guide.md#step-5-construct-the-consent-claims); for Agri Stack:

| Claim | Value | Rule |
| --- | --- | --- |
| `jti` | a new UUID | **New for every consent.** Re-sending the same signed consent to the same registry returns its earlier decision; a different consent reusing a `jti` is denied `replay`. |
| `aud` | your partner ID | |
| `subject_id` | `{"type": …, "value": …}`, a type from the use case's `input.subject.id_types` | Must equal `message.subject` in your request: **same type and value** |
| `purpose` | `{"code": <the use case's purpose>}` | Allowed by each registry's policy |
| `grants` | `[{"data_controller": <registry>, "data_scopes": [<scope IDs>]}]`, one per registry in `consent_grants_needed` | Each registry once; scope IDs from that registry's catalogue, within its policy and within what the farmer agreed to |
| `fetch_type` | `oneshot` | |
| `validity` | `{"valid_from": …, "valid_until": …}` | Within the policy's `max_validity_duration`; the composite rejects a consent outside its window |
| `issued_at` | now (UTC) | Within **±300 seconds** of the Consent Manager's clock (its freshness window), so sign a **fresh consent for each request** and keep clocks in sync |

Example: `loan-profile`, for partner `bank-a`.

```json
{
  "jti": "5f0c2a8e-3d1b-4a51-9a0e-2b8f2e7c9d10",
  "aud": "bank-a",
  "subject_id": {"type": "FAYDA_FAN", "value": "123456789012"},
  "purpose": {"code": "credit-assessment"},
  "grants": [
    {"data_controller": "farmer-registry",
     "data_scopes": ["farmer-registry.farmer_identifiers", "farmer-registry.personal_details",
                     "farmer-registry.household_location", "farmer-registry.land",
                     "farmer-registry.land_location", "farmer-registry.main_crops"]},
    {"data_controller": "crop-sown-registry",
     "data_scopes": ["crop-sown-registry.farmer_reference", "crop-sown-registry.crop_season",
                     "crop-sown-registry.measures", "crop-sown-registry.location"]}
  ],
  "fetch_type": "oneshot",
  "validity": {"valid_from": "2026-10-01T10:00:00+00:00", "valid_until": "2026-10-31T10:00:00+00:00"},
  "issued_at": "2026-10-01T10:00:00+00:00"
}
```

Sign it with your key and `kid` (any RFC 7515 library):

```python
import json
from jwt import PyJWS  # PyJWT

def canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()

consent_jws = PyJWS().encode(canonical(claims), private_key, algorithm="ES256", headers={"kid": "bank-a-2026-01"})
# "eyJhbGciOiJFUzI1NiIs…" + "." + payload + "." + signature
```

The same consent goes to every registry: the composite forwards it unchanged, and each registry validates only its own grant.

## Step 8 — Sign the request envelope

The request is a DCI-style envelope: `header`, `message`, and a **detached JWS** over `{header, message}`.

| Field | Value |
| --- | --- |
| `header.version` | `1.0.0` |
| `header.message_id` | a new UUID |
| `header.message_ts` | now, ISO 8601 UTC, e.g. `2026-10-01T10:00:00.000Z`. Must be within **300 seconds** of the composite's clock. |
| `header.action` | `query` |
| `header.sender_id` | your partner ID |
| `header.receiver_id` | the composite's ID, `agri-composite` (if present, it must match) |
| `message.subject` | `{"type": "FAYDA_FAN" \| "FARMER_ID", "value": "…"}` |
| `message.parameters` | the use case's `input.parameters`, e.g. `{"crop_year": 2019, "season": "SEASON_MEHER"}` for `loan-profile`; omit or `{}` for none |
| `message.consent_jws` | the consent from step 7 |
| `message.consent_id` | *instead of `consent_jws`:* the ID of a consent the farmer gave through the Consent Manager (e.g. collected in person in the partner portal and verified by staff; see [consent collection](../../consent-management/design/consent-collection.md)). The exchange Consent Manager checks it (active, in its validity, obtained by you, about this farmer) and what it grants; needs the composite's exchange consent mode. Send one of the two, not both. |

**The signature** is a JWS whose payload is the canonical JSON of `{"header": …, "message": …}` (keys sorted, no whitespace, UTF-8), with the payload part removed: `<protected header>..<signature>`.

Example (`loan-profile`, partner `bank-a`):

```python
import uuid
from datetime import datetime, timezone

def sign_detached(payload: dict, key, kid: str) -> str:
    h, _p, s = PyJWS().encode(canonical(payload), key, algorithm="ES256", headers={"kid": kid}).split(".")
    return f"{h}..{s}"

header = {"version": "1.0.0", "message_id": str(uuid.uuid4()),
          "message_ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
          "action": "query", "sender_id": "bank-a", "receiver_id": "agri-composite"}
message = {"subject": {"type": "FAYDA_FAN", "value": "123456789012"},
           "parameters": {"crop_year": 2019, "season": "SEASON_MEHER"},
           "consent_jws": consent_jws}
envelope = {"signature": sign_detached({"header": header, "message": message}, private_key, "bank-a-2026-01"),
            "header": header, "message": message}
```

## Step 9 — Call the use case

```
POST https://agri-composite.<ns>.openg2p.org/composite/v1/use-cases/<use_case>/query
Content-Type: application/json

<envelope>
```

* `<use_case>` gets the highest published major version; `<use_case>@1` pins major 1 (or send the header `X-Use-Case-Major: 1`). For example `loan-profile` or `loan-profile@1`.
* How many subjects one request may carry is the use case's `input.batch.max_subjects` (one for `loan-profile`).

## Step 10 — Read the response

The response is an envelope signed by the composite. Example (`loan-profile`):

```json
{
  "signature": "<protected header>..<signature>",
  "header": {"version": "1.0.0", "message_id": "…", "message_ts": "…", "action": "on-query",
             "status": "succ", "sender_id": "agri-composite", "receiver_id": "bank-a",
             "meta": {"in_reply_to": "<your header.message_id>"}},
  "message": {"use_case": "loan-profile@1", "version": "1.0.0", "request_id": "…",
              "subject": {"type": "FAYDA_FAN", "value": "123456789012"},
              "sources": {"farmer": {"status": "ok"}, "season_summaries": {"status": "ok"},
                          "crop_seasons": {"status": "ok"}},
              "data": {"…": "…"}}
}
```

* `header.status` is `succ` or `rjct`; on `rjct`, `header.status_reason_code` and `status_reason_message` say why, and `message` carries `error: {code, message}` instead of `data`.
* `message.request_id` is the composite's ID for this request; quote it when reporting a problem (audit events are linked by it).
* `message.sources` has a status per source, and a `detail` when there is something to say:

| Source status | Meaning |
| --- | --- |
| `ok` | The registry returned records |
| `no_record` | The registry answered, with no matching record |
| `denied` | The registry refused (consent, policy or subject check), or your consent has no grant for it (an optional source is then not called) |
| `unavailable` | The registry could not be reached, timed out, or answered 408/429/5xx; or the overall timeout was reached |
| `error` | Any other failure (a rejected search, a malformed answer) |

A source whose dependency is not `ok` is not called; it takes the dependency's status, with `detail: "not called: …"`. With `partial_response: allowed` (e.g. `loan-profile`), only a failing **mandatory** source fails the request; optional sources that fail just show their status, and their output fields are empty.

**HTTP status and error codes:**

| HTTP | `error.code` | Meaning |
| --- | --- | --- |
| 200 | — | Success (some optional sources may still be `denied` / `unavailable` / `error`) |
| 400 | `invalid_envelope`, `wrong_receiver`, `stale_request`, `invalid_use_case`, `invalid_input` | Bad envelope, wrong `receiver_id`, `message_ts` more than 300 s from now, bad `@major`, bad subject or parameters |
| 401 | `signature_invalid` | The envelope signature does not verify against your PM key (or you are unknown in PM) |
| 403 | `partner_not_allowed` | You are not in the use case's `allowed_partners` |
| 403 | `consent_required`, `consent_malformed`, `consent_signature_invalid`, `consent_subject_mismatch`, `consent_not_yet_valid`, `consent_expired`, `consent_grant_missing` | A consent problem found by the composite before any registry is called |
| 403 | `source_denied` | A mandatory source was denied (e.g. by the Consent Manager at the registry) |
| 404 | `unknown_use_case` | No published use case of that name / major |
| 429 | `rate_limited` | Rate limit reached |
| 502 / 503 / 504 | `source_error` / `source_unavailable` | A mandatory source failed: error / unavailable / timed out |
| 500 | `signing_unavailable` | The composite cannot sign (its key is missing); the body is unsigned |

When a registry denies your consent, the reason in `sources.<id>.detail` comes from the Consent Manager's `reason_code`; see the table in the [Partner Integration Guide, step 8](../../consent-management/partner-integration-guide.md).

## Step 11 — Verify the composite's signature

Verify every response before you use it. The `signature` is a detached JWS over the canonical JSON of the response's `{header, message}`, signed with the composite's key (`PARTNER_AGRI_COMPOSITE` in PM; the JWS header carries its `kid`):

```python
import base64

def verify_response(body: dict, composite_public_key) -> None:
    h, _, s = body["signature"].split(".")
    payload = base64.urlsafe_b64encode(canonical({"header": body["header"], "message": body["message"]})).decode().rstrip("=")
    PyJWS().decode(f"{h}.{payload}.{s}", composite_public_key, algorithms=["ES256", "RS256", "EdDSA"])  # raises if invalid
```

Get the composite's public key from the operator, or from PM's key API (`GET {pm}/keys/PARTNER_AGRI_COMPOSITE`) where it is reachable to you; the key-fetch API is served on the cluster-internal gateway.

## Rate limits

Each use case sets a rate per partner (its `rate_per_partner`; `loan-profile` allows **60 requests per minute**), and `429 rate_limited` is returned beyond it. The limit is applied per composite pod and worker, so it is a floor rather than an exact ceiling; limits across all pods and daily quotas are [not built yet](../open-items/README.md).

## Worked example: `loan-profile`

**Request:** farmer by FAN, Meher 2019.

```json
{
  "signature": "eyJhbGciOiJFUzI1NiIsImtpZCI6ImJhbmstYS0yMDI2LTAxIn0..MEUCIQ…",
  "header": {"version": "1.0.0", "message_id": "0b6f6c1e-…", "message_ts": "2026-10-01T10:00:00.000Z",
             "action": "query", "sender_id": "bank-a", "receiver_id": "agri-composite"},
  "message": {"subject": {"type": "FAYDA_FAN", "value": "123456789012"},
              "parameters": {"crop_year": 2019, "season": "SEASON_MEHER"},
              "consent_jws": "eyJhbGciOiJFUzI1NiIsImtpZCI6ImJhbmstYS0yMDI2LTAxIn0.eyJhdWQiOiJiYW5rLWEi….…"}
}
```

**What the composite does:**

1. Verifies your signature (`PARTNER_BANK_A`), checks `allowed_partners`, the parameters and the rate limit.
2. Checks the consent: your signature, subject `FAYDA_FAN 123456789012` = the request's, valid now, a grant for `farmer-registry` (mandatory) and `crop-sown-registry`.
3. Calls the **Farmer Registry**: `reg_type: Farmer`, search `foundational_id $eq 123456789012`.
4. Reads `FARMER_ID` from the farmer record, then calls the **Crop Sown Registry** twice in parallel: season summaries (`FARMER_SEASON_SUMMARY`, crop year 2019, Meher) and crop seasons (crop year 2019, Meher).
5. Maps and derives the output, signs and returns it.

**Response** (`message`; record contents abbreviated — each keeps its registry's DCI record shape):

```json
{
  "use_case": "loan-profile@1",
  "version": "1.0.0",
  "request_id": "7d2e…",
  "subject": {"type": "FAYDA_FAN", "value": "123456789012"},
  "sources": {"farmer": {"status": "ok"}, "season_summaries": {"status": "ok"}, "crop_seasons": {"status": "ok"}},
  "data": {
    "farmer": {
      "name": "…", "sex": "…", "birth_date": "…",
      "identifiers": [{"@type": "Identifier", "identifier_type": "UIN", "identifier_value": "123456789012"},
                      {"@type": "Identifier", "identifier_type": "FARMER_ID", "identifier_value": "FR-0007"}],
      "location": {"…": "…"},
      "main_crops": ["CROP_TEFF", "CROP_WHEAT"]
    },
    "land": {"parcels": [{"…": "…"}, {"…": "…"}], "parcel_count": 2, "total_size": 1.4},
    "crops": {
      "seasons": [{"crop_season": {"…": "…"}, "measures": {"area_sown_ha": 0.9, "…": "…"}, "location": {"…": "…"}, "farmer_reference": {"…": "…"}}],
      "season_summaries": [{"…": "…"}],
      "total_area_sown_ha": 1.3
    }
  }
}
```

* `land.total_size` is the sum of each parcel's `land_size`, in the parcels' unit (`farm_details[].measurement`).
* `crops.total_area_sown_ha` sums `measures.area_sown_ha` over the crop seasons returned; with `crop_year` and `season` it is that season's.
* Without `crop_year` and `season`, all of the farmer's seasons come back, newest first.

If the farmer had not consented to the Crop Sown Registry (no grant), `season_summaries` and `crop_seasons` would be `denied` with `detail: "the consent has no grant for crop-sown-registry"`, `crops.*` would be empty, and the request would still succeed. If the Farmer Registry denied the consent, the request would fail `403 source_denied`.

## Test kit

[`scripts/partner_kit.py`](https://github.com/openg2p/agri-stack/blob/develop/scripts/partner_kit.py) does all of the above for testing (`pip install cryptography pyjwt`):

```bash
python scripts/partner_kit.py keys          # partner key + composite .p12 in scripts/kit-out (git-ignored), and what to onboard
python scripts/partner_kit.py consent --subject FAYDA_FAN:123456789012
python scripts/partner_kit.py describe --url https://agri-composite.<ns>.openg2p.org
python scripts/partner_kit.py call --url https://agri-composite.<ns>.openg2p.org \
    --subject FAYDA_FAN:<FAN of a registered farmer> --param crop_year=2019 --param season=SEASON_MEHER
```

* `keys` (defaults: partner `bank-a`, composite `agri-composite`) prints the PM onboarding requests for `PARTNER_BANK_A` and `PARTNER_AGRI_COMPOSITE`, the `kubectl create secret generic agri-composite-signing …` command, and the CM bindings and policies for audience `bank-a`.
* `call` builds a consent with both grants (`--controllers` narrows it), signs the envelope, verifies the composite's signature on the answer and prints it.

To set everything up against a cluster namespace in one go, use the [end-to-end test](end-to-end-test.md).

## Checklist

* [ ] Your key is registered and **active** in PM under `PARTNER_<YOUR_ID>`; the JWS `kid` and `alg` match it.
* [ ] CM has a binding and an **active** policy for your audience with **each** registry the use case reads.
* [ ] Your partner ID is in the use case's `allowed_partners`.
* [ ] The consent's `subject_id` equals `message.subject` (type and value); `aud` is your partner ID; one grant per registry, with scope IDs from that registry's catalogue, within its policy.
* [ ] A new `jti` and a fresh `issued_at` for each consent; `message_ts` fresh; clocks in sync.
* [ ] You verify the composite's signature and check `sources` before using `data`.
* [ ] You keep evidence of how each consent was obtained.
