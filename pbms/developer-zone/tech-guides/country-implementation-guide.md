# Country Implementation Guide

This guide is the end-to-end spine for building a **country-specific PBMS
implementation**: taking the generic PBMS platform and wiring it to a country's own
registry (or a new registry type), its own branding, and its own deployment.

It ties together the focused sub-guides — [Registry Database Contract](./registry-database-contract.md),
[Registry Add-ons](./registry-addons/README.md), [Registry Connectors](./registry-connectors/README.md),
[Summary Views](./summary-view/README.md) and [Theme Extension](./theme-extension.md) — into
one ordered sequence. Read this page first, then dive into the sub-guide referenced at each
step.

Throughout, the two registry types that ship with PBMS — **`farmer`** and **`households`** —
are used as the running examples. A new country type (call it `<type>`) follows the exact
same pattern; every place you see `farmer` / `households` is a place you add your own type.

## How the pieces fit together

A PBMS deployment has three databases and several services:

- **PBMS core DB** — Odoo. Holds programs, eligibility / entitlement / priority rules, and
  the registry *type* definitions.
- **Registry DB** (`sr_session`) — the source registry PBMS reads. This is where your
  `g2p_register_<type>` view lives (the [Registry Database Contract](./registry-database-contract.md)).
- **Bg-task DB** — beneficiary lists and computed summaries.

The registry *type* string (`target_registry`) is the thread that runs through all of them:
you pick it on a rule in Odoo, it names the source table (`g2p_register_<type>`), and it
selects the Python adapter (`RegistryFactory.get_registry_class(target_registry)`) that runs
eligibility, entitlement, search and summary computations. A country implementation is,
essentially, defining a new `target_registry` end to end.

## Step 1 — Define the source-registry database view

Start from the data. Your country registry must be exposed in the registry DB as a
table/view named `g2p_register_<type>`, with an `internal_record_id` primary column and the
standard columns the adapter will read.

This is specified in full — including the exact columns for `farmer` and `households` — in
the [Registry Database Contract](./registry-database-contract.md). Do this first: the table
name and column names you settle on here are referenced by every later step.

```sql
CREATE VIEW g2p_register_farmer AS
SELECT
    r.registry_pk::varchar AS internal_record_id,
    r.given_name           AS first_name,
    r.family_name          AS last_name,
    r.sex                  AS gender,
    r.age                  AS estimated_age
    -- ...the remaining standard columns
FROM my_country_farmer_registry r;
```

## Step 2 — Add the Odoo registry add-on

PBMS core (Odoo) needs a model that mirrors your registry so that program staff can build
eligibility / entitlement / priority **domains** against it. The domain is compiled to SQL
that runs on the `g2p_register_<type>` view, so the Odoo model field names should line up
with the view columns.

Follow the [Registry Add-ons](./registry-addons/README.md) sub-guide. The pattern, using the
shipped `g2p_registry_addon` module:

1. **Create the concrete model** inheriting the abstract `g2p.registry`. The model name must
   be `g2p.register.<type>`. See `odoo/extensions/g2p_registry_addon/models/farmer_registry.py`:

   ```python
   from odoo import models, fields
   from .registry import G2PRegistry  # abstract "g2p.registry", provides internal_record_id

   class G2PFarmerRegistry(models.Model):
       _name = "g2p.register.farmer"
       _description = "Farmer Registry"
       _inherit = "g2p.registry"

       first_name = fields.Char(string="First Name")
       gender = fields.Selection(selection=[("MALE", "Male"), ("FEMALE", "Female"), ...])
       estimated_age = fields.Integer(string="Estimated Age")
       # ...one field per column your view exposes
   ```

   Register it in `models/__init__.py`.

2. **Register the type → model mapping** in the `g2p_registry_type_addon` module
   (`odoo/extensions/g2p_registry_type_addon/models/registry_type.py`). Add your type to
   both `MODEL_MAPPING` and the `G2PRegistryType` enum:

   ```python
   class G2PTargetModelMapping:
       MODEL_MAPPING = {
           "farmer": "g2p.register.farmer",
           "households": "g2p.register.households",
           # "<type>": "g2p.register.<type>",
       }

   class G2PRegistryType(Enum):
       FARMER = "farmer"
       HOUSEHOLDS = "households"
       # <TYPE> = "<type>"
   ```

   This is what makes your type appear in the **Target Registry** dropdown on rule
   definitions (`G2PRegistryType.selection()` feeds
   `g2p.eligibility.rule.definition.target_registry` and the entitlement / priority
   equivalents) and what lets Odoo translate a domain to SQL for the right model
   (`get_target_model_name`).

3. **Add security rules.** In `odoo/extensions/g2p_registry_addon/security/ir.model.access.csv`
   add read/write rows for your model. The model id follows Odoo's convention
   `model_g2p_register_<type>`:

   ```csv
   g2p_register_farmer_read,Read Farmer Registry,model_g2p_register_farmer,g2p_pbms.group_beneficiary_list_viewer,1,0,0,0
   g2p_register_farmer_write,Write Farmer Registry,model_g2p_register_farmer,g2p_pbms.group_beneficiary_list_editor,1,1,1,1
   ```

## Step 3 — Add the bg-task registry adapter

The Python side is the `openg2p-bg-task-registry-adapters` extension. It contains the
adapters that actually run eligibility, entitlement, search and summary computations against
your `g2p_register_<type>` view. This is the [Registry Connectors](./registry-connectors/README.md)
sub-guide.

1. **Declare the SQLAlchemy model** for the view, in
   `.../models/registry_<type>.py`, inheriting the base `G2PRegistry`
   (which supplies the `internal_record_id` primary key). Mirror the view columns. See
   `models/registry_farmer.py`:

   ```python
   from openg2p_pbms_models.models import G2PRegistry
   from sqlalchemy import Integer, String
   from sqlalchemy.orm import Mapped, mapped_column

   class G2PFarmerRegistry(G2PRegistry):
       __tablename__ = "g2p_register_farmer"
       first_name: Mapped[str] = mapped_column(String, nullable=True)
       gender: Mapped[str] = mapped_column(String, nullable=True)
       estimated_age: Mapped[int] = mapped_column(Integer, nullable=True)
       # ...
   ```

   Export it from `models/__init__.py`.

2. **Implement the adapter** in `.../computations/registry_<type>.py` as a subclass of
   `RegistryInterface` (`interface/registry_interface.py`). You must implement the abstract
   methods: `get_summary`, `get_summary_sync`, `compute_eligibility_statistics`,
   `compute_entitlement_statistics`, `get_registrants_by_ids`, `get_is_registant_entitled`,
   `get_entitlement_multiplier`, and `search_beneficiaries`. The base class already provides
   the SQL constructors (`construct_beneficiary_search_sql_query`,
   `construct_multiplier_sql_query`, etc.) that build `g2p_register_<type>` queries for you —
   pass your `target_registry` string through. Use `RegistryFarmer`
   (`computations/registry_farmer.py`) and `RegisterHousehold`
   (`computations/register_household.py`) as references. Export it from
   `computations/__init__.py`.

3. **Register it in the factory** (`factory/registry_factory.py`):

   ```python
   class RegistryFactory:
       @staticmethod
       def get_registry_class(target_registry) -> RegistryInterface:
           if target_registry == G2PRegistryType.FARMER.value:
               return RegistryFarmer()
           elif target_registry == G2PRegistryType.HOUSEHOLDS.value:
               return RegisterHousehold()
           # elif target_registry == G2PRegistryType.<TYPE>.value:
           #     return Registry<Type>()
           else:
               raise BGTaskException(code=BGTaskErrorCodes.INVALID_REQUEST)
   ```

4. **Add the type to the adapters' enum** (`models/registry_type.py`). This is a *separate*
   enum from the Odoo one, but the string values must match:

   ```python
   class G2PRegistryType(Enum):
       FARMER = "farmer"
       HOUSEHOLDS = "households"
       # <TYPE> = "<type>"
       OTHER = "other"
   ```

5. **Register the summary table in `migrate.py`.** The registry *view* is not created by
   PBMS (it belongs to the source registry), but the per-type **summary** table is. Add your
   summary model to `get_models()` in `migrate.py` so its table is created in the bg-task DB:

   ```python
   def get_models():
       return [
           BeneficiaryListSummaryFarmer,
           BeneficiaryListSummaryHousehold,
           # BeneficiaryListSummary<Type>,
       ]
   ```

## Step 4 — Add or extend the summary views

Each registry type has its own summary shape (age quartiles for farmers; household-size and
overcrowding quartiles for households). To add a country-specific summary, define its
summary ORM model + schema and compute it in your adapter's
`compute_eligibility_statistics` / `compute_entitlement_statistics`.

The two flavours of summary — eligibility and entitlement — and how they are built and read
are covered in the [Summary Views](./summary-view/README.md) sub-guide
([eligibility](./summary-view/eligibility-summary-view.md),
[entitlement](./summary-view/entitlement-summary-view.md)). The farmer adapter
(`computations/registry_farmer.py`) is the fullest worked example, including gender-split
entitlement statistics.

## Step 5 — (Optional) Fork the theme extension for branding

For a country deployment you usually want your own login page, favicon, logo, fonts and
company branding. This is the `pbms_theme_extension` Odoo module. Forking it — login-page
templates, favicon/logo assets, fonts, and the `res.company` / `res.users` overrides — is
covered in the [Theme Extension](./theme-extension.md) sub-guide. This step is independent of
the registry work in steps 1–4 and can be done at any time.

## Step 6 — Build the custom Docker images

Your changes live in in-repo modules and extensions, so they are baked into the images at
build time from the local source tree. There are three images to rebuild:

- **Odoo image** (`docker/openg2p-pbms-odoo/utils/Dockerfile`) — the whole `odoo/extensions`
  tree is copied into the addons path (`COPY odoo/extensions ${EXTRA_ADDONS_DIR}/pbms-extensions`),
  so your changes to `g2p_registry_addon`, `g2p_registry_type_addon` and
  `pbms_theme_extension` are picked up automatically.
- **Bg-task images** (`docker/openg2p-pbms-bg-tasks/bg-task-celery-worker/Dockerfile` and
  `.../bg-task-celery-beat/Dockerfile`) — install the adapters from local source
  (`COPY extensions/openg2p-bg-task-registry-adapters ... && pip install ...`), so your new
  adapter, model and factory changes ship here.
- **API images** (`docker/openg2p-pbms-apis/bene-portal-api/Dockerfile` and
  `.../staff-portal-api/Dockerfile`) — also install the adapters extension, for the
  beneficiary-search endpoints.

Build and push them to a registry you control, e.g.:

```bash
docker build -f docker/openg2p-pbms-odoo/utils/Dockerfile \
  -t myregistry/openg2p-pbms-core:mycountry .
docker build -f docker/openg2p-pbms-bg-tasks/bg-task-celery-worker/Dockerfile \
  -t myregistry/openg2p-pbms-bg-task-celery-workers:mycountry .
# ...repeat for beat, bene-portal-api, staff-portal-api
```

## Step 7 — Point Helm at the custom images and register the target registry

Finally, update the deployment (`deployment/charts/openg2p-pbms/`).

1. **Point each component at your image.** In `values.yaml` each service has an
   `image.repository` / `image.tag`. Override them to your custom images:

   ```yaml
   # Odoo (PBMS core)
   image:
     repository: myregistry/openg2p-pbms-core
     tag: "mycountry"
   # bg-task celery workers
   image:
     repository: myregistry/openg2p-pbms-bg-task-celery-workers
     tag: "mycountry"
   # staff-portal-api, bene-portal-api, bg-task-celery-beat-producers likewise
   ```

2. **Point PBMS at the registry DB** where your `g2p_register_<type>` view lives, via the
   `global.registryDB` block (see the [Registry Database Contract](./registry-database-contract.md)):

   ```yaml
   global:
     registryDB: 'registry'
     registryDBUser: 'registry_user'
     registryDBSecret: 'registry'
     registryDBUserPasswordKey: 'registry-db-user'
   ```

3. **Register the target registry in Odoo.** Once deployed, create/configure programs and
   set the **Target Registry** on the eligibility / entitlement / priority rules to your new
   `<type>`. That value flows down to `g2p_register_<type>` and to
   `RegistryFactory.get_registry_class("<type>")`, closing the loop.

## End-to-end checklist

| Step | What | Where |
| ---- | ---- | ----- |
| 1 | `g2p_register_<type>` view with `internal_record_id` | Registry DB / [contract](./registry-database-contract.md) |
| 2 | Odoo model `g2p.register.<type>`, `MODEL_MAPPING`, enum, security CSV | `odoo/extensions/g2p_registry_addon`, `g2p_registry_type_addon` |
| 3 | SQLAlchemy model, adapter, factory, adapters enum, `migrate.py` | `extensions/openg2p-bg-task-registry-adapters` |
| 4 | Summary model + schema + computation | adapter `computations/` + [summary view](./summary-view/README.md) |
| 5 | (Optional) branding | `pbms_theme_extension` / [theme extension](./theme-extension.md) |
| 6 | Build custom images | `docker/` |
| 7 | Point Helm at images + registry DB, set Target Registry | `deployment/charts/openg2p-pbms/values.yaml` |
