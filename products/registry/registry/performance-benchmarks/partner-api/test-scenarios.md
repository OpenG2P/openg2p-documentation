# Test scenarios — partner-api

Runnable cases live under `locust/api/partner-api/`. Commands are in
`partner.txt` at the repo root. The short run notes are
`locust/api/partner-api/dci/SCENARIOS.md`.

Host: `https://partner-farmer-registry.perftest.openg2p.org`

## 1. What is under test

Three search shapes, each run once as sync and once as async, plus ingest.

| Tag | What it measures |
|---|---|
| `btree_fid` | `functional_record_id` `$eq` on the unique btree |
| `gin_text` | `search_text` `$contains` one 4-letter anchor from `perf-seed/register_search_terms.txt` (50000 terms, about 1000 hits each), on the GIN trigram index |
| `composite` | `last_name` `$startsWith` and `first_name` `$startsWith` (GIN) plus `birth_date` `$eq` (btree) |
| `ingest` | `POST /partner/ingest_data?data_model=IMPORT_FARMER_CSV` |

DCI query types from `search/dci/queries`. `gin_text` and `composite` stay the index cases above. `expression`, `predicate`, and `graphql` use `birth_date` only. Each request uses a new farmer and the seven days from that birth date, so the page is not one shared birth date. `idtype-value` has no range operator, so it looks up `FID`.

| Tag | `query_type` | Filter |
|---|---|---|
| `expression` | `expression` | `birth_date` `$gte` day and `$lte` day+6 |
| `predicate` | `predicate` | `birth_date` `ge` day and `le` day+6 |
| `graphql` | `graphql` | `birth_date: { gte: day, lte: day+6 }` |
| `idtype_value` | `idtype-value` | `FID` equals `functional_record_id` |

`btree_uin`, `btree_birth`, `gin_first`, `gin_last`, `id_fid`, and `id_uin` are still tasks in the locust file. `./run_all.sh` does not run them.

Sync is `POST /dci/sync/search`. A row passes when HTTP is 200 and `header.status` is `succ`.

Async is `POST /dci/async/search`. A row passes when HTTP is 200 and `message.ack_status` is `ACK`. `ACK` means the Staff Portal topic was found and the search was accepted. The farmer result is published after that. Async needs an active `outgoing_topics` row for `PARTNER_STAFF_PORTAL` with `websub_register_status=PROCESSED`, and `REGISTRY_PARTNER_API_WEBSUB_BASE_URL=http://websub`. `./prepare_dci.sh` sets both.

Ingest passes when HTTP is 200 and `response_header.response_status` is `SUCCESS`.

## 2. Pod and database

The partner pod has a 2 vCPU limit and 2 Gunicorn workers, matching the live staff API worker count for the same CPU limit. The staff image default is 8 workers; the partner image default in `docker/ofr-partner/Dockerfile` is 2.

The app database goes through PgBouncer, the same way staff does: host `172.29.2.191`, port `6432`, SQLAlchemy pool 12, overflow 18. Master data stays on Postgres port `5432`.

Signature validation is on. Consent enforcement is off. Audit emission is off (`REGISTRY_PARTNER_API_AUDIT_ENABLED=false`). The first search in a process fetches the Staff Portal key from Partner Management. Later searches in that process use the key cache.

## 3. Search terms

Values are real farmers, not invented strings. `./prepare_dci.sh` reads `g2p_register_farmers` in `functional_record_id` order (`WHERE functional_record_id >= 'FR-' ORDER BY functional_record_id LIMIT 20000`) and keeps the first 10000 rows that have a functional id, foundational id, birth date, `first_name` of at least 3 characters, and `last_name` of at least 4 characters. It writes:

`perf-seed/partner_search_pool.csv`

Locust only reads that file. It does not query the register while the run is going.

Checked on the current file:

| Check | Result |
|---|---|
| Rows | 10000 |
| Empty or short fields | 0 |
| Distinct `functional_record_id` | 10000 |
| Distinct `foundational_id` | 10000 |
| Distinct GIN terms (`last_name` first 4 characters) | 788 |
| Distinct composite keys (last 3, first 3, birth date) | 10000 |

10000 anchors is more than the 100-user cap. Each user holds one row, then picks another at random.

## 4. How one user searches

`page_size` is 10. There is no sort.

1. The user picks one random row and stays on it.
2. The first request is page 1. A sync response includes `total_count`, so the page count is `ceil(total_count / 10)`.
3. The user then requests the other pages in random order. If the term has more than 10 pages, it picks 10 pages at random, including page 1. If it has fewer, it requests every page.
4. When those pages are done, it picks a different random row and starts again.

`btree_fid` matches one farmer, so that user moves on after page 1. `gin_text` and `composite` are the cases that walk several pages. An async HTTP body is only the ACK, so that mode still requests 10 pages of the same term without a page count in the response.

## 5. Ramp and SLO

Same shape as staff (`locust/api/shared/slo_shape.py`). Click Start in the web UI. The shape then owns the user count.

- Search starts at 2 users, then adds 2 every 30 seconds, up to 100.
- Ingest still starts at 4 users and adds 4 every 30 seconds.
- RPS is the first stop. If a step's successful requests/s do not rise above the previous step, freeze at the previous user count.
- Also freeze when the partner pod stays at 1.85 cores for 2 polls, or when p99 stays above 1000 ms for 2 windows.
- Soak 5 minutes at that user count, then stop.

p95 is not the gate. CPU is read with `kubectl top` on pods whose name contains `farmer-registry-partner-api`. One pod is running, so one pod at 1.85 cores is enough to freeze.

## 6. Ingest

Each request inserts one raw farmer payload. Coded fields stay fixed: gender `MALE`, marital status `MARRIED`, education `BASIC`, income `SOI_CROP_PRODUCTION`, language `ENGLISH`, crop `WHEAT`, season `WINTER`, livestock `GOAT`, ownership `OWNER`, unit `HECTARE`.

Names, middle name, household member, birth date, foundational id, address, locality, postal code, land size, and head count change on every request. The signature field is `test`. The ingest signature check in the service is still not called.

## 7. Run and collect

Web UI: http://127.0.0.1:8089. One Locust process at a time.

```bash
cd farmer-registry/performance-testing/locust/api/partner-api/dci
./prepare_dci.sh
./run_case.sh sync btree_fid
./run_case.sh sync gin_text
./run_case.sh sync composite
./run_case.sh sync expression
./run_case.sh sync predicate
./run_case.sh sync graphql
./run_case.sh sync idtype_value
./run_case.sh async btree_fid
./run_case.sh async gin_text
./run_case.sh async composite
./run_case.sh async expression
./run_case.sh async predicate
./run_case.sh async graphql
./run_case.sh async idtype_value
./run_all.sh sync
./run_all.sh async

cd ../ingest
./run_ingest.sh
```

`./run_case.sh` and `./run_ingest.sh` open the UI and wait. `./run_all.sh` runs the three search tags without the UI. The interpreter is `venv/.perf-venv` at the repo root.

Results:

- `locust/api/partner-api/dci/results/sync/<tag>_stats.csv`
- `locust/api/partner-api/dci/results/async/<tag>_stats.csv`
- `locust/api/partner-api/ingest/results/ingest_stats.csv`

The same folders hold the failures CSV. The columns that matter are Request Count, Failure Count, Requests/s, Median Response Time, 95%, and 99%.

CPU during a run:

```bash
export KUBECONFIG="$HOME/.kube/perftest.yaml"
kubectl -n perftest top pod | grep farmer-registry-partner-api
```
