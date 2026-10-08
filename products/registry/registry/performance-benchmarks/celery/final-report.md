# Farmer Registry Celery — Backlog Drain Performance Test Report

Detailed, per-scenario interpretation of the Celery beat + worker backlog-drain runs in [`raw-report.md`](raw-report.md), against the test design in [`test-scenarios.md`](test-scenarios.md). One scenario at a time, beat held at 1 pod, worker pods at 1 → 2 → 3, from a fixed backlog populated fresh before each worker count (test-scenarios.md §3/§6). Every table below is built from the same per-minute CSVs as `raw-report.md`; the "done this minute" column and the Observations sections are this document's own interpretation, not raw Locust/collector output.

**A cross-cutting note on beat's claim size:** `cases.py`'s per-scenario `frequency_s` (20s/30s) is only a code-level fallback. The live `farmer-registry-celery-beat-producer` deployment on the compute node overrides every producer to fire every **10s**, with a per-producer `..._NO_OF_TASKS` claim size of either **3,000** or **20,000** per tick (confirmed directly off the deployment's env vars — see `final-report-summary.md` § Measurements). That fully explains why `pending` reaches 0 so early in almost every run below: e.g. `ingest_data_classification` claims 3,000/tick × 5 ticks in the first ~50s = 15,000 — exactly what mark 1 shows. These runs measure worker throughput, not beat's enqueue ceiling (the one likely exception is called out under `score_compute`).

## Partner ingest

### `ingest_data_classification`

Partner ingest classification.

**1. Items in the queue at the beginning:** 50,000 rows — `incoming_raw_data.classification_status` re-seeded to `PENDING` for this cohort before each of the pod-1/pod-2/pod-3 runs below (same size every time).

**2. Beat parameters:** fires every **10s** (`REGISTRY_CELERY_BEAT_INGEST_DATA_CLASSIFICATION_BEAT_PRODUCER_FREQUENCY` on this cluster, confirmed via the live deployment; code default differs). Claims **3,000** tasks/tick (confirmed via the live deployment). The producer does mark the row before `send_task`. Beat claims classification_status before enqueue.

**3. Worker Pod-1 (1 worker pod) — Measurements: Tasks vs Time** (`ingest_data_classification-workers-1-size-50000.csv`, finished at mark_min 24)

| mark_min | pending | in_progress | done | done this minute |
|---|---|---|---|---|
| 0 | 50000 | 0 | 0 | +0 |
| 1 | 35000 | 13106 | 1894 | +1894 |
| 2 | 17000 | 29131 | 3869 | +1975 |
| 3 | 2000 | 42232 | 5768 | +1899 |
| 4 | 0 | 42461 | 7539 | +1771 |
| 5 | 0 | 40282 | 9718 | +2179 |
| 6 | 0 | 37820 | 12180 | +2462 |
| 7 | 0 | 35676 | 14324 | +2144 |
| 8 | 0 | 33445 | 16555 | +2231 |
| 9 | 0 | 31235 | 18765 | +2210 |
| 10 | 0 | 28700 | 21300 | +2535 |
| 11 | 0 | 26579 | 23421 | +2121 |
| 12 | 0 | 24411 | 25589 | +2168 |
| 13 | 0 | 22234 | 27766 | +2177 |
| 14 | 0 | 19678 | 30322 | +2556 |
| 15 | 0 | 17563 | 32437 | +2115 |
| 16 | 0 | 15425 | 34575 | +2138 |
| 17 | 0 | 13247 | 36753 | +2178 |
| 18 | 0 | 10701 | 39299 | +2546 |
| 19 | 0 | 8585 | 41415 | +2116 |
| 20 | 0 | 6423 | 43577 | +2162 |
| 21 | 0 | 3919 | 46081 | +2504 |
| 22 | 0 | 2065 | 47935 | +1854 |
| 23 | 0 | 29 | 49971 | +2036 |
| 24 | 0 | 0 | 50000 | +29 |

**4. Worker Pod-2 (2 worker pods) — Measurements: Tasks vs Time** (`ingest_data_classification-workers-2-size-50000.csv`, finished at mark_min 15)

| mark_min | pending | in_progress | done | done this minute |
|---|---|---|---|---|
| 0 | 50000 | 0 | 0 | +0 |
| 1 | 35000 | 12076 | 2924 | +2924 |
| 2 | 17000 | 26502 | 6498 | +3574 |
| 3 | 0 | 40070 | 9930 | +3432 |
| 4 | 0 | 36565 | 13435 | +3505 |
| 5 | 0 | 32670 | 17330 | +3895 |
| 6 | 0 | 30177 | 19823 | +2493 |
| 7 | 0 | 27087 | 22913 | +3090 |
| 8 | 0 | 23231 | 26769 | +3856 |
| 9 | 0 | 19126 | 30874 | +4105 |
| 10 | 0 | 15804 | 34196 | +3322 |
| 11 | 0 | 12023 | 37977 | +3781 |
| 12 | 0 | 7995 | 42005 | +4028 |
| 13 | 0 | 4287 | 45713 | +3708 |
| 14 | 0 | 184 | 49816 | +4103 |
| 15 | 0 | 0 | 50000 | +184 |

**5. Worker Pod-3 (3 worker pods) — Measurements: Tasks vs Time** (`ingest_data_classification-workers-3-size-50000.csv`, finished at mark_min 13)

| mark_min | pending | in_progress | done | done this minute |
|---|---|---|---|---|
| 0 | 50000 | 0 | 0 | +0 |
| 1 | 38000 | 7744 | 4256 | +4256 |
| 2 | 26000 | 16010 | 7990 | +3734 |
| 3 | 11000 | 27000 | 12000 | +4010 |
| 4 | 0 | 32880 | 17120 | +5120 |
| 5 | 0 | 31172 | 18828 | +1708 |
| 6 | 0 | 27758 | 22242 | +3414 |
| 7 | 0 | 23912 | 26088 | +3846 |
| 8 | 0 | 19741 | 30259 | +4171 |
| 9 | 0 | 14279 | 35721 | +5462 |
| 10 | 0 | 10447 | 39553 | +3832 |
| 11 | 0 | 6792 | 43208 | +3655 |
| 12 | 0 | 2000 | 48000 | +4792 |
| 13 | 0 | 0 | 50000 | +2000 |

**6. Pod CPU / Memory (per run):**

No limit/threshold lines are visible on any graph (axes show auto-scaled max, not a configured limit).

| Pod-Scale | Pod | CPU | Memory | Notes |
|---|---|---|---|---|
| pod-1 | beat-pod | 0→1.5 cpu, peak ~start, settles ~0.1 cpu | 215→236 MiB plateau | Brief startup spike, idles low |
| pod-1 | worker-pod-1 | 0→2 cpu, plateaus ~1.5-1.8 cpu | 0→477 MiB, plateau ~430-477 | Sustained high CPU, headroom to 2 cpu axis |
| pod-2 | beat-pod | 0→1.7 cpu, peak, settles ~0.3 cpu | 221→238 MiB plateau | Startup spike then idle |
| pod-2 | worker-pod-1 | 0→2 cpu, plateau ~1.5-1.8, dip to ~0.8 mid-run | 190→477 MiB plateau | Transient dip mid-run |
| pod-2 | worker-pod-2 | 0→2 cpu, plateau ~1.5-1.8 | ~430-477 MiB plateau | Steady sustained load |
| pod-3 | beat-pod | 0→1.6 cpu peak, settles ~0.3 cpu | 0→286 MiB plateau | Startup spike then idle |
| pod-3 | worker-pod-1 | 0→2 cpu, plateau ~1.5-1.7, dip ~1.0 mid-run | 0→477 MiB plateau | Transient dip mid-run |
| pod-3 | worker-pod-2 | 0→2 cpu, plateau ~1.5-1.7 | ~430-477 MiB plateau | Steady sustained load |
| pod-3 | worker-pod-3 | 0→2 cpu, plateau ~1.5-1.7 | ~430-477 MiB plateau | Steady sustained load |

**7. Observations / Bottlenecks / Potential improvements:**

- **Scaling:** finish minute drops 24 → 15 → 13 as worker pods go 1 → 2 → 3 (steady rate 2,185 → 3,607 → 3,977 rows/min). 1→2 nearly halves the run (-38%); 2→3 is a much smaller gain (-13%) — diminishing returns from the third worker pod.
- **Where the time goes:** beat claims ~15,000 of the 50,000-row cohort (30%) within the first minute at every pod-scale — far more than a 4-tasks/20s default tick would explain, so beat is not the limiting factor here (see the cross-cutting beat-ceiling note above). `pending` reaches 0 by mark 3–4 in all three runs while `in_progress` stays high for most of the run, so drain time is worker time (test-scenarios.md §5).
- **Bottleneck:** the worker pod's CPU plateaus near 1.5–2 cpu (close to the 2-vCPU pod ceiling) at every pod-scale — CPU-bound, consistent with the sub-linear 2→3 scaling above.
- **Potential improvement:** try a 4th/5th worker pod and watch whether finish-minute keeps dropping or flattens — if it flattens, beat's own claim rate (or Postgres) has become the next ceiling, not the worker CPU.

### `ingest_data_transformation`

Partner ingest transformation.

**1. Items in the queue at the beginning:** 10,000 rows — `incoming_classified_data.transformation_status` re-seeded to `PENDING` for this cohort before each of the pod-1/pod-2/pod-3 runs below (same size every time).

**2. Beat parameters:** fires every **10s** (`REGISTRY_CELERY_BEAT_DATA_TRANSFORMATION_BEAT_PRODUCER_FREQUENCY` on this cluster, confirmed via the live deployment; code default differs). Claims **3,000** tasks/tick (confirmed via the live deployment). The producer does mark the row before `send_task`. Shares the transformation frequency with outgest transformation.

**3. Worker Pod-1 (1 worker pod) — Measurements: Tasks vs Time** (`ingest_data_transformation-workers-1-size-10000.csv`, finished at mark_min 16)

| mark_min | pending | in_progress | done | done this minute |
|---|---|---|---|---|
| 0 | 10000 | 0 | 0 | +0 |
| 1 | 0 | 9550 | 450 | +450 |
| 2 | 0 | 8895 | 1105 | +655 |
| 3 | 0 | 8228 | 1772 | +667 |
| 4 | 0 | 7566 | 2434 | +662 |
| 5 | 0 | 6914 | 3086 | +652 |
| 6 | 0 | 6266 | 3734 | +648 |
| 7 | 0 | 5606 | 4394 | +660 |
| 8 | 0 | 4958 | 5042 | +648 |
| 9 | 0 | 4296 | 5704 | +662 |
| 10 | 0 | 3642 | 6358 | +654 |
| 11 | 0 | 2979 | 7021 | +663 |
| 12 | 0 | 2344 | 7656 | +635 |
| 13 | 0 | 1673 | 8327 | +671 |
| 14 | 0 | 1004 | 8996 | +669 |
| 15 | 0 | 339 | 9661 | +665 |
| 16 | 0 | 0 | 10000 | +339 |

**4. Worker Pod-2 (2 worker pods) — Measurements: Tasks vs Time** (`ingest_data_transformation-workers-2-size-10000.csv`, finished at mark_min 9)

| mark_min | pending | in_progress | done | done this minute |
|---|---|---|---|---|
| 0 | 10000 | 0 | 0 | +0 |
| 1 | 0 | 9106 | 894 | +894 |
| 2 | 0 | 7935 | 2065 | +1171 |
| 3 | 0 | 6696 | 3304 | +1239 |
| 4 | 0 | 5532 | 4468 | +1164 |
| 5 | 0 | 4326 | 5674 | +1206 |
| 6 | 0 | 3075 | 6925 | +1251 |
| 7 | 0 | 1937 | 8063 | +1138 |
| 8 | 0 | 667 | 9333 | +1270 |
| 9 | 0 | 0 | 10000 | +667 |

**5. Worker Pod-3 (3 worker pods) — Measurements: Tasks vs Time** (`ingest_data_transformation-workers-3-size-10000.csv`, finished at mark_min 7)

| mark_min | pending | in_progress | done | done this minute |
|---|---|---|---|---|
| 0 | 10000 | 0 | 0 | +0 |
| 1 | 0 | 8776 | 1224 | +1224 |
| 2 | 0 | 7116 | 2884 | +1660 |
| 3 | 0 | 5408 | 4592 | +1708 |
| 4 | 0 | 3704 | 6296 | +1704 |
| 5 | 0 | 2033 | 7967 | +1671 |
| 6 | 0 | 259 | 9741 | +1774 |
| 7 | 0 | 0 | 10000 | +259 |

**6. Pod CPU / Memory (per run):**

| Pod-Scale | Pod | CPU | Memory | Notes |
|---|---|---|---|---|
| 1 | beat | 0→0.57→0.1 cpu | 248→267 MiB | brief spike then idles low, no limit line |
| 1 | worker-1 | 0→1.7-2 cpu (dip to ~0.9) | 191→572 MiB (rising) | near 2-cpu plateau, headroom unclear (no limit shown) |
| 2 | beat | 0→0.57→0.1 cpu | 0→286 MiB plateau | same spike-then-idle pattern |
| 2 | worker-1 | 0→1.5-2 cpu plateau | 191→381 MiB plateau | steady high CPU, flat memory after ramp |
| 2 | worker-2 | 0→~1.9 cpu plateau | 191→381 MiB plateau | mirrors worker-1 |
| 3 | beat | 0→0.6→0.1-0.15 cpu | 0→238 MiB plateau | spike-then-idle pattern |
| 3 | worker-1 | 0→1.9-2 cpu, tapers to ~0.4 end | 191→~477 MiB, sharp step up at end (possibly clipped) | end-of-run taper + mem jump |
| 3 | worker-2 | 0→1.9-2 cpu, tapers to ~1.1 end | 191→~477 MiB, sharp step up at end | similar end-of-run jump |
| 3 | worker-3 | 0→1.9-2 cpu, tapers to ~0.9 end | 191→~477 MiB, sharp step up at end | similar end-of-run jump |

Note: No pod CPU/memory limit or threshold line is drawn in any of the 9 screenshots, so throttling cannot be confirmed visually — all worker CPUs approach a ~2 cpu plateau, suggesting a possible 2-core limit, but this is inferred, not labeled on the graphs.

**7. Observations / Bottlenecks / Potential improvements:**

- **Scaling:** finish minute drops 16 → 9 → 7 (steady rate 658 → 1,206 → 1,703 rows/min) across the smallest backlog (10,000 rows) in the ingest family.
- **Where the time goes:** `pending` hits 0 at mark 1 in *all three* pod-scales — beat enqueues the entire 10k cohort in under a minute every time, so the whole run is worker-bound from minute 1 onward.
- **Bottleneck:** the worker pod's CPU plateaus at 1.7–2 cpu — right at the top of the 2-vCPU axis — at every pod-scale. This is the most clearly CPU-saturated scenario in the whole test cycle.
- **Potential improvement:** this is the strongest signal in this cycle that the transformation worker could use more than 2 vCPU if headroom exists on the node. It shares its beat frequency env var (`REGISTRY_CELERY_BEAT_DATA_TRANSFORMATION_BEAT_PRODUCER_FREQUENCY`) with `outgest_data_transformation` — not a contention risk in these isolated runs, but relevant if both are ever run together.

### `ingest_data`

Partner ingest into the register (pipeline_action ADD).

**1. Items in the queue at the beginning:** 40,000 rows — `incoming_classified_data.ingestion_status` re-seeded to `PENDING` for this cohort before each of the pod-1/pod-2/pod-3 runs below (same size every time).

**2. Beat parameters:** fires every **10s** (`REGISTRY_CELERY_BEAT_INGEST_DATA_BEAT_PRODUCER_FREQUENCY` on this cluster, confirmed via the live deployment; code default differs). Claims **20,000** tasks/tick (confirmed via the live deployment). The producer does mark the row before `send_task`. The ingest beat producer sends UPDATE rows to change_request_ingest_worker instead.

**3. Worker Pod-1 (1 worker pod) — Measurements: Tasks vs Time** (`ingest_data-workers-1-size-40000.csv`, finished at mark_min 24)

| mark_min | pending | in_progress | done | done this minute |
|---|---|---|---|---|
| 0 | 40000 | 0 | 0 | +0 |
| 1 | 25000 | 13822 | 1178 | +1178 |
| 2 | 7000 | 30261 | 2739 | +1561 |
| 3 | 0 | 35643 | 4357 | +1618 |
| 4 | 0 | 33888 | 6112 | +1755 |
| 5 | 0 | 32201 | 7799 | +1687 |
| 6 | 0 | 30458 | 9542 | +1743 |
| 7 | 0 | 28747 | 11253 | +1711 |
| 8 | 0 | 27021 | 12979 | +1726 |
| 9 | 0 | 25323 | 14677 | +1698 |
| 10 | 0 | 23578 | 16422 | +1745 |
| 11 | 0 | 21879 | 18121 | +1699 |
| 12 | 0 | 20145 | 19855 | +1734 |
| 13 | 0 | 18442 | 21558 | +1703 |
| 14 | 0 | 16728 | 23272 | +1714 |
| 15 | 0 | 15061 | 24939 | +1667 |
| 16 | 0 | 13357 | 26643 | +1704 |
| 17 | 0 | 11589 | 28411 | +1768 |
| 18 | 0 | 9847 | 30153 | +1742 |
| 19 | 0 | 8077 | 31923 | +1770 |
| 20 | 0 | 6331 | 33669 | +1746 |
| 21 | 0 | 4564 | 35436 | +1767 |
| 22 | 0 | 2813 | 37187 | +1751 |
| 23 | 0 | 1035 | 38965 | +1778 |
| 24 | 0 | 0 | 40000 | +1035 |

**4. Worker Pod-2 (2 worker pods) — Measurements: Tasks vs Time** (`ingest_data-workers-2-size-40000.csv`, finished at mark_min 13)

| mark_min | pending | in_progress | done | done this minute |
|---|---|---|---|---|
| 0 | 40000 | 0 | 0 | +0 |
| 1 | 25000 | 12693 | 2307 | +2307 |
| 2 | 7000 | 27862 | 5138 | +2831 |
| 3 | 0 | 31687 | 8313 | +3175 |
| 4 | 0 | 28505 | 11495 | +3182 |
| 5 | 0 | 25303 | 14697 | +3202 |
| 6 | 0 | 22142 | 17858 | +3161 |
| 7 | 0 | 19037 | 20963 | +3105 |
| 8 | 0 | 15788 | 24212 | +3249 |
| 9 | 0 | 12638 | 27362 | +3150 |
| 10 | 0 | 9396 | 30604 | +3242 |
| 11 | 0 | 6235 | 33765 | +3161 |
| 12 | 0 | 3003 | 36997 | +3232 |
| 13 | 0 | 0 | 40000 | +3003 |

**5. Worker Pod-3 (3 worker pods) — Measurements: Tasks vs Time** (`ingest_data-workers-3-size-40000.csv`, finished at mark_min 10)

| mark_min | pending | in_progress | done | done this minute |
|---|---|---|---|---|
| 0 | 40000 | 0 | 0 | +0 |
| 1 | 25000 | 11751 | 3249 | +3249 |
| 2 | 7000 | 25726 | 7274 | +4025 |
| 3 | 0 | 28486 | 11514 | +4240 |
| 4 | 0 | 24142 | 15858 | +4344 |
| 5 | 0 | 19775 | 20225 | +4367 |
| 6 | 0 | 15368 | 24632 | +4407 |
| 7 | 0 | 12018 | 27982 | +3350 |
| 8 | 0 | 8186 | 31814 | +3832 |
| 9 | 0 | 3857 | 36143 | +4329 |
| 10 | 0 | 0 | 40000 | +3857 |

**6. Pod CPU / Memory (per run):**

No limit/threshold lines are drawn on any of the 9 graphs (axes just autoscale); "throttled" judgments below are inferred from flat plateaus only.

| Pod-Scale | Pod | CPU | Memory | Notes |
|---|---|---|---|---|
| pod-1 | beat-pod | 0→0.55 cpu spike, back to ~0.05 | 220→267 MiB plateau | Brief beat burst, then idle |
| pod-1 | worker-pod-1 | 0→1.5-1.75 cpu, sawtooth plateau | 238→335 MiB, rising slowly | Plateau near ~1.5-1.75 cpu, possible soft ceiling, otherwise headroom to 2 cpu axis |
| pod-2 | beat-pod | 0→1.3 cpu spike, decays to 0 | 243→271 MiB plateau | Single burst, no sustained load |
| pod-2 | worker-pod-1 | 0→~1.5 cpu, flat sawtooth plateau | 238→335 MiB, flat plateau | Plateau flatlines at ~1.5 cpu, likely throttled |
| pod-2 | worker-pod-2 | 0→~1.5 cpu, flat sawtooth plateau | 238→335 MiB, flat plateau | Same ~1.5 cpu ceiling pattern as worker-1 |
| pod-3 | beat-pod | 0→1.6 cpu spike, decays to 0 | 0→259 MiB plateau | Single burst |
| pod-3 | worker-pod-1 | 0→1.5-1.75 cpu, mild dip/recover | 0→335 MiB plateau | Near-plateau ~1.5-1.75 cpu, some headroom to 2 cpu |
| pod-3 | worker-pod-2 | 0→1.5-1.75 cpu, mild dip/recover | 0→335 MiB plateau | Same pattern as worker-1 |
| pod-3 | worker-pod-3 | 0→1.5-1.75 cpu, mild dip/recover | 0→335 MiB plateau | Same pattern, 3 workers share similar load |

**7. Observations / Bottlenecks / Potential improvements:**

- **Scaling:** finish minute drops 24 → 13 → 10 (steady rate 1,718 → 3,154 → 4,112 rows/min).
- **Where the time goes:** `pending` clears by mark 3 each time; `in_progress` dominates the rest of the run — worker-bound, same pattern as the other partner-ingest scenarios.
- **Bottleneck:** worker CPU plateaus 1.0–1.8 cpu across the three pod-scales, generally with more headroom to the 2-cpu ceiling than `ingest_data_transformation` shows — consistent with a plain register write costing less per row than the transformation step.
- **Shared producer:** this scenario and `change_request_ingest` share one beat producer (same table/column, filtered by `pipeline_action`) — see that scenario's notes for the two-step claim pattern visible on the shared producer.

### `change_request_ingest`

Partner ingest that updates an existing record.

**1. Items in the queue at the beginning:** 50,000 rows — `incoming_classified_data.ingestion_status` re-seeded to `PENDING` for this cohort before each of the pod-1/pod-2/pod-3 runs below (same size every time).

**2. Beat parameters:** fires every **10s** (`REGISTRY_CELERY_BEAT_INGEST_DATA_BEAT_PRODUCER_FREQUENCY` on this cluster, confirmed via the live deployment; code default differs). Claims **20,000** tasks/tick (confirmed via the live deployment). The producer does mark the row before `send_task`. Same beat producer as ingest_data. Isolation is pipeline_action = UPDATE.

**3. Worker Pod-1 (1 worker pod) — Measurements: Tasks vs Time** (`change_request_ingest-workers-1-size-50000.csv`, finished at mark_min 16)

| mark_min | pending | in_progress | done | done this minute |
|---|---|---|---|---|
| 0 | 50000 | 0 | 0 | +0 |
| 1 | 10000 | 38638 | 1362 | +1362 |
| 2 | 10000 | 35862 | 4138 | +2776 |
| 3 | 0 | 42697 | 7303 | +3165 |
| 4 | 0 | 39280 | 10720 | +3417 |
| 5 | 0 | 35912 | 14088 | +3368 |
| 6 | 0 | 32653 | 17347 | +3259 |
| 7 | 0 | 29166 | 20834 | +3487 |
| 8 | 0 | 25737 | 24263 | +3429 |
| 9 | 0 | 22280 | 27720 | +3457 |
| 10 | 0 | 18791 | 31209 | +3489 |
| 11 | 0 | 15397 | 34603 | +3394 |
| 12 | 0 | 11918 | 38082 | +3479 |
| 13 | 0 | 8497 | 41503 | +3421 |
| 14 | 0 | 5124 | 44876 | +3373 |
| 15 | 0 | 1700 | 48300 | +3424 |
| 16 | 0 | 0 | 50000 | +1700 |

**4. Worker Pod-2 (2 worker pods) — Measurements: Tasks vs Time** (`change_request_ingest-workers-2-size-50000.csv`, finished at mark_min 10)

| mark_min | pending | in_progress | done | done this minute |
|---|---|---|---|---|
| 0 | 50000 | 0 | 0 | +0 |
| 1 | 10000 | 37820 | 2180 | +2180 |
| 2 | 10000 | 32677 | 7323 | +5143 |
| 3 | 0 | 37319 | 12681 | +5358 |
| 4 | 0 | 31425 | 18575 | +5894 |
| 5 | 0 | 25284 | 24716 | +6141 |
| 6 | 0 | 19477 | 30523 | +5807 |
| 7 | 0 | 13469 | 36531 | +6008 |
| 8 | 0 | 7448 | 42552 | +6021 |
| 9 | 0 | 1412 | 48588 | +6036 |
| 10 | 0 | 0 | 50000 | +1412 |

**5. Worker Pod-3 (3 worker pods) — Measurements: Tasks vs Time** (`change_request_ingest-workers-3-size-50000.csv`, finished at mark_min 9)

| mark_min | pending | in_progress | done | done this minute |
|---|---|---|---|---|
| 0 | 50000 | 0 | 0 | +0 |
| 1 | 10000 | 36940 | 3060 | +3060 |
| 2 | 10000 | 30125 | 9875 | +6815 |
| 3 | 0 | 35245 | 14755 | +4880 |
| 4 | 0 | 31964 | 18036 | +3281 |
| 5 | 0 | 26198 | 23802 | +5766 |
| 6 | 0 | 18342 | 31658 | +7856 |
| 7 | 0 | 10647 | 39353 | +7695 |
| 8 | 0 | 2840 | 47160 | +7807 |
| 9 | 0 | 0 | 50000 | +2840 |

**6. Pod CPU / Memory (per run):**

| Pod-Scale | Pod | CPU | Memory | Notes |
|---|---|---|---|---|
| 1-worker | beat | 0→1.5 cpu | 0→~310 MiB | spike then idle to 0 |
| 1-worker | worker | 0→1.3–1.7 cpu | 0→~330 MiB plateau | plateau, no limit line, headroom to 2 cpu axis max |
| 2-worker | beat | 0→1.5 cpu | 0→~330 MiB, settles ~310 | spike then idle to 0 |
| 2-worker | worker-1 | 0→1.3–1.7 cpu | 0→~310 MiB plateau | fluctuating plateau, headroom |
| 2-worker | worker-2 | 0→1.5–1.7 cpu | ~215→~330 MiB plateau | fluctuating plateau, headroom |
| 3-worker | beat | 0→1.2 cpu | 0→~310 MiB | spike then idle to ~0 |
| 3-worker | worker-1 | 0→0.5–1.4 cpu (dip mid-run) | 0→~310 MiB plateau | tapers to 0 near end (drain finished) |
| 3-worker | worker-2 | 0→0.6–1.5 cpu (dip mid-run) | 0→~310 MiB, drops to ~130 MiB late | work finished early, idled down |
| 3-worker | worker-3 | 0→0.6–1.4 cpu (dip mid-run) | 0→~310 MiB plateau | tapers to 0 near end (drain finished) |

Note: No CPU/memory limit threshold lines are drawn in any of the 9 graphs, so throttling can't be confirmed visually; CPU stays below axis max in all cases, suggesting headroom.

**7. Observations / Bottlenecks / Potential improvements:**

- **Scaling:** finish minute drops 16 → 10 → 9 (steady rate 3,353 → 5,801 → 6,300 rows/min) — the fastest per-row throughput of the four partner-ingest scenarios.
- **Where the time goes — distinctive claim pattern:** `pending` drops from 50,000 → 10,000 at mark 1 and *stays* at 10,000 through mark 2, then hits 0 at mark 3 — identically at all three pod-scales. Beat claims this cohort in (at least) two batches rather than one; that's a property of the shared `ingest_data` beat producer and this cohort, not of worker count.
- **Bottleneck:** worker CPU plateaus 1.3–1.7 cpu with headroom at pod-1/pod-2; the pod-3 run shows wider swings (0.5–1.5 cpu) with one worker tapering toward 0 near the end — the 3-pod run still finishes fastest in wall-clock terms, but the tail of work isn't split evenly across the three pods.

## Outgest

### `outgest_data_transformation`

Outgest payload transformation.

**1. Items in the queue at the beginning:** 10,000 rows — `outgoing_raw_data.transformation_status` re-seeded to `PENDING` for this cohort before each of the pod-1/pod-2/pod-3 runs below (same size every time).

**2. Beat parameters:** fires every **10s** (`REGISTRY_CELERY_BEAT_DATA_TRANSFORMATION_BEAT_PRODUCER_FREQUENCY` on this cluster, confirmed via the live deployment; code default differs). Claims **20,000** tasks/tick (confirmed via the live deployment). The producer does mark the row before `send_task`. Shares the transformation frequency with ingest transformation.

**3. Worker Pod-1 (1 worker pod) — Measurements: Tasks vs Time** (`outgest_data_transformation-workers-1-size-10000.csv`, finished at mark_min 28)

| mark_min | pending | in_progress | done | done this minute |
|---|---|---|---|---|
| 0 | 10000 | 0 | 0 | +0 |
| 1 | 0 | 9762 | 238 | +238 |
| 2 | 0 | 9394 | 606 | +368 |
| 3 | 0 | 9025 | 975 | +369 |
| 4 | 0 | 8655 | 1345 | +370 |
| 5 | 0 | 8280 | 1720 | +375 |
| 6 | 0 | 7912 | 2088 | +368 |
| 7 | 0 | 7537 | 2463 | +375 |
| 8 | 0 | 7168 | 2832 | +369 |
| 9 | 0 | 6793 | 3207 | +375 |
| 10 | 0 | 6425 | 3575 | +368 |
| 11 | 0 | 6052 | 3948 | +373 |
| 12 | 0 | 5685 | 4315 | +367 |
| 13 | 0 | 5319 | 4681 | +366 |
| 14 | 0 | 4954 | 5046 | +365 |
| 15 | 0 | 4594 | 5406 | +360 |
| 16 | 0 | 4225 | 5775 | +369 |
| 17 | 0 | 3855 | 6145 | +370 |
| 18 | 0 | 3487 | 6513 | +368 |
| 19 | 0 | 3124 | 6876 | +363 |
| 20 | 0 | 2753 | 7247 | +371 |
| 21 | 0 | 2388 | 7612 | +365 |
| 22 | 0 | 2021 | 7979 | +367 |
| 23 | 0 | 1660 | 8340 | +361 |
| 24 | 0 | 1288 | 8712 | +372 |
| 25 | 0 | 922 | 9078 | +366 |
| 26 | 0 | 551 | 9449 | +371 |
| 27 | 0 | 186 | 9814 | +365 |
| 28 | 0 | 0 | 10000 | +186 |

**4. Worker Pod-2 (2 worker pods) — Measurements: Tasks vs Time** (`outgest_data_transformation-workers-2-size-10000.csv`, finished at mark_min 15)

| mark_min | pending | in_progress | done | done this minute |
|---|---|---|---|---|
| 0 | 10000 | 0 | 0 | +0 |
| 1 | 0 | 9558 | 442 | +442 |
| 2 | 0 | 8835 | 1165 | +723 |
| 3 | 0 | 8098 | 1902 | +737 |
| 4 | 0 | 7376 | 2624 | +722 |
| 5 | 0 | 6639 | 3361 | +737 |
| 6 | 0 | 5853 | 4147 | +786 |
| 7 | 0 | 5175 | 4825 | +678 |
| 8 | 0 | 4449 | 5551 | +726 |
| 9 | 0 | 3706 | 6294 | +743 |
| 10 | 0 | 2996 | 7004 | +710 |
| 11 | 0 | 2260 | 7740 | +736 |
| 12 | 0 | 1544 | 8456 | +716 |
| 13 | 0 | 811 | 9189 | +733 |
| 14 | 0 | 96 | 9904 | +715 |
| 15 | 0 | 0 | 10000 | +96 |

**5. Worker Pod-3 (3 worker pods) — Measurements: Tasks vs Time** (`outgest_data_transformation-workers-3-size-10000.csv`, finished at mark_min 11)

| mark_min | pending | in_progress | done | done this minute |
|---|---|---|---|---|
| 0 | 10000 | 0 | 0 | +0 |
| 1 | 0 | 9338 | 662 | +662 |
| 2 | 0 | 8290 | 1710 | +1048 |
| 3 | 0 | 7245 | 2755 | +1045 |
| 4 | 0 | 6215 | 3785 | +1030 |
| 5 | 0 | 5194 | 4806 | +1021 |
| 6 | 0 | 4141 | 5859 | +1053 |
| 7 | 0 | 3154 | 6846 | +987 |
| 8 | 0 | 2163 | 7837 | +991 |
| 9 | 0 | 1209 | 8791 | +954 |
| 10 | 0 | 199 | 9801 | +1010 |
| 11 | 0 | 0 | 10000 | +199 |

**6. Pod CPU / Memory (per run):**

| Pod-Scale | Pod | CPU | Memory | Notes |
|---|---|---|---|---|
| pod-1 | beat-pod | 0→0.45 cpu, drops to ~0 | ramps to flat ~238 MiB | spike then idle; headroom |
| pod-1 | worker-pod-1 | ramps to ~1.7-2 cpu plateau (dips to ~1.3) | ramps to flat ~286 MiB | plateau near top of 2-cpu axis; likely throttled |
| pod-2 | beat-pod | 0→0.55 cpu, drops to ~0 | ramps to flat ~238 MiB | spike then idle; headroom |
| pod-2 | worker-pod-1 | ramps to ~1.7-2 cpu, flat top | ramps to flat ~310 MiB | flat ceiling near 2 cpu; likely throttled |
| pod-2 | worker-pod-2 | — | — | screenshot missing on disk |
| pod-3 | beat-pod | 0→0.45 cpu, drops to ~0 | ramps to flat ~286 MiB (higher than pod-1/2 beat) | spike then idle; headroom |
| pod-3 | worker-pod-1 | ramps to ~1.9 cpu plateau, dips mid-run, tapers at end | ramps to flat ~310 MiB | near-ceiling plateau; likely throttled |
| pod-3 | worker-pod-2 | ramps to ~1.9 cpu plateau (dip to ~1.3 mid) | ramps to flat ~310 MiB | near-ceiling plateau; likely throttled |
| pod-3 | worker-pod-3 | ramps to ~1.9 cpu plateau, variable | ramps to flat ~310 MiB | near-ceiling plateau; likely throttled |

No axis showed an explicit limit/threshold line; "likely throttled" is inferred from flat plateaus pinned near the 2-cpu axis top on all worker pods. pod-2/worker-pod-2.png is genuinely missing on disk (not an agent error).

**7. Observations / Bottlenecks / Potential improvements:**

- **Scaling:** finish minute drops 28 → 15 → 11 (steady rate 368 → 728 → 1,015 rows/min) — the slowest-draining scenario in the whole set, even slower than its same-size (10,000-row) sibling `ingest_data_transformation`.
- **Where the time goes:** `pending` hits 0 at mark 1 in all three runs — fully worker-bound from the start.
- **Bottleneck:** worker CPU plateaus right at the top of the 2-cpu axis at every pod-scale (near-ceiling / "likely throttled") — the same CPU-saturation signature as `ingest_data_transformation`, making the two transformation-step workers the most CPU-constrained scenarios measured this cycle.
- **Known gap:** `pod-2/worker-pod-2.png` is missing from the results directory — the second worker pod's CPU/Memory graph for the 2-worker-pod run was never captured, so that one data point couldn't be transcribed for this report.

### `outgest_data_publish`

Outgest publish.

**1. Items in the queue at the beginning:** 50,000 rows — `outgoing_raw_data.publish_status` re-seeded to `PENDING` for this cohort before each of the pod-1/pod-2/pod-3 runs below (same size every time).

**2. Beat parameters:** fires every **10s** (`REGISTRY_CELERY_BEAT_OUTGEST_DATA_PUBLISH_BEAT_PRODUCER_FREQUENCY` on this cluster, confirmed via the live deployment; code default differs). Claims **20,000** tasks/tick (confirmed via the live deployment). The producer does mark the row before `send_task`. Beat claims publish_status before enqueue.

**3. Worker Pod-1 (1 worker pod) — Measurements: Tasks vs Time** (`outgest_data_publish-workers-1-size-50000.csv`, finished at mark_min 22)

| mark_min | pending | in_progress | done | done this minute |
|---|---|---|---|---|
| 0 | 50000 | 0 | 0 | +0 |
| 1 | 10007 | 39094 | 899 | +899 |
| 2 | 0 | 46967 | 3033 | +2134 |
| 3 | 1 | 44660 | 5339 | +2306 |
| 4 | 0 | 42202 | 7798 | +2459 |
| 5 | 0 | 39782 | 10218 | +2420 |
| 6 | 1 | 37120 | 12879 | +2661 |
| 7 | 0 | 34960 | 15040 | +2161 |
| 8 | 2 | 32471 | 17527 | +2487 |
| 9 | 0 | 30043 | 19957 | +2430 |
| 10 | 0 | 27614 | 22386 | +2429 |
| 11 | 1 | 25260 | 24739 | +2353 |
| 12 | 0 | 22879 | 27121 | +2382 |
| 13 | 0 | 20423 | 29577 | +2456 |
| 14 | 0 | 18043 | 31957 | +2380 |
| 15 | 1 | 15579 | 34420 | +2463 |
| 16 | 0 | 13193 | 36807 | +2387 |
| 17 | 2 | 10841 | 39157 | +2350 |
| 18 | 1 | 8462 | 41537 | +2380 |
| 19 | 0 | 6030 | 43970 | +2433 |
| 20 | 1 | 3607 | 46392 | +2422 |
| 21 | 2 | 1180 | 48818 | +2426 |
| 22 | 0 | 0 | 50000 | +1182 |

**4. Worker Pod-2 (2 worker pods) — Measurements: Tasks vs Time** (`outgest_data_publish-workers-2-size-50000.csv`, finished at mark_min 15)

| mark_min | pending | in_progress | done | done this minute |
|---|---|---|---|---|
| 0 | 50000 | 0 | 0 | +0 |
| 1 | 10011 | 38432 | 1557 | +1557 |
| 2 | 10046 | 35006 | 4948 | +3391 |
| 3 | 0 | 41431 | 8569 | +3621 |
| 4 | 0 | 37599 | 12401 | +3832 |
| 5 | 9 | 33936 | 16055 | +3654 |
| 6 | 0 | 31276 | 18724 | +2669 |
| 7 | 10 | 27608 | 22382 | +3658 |
| 8 | 0 | 23770 | 26230 | +3848 |
| 9 | 5 | 19930 | 30065 | +3835 |
| 10 | 0 | 16011 | 33989 | +3924 |
| 11 | 0 | 12213 | 37787 | +3798 |
| 12 | 0 | 8276 | 41724 | +3937 |
| 13 | 0 | 4425 | 45575 | +3851 |
| 14 | 0 | 607 | 49393 | +3818 |
| 15 | 0 | 0 | 50000 | +607 |

**5. Worker Pod-3 (3 worker pods) — Measurements: Tasks vs Time** (`outgest_data_publish-workers-3-size-50000.csv`, finished at mark_min 13)

| mark_min | pending | in_progress | done | done this minute |
|---|---|---|---|---|
| 0 | 50000 | 0 | 0 | +0 |
| 1 | 10037 | 38179 | 1784 | +1784 |
| 2 | 10128 | 34142 | 5730 | +3946 |
| 3 | 2 | 40287 | 9711 | +3981 |
| 4 | 4 | 36038 | 13958 | +4247 |
| 5 | 4 | 31828 | 18168 | +4210 |
| 6 | 5 | 27500 | 22495 | +4327 |
| 7 | 2 | 23188 | 26810 | +4315 |
| 8 | 3 | 19073 | 30924 | +4114 |
| 9 | 7 | 14732 | 35261 | +4337 |
| 10 | 4 | 10435 | 39561 | +4300 |
| 11 | 5 | 6086 | 43909 | +4348 |
| 12 | 4 | 1828 | 48168 | +4259 |
| 13 | 0 | 0 | 50000 | +1832 |

**6. Pod CPU / Memory (per run):**

Note: none of the 9 graphs show an explicit limit/threshold line — axis max appears auto-scaled to observed data, not a pod resource limit.

| Pod-Scale | Pod | CPU | Memory | Notes |
|---|---|---|---|---|
| pod-1 | beat-pod | 0→1.65 cpu, spike then drops to 0 | 0→335 MiB plateau | Brief burst only, idle rest of run |
| pod-1 | worker-pod-1 | ~1.0→1.5 cpu plateau (dips to ~0.9) | ~335 MiB plateau | Sustained load, headroom to axis max (2 cpu) |
| pod-2 | beat-pod | 0→1.4 cpu spike then drops to 0 | 0→330 MiB plateau | Same burst pattern as pod-1 beat |
| pod-2 | worker-pod-1 | ~0.9→1.15 cpu plateau, minor dips | 238→333 MiB, rising then flat | Headroom, no flatline/throttle |
| pod-2 | worker-pod-2 | ~1.0→1.3 cpu plateau, saw-tooth | ~310 MiB plateau | Mild oscillation, IO-wait-like pattern |
| pod-3 | beat-pod | 0→1.45 cpu spike then drops to 0 | 0→335 MiB plateau (axis max 476.8 MiB) | Consistent beat burst-then-idle behavior |
| pod-3 | worker-pod-1 | ~0.5→1.05 cpu plateau, dips | 238→335 MiB rising then flat | No ceiling flatline, headroom |
| pod-3 | worker-pod-2 | ~1.0 cpu plateau, minor dip | 238→345 MiB rising then flat | Similar to worker-1, no throttling |
| pod-3 | worker-pod-3 | ~0.9→1.05 cpu plateau, saw-tooth | 238→345 MiB rising then flat | No ceiling flatline, headroom |

Overall: beat pods show a short burst then idle; worker pods sustain ~1–1.5 cpu plateaus, none hard-flatlined at a ceiling — consistent with the scenario's IO-wait-bound publish calls rather than CPU saturation.

**7. Observations / Bottlenecks / Potential improvements:**

- **Scaling:** finish minute drops 22 → 15 → 13 (steady rate 2,396 → 3,680 → 4,217 rows/min).
- **Where the time goes — unlike every other scenario:** `pending` does not stay flat at 0 after the initial claim; it bounces between 0 and 1–10 rows for most of the run (e.g. pod-3, mark 3 onward: 2, 4, 4, 5, 2, 3, 7, 4, 5, 4). Small groups of rows keep cycling back to `PENDING` instead of draining in one pass — consistent with retries against the external `https://websub.perftest.openg2p.org` publish endpoint re-queuing a handful of rows each tick.
- **Bottleneck:** worker CPU plateaus in the 0.9–1.5 cpu band with headroom to the 2-cpu ceiling at every pod-scale — not CPU-bound, consistent with time spent waiting on the external HTTP call rather than computing.
- **Potential improvement:** instrument the external endpoint's own latency/retry count — it isn't visible in this results set — before concluding whether 3 worker pods is the practical ceiling for this scenario.

## Intake ingest

### `intake_register_ingest`

Approved intake submission ingest into the register.

**1. Items in the queue at the beginning:** 10,000 rows — `g2p_intake_form_submissions.register_ingest_process_status` re-seeded to `PENDING` for this cohort before each of the pod-1/pod-2/pod-3 runs below (same size every time).

**2. Beat parameters:** fires every **10s** (`REGISTRY_CELERY_BEAT_INTAKE_FORM_REGISTER_INGEST_BEAT_PRODUCER_FREQUENCY` on this cluster, confirmed via the live deployment; code default differs). Claims **3,000** tasks/tick (confirmed via the live deployment). The producer does **not** mark the row before `send_task`. The ingest producer does not mark the row PROCESSING before send_task. The worker does, and it also requires draft_status FINAL. A faster beat re-enqueues the same submissions until that mark lands, so failed duplicate tasks show up in the worker logs. Processed submissions also fan out score and outgest work.

**3. Worker Pod-1 (1 worker pod) — Measurements: Tasks vs Time** (`intake_register_ingest-workers-1-size-10000.csv`, finished at mark_min 18)

| mark_min | pending | in_progress | done | done this minute |
|---|---|---|---|---|
| 0 | 10000 | 0 | 0 | +0 |
| 1 | 0 | 9566 | 434 | +434 |
| 2 | 0 | 9049 | 951 | +517 |
| 3 | 0 | 8474 | 1526 | +575 |
| 4 | 0 | 7884 | 2116 | +590 |
| 5 | 0 | 7307 | 2693 | +577 |
| 6 | 0 | 6855 | 3145 | +452 |
| 7 | 0 | 6303 | 3697 | +552 |
| 8 | 0 | 5714 | 4286 | +589 |
| 9 | 0 | 5118 | 4882 | +596 |
| 10 | 0 | 4524 | 5476 | +594 |
| 11 | 0 | 3962 | 6038 | +562 |
| 12 | 0 | 3423 | 6577 | +539 |
| 13 | 0 | 2862 | 7138 | +561 |
| 14 | 0 | 2272 | 7728 | +590 |
| 15 | 0 | 1670 | 8330 | +602 |
| 16 | 0 | 1053 | 8947 | +617 |
| 17 | 0 | 509 | 9491 | +544 |
| 18 | 0 | 0 | 10000 | +509 |

**4. Worker Pod-2 (2 worker pods) — Measurements: Tasks vs Time** (`intake_register_ingest-workers-2-size-10000.csv`, finished at mark_min 11)

| mark_min | pending | in_progress | done | done this minute |
|---|---|---|---|---|
| 0 | 10000 | 0 | 0 | +0 |
| 1 | 0 | 9137 | 863 | +863 |
| 2 | 0 | 8045 | 1955 | +1092 |
| 3 | 0 | 7000 | 3000 | +1045 |
| 4 | 0 | 6384 | 3616 | +616 |
| 5 | 0 | 5507 | 4493 | +877 |
| 6 | 0 | 4389 | 5611 | +1118 |
| 7 | 0 | 3448 | 6552 | +941 |
| 8 | 0 | 2563 | 7437 | +885 |
| 9 | 0 | 1442 | 8558 | +1121 |
| 10 | 0 | 480 | 9520 | +962 |
| 11 | 0 | 0 | 10000 | +480 |

**5. Worker Pod-3 (3 worker pods) — Measurements: Tasks vs Time** (`intake_register_ingest-workers-3-size-10000.csv`, finished at mark_min 8)

| mark_min | pending | in_progress | done | done this minute |
|---|---|---|---|---|
| 0 | 10000 | 0 | 0 | +0 |
| 1 | 0 | 8805 | 1195 | +1195 |
| 2 | 0 | 7246 | 2754 | +1559 |
| 3 | 0 | 6071 | 3929 | +1175 |
| 4 | 0 | 4594 | 5406 | +1477 |
| 5 | 0 | 3532 | 6468 | +1062 |
| 6 | 0 | 2238 | 7762 | +1294 |
| 7 | 0 | 929 | 9071 | +1309 |
| 8 | 0 | 0 | 10000 | +929 |

**6. Pod CPU / Memory (per run):**

No limit/threshold lines are visible on any of these panels; Notes reflect pattern shape only.

| Pod-Scale | Pod | CPU | Memory | Notes |
|---|---|---|---|---|
| 1 | beat | 0.2→0.85 cpu | 249→264 MiB | ramp, plateau, taper off |
| 1 | worker-1 | 0→1.4 cpu (osc 1.0–1.4) | 215→310 MiB | plateau, headroom (no limit shown) |
| 2 | beat | 0.1→1.0 cpu | 261→265 MiB | plateau then drop at end |
| 2 | worker-1 | 0→1.5 cpu, dip to 0.8 mid | ~286 MiB plateau | ramp, slight dip, headroom |
| 2 | worker-2 | 0→1.5 cpu plateau | 215→310 MiB plateau | steady plateau, headroom |
| 3 | beat | 0.2→0.85 cpu | 262→264.6 MiB | mild fluctuation, taper off |
| 3 | worker-1 | 0→1.3 cpu, oscillates 0.3–1.3 | 215→310 MiB plateau | variable load, headroom |
| 3 | worker-2 | 0→1.1 cpu, oscillates 0.3–1.1 | 215→310 MiB plateau | variable load, headroom |
| 3 | worker-3 | 0→1.1 cpu, oscillates 0.3–1.1 | 215→310 MiB plateau | variable load, headroom |

**7. Observations / Bottlenecks / Potential improvements:**

- **Scaling:** finish minute drops 18 → 11 → 8 (steady rate 566 → 962 → 1,313 rows/min).
- **Design note (`producer_claims_row=False`):** this is the only tested scenario where the beat producer does *not* mark the row `PROCESSING` before `send_task` — the worker does, and only after also checking `draft_status = FINAL`. `cases.py` warns that a faster beat (or shorter interval) risks re-enqueuing the same submissions until that mark lands, producing duplicate failed tasks in the worker log. Worker logs weren't captured in this results set, so that risk couldn't be confirmed or ruled out from the CSV/CPU data alone — worth closing before this scenario's beat frequency is tuned.
- **Bottleneck:** worker CPU plateaus 1.0–1.5 cpu with headroom across all three pod-scales — not CPU-bound.
- **Scope note:** a processed submission fans out score and outgest work in a live system (`cases.py`); this isolated run parks those producers, so the real end-to-end cost of an intake-ingest isn't captured by this scenario alone.

## Functional ID

### `functional_id_allocation`

Functional ID allocation (id generation).

**1. Items in the queue at the beginning:** 50,000 rows — `g2p_functional_id_generation_queue.id_allocation_status` re-seeded to `PENDING` for this cohort before each of the pod-1/pod-2/pod-3 runs below (same size every time).

**2. Beat parameters:** fires every **10s** (`REGISTRY_CELERY_BEAT_FUNCTIONAL_ID_ALLOCATION_BEAT_PRODUCER_FREQUENCY` on this cluster, confirmed via the live deployment; code default differs). Claims **3,000** tasks/tick (confirmed via the live deployment). The producer does mark the row before `send_task`. The allocation worker sets id_updation_status to PENDING, so functional_id_updation_beat_producer starts enqueueing follow-on work onto the same queue. Allocation completion is still the id_allocation_status delta; id_updation_pending shows the leak.

**3. Worker Pod-1 (1 worker pod) — Measurements: Tasks vs Time** (`functional_id_allocation-workers-1-size-50000.csv`, finished at mark_min 26)

| mark_min | pending | in_progress | done | done this minute |
|---|---|---|---|---|
| 0 | 50000 | 0 | 0 | +0 |
| 1 | 35000 | 13548 | 1452 | +1452 |
| 2 | 17000 | 29420 | 3580 | +2128 |
| 3 | 0 | 44343 | 5657 | +2077 |
| 4 | 0 | 42098 | 7902 | +2245 |
| 5 | 0 | 39976 | 10024 | +2122 |
| 6 | 0 | 37988 | 12012 | +1988 |
| 7 | 0 | 36207 | 13793 | +1781 |
| 8 | 0 | 34136 | 15864 | +2071 |
| 9 | 0 | 32093 | 17907 | +2043 |
| 10 | 0 | 30081 | 19919 | +2012 |
| 11 | 0 | 28088 | 21912 | +1993 |
| 12 | 0 | 26096 | 23904 | +1992 |
| 13 | 0 | 24195 | 25805 | +1901 |
| 14 | 0 | 22316 | 27684 | +1879 |
| 15 | 0 | 20356 | 29644 | +1960 |
| 16 | 0 | 18254 | 31746 | +2102 |
| 17 | 0 | 16667 | 33333 | +1587 |
| 18 | 0 | 14717 | 35283 | +1950 |
| 19 | 0 | 12686 | 37314 | +2031 |
| 20 | 0 | 10836 | 39164 | +1850 |
| 21 | 0 | 8996 | 41004 | +1840 |
| 22 | 0 | 7067 | 42933 | +1929 |
| 23 | 0 | 5343 | 44657 | +1724 |
| 24 | 0 | 3393 | 46607 | +1950 |
| 25 | 0 | 1524 | 48476 | +1869 |
| 26 | 0 | 0 | 50000 | +1524 |

**4. Worker Pod-2 (2 worker pods) — Measurements: Tasks vs Time** (`functional_id_allocation-workers-2-size-50000.csv`, finished at mark_min 15)

| mark_min | pending | in_progress | done | done this minute |
|---|---|---|---|---|
| 0 | 50000 | 0 | 0 | +0 |
| 1 | 35000 | 12431 | 2569 | +2569 |
| 2 | 17000 | 27368 | 5632 | +3063 |
| 3 | 0 | 41258 | 8742 | +3110 |
| 4 | 0 | 37900 | 12100 | +3358 |
| 5 | 0 | 34225 | 15775 | +3675 |
| 6 | 0 | 30588 | 19412 | +3637 |
| 7 | 0 | 27451 | 22549 | +3137 |
| 8 | 0 | 24101 | 25899 | +3350 |
| 9 | 0 | 20215 | 29785 | +3886 |
| 10 | 0 | 16753 | 33247 | +3462 |
| 11 | 0 | 13554 | 36446 | +3199 |
| 12 | 0 | 10038 | 39962 | +3516 |
| 13 | 0 | 6328 | 43672 | +3710 |
| 14 | 0 | 2328 | 47672 | +4000 |
| 15 | 0 | 0 | 50000 | +2328 |

**5. Worker Pod-3 (3 worker pods) — Measurements: Tasks vs Time** (`functional_id_allocation-workers-3-size-50000.csv`, finished at mark_min 12)

| mark_min | pending | in_progress | done | done this minute |
|---|---|---|---|---|
| 0 | 50000 | 0 | 0 | +0 |
| 1 | 38000 | 8200 | 3800 | +3800 |
| 2 | 23000 | 19371 | 7629 | +3829 |
| 3 | 8000 | 29701 | 12299 | +4670 |
| 4 | 0 | 32904 | 17096 | +4797 |
| 5 | 0 | 27904 | 22096 | +5000 |
| 6 | 0 | 24000 | 26000 | +3904 |
| 7 | 0 | 20000 | 30000 | +4000 |
| 8 | 0 | 16124 | 33876 | +3876 |
| 9 | 0 | 11981 | 38019 | +4143 |
| 10 | 0 | 6806 | 43194 | +5175 |
| 11 | 0 | 1666 | 48334 | +5140 |
| 12 | 0 | 0 | 50000 | +1666 |

**6. Pod CPU / Memory (per run):**

| Pod-Scale | Pod | CPU | Memory | Notes |
|---|---|---|---|---|
| pod-1 | beat-pod | 0→1.1 cpu spike, settles ~0.1–0.15 cpu | 219→238 MiB, plateau ~230 MiB | Initial dispatch burst then idle; no limit line shown |
| pod-1 | worker-pod-1 | 0→~1.3 cpu, oscillates 0.8–1.2 cpu | 0→381 MiB plateau | Oscillating, not flatlined at axis max; no limit line shown |
| pod-2 | beat-pod | 0→1.4 cpu spike, settles ~0.1–0.2 cpu | 0→286 MiB plateau | Same beat pattern: burst then idle |
| pod-2 | worker-pod-1 | ramps to ~1–1.3 cpu, oscillating plateau | ~333 MiB plateau | No hard ceiling; fluctuation suggests wait/IO bursts |
| pod-2 | worker-pod-2 | ~1–1.3 cpu oscillating | ~333 MiB plateau | Similar to worker-pod-1, no throttle flatline |
| pod-3 | beat-pod | spike to ~1.4 cpu, drops to ~0.2 plateau | ~286 MiB plateau | Burst-then-idle beat pattern |
| pod-3 | worker-pod-1 | ramps to ~1–1.4 cpu, oscillating | ~381 MiB plateau | No sustained ceiling; variable, IO-wait-like dips |
| pod-3 | worker-pod-2 | ~1–1.4 cpu oscillating | ~333 MiB plateau | Same oscillating pattern, no flatline |
| pod-3 | worker-pod-3 | ~1–1.4 cpu oscillating | ~333 MiB plateau | Same oscillating pattern, no flatline |

Note: none of the 9 dashboards display an explicit CPU/memory limit or threshold line. Worker CPU consistently oscillates rather than pinning flat at a ceiling, consistent with wait/IO-bound behavior (calls to the external id-generator service) rather than pure CPU-bound saturation. Beat pods show a short CPU/network burst at job-dispatch time then drop to a near-idle plateau.

**7. Observations / Bottlenecks / Potential improvements:**

- **Scaling:** finish minute drops 26 → 15 → 12 (steady rate 1,959 → 3,469 → 4,453 rows/min) — the slowest-finishing scenario of the 50,000-row cohort group.
- **Bottleneck:** worker CPU *oscillates* 0.8–1.4 cpu rather than plateauing at a ceiling, at every pod-scale — consistent with network/IO-wait time against the external id-generator service (`POST /v1/idgenerator/farmer/id`) rather than CPU-bound work.
- **Follow-on leak (by design of this isolated run):** `cases.py` notes that completing allocation sets `id_updation_status` to `PENDING`, which would wake `functional_id_updation_beat_producer` in a live system. This run parks that producer, so the throughput above is allocation-only — a production run would see allocation and updation load back-to-back on the same queue.

## Scores

### `score_compute`

Score computation queue.

**1. Items in the queue at the beginning:** 100,000 rows — `g2p_score_compute_queue.compute_status` re-seeded to `PENDING` for this cohort before each of the pod-1/pod-2/pod-3 runs below (same size every time).

**2. Beat parameters:** fires every **10s** (`REGISTRY_CELERY_BEAT_SCORE_COMPUTE_BEAT_PRODUCER_FREQUENCY` on this cluster, confirmed via the live deployment; code default differs). Claims **3,000** tasks/tick (confirmed via the live deployment). The producer does mark the row before `send_task`. Done status on this queue is COMPLETED.

**3. Worker Pod-1 (1 worker pod) — Measurements: Tasks vs Time** (`score_compute-workers-1-size-100000.csv`, finished at mark_min 17)

| mark_min | pending | in_progress | done | done this minute |
|---|---|---|---|---|
| 0 | 100000 | 0 | 0 | +0 |
| 1 | 85000 | 10198 | 4802 | +4802 |
| 2 | 67000 | 22143 | 10857 | +6055 |
| 3 | 49000 | 34778 | 16222 | +5365 |
| 4 | 31000 | 48058 | 20942 | +4720 |
| 5 | 13000 | 60047 | 26953 | +6011 |
| 6 | 0 | 66582 | 33418 | +6465 |
| 7 | 0 | 59729 | 40271 | +6853 |
| 8 | 0 | 52920 | 47080 | +6809 |
| 9 | 0 | 47819 | 52181 | +5101 |
| 10 | 0 | 40981 | 59019 | +6838 |
| 11 | 0 | 34062 | 65938 | +6919 |
| 12 | 0 | 27521 | 72479 | +6541 |
| 13 | 0 | 21120 | 78880 | +6401 |
| 14 | 0 | 14268 | 85732 | +6852 |
| 15 | 0 | 7520 | 92480 | +6748 |
| 16 | 0 | 591 | 99409 | +6929 |
| 17 | 0 | 0 | 100000 | +591 |

**4. Worker Pod-2 (2 worker pods) — Measurements: Tasks vs Time** (`score_compute-workers-2-size-100000.csv`, finished at mark_min 12)

| mark_min | pending | in_progress | done | done this minute |
|---|---|---|---|---|
| 0 | 100000 | 0 | 0 | +0 |
| 1 | 85000 | 8770 | 6230 | +6230 |
| 2 | 70000 | 18881 | 11119 | +4889 |
| 3 | 49000 | 32181 | 18819 | +7700 |
| 4 | 31000 | 42106 | 26894 | +8075 |
| 5 | 13000 | 52062 | 34938 | +8044 |
| 6 | 1000 | 59451 | 39549 | +4611 |
| 7 | 0 | 49635 | 50365 | +10816 |
| 8 | 0 | 38634 | 61366 | +11001 |
| 9 | 0 | 27791 | 72209 | +10843 |
| 10 | 0 | 16550 | 83450 | +11241 |
| 11 | 0 | 6056 | 93944 | +10494 |
| 12 | 0 | 0 | 100000 | +6056 |

**5. Worker Pod-3 (3 worker pods) — Measurements: Tasks vs Time** (`score_compute-workers-3-size-100000.csv`, finished at mark_min 12)

| mark_min | pending | in_progress | done | done this minute |
|---|---|---|---|---|
| 0 | 100000 | 0 | 0 | +0 |
| 1 | 85000 | 8235 | 6765 | +6765 |
| 2 | 73000 | 15025 | 11975 | +5210 |
| 3 | 55000 | 25531 | 19469 | +7494 |
| 4 | 31000 | 41883 | 27117 | +7648 |
| 5 | 13000 | 52538 | 34462 | +7345 |
| 6 | 0 | 56809 | 43191 | +8729 |
| 7 | 0 | 45658 | 54342 | +11151 |
| 8 | 0 | 38750 | 61250 | +6908 |
| 9 | 0 | 28959 | 71041 | +9791 |
| 10 | 0 | 18299 | 81701 | +10660 |
| 11 | 0 | 7391 | 92609 | +10908 |
| 12 | 0 | 0 | 100000 | +7391 |

**6. Pod CPU / Memory (per run):**

All 9 images reviewed. No limit/threshold lines are rendered on any panel (axes auto-scale to data), so throttling cannot be directly confirmed — only headroom relative to axis max is inferred.

| Pod-Scale | Pod | CPU | Memory | Notes |
|---|---|---|---|---|
| pod-1 | beat | 0→0.72 cpu | 0→262 MiB plateau | Beat idles after startup, headroom |
| pod-1 | worker-1 | 0→2.0 cpu (plateau ~1.5-1.8) | 0→~300 MiB plateau | Sustained load, no visible ceiling |
| pod-2 | beat | 0→1.0 cpu peak, back to 0 | 0→~270 MiB plateau | Short beat burst, headroom |
| pod-2 | worker-1 | 0→1.4 cpu plateau | 0→~300 MiB plateau | Steady climb then flat, headroom |
| pod-2 | worker-2 | 0→1.5 cpu, variable 0.7-1.5 | 0→~300 MiB plateau | Fluctuating, no ceiling hit |
| pod-3 | beat | 0→1.0 cpu peak, decays to 0 | 0→~270 MiB plateau | Beat finishes early, idles |
| pod-3 | worker-1 | 0→~1.0 cpu, variable, drops end | 0→~300 MiB plateau (axis max label 381 MiB) | Variable load, headroom |
| pod-3 | worker-2 | 0→~1.0 cpu, variable, drops end | 0→~300 MiB plateau | Similar pattern to worker-1 |
| pod-3 | worker-3 | 0→~1.0 cpu, variable, drops end | 0→~300 MiB plateau | Similar pattern to worker-1/2 |

All CPU values in "cpu" units (cores); memory in MiB. No pod appears CPU-throttled — none flatlines at a hard ceiling.

**7. Observations / Bottlenecks / Potential improvements:**

- **Scaling:** finish minute drops 17 → 12 → 12 — the first scenario in this cycle where the 3rd worker pod shows *no* further gain over the 2nd (both finish at minute 12); steady rate jumps 6,307 → 8,771 rows/min from pod-1→pod-2 but is flat pod-2→pod-3 (8,771 → 8,584, within noise).
- **Bottleneck signature:** per test-scenarios.md §5 ("2 worker pods finish in about the same minute as 3 … the single beat pod is the limit"), this is exactly that pattern. Worth a repeat run with a larger backlog, or with beat's claim size raised, to confirm it's genuinely beat-limited rather than sampling noise from a ~12-minute, 100,000-row run.
- **CPU:** worker plateaus 1.5–1.8 cpu at pod-1, falling to ~1.0–1.5 cpu at pod-2/pod-3 — consistent with each pod's CPU share shrinking as more pods split the same claimed backlog.
- **Code dependency:** this scenario only became measurable after the mid-cycle `poverty.py` refactor (see the Final section) — the prior `score_config`-based signature didn't match what the worker passes for `POVERTY`-type scores.

### `completion_score`

Completion-score computation queue.

**1. Items in the queue at the beginning:** 100,000 rows — `g2p_completion_score_computation_queue.compute_status` re-seeded to `PENDING` for this cohort before each of the pod-1/pod-2/pod-3 runs below (same size every time).

**2. Beat parameters:** fires every **10s** (`REGISTRY_CELERY_BEAT_COMPLETION_SCORE_BEAT_PRODUCER_FREQUENCY` on this cluster, confirmed via the live deployment; code default differs). Claims **3,000** tasks/tick (confirmed via the live deployment). The producer does mark the row before `send_task`. Done status on this queue is COMPLETED.

**3. Worker Pod-1 (1 worker pod) — Measurements: Tasks vs Time** (`completion_score-workers-1-size-100000.csv`, finished at mark_min 17)

| mark_min | pending | in_progress | done | done this minute |
|---|---|---|---|---|
| 0 | 100000 | 0 | 0 | +0 |
| 1 | 82000 | 13147 | 4853 | +4853 |
| 2 | 64000 | 25383 | 10617 | +5764 |
| 3 | 46000 | 37285 | 16715 | +6098 |
| 4 | 28000 | 49328 | 22672 | +5957 |
| 5 | 10000 | 61357 | 28643 | +5971 |
| 6 | 0 | 65302 | 34698 | +6055 |
| 7 | 0 | 59029 | 40971 | +6273 |
| 8 | 0 | 52523 | 47477 | +6506 |
| 9 | 0 | 46171 | 53829 | +6352 |
| 10 | 0 | 39771 | 60229 | +6400 |
| 11 | 0 | 33260 | 66740 | +6511 |
| 12 | 0 | 26938 | 73062 | +6322 |
| 13 | 0 | 20566 | 79434 | +6372 |
| 14 | 0 | 14260 | 85740 | +6306 |
| 15 | 0 | 7929 | 92071 | +6331 |
| 16 | 0 | 1566 | 98434 | +6363 |
| 17 | 0 | 0 | 100000 | +1566 |

**4. Worker Pod-2 (2 worker pods) — Measurements: Tasks vs Time** (`completion_score-workers-2-size-100000.csv`, finished at mark_min 11)

| mark_min | pending | in_progress | done | done this minute |
|---|---|---|---|---|
| 0 | 100000 | 0 | 0 | +0 |
| 1 | 70000 | 19668 | 10332 | +10332 |
| 2 | 58000 | 27151 | 14849 | +4517 |
| 3 | 40000 | 37628 | 22372 | +7523 |
| 4 | 16000 | 54101 | 29899 | +7527 |
| 5 | 0 | 62487 | 37513 | +7614 |
| 6 | 0 | 51687 | 48313 | +10800 |
| 7 | 0 | 41138 | 58862 | +10549 |
| 8 | 0 | 30388 | 69612 | +10750 |
| 9 | 0 | 19430 | 80570 | +10958 |
| 10 | 0 | 8662 | 91338 | +10768 |
| 11 | 0 | 0 | 100000 | +8662 |

**5. Worker Pod-3 (3 worker pods) — Measurements: Tasks vs Time** (`completion_score-workers-3-size-100000.csv`, finished at mark_min 12)

| mark_min | pending | in_progress | done | done this minute |
|---|---|---|---|---|
| 0 | 100000 | 0 | 0 | +0 |
| 1 | 82000 | 9472 | 8528 | +8528 |
| 2 | 64000 | 18575 | 17425 | +8897 |
| 3 | 52000 | 21661 | 26339 | +8914 |
| 4 | 34000 | 30714 | 35286 | +8947 |
| 5 | 16000 | 39783 | 44217 | +8931 |
| 6 | 4000 | 42714 | 53286 | +9069 |
| 7 | 0 | 36107 | 63893 | +10607 |
| 8 | 0 | 24305 | 75695 | +11802 |
| 9 | 0 | 18916 | 81084 | +5389 |
| 10 | 0 | 13838 | 86162 | +5078 |
| 11 | 0 | 1978 | 98022 | +11860 |
| 12 | 0 | 0 | 100000 | +1978 |

**6. Pod CPU / Memory (per run):**

All 9 screenshots read successfully. No limit/threshold lines are drawn on any CPU or Memory panel (axis max is just auto-scaled), and no pod flatlines at a hard ceiling — all have headroom relative to their own peak.

| Pod-Scale | Pod | CPU | Memory | Notes |
|---|---|---|---|---|
| pod-1 | beat-pod | 0.1→0.5 cpu | 0→238 MiB plateau | brief startup spike then settles ~0.2-0.35 |
| pod-1 | worker-pod-1 | 0→1.4 cpu, plateau ~1.0-1.3 | 0→381 MiB plateau | ramps up, headroom below axis max |
| pod-2 | beat-pod | 0.3→0.85 cpu | 252→267 MiB | gradual rise/fall, no plateau |
| pod-2 | worker-pod-1 (typo "woker-pod-1" on disk) | 0→1.3 cpu plateau | 190→381 MiB plateau | steady after ramp-up |
| pod-2 | worker-pod-2 | 0→1.3 cpu plateau | 95→381 MiB plateau | steady after ramp-up |
| pod-3 | beat-pod | 0.25→1.1 cpu | 0→286 MiB plateau | peak near run end |
| pod-3 | worker-pod-1 | 0→1.3 cpu plateau | 95→477 MiB rising | memory still climbing at run end |
| pod-3 | worker-pod-2 | 0→1.3 cpu plateau | 95→381 MiB rising | memory still climbing at run end |
| pod-3 | worker-pod-3 | 0→1.3 cpu plateau | 95→381 MiB rising | memory still climbing at run end |

All CPU in cores (cpu unit), memory in MiB.

**7. Observations / Bottlenecks / Potential improvements:**

- **Scaling:** finish minute goes 17 → 11 → 12 — the *only* scenario in this cycle where adding a worker pod made the measured finish time worse (pod-3 is 1 minute slower than pod-2).
- **Why:** the pod-3 run's own numbers explain it — `done` jumps from 86,162 (mark 10) to 98,022 (mark 11) to 100,000 (mark 12), a lumpy, back-loaded finish rather than the smooth ramp every other scenario shows. Most likely a scheduling/measurement artifact of the 1-minute sampling interval (a large batch landing just after a mark) rather than a real pod-3 regression — but it's visible in the raw data and worth a repeat run before trusting the pod-3 number at face value.
- **Memory:** the pod-3 worker's memory is still climbing (not plateaued) at the run's end (~381 → 477 MiB) — the only scenario in this cycle where memory doesn't settle onto a flat plateau within the observed window. The run is far too short (~12 min) to call this a leak, but it's worth watching in a longer run.

## Import file

### `import_file_process`

Import-file intake ingestion.

**1. Items in the queue at the beginning:** 20,000 records (across the populated CSV files) — `import_file_process_queue.intake_form_ingestion_status` re-seeded to `PENDING` for this cohort before each of the pod-1/pod-2/pod-3 runs below (same size every time).

**2. Beat parameters:** fires every **10s** (`REGISTRY_CELERY_BEAT_IMPORT_FILE_PROCESS_BEAT_PRODUCER_FREQUENCY` on this cluster, confirmed via the live deployment; code default differs). Claims **20,000** tasks/tick (confirmed via the live deployment). The producer does mark the row before `send_task`. Beat claims intake_form_ingestion_status before enqueue.

**3. Worker Pod-1 (1 worker pod) — Measurements: Tasks vs Time** (`import_file_process-workers-1-size-2.csv`, finished at mark_min 15)

| mark_min | pending | in_progress | done | done this minute |
|---|---|---|---|---|
| 0 | 20000 | 0 | 0 | +0 |
| 1 | 18909 | 2 | 1089 | +1089 |
| 2 | 17547 | 2 | 2451 | +1362 |
| 3 | 16168 | 2 | 3830 | +1379 |
| 4 | 14749 | 2 | 5249 | +1419 |
| 5 | 13345 | 2 | 6653 | +1404 |
| 6 | 11952 | 2 | 8046 | +1393 |
| 7 | 10536 | 2 | 9462 | +1416 |
| 8 | 9140 | 2 | 10858 | +1396 |
| 9 | 7729 | 2 | 12269 | +1411 |
| 10 | 6342 | 2 | 13656 | +1387 |
| 11 | 4934 | 2 | 15064 | +1408 |
| 12 | 3561 | 2 | 16437 | +1373 |
| 13 | 2166 | 2 | 17832 | +1395 |
| 14 | 739 | 2 | 19259 | +1427 |
| 15 | 0 | 0 | 20000 | +741 |

**6. Pod CPU / Memory (per run):**

Only pod-1 was run (2 files, one process each; by design this scenario is never run at pod-2/pod-3 — see §7).

| Pod-Scale | Pod | CPU | Memory | Notes |
|---|---|---|---|---|
| pod-1 | beat-pod | 0.07→0.02 cpu, brief spike then idle | 0→190.7 MiB plateau | Beat claims both files at job start, then idles |
| pod-1 | worker-pod-1 | 0→2 cpu ramp, plateau ~1.5-1.8 cpu (one dip to ~1 cpu) | 0→381.5 MiB plateau | Both concurrency=2 processes busy (one file each), near the 2-cpu axis top |

**7. Observations / Bottlenecks / Potential improvements:**

- **Result:** 15 minutes to drain 20,000 records across `IMPORT_FILES=2` files (steady ~1,398 records/min). Only run at pod-1, by design.
- **Where the time goes:** only ~1,091 of 20,000 records are logged by mark 1 even though both files are claimed immediately — `in_progress` pins at exactly 2 (the pod's `concurrency=2` process count) from mark 1 onward. Unlike every queue-based scenario above, the limiting resource here is literally "one process per file," not beat's claim size.
- **Bottleneck:** worker CPU plateaus 1.5–1.8 cpu (one dip to ~1 cpu), close to the 2-cpu ceiling — both processes busy for nearly the whole run, consistent with one CPU-bound ingestion thread per file.
- **Why no pod-2/pod-3 run:** a file stays on one process until it finishes; a second pod can't split the same file (test-scenarios.md §4, "Import file"). This 2-file, 1-pod run is already the designed ceiling test — a 3rd/4th file queued alongside would show whether idle processes on *other* pods pick up extra files, which this run doesn't exercise.

## Code changes made during this test/measurement cycle

1. **`poverty.py` — poverty score signature change (`farmer-extension/src/openg2p_registry_farmer_extension/score_compute/services/poverty.py`, commit `705b7c6`).** `G2PScoreComputeServicePoverty.compute_score` took a hardcoded `score_config` dict with two fixed weighted attributes (`size_of_group`, `number_of_children`). It now takes `contributing_attribute_config` — the list of `attribute_name`/`attribute_weightage` rows the worker actually loads from the score definition, with an optional value-lookup table per attribute — and sums `value × weight` over whatever attributes that definition configures. **Required before `score_compute` could be measured at all** for the `POVERTY` score type: the previous signature didn't match what `score_compute_worker` passes, so every task failed closed (`done` stayed 0) until this was fixed (test-scenarios.md §4 "Scores").

2. **Per-producer beat pickup size (`registry-platform`, `celery/openg2p-registry-celery-beat/src/openg2p_registry_celery_beat/config.py` + new `control.py` + every `tasks/*_beat_producer.py`; commit `21315b5`, branch `performance-test`, `vin0dkhichar/registry-platform` — one commit ahead of what's merged into this checkout's `registry-platform` remote).** Before this commit every beat producer shared one `no_of_tasks_to_process` (claim size per tick, code default 4) — per-producer `*_FREQUENCY` overrides already existed (`app.py`'s `beat_schedule`), but claim size was global, so every producer necessarily claimed the same number of rows per tick regardless of how heavy its own downstream work was. This commit added a `<producer>_no_of_tasks` override per producer, read through a new `task_limit()` helper in `control.py` (looks up the calling task function's own name via `sys._getframe(1).f_code.co_name`), which every task now calls instead of reading the shared setting directly. The per-producer pickup sizes confirmed live on the cluster (3,000 or 20,000 depending on producer — `final-report-summary.md` § Measurements) are what let each scenario's beat be tuned independently instead of all sharing one claim size.

3. **Per-beat-producer enable/disable, same commit (`21315b5`).** Same files, plus the worker-side mirror (`celery/openg2p-registry-celery-worker/.../config.py` + new `control.py`). Added a `<producer>_enabled` setting per producer, on both beat and worker, checked via a `task_enabled()` helper (same calling-frame-name trick as `task_limit()`) at the top of every task — a disabled task logs and returns without touching a row. This is a genuine implementation-level toggle, not just a test convenience: a given deployment that doesn't use, say, WebSub outgest or functional-ID generation can turn those beat producers off entirely rather than have them tick uselessly every 10s. It's also **what the isolated-scenario design in test-scenarios.md §4/§6 depends on** — "enables only that scenario's producer and worker and disables the others" needs a real per-producer flag to park every sibling producer while one scenario runs.

4. **DCI outgest payload template — section key rename (`farmer-extension/src/openg2p_registry_farmer_extension/templates/dci_to_openg2p_farmer.json.j2`, commit `d853df2`).** All six top-level section keys gained an `fr_` prefix (e.g. `farmer_personal_info` → `fr_farmer_personal_info`, and the same for `..._socio_&_health`, `..._location`, `..._land`, `..._farm_input`, `..._livestocks`) to match the DCI schema expected downstream.

5. **Test-harness changes (not production code), same commit (`d853df2`):** `import_file_process` progress is now tracked by CSV row in `k8s/collect.sh`/`run.sh` (the `pending`/`in_progress`/`done` semantics documented in test-scenarios.md §3), and the `k8s/sql/populate/*.sql` scripts for the outgest and import-file scenarios were extended to build a real backlog rather than reuse whatever rows already existed.

6. **Performance-test harness itself (commits `9e044f4`, `4671cb7`, `4db782b`):** added from scratch this cycle — `cases.py`/`db.py`/`preflight.py`/`observe.py`, the `k8s/` scripts (`populate.sh`, `run.sh`, `collect.sh`, `pin-case.sh`, `restore-hold.sh`), and the per-scenario `k8s/sql/populate/*.sql` seed scripts that every run above depends on. Test infrastructure, not application code, but the thing that made every measurement in this report possible.
