---
description: >-
  Design of the deduplication engine for identifying and managing duplicate
  records
---

# Deduplication

### Overview

Deduplication detects potential duplicate records before changes are committed to a register. When a change request or intake form submission arrives, the system asynchronously compares the incoming record against existing register records and against other pending submissions using a configurable, weighted field-matching algorithm.

The process is non-blocking: submissions are accepted immediately, and deduplication runs in the background via Celery workers. Results are stored with field-level detail for staff review before approval.

```
Submission (change request or intake form)
    │
    ▼
Beat Producer (periodic)
    │  picks up PENDING dedup jobs
    ▼
Worker (async Celery task)
    │  1. load dedup config for the register
    │  2. find candidate records via DB query
    │  3. score each candidate
    │  4. store results above threshold
    ▼
Staff Portal
    │  reviews matches, approves / rejects
```

Deduplication runs in two independent passes per submission:

* **vs. register** — incoming record against approved records already in the register
* **vs. pending submissions** — incoming record against other change requests / intake forms not yet approved

***

### Matching Strategy

Each register has a list of fields to compare, each with a match type and a weight. The overall score is a weighted average of per-field similarities:

```
score = Σ(field_similarity × field_weight) / Σ(field_weights) × 100
```

A field contributes to the score only when its similarity meets the field's `similarity_threshold`. The final score is compared against the register-level `dedup_threshold_score`; only results at or above that threshold are stored.

**Supported match types:**

| Match Type      | Candidate search (DB)             | Scoring                                  |
| --------------- | --------------------------------- | ---------------------------------------- |
| `EXACT`         | `column = value`                  | 1.0 if equal, 0.0 otherwise              |
| `FUZZY`         | `column ILIKE '%value%'`          | `SequenceMatcher` ratio (0.0 – 1.0)      |
| `PHONETIC`      | `column ILIKE 'prefix%'` (3-char) | 1.0 if same 3-char prefix, 0.5 otherwise |
| `NUMERIC_RANGE` | `column BETWEEN ±range_value`     | 1.0 if exact match                       |
| `DATE_RANGE`    | `column BETWEEN ±range_days`      | 1.0 if exact match, 0.8 if within range  |

**Candidate search and scoring are separate steps.** The DB query casts a wide net (OR across all configured fields) to find any record that could possibly match. The scoring step then computes the precise weighted similarity. This two-phase approach keeps DB queries simple while allowing nuanced scoring.

**Example — Farmer register:**

```
Field           match_type  weight   incoming        candidate      similarity
─────────────────────────────────────────────────────────────────────────────
first_name      FUZZY       0.3      "Ravi"          "Ravikumar"    0.62
last_name       FUZZY       0.3      "Kumar"         "Kumar"        1.00
date_of_birth   EXACT       0.4      "1990-05-12"    "1990-05-12"   1.00

score = (0.62×0.3 + 1.00×0.3 + 1.00×0.4) / (0.3+0.3+0.4) × 100 = 88.6
```

***

### Trigram-Based Search

FUZZY and PHONETIC candidate searches rely on PostgreSQL's `pg_trgm` extension. The register tables maintain a `search_text` column that concatenates all searchable field values into a single string. A GIN trigram index is built on this column.

When an ILIKE query runs against a trigram-indexed column, PostgreSQL uses the index to evaluate 3-character n-gram overlap rather than scanning the table sequentially. This makes fuzzy candidate lookup fast even on large registers.

The `search_text` value for each record is constructed by the domain service implementation (`construct_search_text()` on the register-specific subclass) and is updated whenever a change request is approved.

Change request payloads also carry a `search_text` GIN index so that the vs-pending-submissions pass can run the same fast lookup against the unstructured payload column.

**Requirements:**

* PostgreSQL with `pg_trgm` extension enabled
* GIN index on register table `search_text` column
* GIN index on change request `change_payload` column

***

### Deduplication Schema Configuration

The dedup schema for a register is stored in `G2PRegisterSchema.deduplicate_schema` as a JSON array. Each element is a `DeduplicationFieldConfig`:

| Field                  | Type   | Description                                         |
| ---------------------- | ------ | --------------------------------------------------- |
| `field_name`           | string | Column name on the register table                   |
| `match_type`           | enum   | EXACT, FUZZY, PHONETIC, NUMERIC\_RANGE, DATE\_RANGE |
| `weight`               | float  | Relative importance of this field (e.g. 0.3)        |
| `similarity_threshold` | float  | Minimum per-field similarity to count (0.0–1.0)     |
| `range_value`          | float  | ±tolerance for NUMERIC\_RANGE                       |
| `range_days`           | int    | ±days tolerance for DATE\_RANGE                     |

Global dedup settings are stored on `G2PRegisterDefinition`:

| Field                   | Type    | Description                                   |
| ----------------------- | ------- | --------------------------------------------- |
| `dedup_is_enabled`      | boolean | Master on/off switch per register             |
| `dedup_threshold_score` | float   | Minimum overall score (0–100) to flag a match |

**Example — Farmer register schema:**

```json
[
  { "field_name": "first_name",    "match_type": "fuzzy", "weight": 0.3 },
  { "field_name": "last_name",     "match_type": "fuzzy", "weight": 0.3 },
  { "field_name": "date_of_birth", "match_type": "exact", "weight": 0.4 }
]
```

The schema is configurable via the staff portal API (`POST /update_deduplicate_schema`) without a code change. Domain service subclasses (`G2PRegisterDomainService`) do not need to override any dedup methods — the base class reads the schema dynamically at runtime.

***

### Integration with Change Management

Deduplication is wired into two submission paths: change requests (direct data edits submitted via the staff portal API) and intake form submissions (multi-section forms collected via intake flows).

#### Change Request Path

When a change request is created it is assigned two independent dedup statuses:

| Status field                          | Compared against              |
| ------------------------------------- | ----------------------------- |
| `deduplication_register_status`       | Approved register records     |
| `deduplication_change_request_status` | Other pending change requests |

Both statuses start as `PENDING`. The corresponding beat producers pick them up periodically, set status to `INPROGRESS`, and dispatch worker tasks. Workers update status to `COMPLETED` or `FAILED` (with a failure reason) and save results to `DeduplicationRegisterResult` and `DeduplicationChangerequestResult` tables respectively. Workers retry up to 3 times on failure.

#### Intake Form Path

Intake form submissions have the same two-pass structure:

| Status field                           | Compared against               |
| -------------------------------------- | ------------------------------ |
| `deduplication_status_vs_register`     | Approved register records      |
| `deduplication_status_vs_intake_forms` | Other non-approved submissions |

The intake form worker handles multi-record sections: sections with `purpose == REGISTER` may contain a list of records. Each record in the section is scored individually. Results are stored in `DeduplicationIntakeFormRegisterResult` and `DeduplicationIntakeFormIntakeFormResult`. Workers delete existing results before re-running to stay idempotent on retry.

#### Status Lifecycle

```
PENDING → INPROGRESS → COMPLETED
                    └→ FAILED  (retried up to 3 times)
```

All results include `match_score`, `field_matches` (per-field similarity detail as JSON), and foreign keys to both the incoming submission and the matched candidate. The staff portal reads these results to surface potential duplicates during the review workflow.
