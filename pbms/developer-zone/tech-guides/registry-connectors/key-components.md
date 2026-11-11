# Key Components

A register is served by two small classes, one per connector, built on shared base classes. Callers
never pass SQL: they pass Odoo domains (`pbms_domain`, for example
`[('gender', '=', 'FEMALE'), ('estimated_age', '>=', 18)]`) and beneficiary-list IDs, and the base
classes compile them to SQL (`db`) or a DCI expression (`dci`).

| Component | File | Role |
| --------- | ---- | ---- |
| `RegistryInterface` | `interface/registry_interface.py` | The contract every register implements |
| `RegistryDB` | `computations/_base.py` | Implements the registry methods with SQL on the register's SQLAlchemy `model` |
| `RegistryDCI` | `computations/_base.py` | Implements the registry methods with DCI sync search on the Partner API |
| `<Register>Summaries` | `computations/_summary.py` | The register's summary statistics, shared by its DB and DCI classes |
| `RegistryConnection` | `connection.py` | Decodes a register's connector and connection string |
| `REGISTERS` | `registers.py` | Maps each register to its `(DB, DCI)` classes |
| `RegistryFactory` | `factory/registry_factory.py` | Returns the right class for a register, built with its connection |

## RegistryInterface

### Summaries

Implemented once per register by its `<Register>Summaries` mixin.

| Method | Type | Purpose |
| ------ | ---- | ------- |
| `get_summary(beneficiary_list_id, bg_task_session, formated=False)` | Async | Read the list's summary (staff portal API) |
| `get_summary_sync(beneficiary_list_id, bg_task_session)` | Sync | Same, for Celery tasks |
| `compute_eligibility_statistics(beneficiary_list_details, base_summary, bg_task_session)` | Sync | Compute and store eligibility statistics (for example age quartiles) |
| `compute_entitlement_statistics(beneficiary_list_id, bg_task_session)` | Sync | Compute and store entitlement statistics (for example by gender) |

### Registry methods

Implemented by `RegistryDB` and `RegistryDCI`; a register does not write them.

| Method | Type | Purpose |
| ------ | ---- | ------- |
| `iter_eligible_ids(rules, batch_size)` | Sync | Yield batches of registrant IDs matching `(pbms_domain, set_operator)` rules |
| `iter_priority_ids(priority_domains, enrolled_ids, fallback_rules, batch_size)` | Sync | Yield batches of priority registrant IDs |
| `entitlement_multipliers(registrant_ids, pbms_domain, multiplier_field=None)` | Sync | Return `{registrant_id: multiplier}` for registrants the domain matches |
| `fetch_by_ids(registrant_ids)` | Sync | Load registrant rows, used by the summaries |
| `search_beneficiaries(bg_task_session, beneficiary_list_id, target_registry, search_domain, page, page_size, order_by)` | Async | Paginated search within a beneficiary list |

## RegistryDB

Set two class attributes:

* `model`: the SQLAlchemy model of the register's table or view (see the
  [Registry Database Contract](../registry-database-contract.md)).
* `payload`: the pydantic schema returned in search results.

Registrant IDs are the model's `internal_record_id`.

## RegistryDCI

Set:

* `payload`: the pydantic schema returned in search results.
* `reg_type`, `reg_record_type`: the DCI register and record type sent to the Partner API.
* `match_field`: the field the Partner API filters on to find a registrant. Its value is the
  registrant ID PBMS stores.
* `fields`: the fields PBMS can filter on. They must be in the registry's allowed search fields.
* `flat(record)`: a static method that maps one DCI `reg_record` onto the register's column names. It
  must return `match_field`, and the names must match the DB model so that domains work on both
  connectors.

`computations/_dci_records.py` has helpers for `flat()`: `text`, `code`, `as_bool`, `as_int`,
`identifier_of_type` and `age_from_birth_date`.

## RegistryConnection

Built by `config.get_connection(register)` from `REGISTRY_ADAPTERS_<REGISTER>_CONNECTOR` and
`REGISTRY_ADAPTERS_<REGISTER>_CONNECTION_STRING`. `RegistryConnection.parse()` decodes the string into:

* `db`: driver, username, password, host, port and database name; `sync_url()` and `async_url()` build
  the SQLAlchemy URLs.
* `dci`: `search_url`, `reg_type`, `reg_record_type`, `partner_api_timeout` and
  `partner_api_ssl_verify`.

An empty or invalid string raises `RegistryConnectionError`, which the factory turns into a
`BGTaskException` for that register only. Formats are in the [Registry Connector](README.md#configuration) overview.

## Data models and schemas

* `G2PRegistry` (`openg2p_pbms_models`): base SQLAlchemy model of a register, supplies
  `internal_record_id`.
* `BeneficiaryListSummary` (`openg2p_bg_task_models`): base SQLAlchemy model of a summary table.
* `G2PRegistryPayload` and `BeneficiaryListSummaryPayload` (`schema/` in this package): base search-result
  and summary schemas.
* `BeneficiaryListDetails` and `BeneficiarySearchResponsePayload` (`openg2p_bg_task_models`): beneficiary
  list rows and search responses.

{% hint style="info" %}
New models and schemas inherit their base model or schema.
{% endhint %}
