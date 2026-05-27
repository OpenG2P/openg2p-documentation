---
description: >-
  For each register mnemonic, implement the class set and export everything.
  Core resolves classes by name at runtime.
---

# Build models, schemas and services

### Per mnemonic class set

<table><thead><tr><th>Class</th><th>Location</th><th>Notes</th><th data-hidden>#</th></tr></thead><tbody><tr><td><code>G2P{DomainTrait}</code></td><td><code>models/{snake}.py</code></td><td>Domain columns only - no <code>__tablename__</code></td><td>1</td></tr><tr><td><code>G2PRegister{Mnemonic}</code></td><td>same file</td><td>Live ORM</td><td>2</td></tr><tr><td><code>G2PRegisterHistory{Mnemonic}</code></td><td>same file</td><td>History twin</td><td>3</td></tr><tr><td><code>G2PIntakeForm{Mnemonic}</code></td><td>same file</td><td>Intake staging twin</td><td>4</td></tr><tr><td>Three Pydantic schemas</td><td><code>schemas/{snake}.py</code></td><td>Mirror ORM fields</td><td>5</td></tr><tr><td><code>G2PRegisterDomainService{Mnemonic}</code></td><td><code>services/g2p_register_domain_service_{snake}.py</code></td><td>Validation and display hooks</td><td>6</td></tr></tbody></table>

`CORE_TABLE` registers (e.g. `Score`) use core ORM - seed metadata and optional `G2PScoreComputeService{Type}` only.

***

### Model composition

Platform mixins supply IDs, audit fields, person/geo columns, and `link_internal_record_id`. Your trait mixin adds programme-specific columns:

```python
class G2P{DomainTrait}:
    domain_field: Mapped[str] = mapped_column(String, nullable=True, index=True)

class G2PRegister{Mnemonic}(G2PRegister, G2PPerson, G2PGeo, G2P{DomainTrait}):
    __tablename__ = "g2p_register_{table_plural}"

    def get_record_name_fields(self) -> str:
        return G2PRegisterDomainService{Mnemonic}().construct_record_name(self.to_dict())

    def get_search_text_fields(self) -> str:
        return G2PRegisterDomainService{Mnemonic}().construct_search_text(self.to_dict())
```

History models swap in `G2PRegisterHistory` + history mixins. Intake models use `G2PIntakeForm` + the same domain trait.

Child **TABLE** registers often drop person/geo mixins; the parent link is the inherited `link_internal_record_id` column.

Keep `models/enums.py` aligned with lookup SQL and section widget option values.

***

### Pydantic schemas

Mirror ORM fields using bases from `openg2p_registry_core.schemas`:

```python
class G2PRegisterSchema{Mnemonic}(G2PRegisterSchemaBase):
    domain_field: Optional[str] = None
```

Change-request attribute validation reads rules from metadata JSON in Postgres. Pydantic schemas still matter for API consistency and developer clarity - keep them in sync.

***

### Domain services - where core calls you

```mermaid
flowchart LR
    CR[Change request create] --> V[validate_domain_attributes]
    CR --> N[construct_record_name / search_text]
    AP[Approval] --> P[post_approve]
    IN[Ingestion worker] --> I[post_ingest]
```

| Method                       | Runs on                      | Typical implementation                               |
| ---------------------------- | ---------------------------- | ---------------------------------------------------- |
| `validate_domain_attributes` | API controller, before save  | Date ranges, required combinations, external lookups |
| `construct_record_name`      | CR payload assembly          | `"Last, First (ID)"` display string                  |
| `construct_search_text`      | CR payload assembly          | Concatenated searchable fields                       |
| `post_approve`               | After approval commit        | Side effects, notifications                          |
| `post_ingest`                | Celery after pipeline insert | Bulk-load follow-up logic                            |

Example validation gate:

```python
async def validate_domain_attributes(self, change_request_request_payload):
    attrs = change_request_request_payload.change_request_attributes or {}
    if attrs.get("start_date") and attrs.get("end_date"):
        if attrs["start_date"] > attrs["end_date"]:
            raise G2PValidationError("start_date must be before end_date")
```

Child TABLE services can be minimal if they only need display strings. Root registers typically implement full validation and search text construction.

***

### Intake parent linking

Multi-step intake (parent register, then child) overrides **`get_link_internal_record_id`** on the intake model:

```python
async def get_link_internal_record_id(self, session) -> str | None:
    # Resolve parent register UUID from batch context or identifier field
    ...
```

Used when portal or pipeline intake submits child rows that must attach to an approved parent.

***

### Optional: scores and enrichers

**`G2PScoreComputeService{ScoreType}`** - Celery `score_compute_worker` invokes by metadata `score_type`.

**`G2P{EnricherName}`** - implements `G2PPayloadEnricherInterface.enrich()`; class name must match ingestion semantic pattern SQL.

Export from package `__init__.py`. No `app.py` registration.

***

### Before proceeding to the next step

* [ ] Six-class set per mnemonic (except `CORE_TABLE`)
* [ ] Every model in extension `migrate_database()`
* [ ] Full exports from `models/`, `schemas/`, `services/` `__init__.py`
* [ ] Optional ID generator, scores, enrichers as planned
