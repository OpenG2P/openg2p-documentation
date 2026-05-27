---
description: Identify and manage duplicate records within the registry.
---

# Deduplication

### Per-Register Enable / Disable

Deduplication can be turned on or off independently for each register without a code change or restart. The toggle is a boolean flag on the register definition and is updatable via the staff portal API.

When disabled, all incoming change requests and intake forms skip the dedup pipeline entirely — no Celery tasks are queued and no results are stored.

**API:** `POST /update_dedup_is_enabled`

***

### Configurable Match Threshold

Each register has a `dedup_threshold_score` (0–100) that controls how strict the duplicate detection is. Only candidate records whose overall weighted similarity score meets or exceeds this threshold are flagged and stored for staff review.

Raising the threshold reduces false positives; lowering it catches more near-duplicates at the cost of more manual review work.

**API:** `POST /update_dedup_threshold_score`

***

### Field-Level Deduplication Schema

Administrators configure which fields participate in deduplication and how they are matched, entirely through the API. Each field entry specifies:

* **Field name** — which column to compare
* **Match type** — the comparison algorithm (see Match Types below)
* **Weight** — how much this field contributes to the overall score
* **Similarity threshold** — the minimum per-field similarity for the field to count
* **Range tolerance** — for date or numeric fields, the ±window to allow

Different registers can use entirely different schemas. For example, a Farmer register might weight `date_of_birth` heavily (exact match, weight 0.4) while a Household register might rely on `household_name` and `address` (both fuzzy).

**API:** `POST /update_deduplicate_schema`

***

### Multiple Match Types

Five matching strategies are available and can be mixed within a single register's schema:

**EXACT** — strict string equality (case-insensitive). Suitable for identity numbers, dates, and codes where any variation indicates a different record.

**FUZZY** — edit-distance similarity using `SequenceMatcher`. Returns a score between 0 and 1 reflecting how closely two strings match character-by-character. Suitable for names and addresses where typos and abbreviations are common.

**PHONETIC** — matches on the first three characters of each value, catching common spelling variations of names that start similarly (e.g. "Ravi" and "Ravindran"). Simple prefix heuristic; does not require additional libraries.

**NUMERIC\_RANGE** — matches numeric values within a configurable ±tolerance. Suitable for income, age, or other numeric fields where small differences may indicate the same person.

**DATE\_RANGE** — matches dates within a configurable ±day window. Useful for date-of-birth fields where data entry errors (off-by-one day or month) are common.

***

### Dual-Pass Duplicate Detection

Each submission is checked against two sources independently:

**vs. Register** — the incoming record is compared against all approved records already in the register. This detects attempts to re-register someone who is already enrolled.

**vs. Pending Submissions** — the incoming record is compared against other change requests or intake forms that have not yet been approved. This detects concurrent duplicate submissions (e.g. two staff members entering the same person from different offices at the same time).

Both passes run in parallel as separate Celery tasks with separate status tracking. A submission may be flagged by one pass, both, or neither.

***

### Asynchronous Processing via Celery

Deduplication does not block submission acceptance. Change requests and intake forms are accepted immediately; dedup jobs are queued and processed asynchronously.

The pipeline has two layers:

* **Beat producers** run on a periodic schedule. They query for submissions with `PENDING` dedup status and dispatch worker tasks in configurable batch sizes.
* **Workers** execute the actual candidate search and scoring for a single submission. They update status to `COMPLETED` or `FAILED` and store results.

This design allows dedup throughput to be scaled independently by adding more Celery workers, and prevents large volumes of pending submissions from affecting API response times.

***

### Fault Tolerance and Retry

If a dedup worker fails (database error, network issue, unexpected exception), it automatically retries up to 3 times. The failure reason is recorded on the submission record so operators can diagnose persistent failures.

For intake forms, workers delete existing results before re-running, making retries idempotent — re-running a completed job produces the same results without duplicate entries.

***

### Field-Level Match Detail in Results

Every flagged match stores a `field_matches` JSON object alongside the overall score. For each configured field, this includes:

* The incoming value
* The candidate value
* The per-field similarity score
* The match type used

This gives staff reviewers enough information to make an informed accept/reject decision without looking up the candidate record separately.

***

### Register-Specific Domain Service Extension

The dedup scoring logic lives in the base `G2PRegisterDomainService` class and requires no override for standard use cases. The schema drives all field selection, match types, and weights at runtime.

For registers with non-standard data shapes (e.g. nested or multi-record sections in intake forms), domain service subclasses can override `construct_search_text()` and `construct_record_name()` to control how record identifiers are built, while inheriting all dedup logic unchanged.

The domain factory loads the correct service class by register mnemonic, so new register types are added by registering a new mnemonic — no changes to the dedup pipeline are needed.

{% content-ref url="../design/deduplication.md" %}
[deduplication.md](../design/deduplication.md)
{% endcontent-ref %}
