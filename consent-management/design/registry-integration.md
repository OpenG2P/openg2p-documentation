# Registry integration (the PEP side)

This page describes how an OpenG2P **Registry** (e.g. the Farmer Registry) integrates
with the Consent Manager (CM) to govern outbound data sharing. The registry is the
**Policy Enforcement Point (PEP)**; CM is the **Policy Decision Point (PDP)**. The
registry never interprets consent — it forwards the partner-signed consent object to
CM, and enforces the decision CM returns.

The concrete integration lives in the **registry partner-api** (the DCI search API,
`POST /dci/registry/sync/search`).

## Two independent signatures, one key source

A partner call carries **two** signatures, both verified against the partner's public
keys **served by Partner Management (PM)** — a single trust root:

| Signature | Covers | Verified by | Purpose |
| --- | --- | --- | --- |
| **DCI envelope signature** | the whole `{header, message}` (detached JWS) | the **registry** | transport auth — "this call is fresh and from partner X" |
| **Consent object signature** | the CM consent object (a compact JWS) | the **Consent Manager** | authorisation — "partner X holds valid consent for subject S, scope Z" |

Both are **JWS** verified against PM keys via the shared `CryptoHelper.verify_jwt` — one signature format, one verify path across the platform.

The registry verifies the envelope with openg2p-fastapi-common's `build_crypto_helper`
using the **`partner-mgmt`** backend (partner keys fetched from PM). The legacy Mosip
**Keymanager** remains a selectable backend (`crypto_backend: keymanager`) but is not
the default — we are not encrypting payloads yet. Partner keys are looked up under the
platform-standard reference **`PARTNER_<sender_id>`** (upper-cased, `-`→`_`), the same
convention used by Partner Management, g2p-bridge, and openg2p-fastapi-partner-auth.

## Where the consent object is embedded

The DCI search criteria already reserve an `authorize` block (the DCI-standard slot for
the authorisation artefact). The partner embeds the **CM consent object as a compact
JWS string** at:

```
message.search_request[i].search_criteria.authorize.consent_jws
```

```jsonc
{
  "signature": "<detached JWS over {header, message}>",   // DCI envelope signature
  "header":  { "sender_id": "pilot-bank", ... },
  "message": {
    "transaction_id": "...",
    "search_request": [
      {
        "reference_id": "req-1",
        "search_criteria": {
          "reg_type": "Farmer",
          "reg_record_type": "spdci-extensions-dci:Farmer",
          "query_type": "predicate", "query": { ... },
          "authorize": {
            "@context": "...", "@type": "...",
            // the CM consent object, a self-contained compact JWS.
            // payload claims: jti, subject_id, aud, data_controller,
            //   purpose, data_scopes, validity, issued_at
            // protected header: alg + kid
            "consent_jws": "eyJhbGciOiJFZERTQS{...}.eyJqdGkiOiJ7...}.{signature}"
          }
        }
      }
    ]
  }
}
```

The registry forwards `consent_jws` **verbatim** to CM `/validate` (as
`{ "consent_jws": "...", "partner_id": "<sender_id>" }`). The JWS is self-contained — its
signed bytes travel in the payload segment — so no reshaping or byte-preservation care is
needed. CM recovers the claims from the payload and keys the partner off the `aud` claim;
`partner_id` is sent for traceability only.

## Field-level enforcement (the clamp)

CM `/validate` returns a decision with `effective_data_scopes` = consent scope ∩ partner
policy. The registry **clamps every returned record to those scopes** — a strict
allow-list over the rendered record's top-level fields. A narrower consent or policy can
only ever *remove* fields, never add them.

Scope names are the registry's **outgoing-template output field names**. Deployers must
keep a shared **scope ↔ field catalog** so a policy's `data_scopes` line up with what the
registry can return (e.g. `first_name`, `birth_date`, and farmer-extension fields like
`crop`, `livestock`). Fields the partner may *filter* on are separately bounded by
`dci_expression_allowed_fields`.

## Two kill-switches (testing)

Two **independent** flags gate the two checks. Both default **on** in code (safe PII
posture); the Farmer Registry chart ships them **off** so a fresh install works before
CM/PM are wired. Turn both **on** for production.

| Config (env) | Off behaviour |
| --- | --- |
| `signature_validation_enabled` | skip DCI envelope verification — accept any/unsigned caller |
| `consent_enforcement_enabled` | skip CM `/validate` — return **all** fields (no clamp) |

When a switch is off the bypass is logged (`WARNING`) and **stamped into the response
header meta** (`signature_validation` / `consent_enforcement` = `enabled`/`disabled`), and
the response `signature` carries a `signature_validation_disabled` marker — so a bypassed
response is never mistaken for an authorised one. Enforcement is otherwise **fail-closed**:
a missing consent object, a non-permit decision, or an unreachable CM rejects the request.

## Configuration (registry partner-api)

| Env var | Meaning |
| --- | --- |
| `REGISTRY_PARTNER_API_CRYPTO_BACKEND` | `partner-mgmt` (default) / `keymanager` / `local` |
| `REGISTRY_PARTNER_API_PARTNER_MGMT_API_URL` | PM partner-api (source of partner keys) |
| `REGISTRY_PARTNER_API_CONSENT_MANAGER_URL` | CM partner-api base URL (the `/validate` PDP) |
| `REGISTRY_PARTNER_API_SIGNATURE_VALIDATION_ENABLED` | gate the envelope signature check |
| `REGISTRY_PARTNER_API_CONSENT_ENFORCEMENT_ENABLED` | gate consent enforcement + field clamp |

In the Farmer Registry Helm chart these map to `global.registryCryptoBackend`,
`global.partnerManagementApiUrl`, `global.consentManagerUrl`,
`global.partnerSignatureValidationEnabled`, and `global.consentEnforcementEnabled`.

## Request flow

1. Partner signs the consent object as a compact JWS (its key, PM-registered) and embeds
   it at `search_criteria.authorize.consent_jws`.
2. Partner signs the whole DCI envelope (same key) and calls the registry partner-api.
3. Registry verifies the envelope signature via PM keys (if `signature_validation_enabled`).
4. Registry POSTs each item's `consent_object` to CM `/validate` (if
   `consent_enforcement_enabled`); CM verifies, evaluates policy, returns
   `effective_data_scopes`.
5. Registry fetches records and **clamps** each to the effective scopes.
6. Registry returns the DCI response, signed and stamped with the enforcement posture.

> **Note — farmer consent is never a government approval.** The AWE approval workflow
> gates only partner onboarding and policy widening (see
> [Approval Workflow integration](approval-workflow-integration.md)); it is never in the
> path of a beneficiary's data-share consent or of `/validate`.
