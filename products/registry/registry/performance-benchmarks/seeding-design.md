# Seeding Design

Read-path latency (search, dedup, history) is **highly sensitive to table size**.
The DB is seeded to the target volume — and warmed — **before** the app-tier
benchmark, not after. This document is the design rationale for the bulk
generator at [`../seeding/`](../seeding/); for the install/run commands, see
[`../seeding/README.md`](../seeding/README.md).

## Target data volumes (Volume-Tier)

| Volume-Tier | Farmer records | Purpose |
|------|---------------:|---------|
| `smoke` | 10 K | Functional sanity of the harness; not a benchmark figure. |
| **`primary`** | **10 M** | Headline national-farmer-registry scale; the figure most results are reported at. |
| `stretch` | 50 M | Scaling/headroom characterisation. |
| `stress` | 100 M | DB-ceiling and worst-case search/dedup behaviour. |

`smoke` is a harness-validation tier only; numbers measured against it aren't
reported as capacity figures. `primary` is the volume most cells in the matrix run at (see
[`test-scenarios.md`](staff-api/test-scenarios.md) §3); `stretch`/`stress` are mainly
used by `db-sweep` (DB ceiling / data-volume sensitivity) and by
volume-sensitivity comparisons across Steps 1–2.

Per farmer, the generator seeds **proportional related rows** so the schema is
realistic — see `seeding/config.py`'s `RATIOS` and the generation DAG below.

## Configuration/meta-data prerequisite (always first)

The `openg2p-farmer-registry-db-seed` image loads register definitions,
schemas, UI tabs/sections, attribute lookups, registry config, and AWE
meta-data. This is run by the chart's db-seed Job (`dbSeed.enabled=true`). It
is a prerequisite for any bulk data load — the generator queries
`g2p_register_definitions` / `g2p_register_ui_tab_sections` /
`g2p_register_sections` at runtime (for history rows' `tab_id`/`section_id`,
see "History rows" below) and fails loudly if they're missing.
`dbSeed.loadSampleData=true` demo rows aren't used for scale testing — that's
a handful of demo records, not a volume tier.

## The generation DAG

Ratios in the target-volumes table above aren't all "relative to Farmer" —
`crop` is per-`land` (not per-farmer), and `household` is the *parent* of
multiple farmers (fan-out the other direction). `seeding/config.py`'s `RATIOS`
models this as a parent → child fan-out graph matching the real FK structure,
not a flat "everything vs. Farmer" table:

```
household  (root; count derived from the farmer target)
├─ household_member   (3-5 per household)
└─ farmer              (2-3 per household)
   ├─ land              (1-2 per farmer)
   │  └─ crop            (1-3 per land)
   ├─ livestock          (0-1 per farmer)
   ├─ farm_inputs        (1 per farmer)
   └─ membership_details (1 per farmer)
```

Each child's count is sampled independently per parent from a `(min, max)`
range, not a fixed multiplier — e.g. each farmer gets `randint(1, 2)` lands, so
the *average* across the dataset lands on ~1–2× without ever needing a
fractional row count. The distribution is **uniform**, not the more Zipfian
shape of real data (some households much larger than others).

`link_internal_record_id` (the generic parent-link column every `G2PRegister`
table has) is how children point at their parent — e.g. a `Crop` row's
`link_internal_record_id` is its `Land` row's `internal_record_id`, not a
Farmer's.

Poverty score isn't a plain column on any generated model — it's
metadata-driven: a generic `g2p_register_scores` table holds the latest
computed score per `(link_internal_record_id, score_type)`, configured via
`g2p_register_score_definitions` (which score types exist per register
mnemonic) and `g2p_register_score_contributing_attributes` (which fields
feed a given score type, with weights). Computation itself is asynchronous —
a change-request approval enqueues a row on `g2p_score_compute_queue`, and a
Celery worker resolves the score type to a domain-supplied class via
`G2PScoreComputeFactory` (farmer-extension contributes
`G2PScoreComputeServicePoverty` for `POVERTY`). None of this is seeded — the
generator populates neither `g2p_register_scores` nor
`g2p_score_compute_queue`, so bulk-seeded records carry no score rows at
all. Exercising score-dependent reads at scale would need a generator step
for these tables, not a `poverty_score` column on an existing model.

## Why fields are generator-computed instead of business-logic-computed

In production these fields are computed by the app's business logic —
domain-service classes (`G2PRegisterDomainService*`, `G2PGeoHierarchyService`)
and, for `functional_record_id`, an async Celery worker calling an external
id-allocation service. SQLAlchemy's `before_insert`/`before_update` events and
`@validates` hooks are only the trigger, not the computation: each register
model's `get_search_text_fields()`/`get_record_name_fields()`
(`registry-platform/.../models/g2p_register.py`) immediately delegates to its
own domain service's `construct_search_text()`/`construct_record_name()`
(`G2PRegisterDomainService`, overridden per register — e.g.
`G2PRegisterDomainServiceFarmer` in
`farmer-extension/.../services/g2p_register_domain_service_farmer.py`). Bulk
`COPY` bypasses both the ORM (so those events never fire) and the Celery
pipeline, so the generator computes each of these itself:

- **`search_text`** — computed by each register's domain-service
  `construct_search_text()`, invoked from `get_search_text_fields()` when
  SQLAlchemy's `before_insert`/`before_update` fires. The generator
  replicates that field-list logic per table (`generators/*.py:
  SEARCH_TEXT_FIELDS`) — **except Farmer**, where the perf-testing dataset
  deliberately uses a *reduced* list (`config.FARMER_SEARCH_TEXT_FIELDS`:
  `functional_record_id`, `first_name`, `last_name`, `middle_name`,
  `foundational_id`, `birth_date`, `address_line_1`, `address_line_2`) rather
  than production's full ~22-field list. This only affects the seed dataset —
  the app's real `construct_search_text()` for Farmer is untouched.
- **`functional_record_id`** — allocated *asynchronously* in production: a
  Celery worker calls an external HTTP id-allocation service and writes the
  result back later (`functional_id_allocation_worker.py`). That pipeline
  doesn't scale to a bulk load and isn't guaranteed reachable from a seeding
  job. `id_scheme.py` synthesizes ids directly instead, using the same prefix
  scheme as production (`HH-` Household, `FR-` Farmer, `DEFAULT-` everything
  else — from `g2p_id_generator_service.py`) with a simple per-mnemonic
  counter standing in for the real allocator's sequence.
- **`internal_record_id`** — production's default is a plain client-side
  Python `uuid4()` (not a DB default, no domain-service logic involved), so
  the generator does the same thing.
- **`record_name`** — replicates each register's domain-service
  `construct_record_name()` field list directly (these are short, e.g. Farmer
  is just `first_name last_name`).
- **`geo_lowest_level_value_id` / `geo_code_hierarchy_json`** — in the app,
  setting `geo_lowest_level_value_id` triggers an ORM `@validates` hook that
  calls `G2PGeoHierarchyService`
  (`registry-platform/.../services/g2p_geo_hierarchy_service.py`) to fetch
  the hierarchy from master-data-db. The generator leaves both **unset** —
  geo-hierarchy filtering isn't exercised as a result.
- **History rows' `tab_id`/`section_id`** — real UI metadata, not invented.
  `generators/history.py` reads them back from `g2p_register_definitions` /
  `g2p_register_sections` / `g2p_register_ui_tab_sections`. Only Household and
  Farmer are UI-navigable registers with their own tabs — every other table
  (HouseholdMember, Land, Crop, Livestock, FarmInputs, MembershipDetails) is
  surfaced as a *section embedded in* Household's or Farmer's tabs, not as a
  register with tabs of its own. A `g2p_register_sections` row for one of
  these has `section_register_id` pointing at the child table's own
  `register_id`, while its (owning) `register_id` points at whichever of
  Household/Farmer displays it — filtering on `section_register_id` finds the
  right tab/section pair uniformly for both top-level registers and child
  tables.
- **`change_request_id` on history rows** — a fabricated uuid per row
  (unique, non-null, but doesn't correspond to any real
  `g2p_register_change_requests` row), needed because `RecordHistoryData` /
  `VersionForDateData` (registry-platform's `schemas/register_payload.py`)
  declare it as a required non-`Optional[str]` field.

Every live insert gets a corresponding history insert (1:1, not a sampled
subset).

## Search-text anchors

`search_in_a_register` matches via
`implementation_class.search_text.ilike(f"%{search_text}%")`, accelerated by a
`gin_trgm_ops` GIN index directly on `search_text` (`ILIKE` + `pg_trgm` is
index-accelerated regardless of case — no casing concerns between generated
data and the query).

To guarantee benchmark searches hit real, spread-out data instead of either
matching nothing or all piling onto one hot term:

1. `search_anchors.py` generates a fixed pool of `SEARCH_ANCHOR_COUNT` (100)
   random 4-character strings up front. Kept small deliberately: at 10,000
   anchors, each one only matches on the order of `target_farmers / 10,000`
   rows — too few for a meaningful paginated result set at the `smoke` tier,
   and uneven besides. 100 anchors keeps every anchor's match count large
   regardless of tier.
2. Every seeded farmer's `first_name` gets exactly one anchor, assigned
   **round-robin** across the pool (`search_anchors.next_anchor`, not random
   choice) so every anchor gets an (almost) exactly equal share of farmers —
   `target_farmers // 100` each, not merely "uniform on average" the way
   random sampling would give. It's then **spliced into a random position** in
   the name (not just prefixed) — pg_trgm doesn't care about position the way
   a B-tree prefix index would, so this exercises real infix matching rather
   than only prefix matching.
3. `search_text` (built from the reduced field list above) includes
   `first_name`, so the anchor is guaranteed to be indexed and searchable.
4. The full anchor list is written to `seed_manifest.json`'s `search_terms` —
   the Locust side (see [`test-scenarios.md`](staff-api/test-scenarios.md)) has each
   simulated user pick one anchor at `on_start` and stay "sticky" to it for
   the session: spread across users, but stable within a user, which mirrors
   how a real staff user searches repeatedly for similar things in one
   session. `intake_create` also embeds a randomly-chosen anchor into every
   generated farmer's first name at submission time (not round-robin — no
   fixed total to spread evenly over a live run), so `cr_read_and_approve`
   and `intake_read_and_approve`'s anchor-filtered searches over live-created
   data return real results, not just the bulk-seeded rows.

Record-id-level reads (`get_subject_record`, `get_change_request`, etc.) do
**not** need anchor-style treatment — `register_read`'s Locust flow already
samples a random page from `search_in_a_register`'s real pagination and pulls
a record id from whatever lands on that page, which spreads reads across the
full key space without needing a pre-generated id list.

## Load mechanics

- Rows are batched and written via `COPY ... FROM STDIN` (`db.BatchWriter`,
  `config.BATCH_SIZE` = 75K rows/batch), not row-by-row `INSERT` — orders of
  magnitude faster at 10M+.
- `config.DEFER_INDEXES` (default `True`): before loading, every target
  table's non-PK indexes (including the `pg_trgm` GIN index) are captured via
  `pg_indexes.indexdef` and dropped; after the full load, they're recreated
  from the captured definitions and every table gets `ANALYZE`. This avoids
  paying per-row index-maintenance cost during the load. This is only run
  against a dedicated/disposable perf-testing database — it modifies real
  index state on the target tables, briefly leaving them unindexed for
  anything else querying the same DB during the load. For a `smoke`-tier
  correctness check, it's turned off — the perf benefit is negligible at 10K
  rows, and real index state stays untouched while the generator's logic is
  verified end to end.
- Farmer/household counts aren't exact-to-the-row at the target tier: the
  household loop stops adding farmers once the tier target is hit mid-loop,
  which can undershoot/overshoot the *household*'s last per-parent draw by a
  few rows. Fine for a benchmark; not exact for reproducible row-count
  assertions.

## Storage sizing

The storage node ships **256 GB gp3** by default (see
[`environment-topology.md`](environment-topology.md)). Free space is
confirmed before the `stretch`/`stress` tiers, with the data disk resized if
needed — gp3 IOPS remains a separate ceiling regardless of disk size.

### Measured sizes

Row counts and table/index sizes from `psql`, captured per tier in
[`../seeding/primary-volume/`](../seeding/primary-volume/) and
[`../seeding/stretch-volume/`](../seeding/stretch-volume/)
(`table_sizes.txt`, `index_sizes.txt`):

| Volume-Tier | Farmer rows | Total rows (all tables) | Table size | Index size | Total DB size |
|---|---:|---:|---:|---:|---:|
| `primary` (10M target) | 10,150,268 | 203,079,145 | 79.6 GB | 59.1 GB | 139.3 GB |
| `stretch` (50M target) | 50,000,264 | 1,000,170,349 | 393.9 GB | 318.8 GB | 715.1 GB |

Farmer rows land slightly above each tier's round target (10M/50M) for the
same reason noted above — the household loop overshoots its last draw, not
a bug. Growth from `primary` to `stretch` (5× the farmer target) is ~5.13×
in total DB size — close to linear, marginally super-linear.

Largest tables, both tiers (register + history, `crop`/`land` fan out the
most per farmer — see the generation DAG above):

| Table | `primary` total size | `stretch` total size |
|---|---:|---:|
| `g2p_register_history_crops` | 19 GB | 96 GB |
| `g2p_register_household_members` | 16 GB | 86 GB |
| `g2p_register_crops` | 14 GB | 68 GB |
| `g2p_register_lands` | 13 GB | 72 GB |
| `g2p_register_history_household_members` | 13 GB | 64 GB |

**Storage disk resized for `stretch`.** The default 256 GB gp3 disk was
expanded by +768 GB to **1024 GB (1 TiB)**, a single volume, ahead of the
`stretch` run — consistent with this section's own "resized if needed."
`stretch`'s measured 715.1 GB leaves **~308.9 GB headroom** on that
volume (~70% utilized). `stress` (100M target, double `stretch`'s row
count) will need this resized further before it can be seeded — projecting
`primary`→`stretch`'s growth rate (5.13× total size for a 5× farmer
target, i.e. slightly super-linear) forward to 100M lands around
**~1.4 TB**, well past the current 1 TiB volume, so plan the next resize
rather than discovering the shortfall mid-load.

**Schema changed between the two measurements, not just the data volume.**
`stretch`'s index dump includes 17 `_search_text_fts` indexes — a
full-text-search GIN index, alongside the existing `_search_text_trigram`
one, on `household_members`/`farmers`/`lands`/`households`/`crops`/etc.
**None exist in `primary`'s dump at all.** The populated ones (register
tables; the intake-form-table copies are ~16 kB each, effectively empty)
total ~31.7 GB — about 10% of `stretch`'s 318.8 GB index total. So the
5.13× total-size growth above isn't purely a volume effect: part of
`stretch`'s larger footprint is a schema addition `primary`'s measurement
predates, not more rows against the same index set. Confirm when
`idx_*_search_text_fts` was added, and re-baseline `primary` (or discount
~32 GB from the comparison) if a clean volume-only growth figure is
needed.

## Reset between tiers

Tiers are kept reproducible by snapshotting the storage volume (or
`pg_dump`/restore, or a templated database) after each tier load, so a run
can be repeated without re-generating, and a failed write-phase can be
rolled back to a known size.

## Seed manifest

`seed_manifest.json` (written next to the generator):

```json
{
  "record_ids":  ["...", "..."],   // reservoir-sampled Farmer internal_record_ids
  "search_terms": ["...", "..."],  // the full 100-anchor pool
  "household_ids": ["..."],        // reservoir-sampled Household internal_record_ids
  "data_volume": "10M",
  "generated_at": "..."
}
```

`record_ids`/`household_ids` are a fixed-size (10,000) **reservoir sample**
(`seed_manifest.py`), not the full set — needed for scripts that read by id
directly without holding 100M ids in memory. `household_ids` is load-bearing
today (`intake_create` links every farmer intake submission to a real
household via it, replacing a hardcoded placeholder list). `record_ids` has
no current consumer — `register_read` discovers ids by paginating real
search results instead — but is kept for any future by-id-only scenario.

## Pre-benchmark verification

```sql
-- row counts
SELECT relname, n_live_tup FROM pg_stat_user_tables
 WHERE relname LIKE 'g2p_register_%' ORDER BY n_live_tup DESC;

-- pg_trgm present
SELECT extname FROM pg_extension WHERE extname='pg_trgm';
\di+ *register*

-- a representative anchor search uses an index (not a seq scan)
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM g2p_register_farmers WHERE search_text ILIKE '%<an anchor>%' LIMIT 20;
```

The cache is then warmed (representative reads) before measuring.

## Known simplifications

- No score rows seeded — `g2p_register_scores` / `g2p_score_compute_queue`
  (poverty score, or any other metadata-defined score type) aren't populated
  by the generator.
- `geo_lowest_level_value_id` / `geo_code_hierarchy_json` left null —
  geo-hierarchy filter testing isn't exercised as a result.
- Enum value lists (`common.py`, `generators/*.py`) are hardcoded copies of
  the real `StrEnum` classes, not imported from the app packages, so they can
  drift out of sync if those enums change.
- Attribute-lookup fields (crop `commodity`, livestock `livestock_type`/
  `breed`, etc.) use plausible hardcoded value lists, not the deployment's
  actual configured attribute lookups.
- Anchor-to-farmer assignment is round-robin (exactly even) for bulk-seeded
  data, not Zipfian/skewed — real search-term popularity isn't flat in
  production.
