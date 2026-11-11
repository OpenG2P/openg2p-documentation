# Country Implementation Guide

This guide is the end-to-end spine for building a **country-specific PBMS
implementation**: taking the generic PBMS platform and wiring it to a country's own
registry (or a new register type), its own branding, and its own deployment.

It ties together the focused sub-guides — [Registry Database Contract](./registry-database-contract.md),
[Registry Add-ons](./registry-addons/README.md), [Registry Connectors](./registry-connectors/README.md),
[Summary Views](./summary-view/README.md) and [Theme Extension](./theme-extension.md) — into
one ordered sequence. Read this page first, then dive into the sub-guide referenced at each
step.

PBMS is split across two repos:

- [**pbms**](https://github.com/OpenG2P/pbms) — the platform: PBMS core (Odoo), the background
  tasks, the APIs, their base images and the `openg2p-pbms-platform` Helm chart. A country
  implementation does not change it.
- [**pbms-connectors**](https://github.com/OpenG2P/pbms-connectors) — the registry layer on top: the
  Odoo registry add-ons, the theme extension, the registry adapters, the images that a cluster runs
  and the `openg2p-pbms` Helm chart you install. This is where a country implementation lives (fork it).

The three registers that ship — **`farmer`**, **`household`** and **`disability`** — are the running
examples. A new country register (call it `<type>`) follows the same pattern.

## How the pieces fit together

A PBMS deployment reads from three kinds of data:

- **PBMS core DB** — Odoo. Holds programs, eligibility / entitlement / priority rules, and
  the register *type* definitions.
- **The registers** — the source registries PBMS reads. Each register has its own connector and
  connection string: `db` reads a table or view in the registry database
  ([Registry Database Contract](./registry-database-contract.md)); `dci` calls the registry's Partner
  API ([Registry Connectors](./registry-connectors/README.md)). Registers can live in different
  databases or different registry installations.
- **Bg-task DB** — beneficiary lists and computed summaries.

The register *type* string (`target_registry`) is the thread that runs through all of them:
you pick it on a rule in Odoo, it selects the register's model, and it selects the Python classes
(`REGISTERS` in `registers.py`, through `RegistryFactory.get_registry_class(target_registry)`) that run
eligibility, entitlement, search and summary computations over that register's connector. A country
implementation is, essentially, defining a new `target_registry` end to end.

## Step 1 — Expose the register

Start from the data, and decide how PBMS reaches it:

- **`db`**: expose the register in the registry database as a table or view with an
  `internal_record_id` primary column and the columns the register's model declares. This is
  specified in the [Registry Database Contract](./registry-database-contract.md).
- **`dci`**: the registry's Partner API serves the register over DCI sync search. Its outgoing template
  decides the record shape, which the register's `flat()` maps onto column names
  ([Registry Connectors](./registry-connectors/README.md#registry-requirements-for-the-dci-connector)
  lists what the registry must allow).

The column names you settle on here are referenced by every later step.

```sql
CREATE VIEW g2p_register_farmers AS
SELECT
    r.registry_pk::varchar AS internal_record_id,
    r.given_name           AS first_name,
    r.family_name          AS last_name,
    r.sex                  AS gender,
    r.age                  AS estimated_age
    -- ...every other column the model declares
FROM my_country_farmer_registry r;
```

## Step 2 — Add the Odoo registry add-on

PBMS core (Odoo) needs a model that mirrors your register so that program staff can build
eligibility / entitlement / priority **domains** against it. The registry adapters evaluate those
domains on the register's columns, so the Odoo field names must match them.

Follow the [Registry Add-ons](./registry-addons/README.md) sub-guide. The pattern, using the
`g2p_registry_addon` module in pbms-connectors:

1. **Create the concrete model** inheriting the abstract `g2p.registry`. See
   `odoo/g2p_registry_addon/models/farmer_registry.py`:

   ```python
   from odoo import fields, models

   class G2PFarmerRegistry(models.Model):
       _name = "g2p.register.farmers"
       _description = "Farmer Registry"
       _inherit = "g2p.registry"

       first_name = fields.Char(string="First Name")
       gender = fields.Selection(selection=[("MALE", "Male"), ("FEMALE", "Female"), ...])
       estimated_age = fields.Integer(string="Estimated Age")
       # ...one field per register column
   ```

   Register it in `models/__init__.py`.

2. **Register the type → model mapping** in `odoo/g2p_registry_type_addon/models/registry_type.py`.
   Add your type to both `MODEL_MAPPING` and the `G2PRegistryType` enum:

   ```python
   class G2PTargetModelMapping:
       MODEL_MAPPING = {
           "farmer": "g2p.register.farmers",
           "household": "g2p.register.households",
           "disability": "g2p.register.persons_with_disability",
           # "<type>": "g2p.register.<types>",
       }

   class G2PRegistryType(Enum):
       FARMER = "farmer"
       HOUSEHOLD = "household"
       DISABILITY = "disability"
       # <TYPE> = "<type>"
   ```

   This is what makes your type appear in the **Target Registry** dropdown on rule
   definitions (`G2PRegistryType.selection()` feeds
   `g2p.eligibility.rule.definition.target_registry` and the entitlement / priority
   equivalents) and what lets Odoo find the right model (`get_target_model_name`).

3. **Add security rules.** In `odoo/g2p_registry_addon/security/ir.model.access.csv`
   add read/write rows for your model. The model id follows Odoo's convention
   `model_g2p_register_<types>`:

   ```csv
   g2p_register_farmer_read,Read Farmer Registry,model_g2p_register_farmers,g2p_pbms.group_beneficiary_list_viewer,1,0,0,0
   g2p_register_farmer_write,Write Farmer Registry,model_g2p_register_farmers,g2p_pbms.group_beneficiary_list_editor,1,1,1,1
   ```

## Step 3 — Add the registry adapter

The Python side is the `registry-adapters` extension (`extensions/registry-adapters` in
pbms-connectors). It runs eligibility, entitlement, search and summary computations against your
register, over the `db` or `dci` connector. The full walkthrough is the
[Example Implementation Workflow](./registry-connectors/example-implementation-workflow.md); in short:

1. Add the type to the adapters' `G2PRegistryType` (`models/enum.py`). It is a separate enum from the
   Odoo one, but the values must match.
2. Add the register's SQLAlchemy model (`models/`) and search-result schema (`schema/`).
3. Add `computations/<type>.py` with two small classes: one on `RegistryDB` (set `model` and
   `payload`) and one on `RegistryDCI` (set `payload`, `reg_type`, `reg_record_type`, `match_field`,
   `fields` and `flat()`). The base classes implement eligibility, priority, multipliers and search.
4. Add the `(DB, DCI)` pair to `REGISTERS` in `registers.py`. The factory needs no change.
5. Add the register's summary table to `get_models()` in `migrate.py`.
6. Add `global.registers.<type>` and its two `REGISTRY_ADAPTERS_*` lines to
   `helm/openg2p-pbms/values.yaml`, and a register block to `helm/openg2p-pbms/questions.own.yaml`.

`test/test_register_config.py` fails CI if the enums, `registers.py` and the chart disagree.

## Step 4 — Add or extend the summary views

Each register type has its own summary shape (age quartiles for farmers; household-size and
overcrowding quartiles for households; age and unmet-needs quartiles for disability). Define the
summary model and schema, and compute them in the register's `<Type>Summaries` mixin in
`computations/_summary.py`, which both its DB and DCI classes share.

The two flavours of summary — eligibility and entitlement — and how they are built and read
are covered in the [Summary Views](./summary-view/README.md) sub-guide
([eligibility](./summary-view/eligibility-summary-view.md),
[entitlement](./summary-view/entitlement-summary-view.md)). `FarmerSummaries` is the fullest worked
example, including gender-split entitlement statistics.

## Step 5 — (Optional) Fork the theme extension for branding

For a country deployment you usually want your own login page, favicon, logo, fonts and
company branding. This is the `pbms_theme_extension` Odoo module (`odoo/pbms_theme_extension` in
pbms-connectors). Forking it — login-page templates, favicon/logo assets, fonts, and the
`res.company` / `res.users` overrides — is covered in the [Theme Extension](./theme-extension.md)
sub-guide. This step is independent of the registry work in steps 1–4 and can be done at any time.

## Step 6 — Build the images

pbms-connectors builds three thin images on top of the pbms base images:

- **`openg2p-pbms-odoo`** (`docker/odoo/Dockerfile`) — copies `pbms_theme_extension`,
  `g2p_registry_type_addon` and `g2p_registry_addon` into the addons path.
- **`openg2p-pbms-celery`** (`docker/celery/Dockerfile`) — installs the registry adapters. The Celery
  workers and beat producers both run it.
- **`openg2p-pbms-staff-api`** (`docker/staff-portal-api/Dockerfile`) — installs the registry adapters
  for beneficiary search and summaries.

The pbms version they build on is pinned in each Dockerfile (`ARG PBMS_VERSION`), in step with the
`openg2p-pbms-platform` dependency in `helm/openg2p-pbms/Chart.yaml`.

In a fork, CI builds and publishes the images and chart on every push to `develop`. To build by hand
and push to a registry you control:

```bash
docker build -f docker/odoo/Dockerfile -t myregistry/openg2p-pbms-odoo:mycountry .
docker build -f docker/celery/Dockerfile -t myregistry/openg2p-pbms-celery:mycountry .
docker build -f docker/staff-portal-api/Dockerfile -t myregistry/openg2p-pbms-staff-api:mycountry .
```

## Step 7 — Install the chart and configure the registers

Install the `openg2p-pbms` chart (`helm/openg2p-pbms` in pbms-connectors). Platform values sit under
`pbms.`.

1. **Point each component at your image**, if you built your own:

   ```yaml
   pbms:
     odoo:
       image:
         repository: myregistry/openg2p-pbms-odoo
         tag: mycountry
     celeryWorkers:
       image:
         repository: myregistry/openg2p-pbms-celery
         tag: mycountry
     beatProducers:
       image:
         repository: myregistry/openg2p-pbms-celery
         tag: mycountry
     staffPortalApi:
       image:
         repository: myregistry/openg2p-pbms-staff-api
         tag: mycountry
   ```

2. **Configure each register's connector and connection string** (Rancher shows one group per
   register). See [Registry Connectors](./registry-connectors/README.md#configuration) for the formats:

   ```yaml
   global:
     registers:
       farmer:
         connector: db
         connectionString: postgresql://farmer_registry_user:secret@commons-postgresql:5432/farmer_registry
       household:
         connector: dci
         connectionString: http://household-registry-partner-api/dci/registry/sync/search
   ```

   For a `dci` register, turn partner signature validation and consent enforcement off on that
   registry ([why](./registry-connectors/README.md#registry-requirements-for-the-dci-connector)).

3. **Set the Target Registry in Odoo.** Once deployed, create/configure programs and
   set the **Target Registry** on the eligibility / entitlement / priority rules to your new
   `<type>`. That value selects the register's model and its classes in `REGISTERS`, closing the
   loop. Pick the register's connector before programs use it: beneficiary lists built with one
   connector store different registrant IDs from the other.

## End-to-end checklist

| Step | What | Where (pbms-connectors) |
| ---- | ---- | ----- |
| 1 | Register exposed: a table or view with `internal_record_id` (`db`), or DCI search on the Partner API (`dci`) | Registry / [contract](./registry-database-contract.md) |
| 2 | Odoo model `g2p.register.<types>`, `MODEL_MAPPING`, enum, security CSV | `odoo/g2p_registry_addon`, `odoo/g2p_registry_type_addon` |
| 3 | Adapters enum, model, schema, `computations/<type>.py`, `registers.py`, `migrate.py`, chart values and questions | `extensions/registry-adapters`, `helm/openg2p-pbms` |
| 4 | Summary model + schema + `<Type>Summaries` | `computations/_summary.py` + [summary view](./summary-view/README.md) |
| 5 | (Optional) branding | `odoo/pbms_theme_extension` / [theme extension](./theme-extension.md) |
| 6 | Build images | `docker/` (CI on `develop`) |
| 7 | Install the chart, set each register's connector and connection string, set Target Registry | `helm/openg2p-pbms`, Odoo |
