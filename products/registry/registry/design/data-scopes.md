---
description: Consent data scopes — named groups of a registry's own fields, independent of any output standard
---

# Data Scopes

A **data scope** is what a consent, and a Consent Manager (CM) policy, names when it says which data a partner may receive from a registry. In the OpenG2P Registry a scope is a **named group of the registry's own fields** — not a key of a DCI record or of any other output format. The registry keeps a **scope catalogue** that maps each scope ID to its fields, version by version, and filters every record to the consented fields **before** rendering it in any output format.

So:

* a consent or a policy never depends on how a record is rendered (DCI today, another standard tomorrow);
* a field can be renamed in the registry without touching any consent or policy;
* a scope can be narrowed at any time, and widening it never reaches consents given before.

## Scope IDs

A scope ID is `<consent_data_controller>.<name>`, for example `farmer-registry.land` or `crop-sown-registry.crop_season`.

* `<consent_data_controller>` is the registry's data-controller ID in the Consent Manager: setting `consent_data_controller`, Helm value `global.consentDataController`, which defaults to the registry variant (`global.registryVariant`).
* `<name>` is letters, digits, `_` and `-`.

A scope ID is **permanent**: it is never renamed and never reused for something else. Its label and description may change. A registry ignores scope IDs from another controller's namespace and scope IDs it does not know: they grant nothing (fail closed).

## Where scopes come from

**Default scopes — one per register section.** Without a catalogue, the registry offers one scope per register section: `<controller>.<section_mnemonic>`, covering every field the section shows (its fields are worked out from the section's UI schema). A section that shows nothing shareable (a score display, for example) gives no scope.

**The extension's catalogue.** An extension can ship catalogue files, every `*.json` in `<extension package>/meta_data/data-scopes/` (the setting `data_scopes_catalogue_path` overrides the directory). Files are merged in name order. A catalogue can:

* **relabel** a section scope: an entry named like the section, with a `label` and `description` and no `fields`;
* **exclude** section scopes: `exclude_section_scopes`, a list of section mnemonics, or `true` for no default scopes at all (only the catalogue's own scopes are offered);
* **add finer scopes**: a subset of a section's fields, or fields across sections and registers;
* **declare field renames**: `field_renames`, old reference → new reference (see [Changing a scope](#changing-a-scope)).

```json
{
  "exclude_section_scopes": ["fr_docs", "fr_farmer_header"],
  "field_renames": {},
  "scopes": [
    {"name": "fr_farmer_land", "label": "Land parcels", "description": "Each parcel's size, tenure and use."},
    {"name": "contact", "label": "Contact details", "description": "Phone numbers and email addresses.",
     "fields": ["Farmer.phone_numbers", "Farmer.emails"]}
  ]
}
```

Other top-level keys (for example `_notes`) are ignored.

### Field references

A scope's `fields` is a list of references to the registry's internal record:

| Reference | Means |
| --- | --- |
| `section:<section_mnemonic>` | every field the section shows (a default scope is exactly this) |
| `<Register>.<field>` | one column of a register, e.g. `Farmer.phone_numbers` |
| `<Register>.*` | all of a register's own fields, e.g. `Land.*` (a child register's whole records) |
| `<Register>.documents`, `<Register>.documents.<label>` | the record's documents, all or one label |
| `<Register>.activity.<field>` | a column of an activity register's activities, e.g. `CropSown.activity.crop` |
| `<Register>.context.<field>` | a column of a context's current state (the projection), e.g. `CropSown.context.stage` |
| `<Register>.aggregate.<field>` | a column of an aggregate (roll-up) row, e.g. `CropSown.aggregate.aggregate_value` |

`<Register>` is the register mnemonic. `.*` works for every form. An aggregate's figures are one JSON column (`aggregate_value`), so aggregates can be scoped by column only.

The catalogue is **validated** against the extension's models and register sections when it is published. An unknown register, field or section refuses the whole catalogue, listing every problem, and the previously published catalogue stays in force.

## Publishing and versions

The services publish the catalogue themselves (the extension package with its `meta_data` is in every service image): at start-up, and again whenever a running service notices that the register sections or the catalogue changed (checked at most every `data_scopes_sync_check_seconds`, default 60). Publishing is idempotent:

* a new scope → version 1, effective now;
* a scope whose fields changed → a new version, effective now;
* unchanged fields → nothing;
* a scope no longer offered → **retired**: its versions stay, consents that name it keep what it last meant until they expire.

Versions are **immutable** (the database rejects updating or deleting them) and scopes are never deleted.

## Enforcement

For each search item the registry's partner API gets the consent's effective scopes from CM (grant ∩ policy) and reads the consent's issue time (`iat`, else `issued_at`). For each scope, the fields allowed are:

> fields of the version in effect when the consent was issued **∩** fields of the scope's current version

* A field **added** after the consent was given never reaches it (widening is not retroactive).
* A field **removed** since (e.g. for privacy) is gone for every consent (backdating a consent cannot widen anything).
* A **renamed** field keeps its meaning (see below).
* For a **retired** scope its last version stands in for "current".
* A consent with no issue time reads each scope's first version (the narrowest reading).

The internal record (with its linked child-register records, or the activity, context-state or aggregate row) is filtered to the allowed fields, **then** rendered. A field outside the consent is null; a linked register's records the consent does not reach become an empty list. The output template never sees a field outside the consent. The consent-subject check runs on the unfiltered record, so identifying fields are used for the check even when no scope lets them out.

Searches across subjects (an activity register's aggregates with no subject, for a benefits run) have no per-person consent: the partners allowed to make them, and their scopes, are configured by the registry operator (`dci_bulk_aggregate_partners`: `sender_id` → scope IDs; a bare name means this registry's scope). Those scopes apply at their current versions.

## Changing a scope

| Change | What to do | Effect on consents and policies |
| --- | --- | --- |
| Relabel / redescribe | edit `label` / `description` | none |
| **Rename a field** (same meaning) | change the reference in the scope and add `"field_renames": {"Farmer.phone": "Farmer.phone_number"}` | none: the new version records the rename and consents keep reading the field |
| **Narrow** (remove a field) | remove it from `fields` | safe: no consent gets it any more |
| **Widen** (add a field) | add it to `fields` | only consents given after the new version get it |
| **Split or merge** | add scopes with **new** names and drop the old scope | the old scope is retired and keeps honouring its consents; move policies to the new IDs |
| Rename a scope | not possible | add a new scope and retire the old one, as for a split |

A section scope follows its section: when a section's widgets change, the scope gets a new version (with the same rules). Renaming a section retires its default scope; an extension that wants stable IDs names its scopes in the catalogue (referencing the section with `section:<mnemonic>`), so a renamed section refuses the catalogue instead of silently retiring a scope.

## APIs

The catalogue holds field references, never values.

* **Partner API:** `POST /partner/data_scopes` with a signed partner envelope (`header`, `message`, `signature`, checked like every other partner call). The unsigned `GET /partner/data_scopes` is **off by default** (HTTP 403 pointing to the POST); an operator who wants to publish the catalogue openly turns it on with `REGISTRY_PARTNER_API_DATA_SCOPES_PUBLIC_GET_ENABLED=true` (Helm `global.partnerDataScopesPublicGetEnabled`).
* **Staff API:** `GET /data_scopes` (and `POST /data_scopes/get_data_scopes`), for the staff UI and, later, for choosing scopes when writing a CM policy.

```json
{
  "data_controller": "farmer-registry",
  "data_scopes": [
    {
      "scope_id": "farmer-registry.land",
      "name": "land",
      "data_controller": "farmer-registry",
      "label": "Land parcels",
      "description": "Each land parcel's ID, size and unit, tenure, …",
      "status": "ACTIVE",
      "source": "EXTENSION",
      "current_version": 1,
      "retired_at": null,
      "versions": [
        {"version": 1, "effective_from": "2026-10-05T10:00:00",
         "fields": ["section:fr_farmer_land", "Land.functional_record_id"],
         "resolved_fields": ["Land.current_land_use", "Land.functional_record_id", "Land.land_size", "…"],
         "renamed_fields": null}
      ]
    }
  ]
}
```

`fields` is what the catalogue says; `resolved_fields` is the concrete field list (sections expanded) that enforcement uses.

## Who uses scope IDs

* **Partners** ask for consent with `grants: [{data_controller, data_scopes}]`, where `data_scopes` are this registry's scope IDs. See the [Consent Manager partner integration guide](../../../../consent-management/partner-integration-guide.md).
* **Registry administrators** set a partner's CM policy `allowed_data_scopes` to scope IDs from the catalogue. See [Partner onboarding and policy](../../../../consent-management/design/partner-onboarding-and-policy.md).
* **CM** treats scopes as opaque strings (`effective = grant ∩ policy`); it needs no change when a registry changes its catalogue.

See also [Consent-aware data sharing](../features/consent-aware-data-sharing.md) and [Partner APIs](partner-apis.md).
