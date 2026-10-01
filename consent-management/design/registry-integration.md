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
  "header":  { "sender_id": "pilot-bank", "meta": { "on_behalf_of": "..." }, ... },  // on_behalf_of: optional
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
            // payload claims: jti, subject_id, aud, purpose, validity,
            //   issued_at, and grants [{data_controller, data_scopes}]
            //   (or the single-registry data_controller + data_scopes)
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
`{ "consent_jws": "...", "partner_id": "<sender_id>", "data_controller": "<this registry>" }`).
The JWS is self-contained — its signed bytes travel in the payload segment — so no reshaping or
byte-preservation care is needed. CM recovers the claims from the payload and keys the partner off
the `aud` claim plus `data_controller`; `partner_id` is sent for traceability only.

**`data_controller` is this registry's controller ID in CM** (config
`consent_data_controller`; in the chart `global.consentDataController`, defaulting to the registry
variant, e.g. `farmer-registry`, `crop-sown-registry`). A consent can cover several registries with
one grant each; CM uses only this registry's grant and this registry's binding policy. If the value
is empty the field is not sent, which works only for single-registry consents.

{% hint style="warning" %}
**Upgrading.** Because the chart now sends `data_controller` by default, a single-registry consent
(`data_controller` + `data_scopes`) whose `data_controller` differs from this registry's value is
denied `controller_not_granted`. Set `global.consentDataController` to the controller ID your
partners are already bound to (and sign their consents with) in CM.
{% endhint %}

**Calling on a partner's behalf.** A composite service or aggregator that fans one partner request
out to several registries forwards the partner's consent **unchanged** to each, signs each DCI
envelope with its **own** key, and names the partner in `header.meta.on_behalf_of`. Each registry
validates its own grant; the registry logs `on_behalf_of` alongside `sender_id`.

## Field-level enforcement (the clamp)

CM `/validate` returns a decision with `effective_data_scopes` = this registry's grant ∩ the
partner's policy for this registry. The registry **clamps every returned record to those scopes** — a strict
allow-list over the rendered record's top-level fields. A narrower consent or policy can
only ever *remove* fields, never add them.

Scope names are the registry's **outgoing-template output field names**. Deployers must
keep a shared **scope ↔ field catalog** so a policy's `data_scopes` line up with what the
registry can return (e.g. `first_name`, `birth_date`, and farmer-extension fields like
`crop`, `livestock`). Fields the partner may *filter* on are separately bounded by
`dci_expression_allowed_fields`.

## Subject enforcement

After a permit, the registry checks that the consent's subject — `subject_id` in CM's decision —
is the person actually searched. A permit that names no subject is rejected.

* **Entity registers** (e.g. Farmer Registry): every returned record's `foundational_id` or
  `functional_record_id` must equal the consent's subject.
* **Activity registers** (e.g. Crop Sown Registry): the searched subject must equal the consent's
  subject, or be linked to it by the register's own data through its `subject_id_fields` (e.g. a
  crop record holding the farmer ID and the farmer's Fayda FAN in `fayda_fan`). All raw activity
  results must belong to the searched subject.

A mismatch fails the whole request (fail-closed, an error response with
`SEARCH_CRITERIA_INVALID`), as a non-permit decision does. The registry does not send
`request_context.subject_id` to CM; the cross-identifier check needs the registry's own data, so it
is done here.

## Data-scope catalog — design (NOT yet implemented) — handover note

> **Status:** design agreed, implementation deferred. This section is the handover
> note for whoever implements the scope catalog later. Nothing here is built yet;
> today `data_scopes` are opaque strings and the clamp is structural only.

**The decision: the catalog is owned by the data source (the registry), NOT the
Consent Manager.** CM is a generic PDP — it only does set math on opaque scope
strings (`consent.data_scopes ⊆ policy.allowed_data_scopes`;
`effective = consent ∩ policy`). It never needs to know what a scope maps to. So a
registry adding/renaming a field must **never** require a CM code change or release.
Baking a per-registry field taxonomy into CM would be wrong — it's data, and it
belongs to the source that owns the schema and changes it.

**Ownership split:**

| Concern | Owner | Form |
| --- | --- | --- |
| Field taxonomy / scope vocabulary | **Registry (PEP)** | data/config, changes with the registry schema — no CM release |
| Scope → field mapping (for the clamp) | **Registry (PEP)** | data/config (a config table, or derived from the DCI outgoing template already in MinIO) |
| Publishing the scope catalog (discovery) | **Registry (PEP)** | a discovery endpoint / documented list |
| Set-math authorization (`⊆`, `∩`) | **Consent Manager** | opaque strings — unchanged, no catalog |
| Knowing which scopes to request/grant | **Partner + CM policy admin** | read the registry's published catalog |

**The only shared contract is the scope-name vocabulary** — CM policies and the
registry's mapping must use the same strings. That is a naming convention, not a code
dependency. The registry **publishes** its catalog so partners and policy admins know
the vocabulary; CM's admin UI *may* fetch it dynamically to populate a scope picker,
but must never hardcode it.

**Recommended model — scopes ARE the registry's published field/bundle names.** Then
the "mapping" is identity and the clamp already written (`record.keys() ⊆ scopes`)
needs no mapping table. Adding a farmer field = a registry data/config change, zero CM
impact.

**To implement (registry side, later):**
- Define the scope → field mapping as **config/data** in the registry
  (registry-platform / farmer-extension) — or make scope = field name (identity).
- Add a small **discovery endpoint** publishing the scope catalog (alongside the DCI
  capabilities).
- Extend `dci_expression_allowed_fields` with the farmer-extension fields.
- The existing `_clamp_record_fields` stays; it reads the mapping instead of guessing.
- **CM: no structural change** (optionally, the admin UI fetches the registry catalog).
- Document the scope naming convention in GitBook as the shared contract.

**Open decision (registry-side, pick when implementing):** scope **granularity** —
field-level (`first_name`, `crops`; scope = field name, no mapping table) vs coarse
**bundles** (`farmer_profile.basic`; needs a bundle→fields mapping, still registry-owned).
Lean: **field-level to start**, add bundles later if raw field lists prove tedious for
partners.

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
| `REGISTRY_PARTNER_API_CONSENT_DATA_CONTROLLER` | This registry's controller ID in CM, sent as `data_controller` on every `/validate` |
| `REGISTRY_PARTNER_API_SIGNATURE_VALIDATION_ENABLED` | gate the envelope signature check |
| `REGISTRY_PARTNER_API_CONSENT_ENFORCEMENT_ENABLED` | gate consent enforcement + field clamp |

In the Farmer Registry Helm chart these map to `global.registryCryptoBackend`,
`global.partnerManagementApiUrl`, `global.consentManagerUrl`, `global.consentDataController`
(default: `global.registryVariant`), `global.partnerSignatureValidationEnabled`, and
`global.consentEnforcementEnabled`.

## Request flow

1. Partner signs the consent object as a compact JWS (its key, PM-registered) and embeds
   it at `search_criteria.authorize.consent_jws`.
2. Partner signs the whole DCI envelope (same key) and calls the registry partner-api.
3. Registry verifies the envelope signature via PM keys (if `signature_validation_enabled`).
4. Registry POSTs each item's `consent_jws` with its own `data_controller` to CM
   `/validate` (if `consent_enforcement_enabled`); CM selects this registry's grant, verifies,
   evaluates this registry's binding policy, and returns `effective_data_scopes` and the
   consent's `subject_id`.
5. Registry fetches records, checks they belong to the consent's subject, and **clamps** each to
   the effective scopes.
6. Registry returns the DCI response, signed and stamped with the enforcement posture.

> **Note — farmer consent is never a government approval.** The AWE approval workflow
> gates only partner onboarding and policy widening (see
> [Approval Workflow integration](approval-workflow-integration.md)); it is never in the
> path of a beneficiary's data-share consent or of `/validate`.
