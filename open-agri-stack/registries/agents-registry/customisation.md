---
description: >-
  What a country changes in the Agents Registry — lists, the assigned area, the
  Agent ID, forms, approvals, trainings — and where each change is made, with
  Ethiopia as the example.
---

# Customisation

The Agents Registry ships generic: no field assumes a country. A country sets its lists, its geography, the Agent ID's shape, its approvers and, if it must, the forms. This page says where each change is made. The examples are Ethiopia's, which ship in the ETH country pack.

## Where a change is made

Work down the table. Make each change at the first layer that can carry it.

| Layer | Change it in | Then | Examples |
| --- | --- | --- | --- |
| **1. Install settings** | Helm values (Rancher form or YAML) | Upgrade the release | Hostname, sample data, the Agent ID's length |
| **2. Master Data** | The country pack, or the Master Data admin UI | Nothing: read live | A new position, specialization, service point type, training topic; a kebele level in the geography |
| **3. Registry definitions** | `scripts/agents_definitions.py`, then regenerate the seed SQL | Rebuild the db-seed image | A new field on a form, a new section or tab, search columns, the duplicate check, a new activity type, indicators |
| **4. Other seed metadata** | SQL under `meta_data/` and `awe_meta_data/` | Rebuild the db-seed image | Approvers and approval stages, reporting views, registry name and theme |
| **5. Training register configuration** | `meta_data/activity-config/AgentTraining.json` | Rebuild all images | Warnings, search fields, list columns, what a batch carries from row to row |
| **6. Domain code** | Python in `agents-extension` | Rebuild all images | A new column, the checks, the training summary, the Agent ID prefix |

Paths are in the [repository](https://github.com/OpenG2P/agents-registry), under `agents-extension/src/openg2p_registry_agents_extension/` unless they start with `scripts/`.

## Lists in Master Data

The registry keeps **no lists**. Every coded field is checked against Master Data, live. The lists are the `AGENT_*` lists in the **agriculture domain** of the country pack ([`openg2p-data`, `packs/<country>/domains/agriculture`](https://github.com/OpenG2P/openg2p-data/tree/develop/packs/ETH/domains/agriculture)), loaded when commons-services is installed with **Dataset Themes** `agriculture`. Gender is the core `GENDER` list.

**Every pack carries the same codes.** A country changes the labels and adds values; it does not rename codes, because the sample trainings and the reports use them. The Kamuntu pack (`XKM`, fictitious) has the generic labels; the ETH pack has Ethiopia's:

| List | Generic (Kamuntu) | Ethiopia (ETH) |
| --- | --- | --- |
| `AGENT_POSITION` | Field extension agent, senior field extension agent, extension supervisor, subject-matter specialist, extension coordinator, community animal health worker | Development Agent (DA), Senior Development Agent, DA supervisor, woreda subject-matter specialist, woreda extension coordinator, community animal health worker (CAHW) |
| `AGENT_SERVICE_POINT_TYPE` | Extension office, farmer training centre, pastoral training centre, animal health post, demonstration site | Woreda agriculture office, Farmer Training Centre (FTC), Pastoral Training Centre (PTC), animal health post, demonstration site |
| `AGENT_SPECIALIZATION` | Crop production, livestock, animal health, natural resources, irrigation, horticulture, cooperatives, agribusiness, home economics and nutrition, general | The same, with Ethiopia's names (plant science, animal science, small-scale irrigation, home economics) |
| `AGENT_QUALIFICATION_LEVEL` | Certificate, vocational levels III and IV, diploma, bachelor's, master's, doctorate | TVET Level III, TVET Level IV, diploma, degrees |
| `AGENT_EMPLOYER_TYPE` | Government, NGO, private company, cooperative, community | Government (Ministry or regional bureau of agriculture), … |
| `AGENT_EMPLOYMENT_TYPE` | Permanent, contract, temporary, volunteer | Permanent (civil service), contract, … |
| `AGENT_SERVICE_STATUS` | Active, on leave, suspended, retired, separated, deceased | The same |
| `AGENT_ASSIGNMENT_REASON` | First posting, transfer, reassignment, promotion, temporary cover, return from leave | The same |
| `AGENT_FIELD_OF_STUDY` | Plant science, animal science, animal health, natural resources, agricultural economics, agricultural extension, irrigation, horticulture, cooperatives | Rural development and agricultural extension, … |
| `AGENT_TRAINING_TOPIC` | Crop production, livestock, animal health, natural resources, soil fertility, irrigation, climate-smart agriculture, post-harvest, extension methods, digital tools, nutrition | The same |
| `AGENT_TRAINING_DELIVERY_MODE` | In person, online, blended | The same |
| `AGENT_TRAINING_RESULT` | Completed, passed, failed, attended only | The same |

* **Codes carry their list's prefix:** `AGPOS_FIELD_AGENT`, `AGSP_TRAINING_CENTRE`, `AGTOP_DIGITAL_TOOLS`.
* **Adding a value** is a change to the pack or in Master Data's admin UI. No registry change.
* **One code is used in code:** `AGST_ACTIVE`, the status that needs no status date.
* The CI build checks that every list and code the registry uses is in every pack, with the same codes.

## The assigned area

The assigned area is a unit of the country's geography, at **any level**. The form's geography widget lists the levels Master Data serves.

* **Ethiopia** assigns Development Agents to a **kebele**. The ETH pack's geography stops at the woreda (its source has no kebele level), so today the assigned area is the woreda, and the kebele is in the service point's name. Adding a kebele level to the pack makes the kebele selectable, with no registry change.
* The reports read the levels by position, so a country with five levels gets five columns.

## Agent ID

* **Length:** the chart's ID generator pool, default eight digits:

  ```yaml
  registry:
    idgenerator:
      idGenerator:
        appConfig:
          idTypes:
            agent:
              idLength: 8
  ```

* **Prefix:** none ships. A prefix (e.g. `DA-`) is set in `register_domain/id_generator/g2p_id_generator_service.py`, a code change.

## Forms and fields

The sections, tabs, intake form, search columns, filters and the duplicate check are all in `scripts/agents_definitions.py`. To change them:

```bash
# edit scripts/agents_definitions.py, then
python3 scripts/build_seed_sql.py          # regenerate the seed SQL
python3 scripts/build_seed_sql.py --check  # what CI runs
```

Commit both. A new **field** also needs a column on the model (`register_domain/models/agent.py`) and the schema; the registry adds missing columns to an existing install's tables when it starts. A field that only rearranges the form needs no code.

## Approvals

Registrations and changes are approved in AWE under the policy keys `registry.intake_form.agent` and `registry.change_request.agent`. The shipped policies (`awe_meta_data/`) have two stages with the platform chart's demo approvers, `alex.carter` and `nina.patel`. Replace them with the country's approvers, for example by role and location: the district office, then the regional office.

## Trainings

* **Fields and types:** `ACTIVITY_TYPES` in `scripts/agents_definitions.py`. Regenerate as above.
* **Verification:** off. Set `requires_verification` on an activity type to have a supervisor verify it.
* **Warnings:** `meta_data/activity-config/AgentTraining.json` (`rules`); date checks are in the domain service.
* **A learning platform** is onboarded as a partner in the registry's Partner Management, with its signing key, and sends trainings through the partner API.

## An existing agent system

A country that already keeps agents elsewhere (in Ethiopia, the Ministry of Agriculture's DA Registry) brings them in through the partner API's `ingest_data`, with an ingestion mapping from its fields to the Agent register's. The mapping is written once that system's fields are known. Sending changes back to it is not built; the registry's change events (outgestion) would carry them.

## Calendar

Dates are entered in the Gregorian calendar. Ethiopian-calendar entry, as the Crop Sown Registry offers for some fields, is not configured.

## Branding and languages

The registry's name, logo and theme are in `meta_data/registry-configurations/`. Labels are plain English and shown as written; a translation for another language goes in the languages file.

## Testing a change

From a checkout of the repository, with [openg2p-data](https://github.com/OpenG2P/openg2p-data) beside it:

```bash
# No platform needed: the seed SQL is current, the platform pin is in lockstep,
# and every list and code is in each country pack (CI runs these)
python3 scripts/build_seed_sql.py --check
OPENG2P_DATA_DIR=../openg2p-data pytest test/test_code_lists_in_pack.py test/test_rp_pin_lockstep.py
```

The integration tests run the registry through the platform's services on a disposable PostgreSQL, with registry-platform checked out beside the repository: the screens, a record with its rows, the checks, trainings and their summary, and the sample data end to end.

```bash
docker run -d --name agents-pg -e POSTGRES_PASSWORD=postgres -p 55432:5432 postgres:16
docker exec agents-pg psql -U postgres -c "create database agents_test"
pip install -e <registry-platform>/core/openg2p-registry-core -e agents-extension pytest pytest-asyncio psycopg2-binary
pytest test/integration
```

## What not to change

* **Codes** in the packs: change labels instead.
* **The register mnemonics** (`Agent`, `AgentSpecialization`, `AgentQualification`, `AgentTraining`) and their IDs in `agents_definitions.py`: the models, the ID pool and the approval bindings depend on them.
* **Generated SQL** by hand: change the definitions and regenerate.
