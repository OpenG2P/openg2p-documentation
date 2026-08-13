---
description: >-
  Everything a domain extension must (and may) implement for the platform to
  load it correctly
---

# Extensions Contract

For each `REGISTER`, `TABLE`, or `PROGRAM_REGISTER` in `g2p_register_definitions`:

<table><thead><tr><th width="216">Artefact</th><th>Class name</th></tr></thead><tbody><tr><td>Live ORM</td><td><code>G2PRegister{Mnemonic}</code></td></tr><tr><td>History ORM</td><td><code>G2PRegisterHistory{Mnemonic}</code></td></tr><tr><td>Intake ORM</td><td><code>G2PIntakeForm{Mnemonic}</code></td></tr><tr><td>Live schema</td><td><code>G2PRegisterSchema{Mnemonic}</code></td></tr><tr><td>History schema</td><td><code>G2PRegisterHistorySchema{Mnemonic}</code></td></tr><tr><td>Intake schema</td><td><code>G2PIntakeFormSchema{Mnemonic}</code></td></tr><tr><td>Domain service</td><td><code>G2PRegisterDomainService{Mnemonic}</code></td></tr></tbody></table>

Export all classes from package `__init__.py` files. `CORE_TABLE` registers (e.g. `Score`) use core ORM - seed metadata only; optional `G2PScoreComputeService{Type}`.

***

### Domain service methods

| Method                       | Required | Purpose                                     |
| ---------------------------- | -------- | ------------------------------------------- |
| `validate_domain_attributes` | **Yes**  | Business rules before change request create |
| `construct_record_name`      | **Yes**  | Display name in lists and headers           |
| `construct_search_text`      | **Yes**  | Full-text search string                     |
| `post_approve`               | Optional | After approval commits                      |
| `post_ingest`                | Optional | After ingestion insert                      |

{% hint style="info" %}
Dedup logic is **inherited**, configure via `g2p_register_schemas.deduplicate_schema` JSON, not in domain services.
{% endhint %}

***

### Package-level requirements

| Component                  | Notes                                                                              |
| -------------------------- | ---------------------------------------------------------------------------------- |
| `G2PRegisterDomainFactory` | Standard boilerplate resolves `G2PRegisterDomainService{Mnemonic}` via `importlib` |
| `app.py` Initializer       | `CoreInitializer()` → factory → optional eager domain services                     |
| `migrate_database()`       | Must call `create_migrate()` on **every** domain ORM class                         |
| `pyproject.toml`           | `name` and `[tool.hatch.version]` point at **your own** package. No source map — see below. A `readme = "README.md"` line means the file must exist, or the build fails |

{% hint style="warning" %}
Celery workers do not run `migrate_database()`, API containers must start first.
{% endhint %}

### The module alias — two halves that look contradictory

1. **Your package installs under its own import name**
   (`openg2p_registry_<domain>_extension`). Do **not** add a
   `[tool.hatch.build.targets.wheel.sources]` map onto
   `openg2p_registry_extensions`. That was the pre-1.0 mechanism; it prevents
   your extension from coexisting with the platform's reference extension in one
   image.

2. **Code the platform resolves must nevertheless import the alias.** The
   container entrypoint (`openg2p_registry_staff_api/main.py` and its siblings)
   installs the module named by `REGISTRY_EXTENSION_MODULE` into `sys.modules` as
   `openg2p_registry_extensions` before any platform import runs. So the
   factories do:

   ```python
   importlib.import_module("openg2p_registry_extensions.register_domain.services")
   ```

   Changing that to your own package name works in your image and breaks the
   moment the reference extension is the one selected. **Copy the factories
   unchanged** — the only thing you adjust is which services exist.

{% hint style="danger" %}
Rule of thumb: **package name → yours. Import target inside the factories →
`openg2p_registry_extensions`.**
{% endhint %}

***

### Optional components

| Component                      | Location                                | Registration                                                                    |
| ------------------------------ | --------------------------------------- | ------------------------------------------------------------------------------- |
| `G2PIdGeneratorService`        | `register_domain/id_generator/`         | Lazy via factory; keys match Helm `idTypes` (lowercase)                         |
| `G2PScoreComputeService{Type}` | `score_compute/services/`               | Factory; `score_type` in metadata → class name                                  |
| Enrichers                      | `ingestion_pipeline/enricher_services/` | Exact class name in semantic pattern config                                     |
| Jinja templates                | `templates/ingest`, `templates/outgest` | Upload to MinIO; and attach to related references and `g2p_registry_documents`  |
