---
description: >-
  What a country changes in the Livestock Registry — lists, locations, the
  Animal and Vet IDs, forms, approvals, events, sharing — and where each change
  is made, with Ethiopia as the example.
---

# Customisation

The Livestock Registry ships generic: no field assumes a country. A country sets its lists, its geography, the IDs' shape, its approvers and, if it must, the forms. This page says where each change is made. The examples are Ethiopia's, which ship in the ETH country pack.

## Where a change is made

Work down the table. Make each change at the first layer that can carry it.

| Layer | Change it in | Then | Examples |
| --- | --- | --- | --- |
| **1. Install settings** | Helm values (Rancher form or YAML) | Upgrade the release | Hostname, sample data, the IDs' length, DCI search fields |
| **2. Master Data** | The country pack, or the Master Data admin UI | Nothing: read live | A new vaccine, disease, treatment, vet cadre; a kebele level in the geography |
| **3. Registry definitions** | `scripts/livestock_definitions.py`, then regenerate the seed SQL | Rebuild the db-seed image | A new field on a form, a new section or tab, search columns, a duplicate check, a new event type, indicators |
| **4. Other seed metadata** | SQL and JSON under `meta_data/` and `awe_meta_data/` | Rebuild all images | Approvers and approval stages, reporting views, data scopes, registry name and theme |
| **5. Events register configuration** | `meta_data/activity-config/LivestockEvent.json` | Rebuild all images | Warnings, search fields, list columns, what a batch carries from row to row |
| **6. Domain code** | Python in `livestock-extension` | Rebuild all images | A new column, the checks, the current state, the IDs' prefix |

Paths are in the [repository](https://github.com/OpenG2P/live-stock-registry), under `livestock-extension/src/openg2p_registry_livestock_extension/` unless they start with `scripts/`.

## Lists in Master Data

The registry keeps **no lists**. Every coded field is checked against Master Data, live. The lists are in the **agriculture domain** of the country pack ([`openg2p-data`, `packs/<country>/domains/agriculture`](https://github.com/OpenG2P/openg2p-data/tree/develop/packs/ETH/domains/agriculture)), loaded when commons-services is installed with **Dataset Themes** `agriculture`. Species and breed type are the Farmer Registry's `LIVESTOCK_TYPE` and `LIVESTOCK_BREED`; gender is the core `GENDER` list.

**Every pack carries the same codes.** A country changes the labels and adds values; it does not rename codes, because the sample data and the reports use them. The Kamuntu pack (`XKM`, fictitious) has generic labels; the ETH pack has Ethiopia's:

| List | Values | Ethiopia (ETH) |
| --- | --- | --- |
| `LIVESTOCK_SEX` | Female, male (entire), castrated male | The same, "castrated male (e.g. ox)" |
| `LIVESTOCK_ACQUISITION` | Born in the herd, purchased, gift, inherited, distributed by a programme, other | Programme: e.g. restocking, PSNP livelihoods |
| `LIVESTOCK_VACCINE` | FMD, lumpy skin disease, anthrax, blackleg, CBPP, pasteurellosis, PPR, sheep and goat pox, CCPP, Newcastle disease, African horse sickness, camel pox, rabies, other | The same |
| `LIVESTOCK_DISEASE` | The vaccinable diseases, trypanosomiasis, internal and external parasites, mastitis, pneumonia, diarrhoea, injury, other, unknown | The same |
| `LIVESTOCK_TREATMENT` | Deworming, acaricide, antibiotic, trypanocide, anti-inflammatory, vitamins and minerals, wound care, surgery, other | The same |
| `LIVESTOCK_BUYER_TYPE` | Another farmer, trader, livestock market, cooperative, abattoir, exporter or feedlot, other | The same |
| `LIVESTOCK_DEATH_CAUSE` | Disease, accident, predator, drought, old age, slaughtered by the household, unknown, other | The same |
| `LIVESTOCK_VET_CADRE` | Veterinarian, animal health technician, animal health assistant, community animal health worker | Veterinarian (DVM), Animal Health Technician (diploma), Animal Health Assistant (certificate), CAHW |
| `LIVESTOCK_VET_EMPLOYER` | Government veterinary service, private practice, NGO, cooperative, community | Government (woreda veterinary clinic or animal health post), … |

* **Codes carry their list's prefix:** `LSEX_FEMALE`, `LVAC_LSD`, `LDIS_PPR`, `LTRT_DEWORMING`, `LBUY_TRADER`, `LDTH_DISEASE`, `LVC_CAHW`.
* **Adding a value** is a change to the pack or in Master Data's admin UI. No registry change.
* The CI build checks that every list and code the registry uses is in every pack, with the same codes.

## Locations

Where an animal is kept and the area a vet serves are units of the country's geography, at **any level**: the form's geography widget lists the levels Master Data serves. The ETH pack's geography stops at the woreda, so today that is the lowest. The reports read the levels by position, so a country with five levels gets five columns.

## Animal ID and Vet ID

* **Length:** the chart's ID generator pools, default ten digits for animals and eight for vets:

  ```yaml
  registry:
    idgenerator:
      idGenerator:
        appConfig:
          idTypes:
            animal:
              idLength: 10
            veterinarian:
              idLength: 8
  ```

* **Generated, never typed:** after the last approval stage the record is created, and a Celery worker gets the ID from the ID generator within seconds ([Functional ID generation](../../../products/registry/registry/design/functional-id-generation.md)). The form shows it read-only.
* **Prefix:** none ships. A prefix is set in `register_domain/id_generator/g2p_id_generator_service.py`, a code change.
* **An existing identification system** (ear tags, RFID boluses) keeps its numbers in the ear tag field; the Animal ID is the registry's own.

## Forms and fields

The sections, tabs, intake forms, search columns, filters and duplicate checks are all in `scripts/livestock_definitions.py`. To change them:

```bash
# edit scripts/livestock_definitions.py, then
python3 scripts/build_seed_sql.py          # regenerate the seed SQL
python3 scripts/build_seed_sql.py --check  # what CI runs
```

Commit both. A new **field** also needs a column on the model (`register_domain/models/`) and the schema; the registry adds missing columns to an existing install's tables when it starts. A field that only rearranges the form needs no code.

## Approvals

Registrations and changes are approved in AWE under the policy keys `registry.intake_form.animal`, `registry.change_request.animal`, `registry.intake_form.veterinarian` and `registry.change_request.veterinarian`. The shipped policies (`awe_meta_data/`) are sample data: two stages with the demo approvers `alex.carter` and `nina.patel`, loaded only with **Load Sample Data**. In production, set the policies up in AWE's admin portal under those keys, with the country's approvers, for example the woreda livestock office, then the zone ([Approval policies and demo staff](../../../products/registry/registry/deployment-and-extension/country-data-and-seeding.md#approval-policies-and-demo-staff)).

## Events

* **Fields and types:** `ACTIVITY_TYPES` in `scripts/livestock_definitions.py`. Regenerate as above.
* **Verification:** on for vaccinations and treatments (`requires_verification`), off for births, sales and deaths.
* **Warnings:** `meta_data/activity-config/LivestockEvent.json` (`rules`); the vet, mother, buyer and death checks are in the domain service.
* **A vet's or an animal identification system** is onboarded as a partner in the registry's Partner Management, with its signing key, and sends events through the partner API.

## Sharing

* **Data scopes:** `meta_data/data-scopes/10_livestock.json`. Narrow or widen a scope by its fields; never rename a scope: add a new one ([Changing a scope](../../../products/registry/registry/design/data-scopes.md#changing-a-scope)).
* **DCI search fields** (Helm, `registry.partnerApi.envVars`): `REGISTRY_PARTNER_API_DCI_ID_TYPE_COLUMNS` (which column an ID type searches: `UIN` the owner's national ID, `FARMER_ID` the owner's Farmer ID), `REGISTRY_PARTNER_API_DCI_ALLOWED_SEARCH_FIELDS` (the columns an expression may name) and `REGISTRY_PARTNER_API_DCI_CONSENT_SUBJECT_FIELDS` (the columns that make an animal the consent subject's: the owner's).
* **DCI output:** the templates `templates/animal_to_dci.json.j2` and `templates/livestock_event_to_dci.json.j2`, and the current state's `meta_data/activity-config/templates/livestock_dci_state.json.j2`.

## Calendar

Dates are entered in the Gregorian calendar. A country calendar (for example the Ethiopian calendar, which the Crop Sown Registry offers for some fields) is not configured.

## Branding and languages

The registry's name, logo and theme are in `meta_data/registry-configurations/`. Labels are plain English and shown as written; a translation for another language goes in the languages file.

**Theme.** The registry ships its own theme, **Livestock Registry Theme**: a light orange background (`#F4A261`) with a deep burnt-orange accent (`#8A3A0C`), and as the home page's illustration (the theme's **Dashboard Image**) a homestead's animals and the vet who serves them. The illustration's source is `assets/dashboard_image.svg` at the repository's root; the seed carries it base64-encoded in `g2p_registry_theme_values.sql`. To change it, edit the SVG and regenerate that value.

* **An administrator** can switch to another theme, edit this one or create one in the staff portal, under **Configuration → Registry**, with the Technical Administrator role. Upgrades keep those choices: the seed inserts the theme only when it is missing, and sets the registry's theme on the first install only.
* **The login page** is not the registry's: every registry in a namespace shares the Keycloak `staff` realm and its one login theme.

**Staff portal UI.** The registry builds its own staff portal image from the platform's UI and its `ui/staff-ui/overrides/`, empty today ([UI Extendability](../../../products/registry/registry/design/ui-engineering-design/ui-extendability.md)).

## Dashboards

The dashboards are defined in `scripts/build_dashboards.py`, which writes the bundle `helm/openg2p-livestock-registry/files/lsr-dashboards.zip`. They read only the reporting views; a chart is a view, a grouping and its metrics. To change one, edit the script and rebuild the bundle against a database that has the current views (it reads their columns):

```bash
PGHOST=<host> PGPORT=5432 PGUSER=<user> PGPASSWORD=<password> LSR_DB=<database> \
  python3 scripts/build_dashboards.py
```

The bundle is deterministic: the same script and views give the same file. Upgrade the release to import it; an upgrade updates the release's own copy in Superset. Use only the chart types the bundle already uses (big number, pie, bar, table): others need a Superset plugin some installs lack. A view that changes needs the bundle rebuilt; `test/integration/test_dashboards.py` fails until it is. To turn the import off, set `registry.dashboards.enabled: false`.

## Testing a change

From a checkout of the repository, with [openg2p-data](https://github.com/OpenG2P/openg2p-data) beside it:

```bash
# No platform needed: the seed SQL is current, the platform pin is in lockstep,
# and every list and code is in each country pack (CI runs these)
python3 scripts/build_seed_sql.py --check
OPENG2P_DATA_DIR=../openg2p-data pytest test/test_code_lists_in_pack.py test/test_rp_pin_lockstep.py
```

The integration tests run the registry through the platform's services on a disposable PostgreSQL, with registry-platform checked out beside the repository: the screens, the records and their checks, the events and each animal's current state, the sample data end to end, and what a partner gets under a farmer's consent.

```bash
docker run -d --name lsr-pg -e POSTGRES_PASSWORD=postgres -p 55432:5432 postgres:16
docker exec lsr-pg psql -U postgres -c "create database lsr_test"
pip install -e <registry-platform>/core/openg2p-registry-core -e <registry-platform>/apis/openg2p-registry-partner-api \
    -e livestock-extension pytest pytest-asyncio psycopg2-binary
pytest test/integration
```

## What not to change

* **Codes** in the packs: change labels instead.
* **The register mnemonics** (`Animal`, `Veterinarian`, `LivestockEvent`) and their IDs in `livestock_definitions.py`: the models, the ID pools, the approval bindings and the data scopes depend on them.
* **Scope IDs:** consents and policies name them.
* **Generated SQL** by hand: change the definitions and regenerate.
