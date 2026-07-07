# Registry Database Contract

This is the load-bearing contract between a **source registry** (the system of record for
your beneficiaries — for example an OpenG2P Social Registry / NSR deployment) and PBMS.

PBMS never talks to your registry through an API when it runs eligibility, entitlement,
priority and beneficiary-search queries. Instead it connects to the **source-registry
database** (referred to internally as the `sr_session`) and runs SQL directly against a
table or view whose name and columns follow a fixed convention. If your source registry
exposes that table/view exactly as described here, PBMS works unchanged. If it does not,
nothing downstream (adapters, summary views, search) will work — hence "contract".

This page specifies that contract. The end-to-end sequence that uses it is in the
[Country Implementation Guide](./country-implementation-guide.md).

## The table-name rule

Every registry in PBMS is identified by a short **registry type** string, the
`target_registry`. Two types ship out of the box:

| `target_registry` | Source table / view name |
| ----------------- | ------------------------ |
| `farmer`          | `g2p_register_farmer`    |
| `households`      | `g2p_register_households`|

The mapping is not configurable — it is hard-coded in the adapter SQL constructors. In
`RegistryInterface` (`openg2p_bg_task_registry_adapters/interface/registry_interface.py`)
every query builds the table name with:

```python
table_name = f"g2p_register_{target_registry}"
```

So the rule is simply:

> **The source registry MUST be exposed, in the registry database that PBMS reads, as a
> table or view named `g2p_register_<target_registry>`.**

For a new country registry type `X`, you expose `g2p_register_X` and register `X` as a new
registry type (see the [Country Implementation Guide](./country-implementation-guide.md),
steps 2–3). Note that `households` is intentionally plural — the type value and the table
suffix must match character-for-character.

## The primary column: `internal_record_id`

Every `g2p_register_*` table/view MUST have a column named **`internal_record_id`**. It is:

- The **primary key** of the registry record (declared `primary_key=True` on the base
  SQLAlchemy model `G2PRegistry` in `openg2p_pbms_models/models/registry.py`).
- The registrant identifier PBMS stores in beneficiary lists. When eligibility runs, the
  IDs it collects are `internal_record_id` values, and every later lookup filters on them.

The SQL constructors reference this column literally. From `RegistryInterface`:

```python
# multiplier lookup
text(f"SELECT {multiplier} FROM {table_name} WHERE internal_record_id = :registrant_id")

# beneficiary search
text(f"""
    SELECT * FROM {table_name}
    WHERE internal_record_id IN ({registrant_placeholders}) {where_clause_sql}
    ORDER BY {order_by}
    OFFSET :offset LIMIT :limit
""")

# entitlement check
sql_query += f" WHERE g2p_register_{target_registry}.internal_record_id = :registrant_id"
```

The default ordering for search is `internal_record_id asc` (see `search_beneficiaries` in
the interface). If `internal_record_id` is missing or not selectable, search and pagination
fail.

## Standard columns the adapters expect

The base `G2PRegistry` model contributes only `internal_record_id`. Each concrete registry
adapter model declares the rest of the columns it reads. Your view must expose **at least
the columns that the corresponding adapter selects**, with compatible types. The two
shipped adapters give the exact list.

### Farmer — `g2p_register_farmer`

Declared in `openg2p_bg_task_registry_adapters/models/registry_farmer.py`
(`class G2PFarmerRegistry`, `__tablename__ = "g2p_register_farmer"`). The columns actually
read by the farmer adapter (`computations/registry_farmer.py`) during search and summary are:

| Column                 | Type      | Used for                              |
| ---------------------- | --------- | ------------------------------------- |
| `internal_record_id`   | string    | primary key / join key                |
| `functional_record_id` | string    | search result payload                 |
| `first_name`           | string    | search result payload                 |
| `last_name`            | string    | search result payload                 |
| `gender`               | string    | search + gender-split entitlement stats |
| `estimated_age`        | integer   | search + age quartile statistics      |
| `disabled`             | boolean   | search result payload                 |
| `source_of_income`     | string    | search result payload                 |
| `education_level`      | string    | search result payload                 |
| `country_code`         | string    | search result payload                 |

The full model also declares the standard identity, person, and geo columns
(`record_name`, `record_status`, `foundational_id`, `middle_name`, `birth_date`,
`phone_numbers`, `emails`, `address_line_1`, `postal_code`, `geo_code_hierarchy_json`, etc.).
Expose the whole set if you want `SELECT *`-style searches and future summary fields to work;
at minimum expose the columns in the table above.

> Note on gender values: the entitlement statistics compare `gender` against
> `Gender.MALE` / `Gender.FEMALE` from `openg2p_pbms_models` whose values are lowercase
> `"male"` / `"female"`. The comparison lowercases the column value first, so a registry
> storing `MALE`/`FEMALE` (as the Odoo model does) still matches.

### Households — `g2p_register_households`

Declared in `openg2p_bg_task_registry_adapters/models/register_household.py`
(`class G2PRegisterHousehold`, `__tablename__ = "g2p_register_households"`). Columns read by
the household adapter (`computations/register_household.py`) include:

| Column                    | Type    | Used for                          |
| ------------------------- | ------- | --------------------------------- |
| `internal_record_id`      | string  | primary key / join key            |
| `functional_record_id`    | string  | search result payload             |
| `household_head_name`     | string  | search result payload             |
| `headship_type`           | string  | search result payload             |
| `size_total`              | integer | search result payload             |
| `size_children_u5`        | integer | search + quartile statistics      |
| `size_elderly`            | integer | search + quartile statistics      |
| `rooms_count`             | integer | search + quartile statistics      |
| `overcrowding_indicator`  | numeric | search + quartile statistics      |
| `number_of_female_members`| integer | search result payload             |
| `number_of_male_members`  | integer | search result payload             |
| `dwelling_type`           | string  | search result payload             |
| `tenure_status`           | string  | search result payload             |
| `water_source_type`       | string  | search result payload             |
| `sanitation_type`         | string  | search result payload             |
| `lighting_source`         | string  | search result payload             |
| `cooking_fuel_type`       | string  | search result payload             |
| `address_line_1`          | string  | search result payload             |
| `address_line_2`          | string  | search result payload             |
| `postal_code`             | string  | search result payload             |
| `country_code`            | string  | search result payload             |

## Where the view must live

PBMS reads the source registry through the **`sr_session`** — a database connection
configured separately from the PBMS core (Odoo) database and the bg-task database. In the
Helm chart (`deployment/charts/openg2p-pbms/values.yaml`) it is the `global.registryDB`
block:

```yaml
global:
  registryDB: 'registry'
  registryDBUser: 'registry_user'
  registryDBSecret: 'registry'
  registryDBUserPasswordKey: 'registry-db-user'
```

The `g2p_register_<type>` tables/views must exist **in that database**, and the
`registryDBUser` must have `SELECT` on them. The defaults above match an OpenG2P Social
Registry (NSR) installed under the release name `registry`; override them if your registry
DB lives elsewhere.

## Table vs. view — which to use

Either works, because the adapters only ever `SELECT`. A **view** is the recommended shape
for a country implementation: it lets you map your registry's native schema onto the
`g2p_register_<type>` contract without copying data, and lets you rename/compute columns
(e.g. derive `overcrowding_indicator`, mask a national ID into `national_id_masked`,
flatten a geo hierarchy into `geo_code_hierarchy_json`) at the view layer.

A minimal shape:

```sql
CREATE VIEW g2p_register_farmer AS
SELECT
    r.registry_pk::varchar        AS internal_record_id,   -- REQUIRED primary column
    r.program_ref                 AS functional_record_id,
    r.given_name                  AS first_name,
    r.family_name                 AS last_name,
    r.sex                         AS gender,
    r.age                         AS estimated_age,
    r.is_disabled                 AS disabled,
    r.income_source               AS source_of_income,
    r.schooling                   AS education_level,
    r.iso_country                 AS country_code
    -- ...add the remaining standard columns as needed
FROM my_country_farmer_registry r;
```

Match the column **names** and **types** in the table above exactly. The adapter reads
result rows by key (e.g. `row["internal_record_id"]`, `row["estimated_age"]`), so a missing
or misnamed column raises a `KeyError` at query time.

## Checklist

- [ ] A table or view named exactly `g2p_register_<target_registry>` exists in the registry
      database (`global.registryDB`).
- [ ] It has an `internal_record_id` primary column, matching the IDs stored in PBMS
      beneficiary lists.
- [ ] It exposes every column the adapter for that type selects, with compatible types.
- [ ] The `registryDBUser` has `SELECT` privileges on it.
- [ ] The registry type is registered in PBMS (Odoo `MODEL_MAPPING`, the adapter
      `G2PRegistryType` enum, and the `RegistryFactory`) — see the
      [Country Implementation Guide](./country-implementation-guide.md).
