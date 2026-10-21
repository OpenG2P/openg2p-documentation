# Registry integration (the PEP side)

This page describes how an OpenG2P **Registry** (e.g. the Farmer Registry) integrates
with the Consent Manager (CM) to govern outbound data sharing. The registry is the
**Policy Enforcement Point (PEP)**; CM is the **Policy Decision Point (PDP)**. The
registry never interprets consent — it passes the partner's consent (or, with none, the
person searched) to CM, and enforces the decision CM returns.

The concrete integration lives in the **registry partner-api** (the DCI search API,
`POST /dci/registry/sync/search`).

## Two independent signatures, one key source

A partner call carries up to **two** signatures, both verified against the partner's public
keys **served by Partner Management (PM)** — a single trust root:

| Signature | Covers | Verified by | Purpose |
| --- | --- | --- | --- |
| **DCI envelope signature** | the whole `{header, message}` (detached JWS) | the **registry** | transport auth — "this call is fresh and from partner X" |
| **Consent object signature** (only a partner-signed consent) | the CM consent object (a compact JWS) | the **Consent Manager** | authorisation — "partner X holds valid consent for subject S, scope Z"; accepted only if X's policy allows partner-signed consents |

Both are **JWS** verified against PM keys via the shared `CryptoHelper.verify_jwt` — one signature format, one verify path across the platform.

The registry verifies the envelope with openg2p-fastapi-common's `build_crypto_helper`
using the **`partner-mgmt`** backend (partner keys fetched from PM). The legacy Mosip
**Keymanager** remains a selectable backend (`crypto_backend: keymanager`) but is not
the default — we are not encrypting payloads yet. Partner keys are looked up under the
platform-standard reference **`PARTNER_<sender_id>`** (upper-cased, `-`→`_`), the same
convention used by Partner Management, g2p-bridge, and openg2p-fastapi-partner-auth.

## Where the consent object is embedded

A partner whose consents the CM holds (collected through the CM) sends **no** consent: the
registry asks the CM to find it ([below](#no-consent-in-the-search)). A partner that signs its
own consents embeds them in the DCI search criteria's `authorize` block (the DCI-standard slot for
the authorisation artefact), as a **compact JWS string** at:

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
one grant each; CM uses only this registry's grant and the partner's policy for this registry.
It is also the `data_controller` of partners' scope policies for this registry in Partner Management. If the value
is empty the field is not sent, which works only for single-registry consents.

{% hint style="warning" %}
**Changing the value.** A single-registry consent (`data_controller` + `data_scopes`) whose
`data_controller` differs from this registry's value is denied `controller_not_granted`, and a
scope policy in Partner Management under another data controller is never found. Keep
`global.consentDataController` equal to the data controller of partners' consents and scope
policies.
{% endhint %}

### No consent in the search

When a search item carries no `consent_jws` and is an **`idtype-value`** search (one person by
`id_type` and `id_value`), the registry asks the CM to look the consent up
([consent by lookup](verification-and-enforcement.md#consent-by-lookup-at-a-registry)):
`{ "partner_id": "<sender_id>", "data_controller": "<this registry>", "request_context": {
"subject_id": {type, value} } }`, with the identifier searched. The CM picks the partner's
active consent for that subject (its main subject or one of its other identifiers, e.g. `FARMER_ID`)
with a grant for this registry, or denies `consent_not_found`. Any other search without a consent
(e.g. a predicate) is refused (`missing_consent`): it names no one person to look a consent up for.

Types are matched as spelled, so the registry maps its DCI identifier type names to the consent's
in `global.consentSubjectIdTypes` (env `REGISTRY_PARTNER_API_CONSENT_SUBJECT_ID_TYPES`, JSON),
e.g. `{"UIN": "FAYDA_FAN"}`; a type not listed is sent as is.

### Calling on a partner's behalf

A composite service or aggregator that fans one partner request
out to several registries presents the partner's consent to an Exchange CM, which issues one signed
consent token per registry ([Exchange consent tokens](exchange-receipts.md)). It sends each registry
only its own consent token, at the same place as a partner's consent, signs each DCI envelope with
its **own** key, and names the partner in `header.meta.on_behalf_of`. Each registry validates its
consent token at its own CM; the registry logs `on_behalf_of` alongside `sender_id`.

## Field-level enforcement

CM `/validate` returns a decision with `effective_data_scopes` = this registry's grant ∩ the
partner's policy for this registry. The registry **filters every record to those scopes' fields
before rendering it** (DCI or any other output). A narrower consent or policy can only ever
*remove* fields, never add them.

Scopes are the registry's **data scope IDs**, `<controller>.<name>` (e.g.
`farmer-registry.land`): named groups of the registry's own fields, by default one per register
section, versioned, and published at `POST /partner/data_scopes` (a signed partner call) and,
unless turned off, an unsigned `GET /partner/data_scopes`. The registry resolves each scope
to its fields as of the consent's issue time (a field added later never reaches an older
consent). See [Data Scopes](../../products/registry/registry/design/data-scopes.md). Fields the
partner may *filter* on are separately bounded by `dci_expression_allowed_fields`.

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
`SEARCH_CRITERIA_INVALID`), as a non-permit decision does. For an `idtype-value` search the
registry also sends the identifier searched as `request_context.subject_id`, so the CM checks it
against the consent's subject and identifiers of that type (`subject_mismatch`) or uses it for a
lookup; the cross-identifier check needs the registry's own data, so it is done here.

## Data-scope catalogue — ownership

The catalogue is owned by the data source (the registry), **not** the Consent Manager. CM is a
generic PDP: it only does set math on opaque scope strings
(`consent.data_scopes ⊆ policy.allowed_data_scopes`; `effective = consent ∩ policy`). A registry
adding, renaming or regrouping fields never needs a CM change.

| Concern | Owner | Form |
| --- | --- | --- |
| Scope vocabulary and scope → field mapping | **Registry (PEP)** | the data scope catalogue: default section scopes plus the extension's `meta_data/data-scopes/*.json`, versioned in the registry database |
| Publishing the catalogue (discovery) | **Registry (PEP)** | `POST /partner/data_scopes` (partners, signed), `GET /partner/data_scopes` (unsigned, on by default in the chart; Partner Management reads it), `GET /data_scopes` (staff API) |
| Set-math authorization (`⊆`, `∩`) | **Consent Manager** | opaque strings — no catalogue |
| Knowing which scopes to request / grant | **Partner + Partner Management staff** (who set the partner's policy) | read the registry's published catalogue |

The only shared contract is the scope IDs: partner policies (in Partner Management) and consents
use the registry's IDs as they are, and no catalogue is hardcoded elsewhere. Design and rules: [Data Scopes](../../products/registry/registry/design/data-scopes.md).

## Two kill-switches (testing)

Two **independent** flags gate the two checks. Both default **on** in code (safe PII
posture); the Farmer Registry chart ships them **off** so a fresh install works before
CM/PM are wired. Turn both **on** for production.

| Config (env) | Off behaviour |
| --- | --- |
| `signature_validation_enabled` | skip DCI envelope verification — accept any/unsigned caller |
| `consent_enforcement_enabled` | skip CM `/validate` — return **all** fields (no filtering) |

When a switch is off the bypass is logged (`WARNING`) and **stamped into the response
header meta** (`signature_validation` / `consent_enforcement` = `enabled`/`disabled`), and
the response `signature` carries a `signature_validation_disabled` marker — so a bypassed
response is never mistaken for an authorised one. Enforcement is otherwise **fail-closed**:
a search with no consent that the CM cannot look up, a non-permit decision, or an unreachable CM
rejects the request.

## Configuration (registry partner-api)

| Env var | Meaning |
| --- | --- |
| `REGISTRY_PARTNER_API_CRYPTO_BACKEND` | `partner-mgmt` (default) / `keymanager` / `local` |
| `REGISTRY_PARTNER_API_PARTNER_MGMT_API_URL` | PM partner-api (source of partner keys) |
| `REGISTRY_PARTNER_API_CONSENT_MANAGER_URL` | CM partner-api base URL (the `/validate` PDP) |
| `REGISTRY_PARTNER_API_CONSENT_DATA_CONTROLLER` | This registry's controller ID in CM, sent as `data_controller` on every `/validate` |
| `REGISTRY_PARTNER_API_CONSENT_SUBJECT_ID_TYPES` | JSON map from a search's identifier type to the consent's subject ID type, e.g. `{"UIN": "FAYDA_FAN"}` |
| `REGISTRY_PARTNER_API_SIGNATURE_VALIDATION_ENABLED` | gate the envelope signature check |
| `REGISTRY_PARTNER_API_CONSENT_ENFORCEMENT_ENABLED` | gate consent enforcement + field filtering |

In the Farmer Registry Helm chart these map to `global.registryCryptoBackend`,
`global.partnerManagementApiUrl`, `global.consentManagerUrl`, `global.consentDataController`
(default: `global.registryVariant`), `global.consentSubjectIdTypes`, `global.partnerSignatureValidationEnabled`, and
`global.consentEnforcementEnabled`.

## Request flow

1. A partner that signs its own consents embeds the consent object (a compact JWS, its
   PM-registered key) at `search_criteria.authorize.consent_jws`; a partner whose consents the CM
   holds sends none and searches the person by identifier (`idtype-value`).
2. Partner signs the whole DCI envelope (same key) and calls the registry partner-api.
3. Registry verifies the envelope signature via PM keys (if `signature_validation_enabled`).
4. Registry POSTs each item's `consent_jws` (or, with none, the searched subject for a
   consent by lookup) with its own `data_controller` to CM `/validate` (if
   `consent_enforcement_enabled`); CM finds or verifies the consent, selects this registry's grant,
   applies the partner's policy for this registry (from Partner Management), and returns `effective_data_scopes` and the
   consent's `subject_id`.
5. Registry fetches records, checks they belong to the consent's subject, and **filters** each to
   the effective scopes' fields before rendering it.
6. Registry returns the DCI response, signed and stamped with the enforcement posture.

> **Note — farmer consent is never a government approval.** Staff approval in Partner Management
> covers only partner onboarding, keys and access policies (see
> [Partner Management integration](partner-management-integration.md)); it is never in the
> path of a beneficiary's data-share consent or of `/validate`.
