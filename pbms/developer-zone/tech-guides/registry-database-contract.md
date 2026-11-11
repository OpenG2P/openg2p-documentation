# Registry Database Contract

This is the contract between a **source registry** (the system of record for your beneficiaries, for
example an OpenG2P Farmer Registry or Social Registry) and PBMS, for registers read with the **`db`
connector**. With that connector PBMS runs SQL directly against a table or view in the registry
database, whose name and columns are fixed by the register's SQLAlchemy model. If the registry
exposes that table or view as described here, PBMS works unchanged.

A register read with the **`dci` connector** does not use this contract: PBMS calls the registry's
Partner API instead (see [Registry Connector](./registry-connectors/README.md)).

The end-to-end sequence that uses this contract is in the
[Country Implementation Guide](./country-implementation-guide.md).

## The table or view

Every register is identified by a short **register type**, the `target_registry`. Its SQLAlchemy model
in the [pbms-connectors](https://github.com/OpenG2P/pbms-connectors) registry adapters
(`extensions/registry-adapters/src/openg2p_bg_task_registry_adapters/models/`) names the table or view:

| `target_registry` | Model | Table or view |
| ----------------- | ----- | ------------- |
| `farmer` | `G2PFarmerRegistry` (`models/registry_farmer.py`) | `g2p_register_farmers` |
| `household` | `G2PRegisterHousehold` (`models/register_household.py`) | `g2p_register_households` |
| `disability` | `G2PDisabilityRegistry` (`models/registry_disability.py`) | `g2p_register_persons_with_disability` |

The name is the model's `__tablename__`. A new register declares its own model
([Example Implementation Workflow](./registry-connectors/example-implementation-workflow.md)).

## The primary column: `internal_record_id`

Every register table or view MUST have a column named **`internal_record_id`**. It is:

- The **primary key** of the record, declared on the base SQLAlchemy model `G2PRegistry`
  (`openg2p_pbms_models`).
- The registrant ID PBMS stores in beneficiary lists. Eligibility collects `internal_record_id`
  values, and every later lookup (entitlement multipliers, summaries, beneficiary search) filters on
  them.
- The default sort column of beneficiary search.

## The other columns

PBMS reads whole rows: fetching registrants and beneficiary search select **every column the model
declares**. So the table or view must expose all of them, with compatible types; a missing column
fails the query. Either expose the full set or remove the column from the model.

Eligibility, entitlement and priority rules are Odoo domains on the register's fields
(for example `[('gender', '=', 'FEMALE'), ('estimated_age', '>=', 18)]`), compiled to SQL on the
model, so every field a rule uses must be a model column.

Columns the summaries depend on:

| Register | Columns | Used for |
| -------- | ------- | -------- |
| `farmer` | `estimated_age`, `gender` | Age quartiles, entitlement by gender |
| `household` | `size_children_u5`, `size_elderly`, `rooms_count`, `overcrowding_indicator` | Quartiles |
| `disability` | `estimated_age` (falls back to `birth_date`), `unmet_support_needs_count`, `gender` | Age and unmet-needs quartiles, entitlement by gender |

> Gender values: entitlement statistics lowercase `gender` before comparing it with `male` / `female`,
> so a registry storing `MALE` / `FEMALE` matches.

## Where the table or view must live

Each register has its own connection string, so registers can be in different databases. In the
`openg2p-pbms` Helm chart:

```yaml
global:
  registers:
    farmer:
      connector: db
      connectionString: postgresql://farmer_registry_user:secret@commons-postgresql:5432/farmer_registry
```

The table or view must exist **in that database**, and the user in the connection string must have
`SELECT` on it. Percent-encode special characters in the password.

## Table or view

Either works, because PBMS only ever `SELECT`s. A **view** is recommended for a country
implementation: it maps the registry's own schema onto the contract without copying data, and can
rename or compute columns (for example derive `overcrowding_indicator` or `estimated_age`).

A minimal shape:

```sql
CREATE VIEW g2p_register_farmers AS
SELECT
    r.registry_pk::varchar        AS internal_record_id,   -- REQUIRED primary column
    r.program_ref                 AS functional_record_id,
    r.national_id                 AS foundational_id,
    r.given_name                  AS first_name,
    r.family_name                 AS last_name,
    r.sex                         AS gender,
    r.dob                         AS birth_date,
    r.age                         AS estimated_age
    -- ...every other column G2PFarmerRegistry declares
FROM my_country_farmer_registry r;
```

## Checklist

- [ ] A table or view named as the register model's `__tablename__` exists in the database of the
      register's connection string.
- [ ] It has an `internal_record_id` primary column.
- [ ] It exposes every column the model declares, with compatible types.
- [ ] The connection string's user has `SELECT` on it.
- [ ] The register type is registered in PBMS (both `G2PRegistryType` enums, Odoo `MODEL_MAPPING`,
      `registers.py` and the chart), see the
      [Country Implementation Guide](./country-implementation-guide.md).
