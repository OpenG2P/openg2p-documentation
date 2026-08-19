---
description: >-
  Adapting the Disability Registry to your country or programme — what is
  configuration, what is seed data, and what actually needs code.
---

# Customisation

The registry ships country-agnostic on purpose. Most of what a country needs to
change is **not** a code change, and knowing which layer a change belongs in is
most of the work.

Four layers, cheapest first:

| Layer | Change it by | Needs a rebuild? | Examples |
|---|---|---|---|
| **1. Environment** | Helm values at install | No | Hostname, demo-data switches, which programmes' dashboards import |
| **2. Country pack** | Master Data Service | No | Geography, code lists, programme names |
| **3. Seed metadata** | SQL in the extension, then rebuild `db-seed` | db-seed only | New field on a screen, new section, new tab, dropdown options, theme |
| **4. Domain code** | Python in the extension, then rebuild all images | All images | A new register, a new validation rule, a changed DCI mapping |

Work down the list. If a change can be made at layer 2, making it at layer 4
means maintaining a fork of the registry forever.

## 1. Geography and code lists — use a country pack

**Do not edit the shipped code lists to add your country's values.** Load a
country pack into the Master Data Service instead and let the registry pick it
up:

```yaml
registry:
  dbSeed:
    loadAttributes: true     # copy the country's code lists from Master Data
    syncGeoWidgets: true     # match the geo dropdowns to the loaded hierarchy
```

`loadAttributes` replaces any list the pack also defines; `syncGeoWidgets`
rewrites the location dropdowns to the hierarchy depth and level names Master
Data actually holds. This is what lets one image serve any country — and it is
why the registry declares no country anywhere.

Geography is seeded by the **master-data** chart (`geoSeed.countryPack`), not by
the registry. Declaring a country in two charts is how registry records end up
pointing at places Master Data has never heard of.

## 2. Programmes

`PROGRAM_NAME` is a code list, deliberately not an enum, because a country's
programmes are its own. The shipped values are generic archetypes — disability
allowance, caregiver allowance, assistive device grant, rehabilitation services,
inclusive education, vocational training, employment quota, housing adaptation,
transport concession.

Replace them from your country pack, or edit them in the staff portal under
**Configuration → Attributes**. No rebuild.

## 3. Adding or changing a field

A field is a **seed-metadata** change, not a code change, *provided the column
already exists*. The metadata is what decides which fields appear, on which
section, with which dropdown.

If the column does **not** exist, it is a code change: add it to the model mixin
(so the register, history and intake tables all get it), the Pydantic schema, and
then the metadata.

{% hint style="danger" %}
**Field names must agree in four places** — the ORM column, the section JSON in
`g2p_register_sections.sql`, the DCI templates, and the reporting views. A
mismatch produces a blank field, an empty dropdown or a missing key, and **never
an error**. The registry ships `test/test_metadata_consistency.py` which turns
each of those into a build failure; run it after any change.

The full list is in
[Contracts that fail silently](../registry/developer-zone/building-a-registry/contracts-that-fail-silently.md).
{% endhint %}

### Code lists are generated

Dropdown values in `meta_data/lookup-data/*_defaults.sql` are **derived from the
domain enums** by a script, and the translation keys from the section metadata:

```bash
./scripts/generate-code-lists.py      # after editing models/enums.py
./scripts/generate-translations.py    # after adding a widget label
```

CI fails if the checked-in SQL is stale. Edit the enum, re-run the script — never
hand-edit the generated SQL, because a value in one and not the other makes the
field refuse to save or the option unreachable, silently.

## 4. Assessment vocabulary

Two fields carry the assessment, and countries differ on both:

* **`impairment_level`** ships as the Washington Group four-point scale
  (`NO_DIFFICULTY` … `CANNOT_DO_AT_ALL`), chosen because it is what national
  censuses already collect — a registry seeded from census or survey data needs
  no re-coding.
* **`disability_status_level`** ships as `MILD` / `MODERATE` / `SEVERE` /
  `PROFOUND`, the severity band an assessment board assigns.

If your certification regime uses percentage bands or a national scale, map it
onto `disability_status_level` and keep the Washington Group scale for
`impairment_level` — that keeps your data comparable internationally while your
certificate stays legally correct.

## 5. Disability certificates and re-assessment

The master register carries `disability_certificate_number`,
`certificate_issue_date`, `certificate_expiry_date` and
`next_reassessment_date`, and the reporting layer derives `certificate_expired`
and `reassessment_overdue` from them.

A lapsed certificate is a **legitimate state** the registry must represent — the
validation deliberately allows an expiry date in the past, because that is
precisely the population a renewal drive needs to find. Do not add a rule
forbidding it.

Verifiable credentials for the certificate are left **unconfigured** on purpose
(`g2p_registry_vc_configurations.sql` ships empty): issuing one is a legal act
tied to a country's certification regime, and a generic descriptor would be
recognised by nobody. To enable it, add a row referencing the register and intake
form, and a matching `VERIFIABLE_CREDENTIAL` row in `g2p_input_mechanisms.sql`.

## 6. Branding and theme

Registry name, logo and theme live in
`meta_data/registry-configurations/`. The shipped theme is chosen for contrast
rather than brand — `#1F4E79` on white is 8.6:1, comfortably past WCAG 2.1 AA.

To use the standard OpenG2P palette instead, point the configuration at the
factory theme:

```sql
registry_theme_id = '68721343-ea47-4675-94da-0437d688e9fe'   -- OpenG2P-Theme
```

{% hint style="warning" %}
If you replace the palette with national brand colours, **check the contrast**.
Caseworkers read these screens all day, and many public-sector bodies are bound
by an accessibility standard for their internal systems. The OpenG2P yellow
`#EABB13` on white is about 1.8:1, well under the 4.5:1 needed for body text.
{% endhint %}

## 7. Approval workflow

`awe_meta_data/` seeds a two-stage policy — case officer, then disability
assessment officer — with `forbid_self_approval` and `forbid_repeat_approvers`
both **on**. That is stricter than the platform's reference registry and
deliberate: disability status determines entitlement, so one official must not be
able to both record and approve it.

The shipped approver rules name demo users. Replace them with role-based rules
for your own officials before going live.

## 8. Data sharing

The **top-level keys** of `templates/dr_person_to_dci.json.j2` are the consent
scopes a partner can be granted. Adding a key creates a scope; renaming one
silently revokes access for every partner consented to the old name.

The registry ships a deliberately conservative PII posture: names, identifiers
and certificate numbers are withheld from every reporting view, and unlike the
social registry `program_name` is **not** allowed through — paired with a
person-level disability attribute in a thin geography it becomes an indirect
identifier. Programme aggregates are available on `dr_rpt_person.programmes`
instead.

## What you should not change

* **The register mnemonics and their frozen UUIDs.** Metadata rows,
  templates and AWE bindings all reference them as literals.
* **`fixtures.py` symbol names** in the sanity suite — the inherited harness
  imports them by name.
* **The `SUPPORT_NEED` score as an eligibility gate.** Re-weight it freely; do
  not wire it to entitlement.
