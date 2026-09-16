# Seeding Design

Read-path latency (search, dedup, history) is **highly sensitive to table size**.
The DB must be seeded to the target volume — and warmed — **before** the app-tier
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

`smoke` is a harness-validation tier only — don't report numbers measured
against it. `primary` is the volume most cells in the matrix run at (see
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
see "History rows" below) and fails loudly if they're missing. **Do not** use
`dbSeed.loadSampleData=true` demo rows for scale testing — that's a handful of
demo records, not a volume tier.

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
fractional row count. The distribution is currently **uniform**; real data is
more Zipfian (some households much larger than others) — revisit if a test
specifically needs to stress the long tail.

`link_internal_record_id` (the generic parent-link column every `G2PRegister`
table has) is how children point at their parent — e.g. a `Crop` row's
`link_internal_record_id` is its `Land` row's `internal_record_id`, not a
Farmer's.

`poverty_score` is **not implemented** — there is currently no
`G2PRegisterPovertyScore` model in `farmer-extension`. Add a
`generators/poverty_score.py` + a `RATIOS`/`TABLE_NAMES` entry once it exists.

## Why fields are generator-computed instead of ORM-computed

Production populates several fields via SQLAlchemy ORM machinery —
`before_insert`/`before_update` event listeners, `@validates` hooks, and an
async Celery pipeline. Bulk `COPY` bypasses the ORM entirely, so the generator
computes each of these itself:

- **`search_text`** — normally built by `_populate_search_text()`
  (`registry-platform/.../models/g2p_register.py`), which calls each table's
  `construct_search_text()`. The generator replicates that field-list logic
  per table (`generators/*.py: SEARCH_TEXT_FIELDS`) — **except Farmer**, where
  the perf-testing dataset deliberately uses a *reduced* list
  (`config.FARMER_SEARCH_TEXT_FIELDS`: `functional_record_id`, `first_name`,
  `last_name`, `middle_name`, `foundational_id`, `birth_date`,
  `address_line_1`, `address_line_2`) rather than production's full ~22-field
  list. This only affects the seed dataset — the app's real
  `construct_search_text()` for Farmer is untouched.
- **`functional_record_id`** — normally allocated *asynchronously*: a Celery
  worker calls an external HTTP id-allocation service and writes the result
  back later (`functional_id_allocation_worker.py`). That pipeline doesn't
  scale to a bulk load and isn't guaranteed reachable from a seeding job.
  `id_scheme.py` synthesizes ids directly instead, using the same prefix
  scheme as production (`HH-` Household, `FR-` Farmer, `DEFAULT-` everything
  else — from `g2p_id_generator_service.py`) with a simple per-mnemonic
  counter standing in for the real allocator's sequence.
- **`internal_record_id`** — production's default is a client-side Python
  `uuid4()` (not a DB default), so the generator just does the same thing.
- **`record_name`** — replicates each table's `construct_record_name()` field
  list directly (these are short, e.g. Farmer is just `first_name last_name`).
- **`geo_lowest_level_value_id` / `geo_code_hierarchy_json`** — in the app,
  setting `geo_lowest_level_value_id` triggers an ORM `@validates` hook that
  calls out to master-data-db per write to populate the hierarchy JSON. The
  generator leaves both **unset**. If a benchmark needs geo-hierarchy
  filtering to be exercised, this is the gap to close first.
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

Record-id-level reads (`get_subject_record`, `get_record_history`, etc.) do
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
  paying per-row index-maintenance cost during the load. **Only run this
  against a dedicated/disposable perf-testing database** — it modifies real
  index state on the target tables, briefly leaving them unindexed for
  anything else querying the same DB during the load. For a `smoke`-tier
  correctness check, turn it off — the perf benefit is negligible at 10K rows
  and it avoids touching real index state before the generator's logic is
  verified end to end.
- Farmer/household counts aren't exact-to-the-row at the target tier: the
  household loop stops adding farmers once the tier target is hit mid-loop,
  which can undershoot/overshoot the *household*'s last per-parent draw by a
  few rows. Fine for a benchmark; not exact for reproducible row-count
  assertions.

## Storage sizing

100M farmer records + supporting tables + history + indexes can be **hundreds
of GB**. The storage node ships **256 GB gp3** (see
[`environment-topology.md`](environment-topology.md)). Confirm free space
before the `stretch`/`stress` tiers; resize the data disk if needed (and
remember gp3 IOPS is a separate ceiling).

## Reset between tiers

Keep tiers reproducible: snapshot the storage volume (or `pg_dump`/restore, or
a templated database) after each tier load so a run can be repeated without
re-generating, and so a failed write-phase can be rolled back to a known size.

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
search results instead — but is kept per the original spec for any future
by-id-only scenario.

## Verify before benchmarking

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

Then warm the cache (representative reads) before measuring.

## Known simplifications (revisit if a benchmark needs them)

- No `poverty_score` generator (model doesn't exist yet).
- `geo_lowest_level_value_id` / `geo_code_hierarchy_json` left null — no
  geo-hierarchy filter testing without closing this gap.
- Enum value lists (`common.py`, `generators/*.py`) are hardcoded copies of
  the real `StrEnum` classes, not imported from the app packages — keep in
  sync manually if those enums change.
- Attribute-lookup fields (crop `commodity`, livestock `livestock_type`/
  `breed`, etc.) use plausible hardcoded value lists, not the deployment's
  actual configured attribute lookups.
- Anchor-to-farmer assignment is round-robin (exactly even) for bulk-seeded
  data, not Zipfian/skewed — real search-term popularity isn't flat in
  production.

## Known upstream issue (not fixable from the seed side)

`get_record_history` (`registry-platform/.../services/g2p_register_service.py`)
does `history_record.change_request_source.value`, assuming an Enum instance.
The column is `mapped_column(String, ...)` (not `sqlalchemy.Enum`), so a
fresh `SELECT` always returns a plain `str`, and `.value` raises
`AttributeError` for **any** history row with `change_request_source` set —
seeded or app-written, once actually queried this way. The column is
`nullable=False`, so this can't be routed around from the generator; it needs
a platform-side fix (drop the `.value`). `get_record_history` will keep
returning `SYS-ERR-001` against seeded data until that lands.
