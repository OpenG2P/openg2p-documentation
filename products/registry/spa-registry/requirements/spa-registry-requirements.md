---
description: >-
  Requirements and design for the SPA Registry (Social Payment Accounts
  Registry): a registry built on the OpenG2P registry-platform that stores the
  financial addresses of beneficiaries, validates them by penny-drop payment
  (through G2P Bridge) or by account lookup, and serves them to partners.
---

# SPA Registry Requirements

## 01. Introduction

### 1.1 Purpose

The **SPA Registry** (Social Payment Accounts Registry, repository `spa_registry`) stores, for each beneficiary, one or more **financial addresses** (bank accounts, mobile wallets, UPI addresses). It replaces the SPAR mapper service. SPAR kept one ID-to-FA mapping as flat strings built by "strategies" (a format string to construct and a regex to deconstruct). The SPA Registry keeps structured, validated, versioned records instead.

It is built on the **registry-platform**, so these come from the platform and are not rebuilt:

* change requests and the approval workflow (AWE),
* version history,
* the Partner API and DCI search,
* the metadata-driven staff UI,
* consent-aware data sharing.

The SPA Registry adds only its models, schemas, domain services, handlers, auxiliary tables, jobs and UI configuration.

### 1.2 Scope

In scope:

* domain models and schemas for beneficiaries and financial addresses,
* two auxiliary tables (financial address types and financial service providers),
* use of Master Data Service for bank and branch directories,
* domain service logic and per-type handlers,
* validation of financial addresses by penny drop or by lookup, and the integration of penny drop with G2P Bridge,
* the Bridge changes needed to support penny-drop payments,
* the staff UI configuration and the new UI widgets,
* Celery jobs and workers,
* the Partner API (DCI) search that returns financial addresses.

Out of scope for this document:

* the beneficiary portal (only the capabilities it needs from this service are noted),
* migration of existing SPAR data.

### 1.3 Context

| Component | Role |
|---|---|
| registry-platform | Base models (`G2PRegister`, history twins, intake forms), domain service hooks, change requests, AWE, Partner API, staff UI |
| `spa_registry` (this repo) | Extension package selected through `REGISTRY_EXTENSION_MODULE` |
| Master Data Service (MDS) | Versioned reference lists, here the bank and branch directory |
| G2P Bridge | Sends penny-drop payments from a sponsor account and reconciles the sponsor bank statements |
| Sponsor bank | Holds the dedicated Account-Validation account |
| Lookup connectors | Adapters that ask a bank, wallet operator or UPI network whether an address exists and who holds it (6.6) |

### 1.4 Key design decisions

| # | Decision |
|---|---|
| D1 | Two registry tables: `g2p_register_beneficiary` (type `REGISTER`) and `g2p_register_financial_address` (type `TABLE`, child of the beneficiary). One beneficiary has one or more financial addresses. |
| D2 | Two auxiliary tables: `financial_address_types` and `financial_service_providers`. They are configuration, not registers: no change requests and no version history. |
| D3 | The shape of a financial address is a single column, `financial_address_type`, whose value is a row in `financial_address_types`. That row names the handler class and the validation method. |
| D4 | The provider is a single column, `provider_code`, whose value is a row in `financial_service_providers`. Provider codes are globally unique. |
| D5 | There are no database foreign keys on `financial_address_type`, `provider_code` or the parent link. These references are validated programmatically by the domain service. |
| D6 | The identifier (`financial_address_identifier`) is encrypted at rest when the environment flag `financial_address_encryption_at_rest` is TRUE. A keyed, type-independent hash supports exact-match search. |
| D7 | Addresses are ranked by `priority` (1 is highest). Addresses are never deleted; they are made inactive through `record_status`. |
| D8 | No auto-approval of changes on any channel. |
| D9 | Each address type has a `validation_method`: `PENNY_DROP`, `LOOKUP` or `NONE`. Penny drops are paid by G2P Bridge. Lookups are made through lookup connectors. In both cases the SPA Registry decides the validation status. |
| D10 | Validation status, next validation date, last validated time and name-match flag on the address are system-maintained and are **not versioned** (no version-history rows). |
| D11 | Bridge gets a new `envelope_type` (`DISBURSEMENT` or `ACCOUNT_VALIDATION`). Penny-drop envelopes carry the account in the request and use a dedicated sponsor account configured in Bridge, with no PBMS dependency. |
| D12 | One Bridge envelope per run of the penny-drop job (a batch), with one disbursement per attempt. |
| D13 | Staff API and Partner API return the unmasked identifier. |
| D14 | Every Celery job is a beat and a worker. The beat selects and claims work; the worker does the work. |
| D15 | Handler logic lives in a handler package separate from the domain service, so the UI, the Partner API and bulk import can use it without going through change requests. |

### 1.5 Terminology

| Term | Meaning |
|---|---|
| FA | Financial address: one bank account, wallet or UPI address of a beneficiary |
| Financial address type | A row in `financial_address_types`, such as `IFSC-BANK-ACCOUNT` |
| Handler | A class that normalizes, validates and masks identifiers for a financial address type |
| Provider | A bank, wallet operator or UPI handle in `financial_service_providers` |
| Penny drop | A very small payment to an account to test that it exists and accepts credits |
| Lookup | A query to a bank, operator or network that confirms an address exists and returns the holder's name |
| Run | One execution of the penny-drop dispatch step, mapped to one Bridge envelope |
| Sponsor account | The bank account Bridge pays from. A dedicated one is used for Account-Validation |
| MDS | Master Data Service |

### 1.6 Decisions on earlier open items, and what remains open

Decisions:

| # | Item | Decision | Where reflected |
|---|---|---|---|
| O1 | Version history for validation status | **None.** The status columns are not part of the history twin, and system updates write no history rows. | 2.3, 6.2 |
| O2 | Identifier masking | For now the Staff API and the Partner API return the **unmasked** identifier. Encryption at rest is controlled by the environment flag `financial_address_encryption_at_rest` (TRUE or FALSE). | 2.5, 5.3, 5.5, 12.6 |
| O3 | Lookup-based validation | A separate queue, `account_lookup_queue`, populated by the validation worker and picked up by `account_lookup_beat` and `account_lookup_worker`. | 6.6, 10 |
| O4 | Name mismatch policy | **Flag only.** A mismatch never changes the status. | 6.5.5, 6.6.4 |
| O5 | Whether the validation hook can change the data | Explained in 5.1. **It cannot.** Normalization, provider derivation, hashing and encryption happen in a persistence hook instead. | 5.1, 5.3 |

Still open:

| # | Open item |
|---|---|
| O6 | Bridge behaviours checked in 8.4. What remains is the sponsor bank's own behaviour (charges, funds block, how rejections appear) and two Bridge changes the check showed to be needed (8.4, items 10 and 11). |
| O7 | Where the lookup connectors run and which lookup APIs are available for each address type (UPI, wallet operators, banks). Not yet known. The connector interface is defined (6.6.3); implementations are per deployment. |
| O8 | Pending change requests and intake forms hold the identifier as submitted (unencrypted) until approval, because the validation hook cannot change the payload (5.1). Whether to encrypt change-request payloads needs a platform change. |
| O9 | Masking for the beneficiary portal and for other channels (decision 2 covers the Staff and Partner APIs only). |

---

## 02. Domain Models and Schemas

All models extend the registry-platform base classes. Each register model has a **history twin** (extending `G2PRegisterHistory`) and, if self-service intake is used, an **intake-form twin** (extending `G2PIntakeForm`), as the reference extension does for households. Columns shared with the history twin sit in a mixin class. Columns that must not be versioned (2.3) sit only on the main model.

### 2.1 Register definitions (seed)

| register_id | register_mnemonic | register_subject | register_purpose | master_register_id | functional_id_generation_required |
|---|---|---|---|---|---|
| a0000000-0000-4000-8000-000000000101 | Beneficiary | Beneficiaries | REGISTER | NULL | TRUE |
| b0000000-0000-4000-8000-000000000102 | FinancialAddress | Financial Addresses | TABLE | a0000000-0000-4000-8000-000000000101 | FALSE |

The mnemonics must match the domain service class names (section 5). The table names follow the requested singular form. The reference extension uses plural names (`g2p_register_households`); decide once and apply to all tables and twins.

### 2.2 `g2p_register_beneficiary`

Extends `G2PRegister`. Inherited columns that SPA Registry relies on:

| Column | Use here |
|---|---|
| `internal_record_id` | Primary key (UUID string) |
| `functional_record_id` | Unique ID assigned by this registry |
| `record_name` | Beneficiary name, built by the domain service (5.2) |
| `record_status` | `ACTIVE`, `INACTIVE`, `ARCHIVED` |
| `search_text` | Trigram-indexed text, populated by the domain service |

The inherited `link_foundational_id` (a link to a foundational ID of another record) is not used by this register.

Added columns:

| Column | Type | Notes |
|---|---|---|
| `first_name` | string | |
| `last_name` | string | |
| `foundational_id` | string, indexed | The beneficiary's foundational (national) ID. Uniqueness among beneficiaries is enforced by the domain service. |
| `alternate_ids` | JSONB, GIN index | Other IDs that resolve to this beneficiary: `[{"type": "PROGRAM_ID", "value": "..."}]` |

There is no `primary_id_type`. If the number of alternate IDs or lookups grows, move them to a separate table. The requirement here is limited to two registry tables, so JSONB is used.

### 2.3 `g2p_register_financial_address`

Extends `G2PRegister`. `link_internal_record_id` (inherited) holds the beneficiary's `internal_record_id`. There are no foreign keys: the parent link, the financial address type and the provider are validated programmatically (5.3).

Columns shared with the history twin (versioned):

| Column | Type | Notes |
|---|---|---|
| `financial_address_type` | string, indexed | Code of a row in `financial_address_types`; selects the handler |
| `financial_address_identifier` | string | Normalized value. **Encrypted at rest** when `financial_address_encryption_at_rest` is TRUE (2.5). |
| `financial_address_identifier_hash` | string, indexed | HMAC of the normalized identifier (2.6). Always computed, whatever the encryption flag. |
| `hash_key_version` | integer | Which key produced the hash |
| `provider_code` | string, nullable, indexed | Code of a row in `financial_service_providers`; required or derived according to the type |
| `details` | JSONB | Type-specific values, such as `{"ifsc": "HDFC0001234"}`, validated against the type's `details_schema` |
| `financial_address_name` | string, nullable | Name of the account holder as known to the registry, used for name matching |
| `currency` | string(3), nullable | ISO 4217 |
| `priority` | integer, nullable | 1 is highest. NULL when the record is inactive. |

Columns on the main model only (**not versioned**: not in the history twin, and updated by system jobs without writing history):

| Column | Type | Notes |
|---|---|---|
| `account_validation_status` | string | `NOT_APPLICABLE`, `UNVERIFIED`, `PENDING`, `VERIFIED`, `REJECTED`, `FAILED` |
| `account_validation_next_date` | date, nullable | When the next validation is due |
| `account_validation_last_validated_at` | timestamp, nullable | When the last successful validation completed |
| `account_validation_name_match` | string, nullable | `MATCH`, `MISMATCH`, `UNKNOWN`. Informational flag only (6.5.5, 6.6.4). |

The validation method that applies (`PENNY_DROP`, `LOOKUP` or `NONE`) is taken from the address type, so `account_validation_status` has the same meaning whichever method is used.

Inherited `record_status` is the **active flag**. The UI toggle sets it to `ACTIVE` or `INACTIVE`. No separate boolean is added.

Constraints and indexes:

* Unique `(link_internal_record_id, priority)`, declared `DEFERRABLE INITIALLY DEFERRED`. Deactivating a record sets `priority` to NULL, so it frees its slot (NULLs do not collide). Deferral lets one change request swap two priorities.
* Index on `financial_address_identifier_hash`.
* Index on `provider_code` and on `financial_address_type`.
* No foreign keys.

`get_search_text_fields` returns only masked values (for example `+91******3210`) and the type, never the plaintext identifier.

### 2.4 Pydantic schemas

| Schema | Purpose |
|---|---|
| `BeneficiarySchema` | `first_name`, `last_name`, `foundational_id`, `alternate_ids`, plus inherited register fields |
| `AlternateId` | `type`, `value` |
| `FinancialAddressInput` | `financial_address_type`, `financial_address_identifier`, `provider_code?`, `details?`, `financial_address_name?`, `currency?`, `priority` |
| `FinancialAddressOutput` | Input fields plus `record_status`, `account_validation_status`, `account_validation_next_date`, `account_validation_last_validated_at`, `account_validation_name_match`. The identifier is unmasked for the Staff API and Partner API (D13). |
| `FinancialAddressValidateRequest` / `Response` | Live validation by the UI: normalized value, derived provider, errors |
| `AccountValidationResult` | Facts used by the validation jobs: for penny drop, the Bridge facts; for lookup, the connector result (section 6) |
| `LookupResult` | `status` (`FOUND`, `NOT_FOUND`, `ERROR`), `name?`, `raw?` (6.6.3) |

### 2.5 Encryption at rest

The environment flag **`financial_address_encryption_at_rest`** (TRUE or FALSE) controls whether `financial_address_identifier` is encrypted when stored.

* TRUE: the persistence hook (5.3) stores `enc:v1:` followed by the ciphertext (authenticated encryption, key from the secrets manager).
* FALSE: the persistence hook stores the normalized value as is.
* Reads detect the `enc:v1:` prefix and decrypt only when it is present. Rows written under either setting can therefore coexist, and changing the flag does not break reads.
* Changing the flag affects records written afterwards. The `identifier_rekey_beat` and `identifier_rekey_worker` jobs (10.3) bring existing rows in line with the flag.
* The hash is computed in both modes, so search works the same way.
* The Staff API and Partner API return the decrypted value (D13).

This covers the registry table and its history rows. It does not cover change-request payloads awaiting approval (O8).

### 2.6 Identifier hash

```
financial_address_identifier_hash = HMAC-SHA256(hash_key[hash_key_version], normalized_identifier)
```

* The input is the normalized identifier only, **not** the type code. Two types that share an identifier, such as `MSISDN-WALLET` and `MSISDN-BANK-ACCOUNT`, then hash to the same value.
* The key is held outside the database (secrets manager or KMS) and is separate from the encryption key.
* A search by value normalizes the input under each active financial address type's handler and matches any of the resulting hashes, and under every active key version during a key rotation.
* Exact match only. There is no partial search on identifiers.

### 2.7 Sample records

`g2p_register_beneficiary` (internal ids shortened):

| internal_record_id | functional_record_id | first_name | last_name | foundational_id | record_name | alternate_ids | record_status |
|---|---|---|---|---|---|---|---|
| bn-001 | SPA-0000001 | Ramesh | Kumar | 4567891230 | Ramesh Kumar | `[{"type":"PROGRAM_ID","value":"PMKISAN-77812"}]` | ACTIVE |
| bn-002 | SPA-0000002 | Lakshmi | Devi | 7788991122 | Lakshmi Devi | `[]` | ACTIVE |
| bn-003 | SPA-0000003 | Amina | Khan | NULL | Amina Khan | `[]` | ACTIVE |

`g2p_register_financial_address` (the identifier is shown unencrypted for reading; with the flag TRUE it is stored as `enc:v1:...`):

| internal_record_id | link_internal_record_id | financial_address_type | financial_address_identifier | provider_code | details | financial_address_name | currency | priority | record_status | account_validation_status |
|---|---|---|---|---|---|---|---|---|---|---|
| fa-001 | bn-001 | IFSC-BANK-ACCOUNT | 50100123456789 | HDFC | `{"ifsc":"HDFC0001234"}` | Ramesh Kumar | INR | 1 | ACTIVE | VERIFIED |
| fa-002 | bn-001 | UPI-VPA-BANK-ACCOUNT | ramesh@okicici | okicici (derived) | – | Ramesh Kumar | INR | 2 | ACTIVE | VERIFIED |
| fa-003 | bn-002 | MSISDN-WALLET | +919876543210 | PAYTM-WALLET | – | Lakshmi Devi | INR | 1 | ACTIVE | VERIFIED |
| fa-004 | bn-002 | MSISDN-WALLET | +919876543210 | AIRTEL-WALLET | – | Lakshmi Devi | INR | 2 | ACTIVE | UNVERIFIED |
| fa-005 | bn-002 | IFSC-BANK-ACCOUNT | 31234567890 | SBIN | `{"ifsc":"SBIN0004321"}` | Lakshmi Devi | INR | 3 | ACTIVE | PENDING |
| fa-006 | bn-003 | MSISDN-BANK-ACCOUNT | +923001234567 | HABBPKKA | `{"rail":"RAAST"}` | Amina Khan | PKR | 1 | ACTIVE | UNVERIFIED |
| fa-007 | bn-003 | MSISDN-WALLET | +923001234567 | HABBPKKA | – | Amina Khan | PKR | NULL | INACTIVE | NOT_APPLICABLE |

---

## 03. Auxiliary Tables: Financial Address Types and Financial Service Providers

Both tables extend `BaseORMModel`. They are configuration, seeded by SQL like the reference extension's metadata, and loaded into memory by the domain service with cache invalidation on update.

### 3.1 `financial_address_types`

| Column | Type | Notes |
|---|---|---|
| `code` | string, PK | `<IDENTIFIER>-<PRODUCT>`, for example `MSISDN-WALLET`. This is the value stored in the address's `financial_address_type` column. |
| `description` | string | |
| `kind` | string | Product category, `BANK_ACCOUNT` or `WALLET`. It is the vocabulary that a provider's `services` uses, so the domain service can check that a provider offers the product. Many types share one kind. |
| `handler` | string, nullable | Name registered in the handler registry (5.4). NULL means the generic regex handler. |
| `validation_regex` | string, nullable | Used by the generic handler |
| `normalizer` | string, nullable | Named normalization rule for the generic handler |
| `provider_required` | boolean | FALSE when the handler derives the provider |
| `details_schema` | JSONB, nullable | JSON Schema for `details` |
| `validation_method` | string | `PENNY_DROP`, `LOOKUP` or `NONE` |
| `active` | boolean | |

Seed rows:

| code | kind | handler | provider_required | details_schema | validation_method |
|---|---|---|---|---|---|
| UPI-VPA-BANK-ACCOUNT | BANK_ACCOUNT | UpiVpaHandler | false (derived from `@handle`) | – | LOOKUP |
| MSISDN-WALLET | WALLET | MsisdnHandler | true | – | LOOKUP |
| MSISDN-BANK-ACCOUNT | BANK_ACCOUNT | MsisdnHandler | true | `rail` optional | LOOKUP |
| IFSC-BANK-ACCOUNT | BANK_ACCOUNT | IfscBankAccountHandler | true | `ifsc` required | PENNY_DROP |
| IBAN-BANK-ACCOUNT | BANK_ACCOUNT | IbanHandler | false (derived via BIC directory) | – | PENNY_DROP |
| BIC-BANK-ACCOUNT | BANK_ACCOUNT | (generic) | true | – | PENNY_DROP |

Seed only the types the deployment's country uses. The rows above show the range of cases.

Notes:

* `MSISDN-WALLET` and `MSISDN-BANK-ACCOUNT` share one handler class registered under one name.
* For `MSISDN-BANK-ACCOUNT`, the phone number is an alias to a bank account. SPA Registry cannot see the account behind it, and the user can re-point it.
* `UPI-VPA-BANK-ACCOUNT` stores only the VPA. The underlying account is not known and is not stored.
* A type whose `validation_method` is `LOOKUP` but for which no lookup connector is configured is treated as `NONE` by the validation worker (6.4), with a logged warning.

### 3.2 `financial_service_providers`

| Column | Type | Notes |
|---|---|---|
| `code` | string, PK | **Globally unique** across bank codes, UPI handles and wallet issuers |
| `name` | string | Display name |
| `group_name` | string, nullable | Brand or legal group, for example "Airtel" |
| `services` | array of string | Subset of `BANK_ACCOUNT`, `WALLET` |
| `needs_review` | boolean | TRUE when created automatically (for example an unseen UPI handle) |
| `active` | boolean | |

Seed rows:

| code | name | group_name | services |
|---|---|---|---|
| okicici | Google Pay (ICICI) | Google Pay | BANK_ACCOUNT |
| AIRTEL-WALLET | Airtel wallet | Airtel | WALLET |
| AIRP | Airtel Payments Bank | Airtel | BANK_ACCOUNT |
| PAYTM-WALLET | Paytm wallet | Paytm | WALLET |
| PYTM | Paytm Payments Bank | Paytm | BANK_ACCOUNT |
| AMAZONPAY | Amazon Pay balance | Amazon Pay | WALLET |
| HDFC | HDFC Bank | HDFC | BANK_ACCOUNT |
| SBIN | State Bank of India | SBI | BANK_ACCOUNT |
| HABBPKKA | Habib Bank Limited | HBL | BANK_ACCOUNT, WALLET |
| COBADEFF | Commerzbank | Commerzbank | BANK_ACCOUNT |

All codes above are illustrative. Verify IFSC bank prefixes, UPI handles and wallet issuer codes against the authoritative lists (NPCI, RBI) before seeding.

### 3.3 References without foreign keys

* The address's `financial_address_type` and `provider_code` have no database foreign key. The domain service checks that they exist and are active (5.3). The persistence hook repeats the check before saving.
* Because the provider scheme is not stored, codes must not collide across namespaces. A seed-time check verifies that provider codes are unique and that each matches the format expected by its handler.
* The domain service checks that the financial address type's `kind` is in the provider's `services`.
* Deactivating a type or a provider does not change existing addresses that use it. The retirement check job (10.3) flags them.

### 3.4 Providers that offer both bank accounts and wallets

A provider that offers both (for example HBL) has one row with both services. The financial address type (`MSISDN-BANK-ACCOUNT` versus `MSISDN-WALLET`) is what tells the payer which product is meant. The same number can therefore appear as two addresses with the same provider.

### 3.5 Duplicate warning

The duplicate check uses `(financial_address_identifier_hash, financial_address_type, provider_code)` among active records. It produces a **warning**, not an error, since households share phones.

---

## 04. Master Data Services: Banks and Branches

### 4.1 Purpose

For bank accounts addressed by an IFSC, MDS holds the national bank and branch directory. The staff UI and the beneficiary portal use it so that a person selects a bank and a branch and does not type the IFSC. `financial_service_providers` remains SPA Registry's own, smaller list of the providers the programme can pay.

### 4.2 List model

MDS lists are `g2p_attributes` (a list) with `g2p_attribute_values` (values), and a value can point to its parent through `parent_value_id` when the list is marked `is_hierarchical`. The directory is one hierarchical list:

| Attribute | Value |
|---|---|
| `attribute_id` | `IFSC_DIRECTORY` |
| `is_hierarchical` | true |

| value_id | value_code | value_display | parent_value_id |
|---|---|---|---|
| SBIN | SBIN | State Bank of India | – |
| SBIN0004321 | SBIN0004321 | Connaught Place, New Delhi | SBIN |
| HDFC | HDFC | HDFC Bank | – |
| HDFC0001234 | HDFC0001234 | Fort, Mumbai | HDFC |

Banks are roots. Branches are children whose code is the IFSC. MDS provides versioning, maker-checker approval, immutable published versions, and retirement of values in a later version.

### 4.3 Gaps in the current MDS API and required enhancements

The current `get_attribute_values` request takes only an optional `attribute_id` and pagination (default page size 1000). The required enhancements:

| # | Enhancement | Reason |
|---|---|---|
| E1 | Optional `parent_value_id` filter | Return the branches of one bank without paging through the entire list |
| E2 | Optional text search (`q`) over `value_display` and `value_code`, within a parent | Branch typeahead by name, city or IFSC |
| E3 | Index on `(attribute_id, parent_value_id)` and a trigram index on `value_display` | A full IFSC list has well over a hundred thousand values |
| E4 | Return only values with `ACTIVE` status unless asked otherwise | The picker must not offer retired branches |
| E5 | Confirm that one version of a list can hold the whole directory, and that the publish and the `/catalogue` reads cope with that size | Not verified |

The existing response cache is keyed per request, so the new parameters must be part of the cache key.

### 4.4 How SPA Registry uses MDS

1. **Pickers (UI and portal):** bank, then branch (E1, E2), through the widgets in section 11.
2. **IFSC validation on write:** the `IfscBankAccountHandler` checks the IFSC format, that its first four characters equal `provider_code`, and (advisory) that the IFSC exists and is active in MDS.
3. **Retirement:** a daily job (section 10) flags addresses whose IFSC has been retired in MDS.
4. **Caching:** SPA Registry keeps a cache of directory lookups. `mds_cache_refresh_beat` and `mds_cache_refresh_worker` refresh it on a fixed interval, by default every **12 hours** (`mds_cache_refresh_hours`). If MDS is unreachable, the IFSC-exists check is skipped with a logged warning. The format and bank-code checks still apply. Branch validation is advisory until failed payments show that it needs to be strict.

### 4.5 Providers and MDS

Bank codes appear in both MDS (national directory) and `financial_service_providers` (programme-supported list). The provider table is the source of truth for **what the programme can pay**. When a bank provider is added, its code is checked to exist in MDS. Names are kept in both places. Wallets and UPI handles are not in the bank directory and live only in the provider table.

---

## 05. Domain Services: Business Logic

### 5.1 Mechanics, and what the validation hook can and cannot do

The platform's `G2PRegisterDomainFactory` finds a domain service by naming convention in the module selected by `REGISTRY_EXTENSION_MODULE`. The class for a register is `G2PRegisterDomainService<Mnemonic>`. This extension provides:

* `G2PRegisterDomainServiceBeneficiary`
* `G2PRegisterDomainServiceFinancialAddress`

Both are created in the extension's `Initializer.initialize()`, and every model, history twin and intake twin is created in `migrate_database`.

Hooks inherited from `G2PRegisterDomainService` and overridden here: `construct_record_name`, `construct_search_text`, `validate_domain_attributes`, `pre_approve`, `post_approve`, `post_ingest`, `validate_intake_parent_link`.

**`validate_domain_attributes` is validation only (O5).** The platform calls it when a change request is created (and for intake forms) with `records`, a list of dictionaries made by `model_dump()` of the payload. Changes made to those dictionaries are discarded: the stored change payload is built from the original payload, not from the dictionaries the hook received. The hook can therefore reject bad data but cannot normalize it, fill in a derived provider, compute the hash, or encrypt the identifier.

Those steps happen when the record is saved, in a **persistence hook**: SQLAlchemy `before_insert` and `before_update` listeners on the financial address model. This is the same pattern the platform already uses to fill `search_text` and `record_name`. The listener calls shared code in the domain service (`prepare_for_save`, 5.3) so that validation and saving use the same handler logic.

Consequences:

* Validation works on a normalized copy of each record and reports errors.
* Between creation and approval, the change payload (and an intake form) keeps the identifier as submitted (O8).
* Anything that runs after approval (`pre_approve`, `post_approve`, the persistence hook) sees the saved, normalized and encrypted values.

### 5.2 `G2PRegisterDomainServiceBeneficiary`

```
construct_record_name(payload):
    return first_name + " " + last_name          # a missing part is omitted, no extra space

construct_search_text(payload, extra):
    parts = [functional_record_id, foundational_id, record_name]
    parts += [alt.value for alt in alternate_ids]
    return join(parts)

validate_domain_attributes(records):
    for r in records:
        if first_name or last_name is empty: error
        if neither foundational_id nor alternate_ids is present: error
        for alt in r.alternate_ids:
            if alt.type empty or alt.value empty: error
            if alt.value already belongs to another beneficiary: error
        if foundational_id belongs to another beneficiary: error     # uniqueness is enforced here

pre_approve(change_request, session):
    pass            # no extra checks beyond validation

post_approve(change_request, session):
    if beneficiary record_status became INACTIVE:
        set all child FA records INACTIVE and priority NULL     # system update; cancel open validation queue rows

post_ingest(register_id, row, session):
    pass
```

### 5.3 `G2PRegisterDomainServiceFinancialAddress`

Validation (change request creation and intake). Works on copies and never changes the data:

```
validate_domain_attributes(records):
    group records by beneficiary (link_internal_record_id)
    for r in records:
        type = address_types.get(r.financial_address_type)       # cached
        if type is None or not type.active: error UNKNOWN_FINANCIAL_ADDRESS_TYPE
        result = prepare(type, r)                                # same code as the persistence hook, on a copy
            # prepare(): handler.normalize, handler.validate, derive provider,
            #            provider checks, details schema, handler.validate_details
        errors += result.errors

    for each beneficiary group:
        resulting = existing active FAs (after this change) + incoming
        require priorities of active FAs are unique and >= 1
        inactive records must have no priority
        duplicates = same (hash, type, provider) among active FAs  -> warning, not error
```

```
prepare(type, r):                                  # shared by validation and the persistence hook
    handler = handler_for(type)
    ctx     = build_context(country, default_region, providers)

    ident = handler.normalize(r.financial_address_identifier, ctx)
    handler.validate(ident, ctx)                   # raises on bad format or checksum

    provider = handler.derive_provider(ident, ctx) # may be None
    if provider:
        if r.provider_code and r.provider_code != provider: error PROVIDER_MISMATCH
        r.provider_code = provider
    if type.provider_required and not r.provider_code: error PROVIDER_REQUIRED
    if r.provider_code:
        p = providers.get(r.provider_code)         # programmatic check, there is no foreign key
        if p is None or not p.active: error UNKNOWN_PROVIDER
        if type.kind not in p.services: error PROVIDER_SERVICE_MISMATCH

    validate r.details against type.details_schema
    handler.validate_details(r.details, r.provider_code, ctx)    # e.g. IFSC prefix == provider_code

    r.financial_address_identifier      = ident
    r.financial_address_identifier_hash = hmac(ident); r.hash_key_version = current_version
    return r
```

```
persistence hook (before_insert / before_update on the FA model):
    parent = load beneficiary(link_internal_record_id)
    if parent is None or parent.record_status != ACTIVE: error          # programmatic parent check
    r = prepare(type, record)
    if config.financial_address_encryption_at_rest:
        r.financial_address_identifier = "enc:v1:" + encrypt(r.financial_address_identifier)
    if r.record_status != ACTIVE: r.priority = NULL
    if insert:
        if type.validation_method in (PENNY_DROP, LOOKUP) and a connector/queue exists:
            r.account_validation_status = UNVERIFIED; r.account_validation_next_date = today
        else:
            r.account_validation_status = NOT_APPLICABLE
    # the account_validation_* columns are not versioned and are never copied to history
```

```
construct_record_name(payload):
    return financial_address_name + " " + financial_address_type        # name omitted if empty

construct_search_text(payload, extra):
    return join(functional_record_id, financial_address_type, provider_code, mask(identifier))
    # never the plaintext identifier

validate_intake_parent_link(record, link_internal_record_id, session):
    parent = load beneficiary(link_internal_record_id)
    if parent is None or parent.record_status != ACTIVE: error

pre_approve(change_request, session):
    for each FA create/update in the change request:
        re-check priority uniqueness against the database state at approval time
        re-check provider is still active

post_approve(change_request, session):
    for each FA where identifier, provider_code, details or financial_address_type changed:
        system update (no history row):
            account_validation_status    = UNVERIFIED (or NOT_APPLICABLE if the type has no method)
            account_validation_next_date = today
            account_validation_name_match = NULL
        cancel any open penny-drop or lookup queue row for the FA
    for each FA made INACTIVE:
        priority = NULL; cancel open queue rows; account_validation_next_date = NULL
    publish a change event (WebSub) so subscribers see the new address list

post_ingest(register_id, row, session):
    same steps as the "changed" branch in post_approve
```

Additional service methods:

```
validate_live(financial_address_type, raw_identifier, provider_code?, details?) -> {normalized, derived_provider, errors}
    # runs prepare() on a copy; no persistence; used by the UI widget and the portal

search_hash_candidates(raw_value) -> list[hash]
    for each active type: try handler.normalize(raw_value); hash it; return distinct hashes
    for each active hash key version: repeat

reveal_identifier(record) -> string
    if value starts with "enc:v1:": decrypt, else return as stored
    write an access-log entry (who, which record, when) for Partner API disclosures

mask_identifier(record) -> string
    handler.mask(identifier)
```

The Staff API and the Partner API call `reveal_identifier` (D13). Masking remains available for other channels (O9).

### 5.4 Handler package

```
spa_registry/handlers/
  base.py        AddressTypeHandler protocol, GenericHandler
  registry.py    HANDLERS = {"UpiVpaHandler": UpiVpaHandler, ...}
  upi_vpa.py  msisdn.py  iban.py  ifsc_bank_account.py
```

Interface:

```
class AddressTypeHandler(Protocol):
    def normalize(self, raw: str, ctx) -> str
    def validate(self, value: str, ctx) -> None                    # raises on failure
    def mask(self, value: str) -> str
    def derive_provider(self, value: str, ctx) -> str | None       # default None
    def validate_details(self, details: dict, provider_code: str | None, ctx) -> None   # default no-op
```

`handler_for(type)` looks the name up in the in-code `HANDLERS` dictionary and falls back to `GenericHandler` built from the type row's regex and normalizer. The dictionary is explicit. A handler name in the database is never turned into an import path. The Initializer checks every seeded `handler` name against the dictionary at startup.

| Handler | normalize | validate | derive_provider | validate_details |
|---|---|---|---|---|
| `UpiVpaHandler` | trim, lowercase | `^[a-z0-9._-]{2,256}@[a-z][a-z0-9]{1,63}$` | the text after `@`, if it exists in providers (creates a `needs_review` provider if allowed by config) | – |
| `MsisdnHandler` | parse with the default region, format as E.164 | valid number per the phone library, not a fixed line | none (number portability) | `rail` optional |
| `IbanHandler` | strip spaces, uppercase | length per country, mod-97 checksum | bank code to provider via a directory, or none | – |
| `IfscBankAccountHandler` | strip spaces and hyphens, uppercase | `^[A-Z0-9]{5,34}$` | none | `ifsc` matches `^[A-Z]{4}0[A-Z0-9]{6}$` and its first four characters equal `provider_code`; branch exists in MDS (advisory) |
| `GenericHandler` | per the row | per the row | none | – |

`mask` keeps the country code and the last four digits for phone numbers, the last four characters for account numbers, and the handle for VPAs (`r****@okicici`).

### 5.5 Configuration

Held in the extension's `Settings`:

| Setting | Notes |
|---|---|
| `financial_address_encryption_at_rest` | TRUE or FALSE (2.5) |
| Hash keys by version, encryption key reference | From a secrets manager. Not stored in the database. |
| Default phone region | For `MsisdnHandler` |
| Validation settings | Section 6.8 |
| Bridge connection | Section 7 |
| MDS connection and `mds_cache_refresh_hours` | Section 4 |
| Lookup connector configuration | Section 6.6.3 |

---

## 06. Financial Address Validation: Detailed Design

### 6.1 Goal

Before an address is relied on for benefit payments, check that it exists and can receive money, and where possible who holds it. Two methods are supported, chosen per financial address type by `financial_address_types.validation_method`:

| Method | For | How |
|---|---|---|
| `PENNY_DROP` | Bank accounts | Send a very small payment through G2P Bridge. Observe, in the sponsor bank statements, whether the bank rejected it. |
| `LOOKUP` | UPI addresses, wallets, phone-number aliases | Ask the bank, operator or network, through a lookup connector, whether the address exists and who holds it. No money moves. |
| `NONE` | Types that need no validation | `account_validation_status = NOT_APPLICABLE` |

A single flow selects work by date (6.4). The method decides which queue the work goes into. Both methods end in the same summary on the address.

### 6.2 State on the FA

| Column | Meaning |
|---|---|
| `account_validation_status` | `NOT_APPLICABLE`, `UNVERIFIED` (due, not queued), `PENDING` (claimed and queued), `VERIFIED`, `REJECTED`, `FAILED` |
| `account_validation_next_date` | Date the next validation is due. NULL if not applicable. |
| `account_validation_last_validated_at` | When the last successful validation completed |
| `account_validation_name_match` | `MATCH`, `MISMATCH`, `UNKNOWN`: informational flag |

These columns are not versioned (D10). The jobs write them directly in the database, outside the change-request flow, and no history row is written. The queue tables hold the full history of each attempt and are the audit trail.

State summary:

```
UNVERIFIED --(account_validation_beat claims)--> PENDING --(queue result)--> VERIFIED | REJECTED | FAILED
     ^                                                                              |
     +----------------------------(re-validation due)-------------------------------+
```

### 6.3 Queues

| Queue table | Method | Detail |
|---|---|---|
| `penny_drop_queue` | `PENNY_DROP` | 6.5.1 |
| `account_lookup_queue` | `LOOKUP` | 6.6.1 |

Both are plain tables, not registers. Each queue row carries its own status. Terminal results are copied to the address summary (6.2).

### 6.4 Selecting and queueing work: `account_validation_beat` and `account_validation_worker`

**`account_validation_beat`** (schedule `account_validation_beat_interval`, default 15 minutes):

1. Select financial addresses where `record_status = ACTIVE`, `account_validation_next_date <= today`, and `account_validation_status` is `UNVERIFIED` or `VERIFIED`. The `VERIFIED` rows are the re-validation of addresses whose interval has elapsed, so no separate re-validation scheduler is needed.
2. Restrict to financial address types whose `validation_method` is `PENNY_DROP` or `LOOKUP`.
3. In one transaction, using `FOR UPDATE SKIP LOCKED` so two beat instances never claim the same row, set the claimed rows' `account_validation_status = PENDING` and publish `account_validation_worker` tasks in chunks of `account_validation_chunk_size` addresses.

**`account_validation_worker`** (one task per chunk). For each address:

1. If an open queue row already exists for the address, skip it (idempotent).
2. Load the address's financial address type.
3. `PENNY_DROP`: insert a `penny_drop_queue` row with `status = PENDING` and `attempt_no` = previous attempts + 1.
4. `LOOKUP`: if a lookup connector is configured for the type, insert an `account_lookup_queue` row with `status = PENDING`. If not, set `account_validation_status = NOT_APPLICABLE` and log a warning.
5. Type is inactive or `NONE`: set `account_validation_status = NOT_APPLICABLE` and clear `account_validation_next_date`.

**Stale claims:** if a worker fails after the beat set an address to `PENDING` but before the queue row was created, `account_validation_stale_retry_beat` and `account_validation_stale_retry_worker` (10.3) find addresses that are `PENDING` for longer than `task_stale_threshold_minutes` with no open queue row, and reset them to `UNVERIFIED` so the next beat claims them again.

### 6.5 Penny drop

#### 6.5.1 Queue table: `penny_drop_queue`

| Column | Notes |
|---|---|
| `attempt_id` | Primary key. Also the **unique transaction reference** sent to Bridge as the `disbursement_id`, for example `PD-<short fa id>-<attempt no>`. One per attempt, never per FA, so a retry never collides in Bridge. |
| `fa_internal_record_id` | The address |
| `attempt_no` | 1, 2, ... |
| `status` | `PENDING`, `PROCESSING`, `SENT`, `CONFIRMING`, `CONFIRMED`, `REJECTED`, `FAILED`, `CANCELLED` |
| `run_id` | The batch (one Bridge envelope) |
| `envelope_id`, `batch_control_id` | Returned by or sent to Bridge |
| `sent_at` | When Bridge accepted the disbursement |
| `confirm_after` | `sent_at` plus the configured confirmation days |
| `result_detail` | Facts returned by Bridge (JSON) |
| `bank_name_returned`, `name_match_score` | For name matching |
| `last_error`, `updated_at`, `created_at` | |

`PENDING` and `PROCESSING` belong to the dispatch stage. `SENT`, `CONFIRMING` and the terminal states belong to the confirmation stage. The same table therefore serves both stages.

#### 6.5.2 State machine

```
Queue: PENDING -> PROCESSING -> SENT -> CONFIRMING -> CONFIRMED | REJECTED
                      |                     |
                      +--> PENDING (retry)  +--> SENT (not enough facts yet) --> FAILED (max wait)
                      +--> FAILED (max attempts)
       any open state -> CANCELLED (address changed or deactivated)
```

#### 6.5.3 Jobs

| Job | Work |
|---|---|
| `penny_drop_beat` | Claim `PENDING` queue rows (up to `penny_drop_batch_size`) with `FOR UPDATE SKIP LOCKED`, mark them `PROCESSING`, assign a `run_id`, and publish `penny_drop_worker(run_id)`. |
| `penny_drop_worker` | Sends the run to Bridge (section 7). On success marks the rows `SENT` and sets `sent_at` and `confirm_after`. On failure returns the rows to `PENDING` with the attempt bookkeeping (6.5.4). Decrypts the identifiers; only this worker and the stale-retry worker handle plaintext for payment. |
| `penny_drop_confirmation_beat` | Claim `SENT` rows where `confirm_after <= now`, mark them `CONFIRMING`, publish `penny_drop_confirmation_worker(batch)`. |
| `penny_drop_confirmation_worker` | Calls Bridge's status endpoint for the attempt ids and applies the rule in 6.5.5. |
| `penny_drop_stale_retry_beat` / `penny_drop_stale_retry_worker` | Reset rows stuck in `PROCESSING` or `CONFIRMING` beyond `task_stale_threshold_minutes`. See 10.3. |

#### 6.5.4 Retries and limits

| Setting | Default | Meaning |
|---|---|---|
| `penny_drop_max_attempts` | 3 | Attempts per due validation before `FAILED` |
| `penny_drop_retry_backoff_hours` | 24 | Delay before a new attempt after a failed dispatch |
| `penny_drop_max_wait_days` | 7 | Maximum time in `SENT` without enough facts |
| `penny_drop_batch_size` | 500 | Rows per run |
| `penny_drop_amount` | 1.00 | Amount per attempt, in the account currency |
| `penny_drop_confirmation_days` | 2 | `n` in 6.5.5 |

A `FAILED` status is terminal until staff request revalidation (6.7). It appears in the UI so staff can act.

#### 6.5.5 Confirmation rule

Bridge returns facts per disbursement. SPA Registry decides the status.

| Bridge facts | Queue result | FA result |
|---|---|---|
| Reversal found | `REJECTED` (reason kept) | `account_validation_status = REJECTED` |
| Debit (remittance) found, no reversal, and statements processed through at least `sent date + n` days | `CONFIRMED` | `VERIFIED`; `account_validation_last_validated_at = now`; next validation date set (6.7) |
| No debit found | Stay `SENT`; retry the status call on the next run; after `penny_drop_max_wait_days` → `FAILED` | After the maximum wait: `FAILED` |
| Statements not yet processed through the window | Stay `SENT` | no change |

* `n` is `penny_drop_confirmation_days`, default **2**. It can be set per sponsor bank.
* "Absence of rejection" is not enough on its own. The debit must be seen, and the statements must cover the window. Otherwise a missed statement day would produce a false success.
* The statement coverage date (`reconciled_through`) is a new field in Bridge's status response (section 8).
* **Name match, flag only:** if Bridge returns `beneficiary_name_from_bank`, it is compared with `financial_address_name` after normalization (uppercase, punctuation and titles removed, tokens compared). The score is kept in the queue row and `account_validation_name_match` is set to `MATCH`, `MISMATCH` or `UNKNOWN` using `account_validation_name_match_threshold`. A mismatch never changes the status.

#### 6.5.6 Controls

* The penny-drop amount, the maximum amount per run, and the maximum number per day are enforced in both SPA Registry and Bridge (section 8).
* Penny-drop traffic uses a dedicated sponsor account, so its statements, limits and reconciliation are separate from programme payments.

### 6.6 Lookup

#### 6.6.1 Queue table: `account_lookup_queue`

| Column | Notes |
|---|---|
| `lookup_id` | Primary key, for example `LK-<short fa id>-<attempt no>` |
| `fa_internal_record_id` | The address |
| `attempt_no` | 1, 2, ... |
| `status` | `PENDING`, `PROCESSING`, `COMPLETED`, `FAILED`, `CANCELLED` |
| `result` | `FOUND`, `NOT_FOUND`, `ERROR` (set when `COMPLETED` or on the last failed attempt) |
| `name_returned`, `name_match_score` | For name matching |
| `connector`, `response_detail` | Which connector served the request; sanitized response (JSON) |
| `last_error`, `next_attempt_at`, `updated_at`, `created_at` | |

A lookup has no confirmation stage: the connector answers directly, so the queue has a single worker stage.

#### 6.6.2 Jobs

| Job | Work |
|---|---|
| `account_lookup_beat` | Claim `PENDING` rows whose `next_attempt_at` is due (up to `account_lookup_batch_size`) with `FOR UPDATE SKIP LOCKED`, mark them `PROCESSING`, and publish `account_lookup_worker(batch)`. |
| `account_lookup_worker` | For each row: decrypt the identifier, call the connector (6.6.3) honouring its rate limit, and apply the rules in 6.6.4. |
| `account_lookup_stale_retry_beat` / `account_lookup_stale_retry_worker` | Reset rows stuck in `PROCESSING` beyond `task_stale_threshold_minutes`. See 10.3. |

#### 6.6.3 Lookup connector

A connector asks the system that holds the address whether it exists. Examples: a UPI address validation through the payment network or sponsor bank; the account-holder information call of a wallet operator; a bank's name-enquiry service. Connectors are registered in code, like handlers, and chosen by configuration per financial address type or provider.

```
class AccountLookupConnector(Protocol):
    async def lookup(self, financial_address_type: str, identifier: str,
                     provider_code: str | None, details: dict) -> LookupResult

LookupResult:  status  = FOUND | NOT_FOUND | ERROR
               name    = holder name if returned
               raw     = sanitized response for the audit trail
```

Settings per connector: timeout, rate limit (requests per second), and credentials from the secrets manager. Where connectors run (inside SPA Registry or behind Bridge) and which lookup APIs exist for each type is not yet known (O7).

#### 6.6.4 Rules

| Connector result | Queue result | FA result |
|---|---|---|
| `FOUND` | `COMPLETED` / `FOUND` | `VERIFIED`; `account_validation_last_validated_at = now`; next validation date set (6.7) |
| `NOT_FOUND` | `COMPLETED` / `NOT_FOUND` | `REJECTED` |
| `ERROR` (timeout, rate limit, provider down) | Back to `PENDING` with `next_attempt_at` = now + backoff | no change until the last attempt |
| `ERROR` on the last attempt (`account_lookup_max_attempts`) | `FAILED` | `FAILED` |

**Name match, flag only:** if the connector returns a name, it is compared with `financial_address_name` as in 6.5.5 and `account_validation_name_match` is set. A mismatch never changes the status.

Lookup settings:

| Setting | Default | Meaning |
|---|---|---|
| `account_lookup_max_attempts` | 3 | Attempts per due validation |
| `account_lookup_retry_backoff_minutes` | 60 | Delay between attempts after an error |
| `account_lookup_batch_size` | 200 | Rows per worker task |

### 6.7 Triggers and re-validation

| Event | Effect |
|---|---|
| FA created, type uses penny drop or lookup | `UNVERIFIED`, next validation date = today |
| Identifier, provider, details or financial address type changed | Reset to `UNVERIFIED`, next date = today, name-match flag cleared; cancel open queue rows (5.3) |
| Validation succeeded | `VERIFIED`; next date = today + `account_validation_revalidation_months` (default 12); when it falls due, `account_validation_beat` claims it again (6.4) |
| Rejected | The address stays at its priority. Staff review. |
| Failed | Same as rejected; staff can request revalidation |
| Staff request revalidation | Staff set `account_validation_next_date = today` and status `UNVERIFIED` (a system action exposed in the UI, not a change request) |
| FA made inactive | Cancel open queue rows; clear next date; priority cleared |

Order matters: a changed account must not keep the previous account's `VERIFIED` status.

### 6.8 Validation settings summary

| Setting | Default |
|---|---|
| `account_validation_beat_interval` | 15 minutes |
| `account_validation_chunk_size` | 200 addresses |
| `account_validation_revalidation_months` | 12 |
| `account_validation_name_match_threshold` | 0.8 |
| `task_stale_threshold_minutes` | 30 |
| Penny-drop settings | 6.5.4 |
| Lookup settings | 6.6.4 |

The defaults are proposals and are configuration values.

---

## 07. Interfacing with Bridge for Penny Drop Disbursements

### 7.1 Call sequence per run

1. `create_disbursement_envelopes`: one envelope of type `ACCOUNT_VALIDATION`.
2. `create_disbursements`: **one call** with every disbursement in the run. Bridge locks its envelope-control row per call, so many small calls are slow.
3. Bridge proceeds on its own: funds check, funds block (once per envelope), dispatch to the sponsor bank, statement reconciliation.
4. After `confirm_after`, `penny_drop_confirmation_worker` calls Bridge's disbursement status endpoint with the attempt ids.

Requests are signed with the same JWT mechanism as other Bridge partner calls. Steps 1 and 2 are made by `penny_drop_worker`.

### 7.2 Envelope fields

| Envelope field | Value for `ACCOUNT_VALIDATION` |
|---|---|
| `envelope_type` | `ACCOUNT_VALIDATION` |
| `benefit_program_id`, `benefit_program_mnemonic` | The Account-Validation program, from SPA Registry config. Bridge takes these from its own config and rejects a mismatch (section 8). |
| `benefit_code_id`, `benefit_code_mnemonic` | Account-Validation benefit code, from config |
| `benefit_type` | `CASH_DIGITAL` |
| `target_registry` | `SPA-Registry` |
| `disbursement_cycle_id` | A counter for the run |
| `disbursement_frequency` | `OnDemand` |
| `cycle_code_mnemonic` | Run identifier, for example `PD-20261104-01` |
| `number_of_beneficiaries`, `number_of_disbursements` | Number of attempts in the run |
| `total_disbursement_quantity` | Attempts times the penny-drop amount |
| `measurement_unit` | Currency |
| `disbursement_schedule_date` | Today (Bridge's funds-check job runs for envelopes scheduled today unless it is configured otherwise) |

The declared counts and total must equal what is received, or Bridge will not start the funds check.

### 7.3 Disbursement fields

| Disbursement field | Value |
|---|---|
| `disbursement_id` | `attempt_id` (the unique transaction reference) |
| `disbursement_envelope_id` | Id returned for the envelope |
| `disbursement_batch_control_id` | One per run |
| `disbursement_cycle_id` | Same as the envelope |
| `beneficiary_id` | FA `internal_record_id` |
| `beneficiary_name` | `financial_address_name` (used for name matching and on the payment) |
| `disbursement_quantity` | Penny-drop amount |
| `narrative` | Fixed text, for example `ACCOUNT VALIDATION`. Not caller-chosen per row. |
| Supplied account (new) | `bank_account_number`, `bank_code`, `branch_code`, `account_type` (the literal `BANK_ACCOUNT`), taken from the decrypted FA and its `details` |

For a financial address type that has no bank code of its own (such as `IFSC-BANK-ACCOUNT`), `bank_code` is the provider code and `branch_code` is derived from the IFSC by the handler. The exact mapping is defined in the type's handler, so the dispatch worker does not contain per-type logic.

### 7.4 Reference and reconciliation

Bridge reconciles per `disbursement_id`. The attempt id therefore must appear on the sponsor bank statement entry, or Bridge's matching cannot link the debit and any reversal to it. This must be tested against the sponsor bank connector before relying on it (8.4).

### 7.5 Failure handling

| Failure | Action |
|---|---|
| Envelope creation fails | Rows return to `PENDING`; attempt not counted until Bridge accepted |
| Envelope created, disbursement creation fails | Cancel the envelope through Bridge's cancel endpoint; rows return to `PENDING` |
| Partial acceptance (some rows rejected with error codes) | Accepted rows are `SENT`; rejected rows are marked `FAILED` with the Bridge error code |
| Bridge unreachable | Rows return to `PENDING`; the next `penny_drop_beat` run retries (the stale-retry job covers a crashed worker) |

### 7.6 Status endpoint use

The confirmation worker sends the attempt ids in batches. For each it reads the remittance facts, the reversal facts and the bank-returned name, plus the `reconciled_through` date (section 8, item 8).

---

## 08. Changes in Bridge to Accommodate Penny Drop Transactions

### 8.1 How Bridge works today (relevant parts)

* Envelope intake creates `DisbursementEnvelope`, `EnvelopeControl` and, for cash benefit types, `EnvelopeBatchStatusForCash`.
* Disbursement intake takes caller-supplied `disbursement_id` and `disbursement_batch_control_id`.
* For `CASH_DIGITAL`, the batch control starts with FA resolution `PENDING`, and sponsor-bank dispatch, geo, warehouse and agency steps `NOT_APPLICABLE`. The mapper resolution worker writes `DisbursementResolutionFinancialAddress` rows and then sets FA resolution `PROCESSED` and dispatch `PENDING`.
* The check-funds job needs the schedule date to be today (by default) and the received counts and total to equal the declared ones. The block-funds job follows. The dispatch job requires `FUNDS_BLOCK_SUCCESS` and dispatch `PENDING`.
* Dispatch builds each payment from the `DisbursementResolutionFinancialAddress` row and uses the sponsor account from the sponsor bank configuration.
* Reconciliation is per `disbursement_id` in `DisbursementRecon` (remittance and reversal facts, bank-returned name). Statements are processed from MT940 files.
* The sponsor bank configuration is read from Bridge configuration when `in_kind_enabled` is false (keyed by program and benefit code, with a `default` fallback), or from PBMS when it is true.
* Controllers validate the request signature only. There is no per-client authorization.

### 8.2 Change list

| # | Area | Change |
|---|---|---|
| 1 | Model and migration | Add `envelope_type` (`DISBURSEMENT` default, `ACCOUNT_VALIDATION`) to `DisbursementEnvelope`, `DisbursementEnvelopePayload` and the migration. Backfill existing rows with `DISBURSEMENT`. |
| 2 | Disbursement payload | Optional supplied-account fields: `bank_account_number`, `bank_code`, `branch_code`, `account_type`. `beneficiary_name` already exists. |
| 3 | Envelope validation | For `ACCOUNT_VALIDATION`: force `benefit_type = CASH_DIGITAL`, frequency `OnDemand`, programme and benefit identifiers from Bridge config (reject a mismatch), schedule date today, and keep the count and total checks. |
| 4 | Disbursement validation | For `ACCOUNT_VALIDATION`: account fields required, per-transaction amount cap, per-envelope cap, fixed narrative. For `DISBURSEMENT`: reject account fields. New error codes for each rule. |
| 5 | Batch control creation | For `ACCOUNT_VALIDATION`: `fa_resolution_status = NOT_APPLICABLE`, `sponsor_bank_dispatch_status = PENDING`, and write the `DisbursementResolutionFinancialAddress` rows from the payload in the same transaction. The mapper beat then never selects the batch. |
| 6 | Authorization | Allow `ACCOUNT_VALIDATION` envelopes only for configured client identities (config list of client ids or token claims). |
| 7 | Sponsor bank configuration | New dedicated setting for the Account-Validation account (same four fields as today: account number, type, branch code, sponsor bank code) plus the pseudo-programme identifiers. New helper that reads only this setting, with no PBMS access and no `default` fallback, and fails closed if missing. The funds-check, funds-block and dispatch workers choose this helper when the envelope type is `ACCOUNT_VALIDATION`. The account-number lookup used by the MT940 processor also checks the validation account first, in both modes. |
| 8 | Status API | Add `reconciled_through` (the latest processed statement date for the sponsor account) to the disbursement status response, in addition to the existing remittance and reversal facts and the bank-returned name. |
| 9 | Configuration | Caps (per transaction, per envelope, per day), pseudo-programme identifiers, allowed clients, validation sponsor account. |

The verification in 8.4 adds items 10 to 12 below.

### 8.3 No change needed

Mapper resolution beat and worker (because the batch is created with FA resolution not applicable), geo, warehouse and agency allocation (already not applicable for `CASH_DIGITAL`), funds check and block jobs (once per envelope, which is why runs are batched), dispatch job, MT940 processor (beyond the account lookup in item 7).

### 8.4 Verification against the Bridge code (O6)

The six items that were open were checked by reading the Bridge workers and beat producers, the bank connector interface and the example bank connector and example bank.

| # | Item | Result | Detail |
|---|---|---|---|
| 1 | Matching a statement entry to a `disbursement_id` | **Confirmed for the example bank.** Real banks depend on their connector. | The MT940 processor takes a `reconciliation_id` from the bank connector (`retrieve_reconciliation_id`) and looks up `Disbursement.id` with it. The example connector writes the `disbursement_id` into narrative 5 on payment and reads it back from the `:86:` field on the statement, because the `:61:` customer reference is limited to 16 characters. The attempt id therefore reconciles as long as the sponsor bank's connector does the same. Each real bank connector must implement this method. |
| 2 | Beneficiary name from the bank | **Not available in the example connector.** | `retrieve_beneficiary_name` returns narrative 4, which the connector fills with `beneficiary_id`, not a name returned by the bank. Name matching can only be tested with a real connector that reads a name from the statement. Until then `account_validation_name_match` will be `UNKNOWN` for penny drops. |
| 3 | Reversal reference | **Confirmed for the example bank.** | A rejected payment appears as an `RD` entry carrying the same narrative 5 (the `disbursement_id`) and a reason in the last narrative (`retrieve_reversal_reason`). The processor matches it to the existing `DisbursementRecon` and sets the reversal facts. The example bank generates random rejections (about 30% of payments to bank codes other than its own) with reasons such as `ACCOUNT_CLOSED` and `ACCOUNT_NOT_FOUND`, which helps testing. |
| 4 | Funds block | **Meaningful and cheap in the example bank; unknown for a real bank.** | The block worker blocks `total_disbursement_quantity` once per envelope (one check call and one block call). The example bank creates a fund block that the payments then consume. Bridge code has no explicit release step. For a dedicated validation account the block must be accepted by the sponsor bank. |
| 5 | Per-file or per-instruction charges and limits | **Cannot be determined from code.** | Bridge sends all payments of one batch control in a single `initiate_payment` call (one request to the example bank). One run is one `create_disbursements` call, so one batch and one bank call. Charges and limits are a question for the sponsor bank. |
| 6 | PBMS reads on the digital-cash path | **Confirmed: none for these envelopes.** | Digital-cash batch controls are created with geo, warehouse and agency steps not applicable, so the agency helper (the only PBMS reader besides the in-kind branch of the sponsor configuration) never runs. Beneficiary notification works only on geo-address rows, which digital cash never creates, so penny drops send no beneficiary notifications. The PBMS database engine object is created at worker start-up but is not connected unless used. |

Additional findings that affect the design:

1. **Reversals can be lost if statements are processed out of order.** Statements are picked up by a beat in no particular order and processed in parallel. A reversal is applied only if the debit's `DisbursementRecon` already exists; otherwise it is stored as an error record (`INVALID_REVERSAL`) and is not retried. A reversal in a statement that is processed before the statement holding the debit is therefore not applied to the penny-drop attempt, and the attempt would look as if it had no reversal. Debits and reversals in the **same** statement are processed in the right order (debits first).
2. **No check that statements are contiguous.** Statement numbers and sequence numbers are stored, but nothing verifies that no statement is missing. `reconciled_through` (item 8 in 8.2) taken as "latest processed statement date" would not detect a gap.
3. **The account type must be a literal.** The example bank routes on `beneficiary_account_type` values such as `BANK_ACCOUNT`. The supplied `account_type` for penny drops must be `BANK_ACCOUNT`.
4. **Fund-block amount mismatch is only logged** by the example bank, not rejected. This is a property of the example bank.

Required additions to the Bridge change list (8.2):

| # | Area | Change |
|---|---|---|
| 10 | Reversal robustness | Keep a reversal that arrives before its debit and apply it when the debit is processed (or reprocess `INVALID_REVERSAL` error records after each statement). Without this, penny-drop rejections can be missed. |
| 11 | Statement coverage | Compute `reconciled_through` as the latest date up to which statements are present and processed **without gaps**, using statement and sequence numbers, so that a missing statement keeps the answer at "pending". |
| 12 | Connector requirements | Each sponsor bank connector must implement `retrieve_reconciliation_id`, `retrieve_beneficiary_name` and `retrieve_reversal_reason` for the validation account's statements, and the payment must carry the `disbursement_id` in a field that returns on the statement. |

Remaining to confirm with the sponsor bank: whether it charges per file or instruction (item 5), whether it will accept the funds block for the validation account (item 4), and the exact way a rejected credit is reported on the statement for the real bank (item 3).

### 8.5 Issues noticed in Bridge while reading (separate fixes)

1. `create_disbursements` calls `session.rollback()` without `await` in its error path.
2. The mapper-resolution beat's stale reset uses `updated_at > stale_at`, whereas the dispatch beat uses `<`. The first looks inverted and would reset batches that were just started.
3. `update_envelope_control` sleeps two seconds while holding the row lock.

None of these block penny drop; the first two should be fixed anyway.

---

## 09. UI Design: Tabs and Sections

The staff UI is configured with registry-platform metadata: tabs in `g2p_register_ui_tabs`, tab-to-section mapping in `g2p_register_ui_tab_sections`, and section layout in `g2p_register_sections.section_ui_schema`. A multi-record section is a section with `is_list = TRUE` and a `table` widget.

### 9.1 Tab layout

One tab for the Beneficiary register: `beneficiary_info_tab`, with two sections.

| Section | section_id | Register | is_list | Content |
|---|---|---|---|---|
| 1 | `bn_beneficiary_details` | Beneficiary | FALSE | Beneficiary attributes |
| 2 | `bn_table_financial_addresses` | FinancialAddress | TRUE | Financial addresses table |

A second tab can be added later (for example validation history from the queue tables) by adding a row to `g2p_register_ui_tabs`.

### 9.2 Section 1: Beneficiary details

| Field | Widget | Behaviour |
|---|---|---|
| `functional_record_id` | text | read-only |
| `first_name` | text | editable, required |
| `last_name` | text | editable, required |
| `foundational_id` | text | editable |
| `record_name` | text | read-only (built from first and last name) |
| `alternate_ids` | table (small) | editable; each row has `type` and `value` |

### 9.3 Section 2: Financial addresses (table)

| Column | Widget | Behaviour |
|---|---|---|
| `priority` | number | editable. Rows are shown in priority order. |
| `financial_address_type` | select | options from a SPA Registry endpoint (section 11) |
| `financial_address_identifier` | text | staff see the unmasked value |
| `provider_code` | select | options from a SPA Registry endpoint, filtered by the chosen type's kind |
| `details` | `address-details` widget (section 11) | fields come from the type's `details_schema` |
| `financial_address_name` | text | editable |
| `currency` | text/select | |
| `account_validation_status` | text/badge | read-only |
| `account_validation_next_date` | date | read-only |
| `account_validation_last_validated_at` | datetime | read-only |
| `account_validation_name_match` | text/badge | read-only; a `MISMATCH` is highlighted |
| `record_status` | toggle | the Active flag |

Table operations: `{"add": true, "edit": true, "remove": false}`. Addresses are never removed; the Active toggle sets `record_status` to `ACTIVE` or `INACTIVE`.

### 9.4 Rules

* **Approvals:** `cr_auto_approve_for_bene_portal`, `..._agent_portal`, `..._staff_portal` and `..._partner` are all `FALSE` for both sections. Approval policies and stages are seeded in the AWE metadata for both registers.
* **Priority order:** the domain service enforces unique priorities (5.3). The UI shows the error and the table is sorted by priority.
* **Live validation:** the identifier field calls `validate_live` as the user leaves it and shows the normalized value, the derived provider and any errors.
* **Validation columns are not approved:** the `account_validation_*` columns are read-only in the UI and are written by the jobs, not by change requests (6.2). A "Request revalidation" action (6.7) is the only staff action on them.
* **Bank accounts with an IFSC:** the staff UI uses a text `ifsc` field inside `details` with backend validation. The cascading bank and branch picker is available through the new widget (section 11) and is required for the beneficiary portal.

### 9.5 Search and result schema

* `search_result_schema`: `functional_record_id`, `foundational_id`, `record_name`, number of active addresses.
* `filter_schema`: text filters on `foundational_id`, `first_name`, `last_name`, and a **financial address identifier (exact)** filter that uses the hashed filter type (section 11).

---

## 10. Celery Jobs and Workers

Every job is a **beat** (selects and claims work, publishes tasks) and a **worker** (does the work). Platform jobs (ingestion, outgestion, scoring, WebSub publishing) are the registry-platform's own and are not listed.

### 10.1 All jobs

| # | Beat | Worker | Purpose | Detail |
|---|---|---|---|---|
| 1 | `account_validation_beat` | `account_validation_worker` | Select addresses due for validation (including re-validation) and fill the penny-drop or lookup queue | 6.4 |
| 2 | `account_validation_stale_retry_beat` | `account_validation_stale_retry_worker` | Recover addresses left `PENDING` without a queue row | 10.3 |
| 3 | `penny_drop_beat` | `penny_drop_worker` | Send queued penny drops to Bridge in runs | 6.5.3, 7 |
| 4 | `penny_drop_confirmation_beat` | `penny_drop_confirmation_worker` | Ask Bridge for results after the wait and set the status | 6.5.3, 6.5.5 |
| 5 | `penny_drop_stale_retry_beat` | `penny_drop_stale_retry_worker` | Recover penny-drop rows stuck `PROCESSING` or `CONFIRMING` | 10.3 |
| 6 | `account_lookup_beat` | `account_lookup_worker` | Run queued lookups through the connectors and set the status | 6.6.2, 6.6.4 |
| 7 | `account_lookup_stale_retry_beat` | `account_lookup_stale_retry_worker` | Recover lookup rows stuck `PROCESSING` | 10.3 |
| 8 | `identifier_rekey_beat` | `identifier_rekey_worker` | Bring stored identifiers and hashes in line with the current hash key version and encryption flag | 10.4 |
| 9 | `directory_retirement_check_beat` | `directory_retirement_check_worker` | Flag addresses whose IFSC or provider has been retired | 10.5 |
| 10 | `mds_cache_refresh_beat` | `mds_cache_refresh_worker` | Refresh the cached bank and branch lookups | 10.6 |

Default schedules (configuration values): jobs 1, 3, 6 every few minutes (6.8); job 4 hourly; jobs 2, 5, 7 every 15 minutes; job 8 on demand; job 9 daily; job 10 every 12 hours.

### 10.2 Common behaviour

* Every beat claims rows before publishing a task, using `FOR UPDATE SKIP LOCKED`, and every worker is idempotent by queue id.
* Queue names, concurrency and beat schedules are configuration values.
* Jobs that read plaintext identifiers (`penny_drop_worker`, `account_lookup_worker`, `identifier_rekey_worker`) run with the key access and logging that other plaintext access has.
* Failures are visible in the queue tables' `status` and `last_error`.

### 10.3 Stale-retry jobs (jobs 2, 5, 7)

A worker can crash after its beat has claimed work. Each queue has a stale-retry pair that returns such work to the pool. All three use `task_stale_threshold_minutes` (default 30).

| Beat / worker | Finds | Action |
|---|---|---|
| `account_validation_stale_retry_*` | Addresses with `account_validation_status = PENDING` for longer than the threshold and no open row in `penny_drop_queue` or `account_lookup_queue` | Set the status to `UNVERIFIED` (the next `account_validation_beat` claims it again). A re-validation of a previously `VERIFIED` address becomes `UNVERIFIED` as well. |
| `penny_drop_stale_retry_*` | `penny_drop_queue` rows in `PROCESSING` or `CONFIRMING` for longer than the threshold | `PROCESSING` → `PENDING`; `CONFIRMING` → `SENT`. A `PROCESSING` row whose `run_id` was already accepted by Bridge is detected through the status endpoint and moved to `SENT`, not re-sent. |
| `account_lookup_stale_retry_*` | `account_lookup_queue` rows in `PROCESSING` for longer than the threshold | → `PENDING`, `next_attempt_at = now`. Lookups are read-only, so repeating one is safe. |

The beat selects the stale rows. The worker performs the reset, so that the reset follows the same claim pattern as every other job.

### 10.4 `identifier_rekey` (job 8)

Runs when the hash key version is advanced or when `financial_address_encryption_at_rest` is changed.

* Beat: selects financial addresses whose `hash_key_version` is older than the current one, or whose stored identifier does not match the current encryption flag (an `enc:v1:` prefix when the flag is TRUE, none when FALSE), in pages. Pages are claimed with `FOR UPDATE SKIP LOCKED`.
* Worker: for each address, decrypts (if needed), recomputes the hash under the current key, re-encrypts or decrypts to match the flag, and updates the row.
* These are system updates. No history rows are written and no change requests are raised.
* The job can be restarted: rows already in line are not selected.

### 10.5 `directory_retirement_check` (job 9)

* Beat (daily): selects active addresses of types that depend on a directory (for example `IFSC-BANK-ACCOUNT`), in pages.
* Worker: checks the IFSC (`details.ifsc`) against the cached MDS directory and the provider against `financial_service_providers`. If the IFSC is retired, or the provider is inactive, it records a flag on the address for staff to see. It records the finding for staff (a review flag or task; the storage is decided with the UI work). It does not change the address's status, priority or `record_status`.

### 10.6 `mds_cache_refresh` (job 10)

* Beat: runs every `mds_cache_refresh_hours` (default **12**).
* Worker: reloads the bank list and, when needed, the branches of banks used by active addresses from MDS, replacing the cache. If MDS is unreachable it keeps the existing cache and logs a warning.

---

## 11. Enhancements in UI Widgets

The staff UI renders widgets from the section's JSON schema. The select widget today supports a `static` source or an `api` source (`service`, `endpoint`, `params`, `valueKey`, `labelKey`). Table widgets support `widget-data-columns` and `widget-data-operations`. The following are needed.

| # | Widget / change | Purpose |
|---|---|---|
| W1 | New `address-details` widget | Renders the `details` fields of a table row according to the `details_schema` of the row's `financial_address_type` (for example an `ifsc` field for IFSC bank accounts, a `rail` field for phone-number bank accounts). Re-renders when the type changes. |
| W2 | Select widget: dependent parameters | `params` values can reference another field of the same row, for example `{"kind": {"$field": "financial_address_type"}}`, so the provider list depends on the chosen financial address type. The dependent select is cleared when its source field changes. |
| W3 | Selects backed by SPA Registry endpoints | Financial address types and providers are SPA Registry tables, not MDS lists. New endpoints in the SPA Registry service: list financial address types, list providers (filter by kind and active), validate an identifier live (`validate_live`), resolve an IFSC. The `service` setting of the select points at them. |
| W4 | Cascading bank and branch widget | Choose a bank, then search the branches of that bank with typeahead and pagination, backed by the enhanced MDS API (E1 to E4). Output: `provider_code` and `details.ifsc`. Also supports typing an IFSC and showing the resolved bank and branch for confirmation. Required by the beneficiary portal; optional in the staff UI. |
| W5 | Active toggle column in table widgets | Edits `record_status` between `ACTIVE` and `INACTIVE` without a remove button, and clears `priority` when set inactive. |
| W6 | Priority ordering | Table sorted by `priority`; an inline error when two active rows share a value. Reordering is an edit of the `priority` values within one change request, which the deferred unique constraint allows. |
| W7 | System-maintained columns | Read-only display of the `account_validation_*` columns, a badge for `account_validation_status` and a highlighted `MISMATCH`. A "Request revalidation" row action that calls a SPA Registry endpoint (6.7). The identifier column shows the unmasked value for staff. |
| W8 | New `hashed_exact` filter type | In `filter_schema` and the platform's filter builder: the entered value is sent to the server, normalized under each financial address type's handler, hashed (all active key versions) and matched on `financial_address_identifier_hash` of the FA table, returning the owning beneficiaries. The key never reaches the browser. |

W1, W2, W5 and W8 need changes to registry-platform (UI renderer and, for W8, the filter builder, which today validates only text, dropdown, ranges and boolean filter types). W3 and W4 need new SPA Registry endpoints and the MDS enhancements in section 4.

---

## 12. Registry Partner API: DCI Controller, ID-Type Search Returning Financial Addresses

### 12.1 Requirement

A partner (for example the payment system or a programme) sends a DCI search with an ID type and ID value, or a list of them, and receives for each ID **all the financial addresses** of the matching beneficiary, ready to use for payment.

### 12.2 How the platform handles ID-type search today

* The Partner API's DCI controller decodes each `search_request` item, and `decode_dci_search` supports four query types: `idtype-value`, `expression`, `predicate`, `graphql`.
* An `idtype-value` query has the shape `{"type": "UIN", "value": "..."}` and resolves through the configured `dci_id_type_columns` map from ID type to a register column. The column must also be in `dci_allowed_search_fields`.
* The default mapping is `UIN → foundational_id` and `FID → functional_record_id`. Both columns are in the default allowed fields.
* The search runs against the register named by `reg_type` and loads related registers (`TABLE` children) with the record. Records are rendered through the register's **outgoing template**. If consent enforcement is on, fields are clamped to the consent's data scopes.

### 12.3 Configuration for the SPA Registry

The beneficiary register has a `foundational_id` column (2.2), so the platform's default mapping works as it is.

| Setting | Value |
|---|---|
| `dci_id_type_columns` | Default: `{"UIN": "foundational_id", "FID": "functional_record_id"}` |
| `dci_allowed_search_fields` | Default list already includes `foundational_id`, `functional_record_id`, `first_name`, `last_name`, `record_name`, `record_status` |
| Register | `reg_type = "Beneficiary"` |
| Outgoing template | New template for `Beneficiary` that includes the related `FinancialAddress` records (12.5) |

Alternate IDs (the JSONB column) are not covered by the column map, which maps an ID type to one column. Supporting them requires an additional ID-type resolver in the extension, for example a case where the type is not in the column map and the value is matched in `alternate_ids`. This is a platform extension point to be added and is not specified further here.

### 12.4 Request

One DCI `search_request` item per ID (the batch is the list of items), each with an `idtype-value` query:

```json
{
  "reference_id": "ref-001",
  "search_criteria": {
    "reg_type": "Beneficiary",
    "reg_record_type": "person",
    "query_type": "idtype-value",
    "query": { "type": "UIN", "value": "4567891230" }
  }
}
```

Several IDs may be sent as several items in one request. A `predicate` query with the operator `in` can also search several values of one ID type. Pagination applies per item.

### 12.5 Response content

Each item returns a beneficiary record that contains its financial addresses:

```json
{
  "reference_id": "ref-001",
  "status": "succ",
  "data": {
    "reg_type": "Beneficiary",
    "reg_records": [{
      "functional_record_id": "SPA-0000001",
      "foundational_id": "4567891230",
      "first_name": "Ramesh",
      "last_name": "Kumar",
      "financial_addresses": [
        {
          "priority": 1,
          "financial_address_type": "IFSC-BANK-ACCOUNT",
          "financial_address_identifier": "50100123456789",
          "provider_code": "HDFC",
          "details": { "ifsc": "HDFC0001234" },
          "currency": "INR",
          "financial_address_name": "Ramesh Kumar",
          "validation": { "status": "VERIFIED", "last_validated_at": "2026-10-01T09:12:00", "name_match": "MATCH" }
        },
        {
          "priority": 2,
          "financial_address_type": "UPI-VPA-BANK-ACCOUNT",
          "financial_address_identifier": "ramesh@okicici",
          "provider_code": "okicici",
          "currency": "INR",
          "financial_address_name": "Ramesh Kumar",
          "validation": { "status": "VERIFIED", "name_match": "UNKNOWN" }
        }
      ]
    }]
  },
  "pagination": { "page_number": 1, "page_size": 10, "total_count": 1 }
}
```

(The envelope fields shown follow the shape built in `G2PDciService.search`. The names in the template body are defined by the outgoing template and are not fixed by the platform. The status code shown is a placeholder: use the code the DCI schema defines for success.)

### 12.6 Rules

* **Only active addresses** (`record_status = ACTIVE`) are returned, ordered by `priority` ascending. Inactive addresses are never returned.
* **Validation state** is included so that the payer can prefer verified accounts and fall back in priority order on failure. A previously verified address that is being re-validated shows `PENDING` for the duration of the re-validation, so the payer should not treat `PENDING` as unusable by itself.
* **Unmasked identifiers** are returned to partners because the payment needs them (D13), subject to the consent data scopes. A consent that does not grant the identifier field produces a record without it. Every disclosure of an unmasked identifier to a partner is logged.
* **Not found:** an ID that matches no beneficiary returns an item with zero records, not an error for the whole request. A beneficiary with no active addresses returns the beneficiary with an empty address list.
* **Several beneficiaries for one ID** is not expected, since ID uniqueness is enforced on write (5.2). If it occurs, all matches are returned.
* **Signature and consent checks** apply as for any DCI search, in both synchronous and WebSub callback delivery.
* **Validation internals** (queue contents, attempt history, bank-returned names) are not part of the partner response. Only the summary status, the last validated time and the name-match flag are.

### 12.7 Work required

| # | Item |
|---|---|
| P1 | Confirm the default ID-type mapping and allowed fields against the final column names (12.3) |
| P2 | Outgoing template for `Beneficiary` with nested `FinancialAddress` records, filtered to active and ordered by priority. Confirm how the template engine handles filtering and ordering of related records. |
| P3 | Decryption of the identifier at render time (`reveal_identifier`, 5.3), with access logging |
| P4 | Alternate-ID resolver (12.3) |
| P5 | Tests: single ID, several IDs, no match, no active addresses, consent clamp, inactive addresses excluded, priority order |
