---
description: >-
  Functional specification for the ID Generator service — ID types, generation
  rules, filters, pool management, and exhaustion handling.
---

# Functional Specifications

## ID types

Each consuming application is assigned an **ID type** (e.g., `farmer`, `household`, `national_id`).

* ID types are **pre-configured** via config file or Helm values — not created via API.
* Each ID type has **one configurable parameter: ID length** (2–32 digits).
* All filter rules are **global** (same across all ID types).
* The **same numeric ID may exist in multiple ID types** — pools are fully independent.

### Adding an ID type

1. Add the new ID type to the configuration (YAML config or Helm values).
2. Restart pods (rolling restart or Helm upgrade).
3. The service auto-creates the database table and fills the initial pool.
4. Existing ID type tables and their data are fully preserved.

### Removing an ID type

1. Remove the ID type from the configuration and restart.
2. The service returns `IDG-003 Unknown ID type` for requests to the removed type.
3. The database table is **not** automatically dropped — a safety measure against configuration typos.
4. A DBA can manually drop the orphaned table if storage reclaim is needed.

## ID generation rules

### Structure

* **Numeric only** — no alphabets or special characters.
* **Length** — configurable per ID type, maximum 32 digits.
* **Last digit** — Verhoeff checksum. The generator produces `(length - 1)` random digits and appends 1 checksum digit.
* **Randomness** — Python `secrets` module (cryptographically secure).

### Filters

Every generated ID must pass **all 10 filters**. These filter rules are inspired by [MOSIP UIN generation filters](https://docs.mosip.io/1.2.0/id-lifecycle-management/supporting-components/commons/id-generator#uin-generation-filters).

| #  | Filter                         | Description                                                                 | Config key                         |
| -- | ------------------------------ | --------------------------------------------------------------------------- | ---------------------------------- |
| 1  | **Length**                      | ID must be exactly the configured length for its ID type                    | Per-ID-type `id_length`            |
| 2  | **Not-Start-With**             | ID must not begin with specified digits (e.g., 0, 1)                        | `not_start_with`                   |
| 3  | **Sequence**                   | No ascending/descending sequences beyond limit (e.g., limit=3 → "123" rejected) | `sequence_limit`              |
| 4  | **Repeating Digit**            | No same digit repeating within N positions (e.g., limit=2 → "11" rejected)  | `repeating_limit`                  |
| 5  | **Repeating Block**            | No repeated digit blocks (e.g., limit=2 → "48xx48" rejected)               | `repeating_block_limit`            |
| 6  | **Conjugative Even Digits**    | No N consecutive even digits (2,4,6,8) in a row                            | `conjugative_even_digits_limit`    |
| 7  | **First = Last**               | First N digits must not equal last N digits                                 | `digits_group_limit`               |
| 8  | **First = Reverse(Last)**      | First N digits must not equal reverse of last N digits                      | `reverse_digits_group_limit`       |
| 9  | **Restricted Numbers**         | ID must not contain any blacklisted substrings                              | `restricted_numbers`               |
| 10 | **Cyclic Numbers**             | ID must not contain any of the 9 known mathematical cyclic number patterns  | Hardcoded list                     |

### Cyclic numbers (hardcoded)

The following cyclic number patterns are banned:

1. `142857`
2. `0588235294117647`
3. `052631578947368421`
4. `0434782608695652173913`
5. `0344827586206896551724137931`
6. `0212765957446808510638297872340425531914893617`
7. `0169491525423728813559322033898305084745762711864406779661`
8. `016393442622950819672131147540983606557377049180327868852459`
9. `010309278350515463917525773195876288659793814432989690721649484536082474226804123711340206185567`

## Pool management

The service maintains a **pre-generated pool** of AVAILABLE IDs per ID type in PostgreSQL.

| Setting                        | Description                                              |
| ------------------------------ | -------------------------------------------------------- |
| `pool_min_threshold`           | Trigger replenishment when AVAILABLE count falls below   |
| `pool_generation_batch_size`   | Number of IDs to generate per replenishment cycle        |
| `pool_check_interval_seconds`  | How often to check pool levels (default: 30s)            |
| `exhaustion_max_attempts`      | Random attempts before declaring space exhausted         |

* **Background replenishment** runs on every pod, coordinated via PostgreSQL advisory locks.
* **No archive table** — at expected scale (up to 50M IDs per type), a single table with a status column is sufficient.
* **Uniqueness** — every generated ID is checked against all existing IDs (AVAILABLE and TAKEN) before insertion.

## ID space exhaustion

The effective ID space is significantly smaller than the raw numeric range due to filters:

* **Raw space**: `8 × 10^(id_length - 2)` (first digit restricted to 2–9, last digit is checksum)
* **After filters**: typically 15–60% of raw space, depending on ID length and filter parameters. An estimation of the effective space size after filters is available in the table below.

### Estimated ID space by length (after filters)

These estimates were generated using [`scripts/space_estimator.py`](https://github.com/OpenG2P/id-generator/blob/main/scripts/space_estimator.py).

| ID Length (digits) | Estimated Valid IDs   |
| ------------------ | --------------------- |
| 6                  | 35,919                |
| 7                  | 244,348               |
| 8                  | 2,382,981             |
| 9                  | 16,379,411            |
| 10                 | 164,804,199           |
| 11                 | 1,621,760,763         |
| 12                 | 15,716,806,211        |
| 13                 | 149,894,769,328       |
| 14                 | 1,416,056,507,189     |
| 15                 | 13,285,071,919,224    |
| 16                 | 123,889,361,047,011   |


When the pool is empty **and** no more valid IDs can be generated:

* The service returns `IDG-002` (HTTP 410 Gone) — ID space permanently exhausted.
* This is distinct from `IDG-001` (HTTP 503) — pool temporarily empty, replenishment in progress.

## Configuration

```yaml
id_generator:
  # Global filter rules
  sequence_limit: 3
  repeating_limit: 2
  repeating_block_limit: 2
  conjugative_even_digits_limit: 3
  digits_group_limit: 5
  reverse_digits_group_limit: 5
  not_start_with: ["0", "1"]
  restricted_numbers: []

  # Pool management
  pool_min_threshold: 1000
  pool_generation_batch_size: 5000
  pool_check_interval_seconds: 30
  exhaustion_max_attempts: 1000

  # ID types
  id_types:
    farmer:
      id_length: 12
    household:
      id_length: 10
```

Any setting can be overridden via environment variables using `__` as the nested delimiter:

```bash
ID_GENERATOR__POOL_MIN_THRESHOLD=5000
ID_GENERATOR__ID_TYPES__NATIONAL_ID__ID_LENGTH=12
```

## Database schema

One table per ID type, auto-created on startup:

```sql
CREATE TABLE IF NOT EXISTS id_pool_farmer (
    id_value    VARCHAR(32)   PRIMARY KEY,
    status      VARCHAR(16)   NOT NULL DEFAULT 'AVAILABLE',
    created_at  TIMESTAMPTZ   NOT NULL DEFAULT now(),
    issued_at   TIMESTAMPTZ   NULL
);

CREATE INDEX idx_farmer_available
    ON id_pool_farmer (status) WHERE status = 'AVAILABLE';
```

## API endpoints

For the complete API reference, see [API Reference](api-reference.md).

| Method | Path                                           | Description                          |
| ------ | ---------------------------------------------- | ------------------------------------ |
| POST   | `/v1/idgenerator/{id_type}/id`                 | Issue one ID from the pool           |
| GET    | `/v1/idgenerator/{id_type}/id/validate/{id}`   | Validate an ID's structure           |
| GET    | `/v1/idgenerator/health`                       | Health check                         |
| GET    | `/v1/idgenerator/version`                      | Service version and build info       |
| GET    | `/v1/idgenerator/config`                       | Active configuration                 |

## Reference

* ID generation filters inspired by: [MOSIP UIN Generator](https://docs.mosip.io/1.2.0/id-lifecycle-management/supporting-components/commons/id-generator#uin-generation-filters)
