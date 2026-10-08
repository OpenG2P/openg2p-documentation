# Raw Report — Celery (beat + worker backlog drain)

Every `mark_min` row Locust's companion collector (`./k8s/run.sh`) actually wrote, verbatim — one row per minute, straight from `locust/celery/results/pod-<workers>/<scenario>/*.csv`. No curation, no derived columns (finish minute, rows/min, CPU/Mem readings), no PASS/FAIL. That interpretation lives in [`final-report.md`](final-report.md), built from this document.

Column meanings are in [`test-scenarios.md`](test-scenarios.md) §3. Only cells that actually have a CSV on disk produce a section — nothing is fabricated for untested cells (`outgest_topic_register`, the four dedup scenarios, `functional_id_updation`, and `import_file_process` at pod-2/pod-3 have none yet).

Built from `locust/celery/results/` — re-run the generator after any new run rather than editing this file by hand.

## Partner ingest

### `ingest_data_classification`

Partner ingest classification. Table `incoming_raw_data`, status column `classification_status`.

**Pod-Scale: `pod-1`** (`ingest_data_classification-workers-1-size-50000.csv`)

Screenshots: `beat-pod.png`, `worker-pod-1.png`

| mark_min | pending | in_progress | done |
|---|---|---|---|
| 0 | 50000 | 0 | 0 |
| 1 | 35000 | 13106 | 1894 |
| 2 | 17000 | 29131 | 3869 |
| 3 | 2000 | 42232 | 5768 |
| 4 | 0 | 42461 | 7539 |
| 5 | 0 | 40282 | 9718 |
| 6 | 0 | 37820 | 12180 |
| 7 | 0 | 35676 | 14324 |
| 8 | 0 | 33445 | 16555 |
| 9 | 0 | 31235 | 18765 |
| 10 | 0 | 28700 | 21300 |
| 11 | 0 | 26579 | 23421 |
| 12 | 0 | 24411 | 25589 |
| 13 | 0 | 22234 | 27766 |
| 14 | 0 | 19678 | 30322 |
| 15 | 0 | 17563 | 32437 |
| 16 | 0 | 15425 | 34575 |
| 17 | 0 | 13247 | 36753 |
| 18 | 0 | 10701 | 39299 |
| 19 | 0 | 8585 | 41415 |
| 20 | 0 | 6423 | 43577 |
| 21 | 0 | 3919 | 46081 |
| 22 | 0 | 2065 | 47935 |
| 23 | 0 | 29 | 49971 |
| 24 | 0 | 0 | 50000 |

**Pod-Scale: `pod-2`** (`ingest_data_classification-workers-2-size-50000.csv`)

Screenshots: `beat-pod.png`, `worker-pod-1.png`, `worker-pod-2.png`

| mark_min | pending | in_progress | done |
|---|---|---|---|
| 0 | 50000 | 0 | 0 |
| 1 | 35000 | 12076 | 2924 |
| 2 | 17000 | 26502 | 6498 |
| 3 | 0 | 40070 | 9930 |
| 4 | 0 | 36565 | 13435 |
| 5 | 0 | 32670 | 17330 |
| 6 | 0 | 30177 | 19823 |
| 7 | 0 | 27087 | 22913 |
| 8 | 0 | 23231 | 26769 |
| 9 | 0 | 19126 | 30874 |
| 10 | 0 | 15804 | 34196 |
| 11 | 0 | 12023 | 37977 |
| 12 | 0 | 7995 | 42005 |
| 13 | 0 | 4287 | 45713 |
| 14 | 0 | 184 | 49816 |
| 15 | 0 | 0 | 50000 |

**Pod-Scale: `pod-3`** (`ingest_data_classification-workers-3-size-50000.csv`)

Screenshots: `beat-pod.png`, `worker-pod-1.png`, `worker-pod-2.png`, `worker-pod-3.png`

| mark_min | pending | in_progress | done |
|---|---|---|---|
| 0 | 50000 | 0 | 0 |
| 1 | 38000 | 7744 | 4256 |
| 2 | 26000 | 16010 | 7990 |
| 3 | 11000 | 27000 | 12000 |
| 4 | 0 | 32880 | 17120 |
| 5 | 0 | 31172 | 18828 |
| 6 | 0 | 27758 | 22242 |
| 7 | 0 | 23912 | 26088 |
| 8 | 0 | 19741 | 30259 |
| 9 | 0 | 14279 | 35721 |
| 10 | 0 | 10447 | 39553 |
| 11 | 0 | 6792 | 43208 |
| 12 | 0 | 2000 | 48000 |
| 13 | 0 | 0 | 50000 |

### `ingest_data_transformation`

Partner ingest transformation. Table `incoming_classified_data`, status column `transformation_status`.

**Pod-Scale: `pod-1`** (`ingest_data_transformation-workers-1-size-10000.csv`)

Screenshots: `beat-pod.png`, `worker-pod-1.png`

| mark_min | pending | in_progress | done |
|---|---|---|---|
| 0 | 10000 | 0 | 0 |
| 1 | 0 | 9550 | 450 |
| 2 | 0 | 8895 | 1105 |
| 3 | 0 | 8228 | 1772 |
| 4 | 0 | 7566 | 2434 |
| 5 | 0 | 6914 | 3086 |
| 6 | 0 | 6266 | 3734 |
| 7 | 0 | 5606 | 4394 |
| 8 | 0 | 4958 | 5042 |
| 9 | 0 | 4296 | 5704 |
| 10 | 0 | 3642 | 6358 |
| 11 | 0 | 2979 | 7021 |
| 12 | 0 | 2344 | 7656 |
| 13 | 0 | 1673 | 8327 |
| 14 | 0 | 1004 | 8996 |
| 15 | 0 | 339 | 9661 |
| 16 | 0 | 0 | 10000 |

**Pod-Scale: `pod-2`** (`ingest_data_transformation-workers-2-size-10000.csv`)

Screenshots: `beat-pod.png`, `worker-pod-1.png`, `worker-pod-2.png`

| mark_min | pending | in_progress | done |
|---|---|---|---|
| 0 | 10000 | 0 | 0 |
| 1 | 0 | 9106 | 894 |
| 2 | 0 | 7935 | 2065 |
| 3 | 0 | 6696 | 3304 |
| 4 | 0 | 5532 | 4468 |
| 5 | 0 | 4326 | 5674 |
| 6 | 0 | 3075 | 6925 |
| 7 | 0 | 1937 | 8063 |
| 8 | 0 | 667 | 9333 |
| 9 | 0 | 0 | 10000 |

**Pod-Scale: `pod-3`** (`ingest_data_transformation-workers-3-size-10000.csv`)

Screenshots: `beat-pod.png`, `worker-pod-1.png`, `worker-pod-2.png`, `worker-pod-3.png`

| mark_min | pending | in_progress | done |
|---|---|---|---|
| 0 | 10000 | 0 | 0 |
| 1 | 0 | 8776 | 1224 |
| 2 | 0 | 7116 | 2884 |
| 3 | 0 | 5408 | 4592 |
| 4 | 0 | 3704 | 6296 |
| 5 | 0 | 2033 | 7967 |
| 6 | 0 | 259 | 9741 |
| 7 | 0 | 0 | 10000 |

### `ingest_data`

Partner ingest into the register (pipeline_action ADD). Table `incoming_classified_data`, status column `ingestion_status`.

**Pod-Scale: `pod-1`** (`ingest_data-workers-1-size-40000.csv`)

Screenshots: `beat-pod.png`, `worker-pod-1.png`

| mark_min | pending | in_progress | done |
|---|---|---|---|
| 0 | 40000 | 0 | 0 |
| 1 | 25000 | 13822 | 1178 |
| 2 | 7000 | 30261 | 2739 |
| 3 | 0 | 35643 | 4357 |
| 4 | 0 | 33888 | 6112 |
| 5 | 0 | 32201 | 7799 |
| 6 | 0 | 30458 | 9542 |
| 7 | 0 | 28747 | 11253 |
| 8 | 0 | 27021 | 12979 |
| 9 | 0 | 25323 | 14677 |
| 10 | 0 | 23578 | 16422 |
| 11 | 0 | 21879 | 18121 |
| 12 | 0 | 20145 | 19855 |
| 13 | 0 | 18442 | 21558 |
| 14 | 0 | 16728 | 23272 |
| 15 | 0 | 15061 | 24939 |
| 16 | 0 | 13357 | 26643 |
| 17 | 0 | 11589 | 28411 |
| 18 | 0 | 9847 | 30153 |
| 19 | 0 | 8077 | 31923 |
| 20 | 0 | 6331 | 33669 |
| 21 | 0 | 4564 | 35436 |
| 22 | 0 | 2813 | 37187 |
| 23 | 0 | 1035 | 38965 |
| 24 | 0 | 0 | 40000 |

**Pod-Scale: `pod-2`** (`ingest_data-workers-2-size-40000.csv`)

Screenshots: `beat-pod.png`, `worker-pod-1.png`, `worker-pod-2.png`

| mark_min | pending | in_progress | done |
|---|---|---|---|
| 0 | 40000 | 0 | 0 |
| 1 | 25000 | 12693 | 2307 |
| 2 | 7000 | 27862 | 5138 |
| 3 | 0 | 31687 | 8313 |
| 4 | 0 | 28505 | 11495 |
| 5 | 0 | 25303 | 14697 |
| 6 | 0 | 22142 | 17858 |
| 7 | 0 | 19037 | 20963 |
| 8 | 0 | 15788 | 24212 |
| 9 | 0 | 12638 | 27362 |
| 10 | 0 | 9396 | 30604 |
| 11 | 0 | 6235 | 33765 |
| 12 | 0 | 3003 | 36997 |
| 13 | 0 | 0 | 40000 |

**Pod-Scale: `pod-3`** (`ingest_data-workers-3-size-40000.csv`)

Screenshots: `beat-pod.png`, `worker-pod-1.png`, `worker-pod-2.png`, `worker-pod-3.png`

| mark_min | pending | in_progress | done |
|---|---|---|---|
| 0 | 40000 | 0 | 0 |
| 1 | 25000 | 11751 | 3249 |
| 2 | 7000 | 25726 | 7274 |
| 3 | 0 | 28486 | 11514 |
| 4 | 0 | 24142 | 15858 |
| 5 | 0 | 19775 | 20225 |
| 6 | 0 | 15368 | 24632 |
| 7 | 0 | 12018 | 27982 |
| 8 | 0 | 8186 | 31814 |
| 9 | 0 | 3857 | 36143 |
| 10 | 0 | 0 | 40000 |

### `change_request_ingest`

Partner ingest that updates an existing record. Table `incoming_classified_data`, status column `ingestion_status`.

**Pod-Scale: `pod-1`** (`change_request_ingest-workers-1-size-50000.csv`)

Screenshots: `beat-pod.png`, `worker-pod.png`

| mark_min | pending | in_progress | done |
|---|---|---|---|
| 0 | 50000 | 0 | 0 |
| 1 | 10000 | 38638 | 1362 |
| 2 | 10000 | 35862 | 4138 |
| 3 | 0 | 42697 | 7303 |
| 4 | 0 | 39280 | 10720 |
| 5 | 0 | 35912 | 14088 |
| 6 | 0 | 32653 | 17347 |
| 7 | 0 | 29166 | 20834 |
| 8 | 0 | 25737 | 24263 |
| 9 | 0 | 22280 | 27720 |
| 10 | 0 | 18791 | 31209 |
| 11 | 0 | 15397 | 34603 |
| 12 | 0 | 11918 | 38082 |
| 13 | 0 | 8497 | 41503 |
| 14 | 0 | 5124 | 44876 |
| 15 | 0 | 1700 | 48300 |
| 16 | 0 | 0 | 50000 |

**Pod-Scale: `pod-2`** (`change_request_ingest-workers-2-size-50000.csv`)

Screenshots: `beat-pod.png`, `worker-pod-1.png`, `worker-pod-2.png`

| mark_min | pending | in_progress | done |
|---|---|---|---|
| 0 | 50000 | 0 | 0 |
| 1 | 10000 | 37820 | 2180 |
| 2 | 10000 | 32677 | 7323 |
| 3 | 0 | 37319 | 12681 |
| 4 | 0 | 31425 | 18575 |
| 5 | 0 | 25284 | 24716 |
| 6 | 0 | 19477 | 30523 |
| 7 | 0 | 13469 | 36531 |
| 8 | 0 | 7448 | 42552 |
| 9 | 0 | 1412 | 48588 |
| 10 | 0 | 0 | 50000 |

**Pod-Scale: `pod-3`** (`change_request_ingest-workers-3-size-50000.csv`)

Screenshots: `beat-pod.png`, `worker-pod-1.png`, `worker-pod-2.png`, `worker-pod-3.png`

| mark_min | pending | in_progress | done |
|---|---|---|---|
| 0 | 50000 | 0 | 0 |
| 1 | 10000 | 36940 | 3060 |
| 2 | 10000 | 30125 | 9875 |
| 3 | 0 | 35245 | 14755 |
| 4 | 0 | 31964 | 18036 |
| 5 | 0 | 26198 | 23802 |
| 6 | 0 | 18342 | 31658 |
| 7 | 0 | 10647 | 39353 |
| 8 | 0 | 2840 | 47160 |
| 9 | 0 | 0 | 50000 |


## Outgest

### `outgest_data_transformation`

Outgest payload transformation. Table `outgoing_raw_data`, status column `transformation_status`.

**Pod-Scale: `pod-1`** (`outgest_data_transformation-workers-1-size-10000.csv`)

Screenshots: `beat-pod.png`, `worker-pod-1.png`

| mark_min | pending | in_progress | done |
|---|---|---|---|
| 0 | 10000 | 0 | 0 |
| 1 | 0 | 9762 | 238 |
| 2 | 0 | 9394 | 606 |
| 3 | 0 | 9025 | 975 |
| 4 | 0 | 8655 | 1345 |
| 5 | 0 | 8280 | 1720 |
| 6 | 0 | 7912 | 2088 |
| 7 | 0 | 7537 | 2463 |
| 8 | 0 | 7168 | 2832 |
| 9 | 0 | 6793 | 3207 |
| 10 | 0 | 6425 | 3575 |
| 11 | 0 | 6052 | 3948 |
| 12 | 0 | 5685 | 4315 |
| 13 | 0 | 5319 | 4681 |
| 14 | 0 | 4954 | 5046 |
| 15 | 0 | 4594 | 5406 |
| 16 | 0 | 4225 | 5775 |
| 17 | 0 | 3855 | 6145 |
| 18 | 0 | 3487 | 6513 |
| 19 | 0 | 3124 | 6876 |
| 20 | 0 | 2753 | 7247 |
| 21 | 0 | 2388 | 7612 |
| 22 | 0 | 2021 | 7979 |
| 23 | 0 | 1660 | 8340 |
| 24 | 0 | 1288 | 8712 |
| 25 | 0 | 922 | 9078 |
| 26 | 0 | 551 | 9449 |
| 27 | 0 | 186 | 9814 |
| 28 | 0 | 0 | 10000 |

**Pod-Scale: `pod-2`** (`outgest_data_transformation-workers-2-size-10000.csv`)

Screenshots: `beat-pod.png`, `worker-pod-1.png`, `worker-pod-2.png`

| mark_min | pending | in_progress | done |
|---|---|---|---|
| 0 | 10000 | 0 | 0 |
| 1 | 0 | 9558 | 442 |
| 2 | 0 | 8835 | 1165 |
| 3 | 0 | 8098 | 1902 |
| 4 | 0 | 7376 | 2624 |
| 5 | 0 | 6639 | 3361 |
| 6 | 0 | 5853 | 4147 |
| 7 | 0 | 5175 | 4825 |
| 8 | 0 | 4449 | 5551 |
| 9 | 0 | 3706 | 6294 |
| 10 | 0 | 2996 | 7004 |
| 11 | 0 | 2260 | 7740 |
| 12 | 0 | 1544 | 8456 |
| 13 | 0 | 811 | 9189 |
| 14 | 0 | 96 | 9904 |
| 15 | 0 | 0 | 10000 |

**Pod-Scale: `pod-3`** (`outgest_data_transformation-workers-3-size-10000.csv`)

Screenshots: `beat-pod.png`, `worker-pod-1.png`, `worker-pod-2.png`, `worker-pod-3.png`

| mark_min | pending | in_progress | done |
|---|---|---|---|
| 0 | 10000 | 0 | 0 |
| 1 | 0 | 9338 | 662 |
| 2 | 0 | 8290 | 1710 |
| 3 | 0 | 7245 | 2755 |
| 4 | 0 | 6215 | 3785 |
| 5 | 0 | 5194 | 4806 |
| 6 | 0 | 4141 | 5859 |
| 7 | 0 | 3154 | 6846 |
| 8 | 0 | 2163 | 7837 |
| 9 | 0 | 1209 | 8791 |
| 10 | 0 | 199 | 9801 |
| 11 | 0 | 0 | 10000 |

### `outgest_data_publish`

Outgest publish. Table `outgoing_raw_data`, status column `publish_status`.

**Pod-Scale: `pod-1`** (`outgest_data_publish-workers-1-size-50000.csv`)

Screenshots: `beat-pod.png`, `worker-pod-1.png`

| mark_min | pending | in_progress | done |
|---|---|---|---|
| 0 | 50000 | 0 | 0 |
| 1 | 10007 | 39094 | 899 |
| 2 | 0 | 46967 | 3033 |
| 3 | 1 | 44660 | 5339 |
| 4 | 0 | 42202 | 7798 |
| 5 | 0 | 39782 | 10218 |
| 6 | 1 | 37120 | 12879 |
| 7 | 0 | 34960 | 15040 |
| 8 | 2 | 32471 | 17527 |
| 9 | 0 | 30043 | 19957 |
| 10 | 0 | 27614 | 22386 |
| 11 | 1 | 25260 | 24739 |
| 12 | 0 | 22879 | 27121 |
| 13 | 0 | 20423 | 29577 |
| 14 | 0 | 18043 | 31957 |
| 15 | 1 | 15579 | 34420 |
| 16 | 0 | 13193 | 36807 |
| 17 | 2 | 10841 | 39157 |
| 18 | 1 | 8462 | 41537 |
| 19 | 0 | 6030 | 43970 |
| 20 | 1 | 3607 | 46392 |
| 21 | 2 | 1180 | 48818 |
| 22 | 0 | 0 | 50000 |

**Pod-Scale: `pod-2`** (`outgest_data_publish-workers-2-size-50000.csv`)

Screenshots: `beat-pod.png`, `worker-pod-1.png`, `worker-pod-2.png`

| mark_min | pending | in_progress | done |
|---|---|---|---|
| 0 | 50000 | 0 | 0 |
| 1 | 10011 | 38432 | 1557 |
| 2 | 10046 | 35006 | 4948 |
| 3 | 0 | 41431 | 8569 |
| 4 | 0 | 37599 | 12401 |
| 5 | 9 | 33936 | 16055 |
| 6 | 0 | 31276 | 18724 |
| 7 | 10 | 27608 | 22382 |
| 8 | 0 | 23770 | 26230 |
| 9 | 5 | 19930 | 30065 |
| 10 | 0 | 16011 | 33989 |
| 11 | 0 | 12213 | 37787 |
| 12 | 0 | 8276 | 41724 |
| 13 | 0 | 4425 | 45575 |
| 14 | 0 | 607 | 49393 |
| 15 | 0 | 0 | 50000 |

**Pod-Scale: `pod-3`** (`outgest_data_publish-workers-3-size-50000.csv`)

Screenshots: `beat-pod.png`, `worker-pod-1.png`, `worker-pod-2.png`, `worker-pod-3.png`

| mark_min | pending | in_progress | done |
|---|---|---|---|
| 0 | 50000 | 0 | 0 |
| 1 | 10037 | 38179 | 1784 |
| 2 | 10128 | 34142 | 5730 |
| 3 | 2 | 40287 | 9711 |
| 4 | 4 | 36038 | 13958 |
| 5 | 4 | 31828 | 18168 |
| 6 | 5 | 27500 | 22495 |
| 7 | 2 | 23188 | 26810 |
| 8 | 3 | 19073 | 30924 |
| 9 | 7 | 14732 | 35261 |
| 10 | 4 | 10435 | 39561 |
| 11 | 5 | 6086 | 43909 |
| 12 | 4 | 1828 | 48168 |
| 13 | 0 | 0 | 50000 |


## Intake ingest

### `intake_register_ingest`

Approved intake submission ingest into the register. Table `g2p_intake_form_submissions`, status column `register_ingest_process_status`.

**Pod-Scale: `pod-1`** (`intake_register_ingest-workers-1-size-10000.csv`)

Screenshots: `beat-pod.png`, `worker-pod-1.png`

| mark_min | pending | in_progress | done |
|---|---|---|---|
| 0 | 10000 | 0 | 0 |
| 1 | 0 | 9566 | 434 |
| 2 | 0 | 9049 | 951 |
| 3 | 0 | 8474 | 1526 |
| 4 | 0 | 7884 | 2116 |
| 5 | 0 | 7307 | 2693 |
| 6 | 0 | 6855 | 3145 |
| 7 | 0 | 6303 | 3697 |
| 8 | 0 | 5714 | 4286 |
| 9 | 0 | 5118 | 4882 |
| 10 | 0 | 4524 | 5476 |
| 11 | 0 | 3962 | 6038 |
| 12 | 0 | 3423 | 6577 |
| 13 | 0 | 2862 | 7138 |
| 14 | 0 | 2272 | 7728 |
| 15 | 0 | 1670 | 8330 |
| 16 | 0 | 1053 | 8947 |
| 17 | 0 | 509 | 9491 |
| 18 | 0 | 0 | 10000 |

**Pod-Scale: `pod-2`** (`intake_register_ingest-workers-2-size-10000.csv`)

Screenshots: `beat-pod.png`, `woker-pod-1.png`, `worker-pod-2.png`

| mark_min | pending | in_progress | done |
|---|---|---|---|
| 0 | 10000 | 0 | 0 |
| 1 | 0 | 9137 | 863 |
| 2 | 0 | 8045 | 1955 |
| 3 | 0 | 7000 | 3000 |
| 4 | 0 | 6384 | 3616 |
| 5 | 0 | 5507 | 4493 |
| 6 | 0 | 4389 | 5611 |
| 7 | 0 | 3448 | 6552 |
| 8 | 0 | 2563 | 7437 |
| 9 | 0 | 1442 | 8558 |
| 10 | 0 | 480 | 9520 |
| 11 | 0 | 0 | 10000 |

**Pod-Scale: `pod-3`** (`intake_register_ingest-workers-3-size-10000.csv`)

Screenshots: `beat-pod.png`, `worker-pod-1.png`, `worker-pod-2.png`, `worker-pod-3.png`

| mark_min | pending | in_progress | done |
|---|---|---|---|
| 0 | 10000 | 0 | 0 |
| 1 | 0 | 8805 | 1195 |
| 2 | 0 | 7246 | 2754 |
| 3 | 0 | 6071 | 3929 |
| 4 | 0 | 4594 | 5406 |
| 5 | 0 | 3532 | 6468 |
| 6 | 0 | 2238 | 7762 |
| 7 | 0 | 929 | 9071 |
| 8 | 0 | 0 | 10000 |


## Functional ID

### `functional_id_allocation`

Functional ID allocation (id generation). Table `g2p_functional_id_generation_queue`, status column `id_allocation_status`.

**Pod-Scale: `pod-1`** (`functional_id_allocation-workers-1-size-50000.csv`)

Screenshots: `beat-pod.png`, `worker-pod-1.png`

| mark_min | pending | in_progress | done |
|---|---|---|---|
| 0 | 50000 | 0 | 0 |
| 1 | 35000 | 13548 | 1452 |
| 2 | 17000 | 29420 | 3580 |
| 3 | 0 | 44343 | 5657 |
| 4 | 0 | 42098 | 7902 |
| 5 | 0 | 39976 | 10024 |
| 6 | 0 | 37988 | 12012 |
| 7 | 0 | 36207 | 13793 |
| 8 | 0 | 34136 | 15864 |
| 9 | 0 | 32093 | 17907 |
| 10 | 0 | 30081 | 19919 |
| 11 | 0 | 28088 | 21912 |
| 12 | 0 | 26096 | 23904 |
| 13 | 0 | 24195 | 25805 |
| 14 | 0 | 22316 | 27684 |
| 15 | 0 | 20356 | 29644 |
| 16 | 0 | 18254 | 31746 |
| 17 | 0 | 16667 | 33333 |
| 18 | 0 | 14717 | 35283 |
| 19 | 0 | 12686 | 37314 |
| 20 | 0 | 10836 | 39164 |
| 21 | 0 | 8996 | 41004 |
| 22 | 0 | 7067 | 42933 |
| 23 | 0 | 5343 | 44657 |
| 24 | 0 | 3393 | 46607 |
| 25 | 0 | 1524 | 48476 |
| 26 | 0 | 0 | 50000 |

**Pod-Scale: `pod-2`** (`functional_id_allocation-workers-2-size-50000.csv`)

Screenshots: `beat-pod.png`, `worker-pod-1.png`, `worker-pod-2.png`

| mark_min | pending | in_progress | done |
|---|---|---|---|
| 0 | 50000 | 0 | 0 |
| 1 | 35000 | 12431 | 2569 |
| 2 | 17000 | 27368 | 5632 |
| 3 | 0 | 41258 | 8742 |
| 4 | 0 | 37900 | 12100 |
| 5 | 0 | 34225 | 15775 |
| 6 | 0 | 30588 | 19412 |
| 7 | 0 | 27451 | 22549 |
| 8 | 0 | 24101 | 25899 |
| 9 | 0 | 20215 | 29785 |
| 10 | 0 | 16753 | 33247 |
| 11 | 0 | 13554 | 36446 |
| 12 | 0 | 10038 | 39962 |
| 13 | 0 | 6328 | 43672 |
| 14 | 0 | 2328 | 47672 |
| 15 | 0 | 0 | 50000 |

**Pod-Scale: `pod-3`** (`functional_id_allocation-workers-3-size-50000.csv`)

Screenshots: `beat-pod.png`, `worker-pod-1.png`, `worker-pod-2.png`, `worker-pod-3.png`

| mark_min | pending | in_progress | done |
|---|---|---|---|
| 0 | 50000 | 0 | 0 |
| 1 | 38000 | 8200 | 3800 |
| 2 | 23000 | 19371 | 7629 |
| 3 | 8000 | 29701 | 12299 |
| 4 | 0 | 32904 | 17096 |
| 5 | 0 | 27904 | 22096 |
| 6 | 0 | 24000 | 26000 |
| 7 | 0 | 20000 | 30000 |
| 8 | 0 | 16124 | 33876 |
| 9 | 0 | 11981 | 38019 |
| 10 | 0 | 6806 | 43194 |
| 11 | 0 | 1666 | 48334 |
| 12 | 0 | 0 | 50000 |


## Scores

### `score_compute`

Score computation queue. Table `g2p_score_compute_queue`, status column `compute_status`.

**Pod-Scale: `pod-1`** (`score_compute-workers-1-size-100000.csv`)

Screenshots: `beat-pod.png`, `worker-pod-1.png`

| mark_min | pending | in_progress | done |
|---|---|---|---|
| 0 | 100000 | 0 | 0 |
| 1 | 85000 | 10198 | 4802 |
| 2 | 67000 | 22143 | 10857 |
| 3 | 49000 | 34778 | 16222 |
| 4 | 31000 | 48058 | 20942 |
| 5 | 13000 | 60047 | 26953 |
| 6 | 0 | 66582 | 33418 |
| 7 | 0 | 59729 | 40271 |
| 8 | 0 | 52920 | 47080 |
| 9 | 0 | 47819 | 52181 |
| 10 | 0 | 40981 | 59019 |
| 11 | 0 | 34062 | 65938 |
| 12 | 0 | 27521 | 72479 |
| 13 | 0 | 21120 | 78880 |
| 14 | 0 | 14268 | 85732 |
| 15 | 0 | 7520 | 92480 |
| 16 | 0 | 591 | 99409 |
| 17 | 0 | 0 | 100000 |

**Pod-Scale: `pod-2`** (`score_compute-workers-2-size-100000.csv`)

Screenshots: `beat-pod.png`, `worker-pod-1.png`, `worker-pod-2.png`

| mark_min | pending | in_progress | done |
|---|---|---|---|
| 0 | 100000 | 0 | 0 |
| 1 | 85000 | 8770 | 6230 |
| 2 | 70000 | 18881 | 11119 |
| 3 | 49000 | 32181 | 18819 |
| 4 | 31000 | 42106 | 26894 |
| 5 | 13000 | 52062 | 34938 |
| 6 | 1000 | 59451 | 39549 |
| 7 | 0 | 49635 | 50365 |
| 8 | 0 | 38634 | 61366 |
| 9 | 0 | 27791 | 72209 |
| 10 | 0 | 16550 | 83450 |
| 11 | 0 | 6056 | 93944 |
| 12 | 0 | 0 | 100000 |

**Pod-Scale: `pod-3`** (`score_compute-workers-3-size-100000.csv`)

Screenshots: `beat-pod.png`, `worker-pod-1.png`, `worker-pod-2.png`, `worker-pod-3.png`

| mark_min | pending | in_progress | done |
|---|---|---|---|
| 0 | 100000 | 0 | 0 |
| 1 | 85000 | 8235 | 6765 |
| 2 | 73000 | 15025 | 11975 |
| 3 | 55000 | 25531 | 19469 |
| 4 | 31000 | 41883 | 27117 |
| 5 | 13000 | 52538 | 34462 |
| 6 | 0 | 56809 | 43191 |
| 7 | 0 | 45658 | 54342 |
| 8 | 0 | 38750 | 61250 |
| 9 | 0 | 28959 | 71041 |
| 10 | 0 | 18299 | 81701 |
| 11 | 0 | 7391 | 92609 |
| 12 | 0 | 0 | 100000 |

### `completion_score`

Completion-score computation queue. Table `g2p_completion_score_computation_queue`, status column `compute_status`.

**Pod-Scale: `pod-1`** (`completion_score-workers-1-size-100000.csv`)

Screenshots: `beat-pod.png`, `worker-pod-1.png`

| mark_min | pending | in_progress | done |
|---|---|---|---|
| 0 | 100000 | 0 | 0 |
| 1 | 82000 | 13147 | 4853 |
| 2 | 64000 | 25383 | 10617 |
| 3 | 46000 | 37285 | 16715 |
| 4 | 28000 | 49328 | 22672 |
| 5 | 10000 | 61357 | 28643 |
| 6 | 0 | 65302 | 34698 |
| 7 | 0 | 59029 | 40971 |
| 8 | 0 | 52523 | 47477 |
| 9 | 0 | 46171 | 53829 |
| 10 | 0 | 39771 | 60229 |
| 11 | 0 | 33260 | 66740 |
| 12 | 0 | 26938 | 73062 |
| 13 | 0 | 20566 | 79434 |
| 14 | 0 | 14260 | 85740 |
| 15 | 0 | 7929 | 92071 |
| 16 | 0 | 1566 | 98434 |
| 17 | 0 | 0 | 100000 |

**Pod-Scale: `pod-2`** (`completion_score-workers-2-size-100000.csv`)

Screenshots: `beat-pod.png`, `worker-pod-1.png`, `worker-pod-2.png`

| mark_min | pending | in_progress | done |
|---|---|---|---|
| 0 | 100000 | 0 | 0 |
| 1 | 70000 | 19668 | 10332 |
| 2 | 58000 | 27151 | 14849 |
| 3 | 40000 | 37628 | 22372 |
| 4 | 16000 | 54101 | 29899 |
| 5 | 0 | 62487 | 37513 |
| 6 | 0 | 51687 | 48313 |
| 7 | 0 | 41138 | 58862 |
| 8 | 0 | 30388 | 69612 |
| 9 | 0 | 19430 | 80570 |
| 10 | 0 | 8662 | 91338 |
| 11 | 0 | 0 | 100000 |

**Pod-Scale: `pod-3`** (`completion_score-workers-3-size-100000.csv`)

Screenshots: `beat-pod.png`, `worker-pod-1.png`, `worker-pod-2.png`, `worker-pod-3.png`

| mark_min | pending | in_progress | done |
|---|---|---|---|
| 0 | 100000 | 0 | 0 |
| 1 | 82000 | 9472 | 8528 |
| 2 | 64000 | 18575 | 17425 |
| 3 | 52000 | 21661 | 26339 |
| 4 | 34000 | 30714 | 35286 |
| 5 | 16000 | 39783 | 44217 |
| 6 | 4000 | 42714 | 53286 |
| 7 | 0 | 36107 | 63893 |
| 8 | 0 | 24305 | 75695 |
| 9 | 0 | 18916 | 81084 |
| 10 | 0 | 13838 | 86162 |
| 11 | 0 | 1978 | 98022 |
| 12 | 0 | 0 | 100000 |


## Import file

### `import_file_process`

Import-file intake ingestion. Table `import_file_process_queue`, status column `intake_form_ingestion_status`.

**Pod-Scale: `pod-1`** (`import_file_process-workers-1-size-2.csv`)

Screenshots: `beat-pod.png`, `worker-pod-1.png`

| mark_min | pending | in_progress | done |
|---|---|---|---|
| 0 | 20000 | 0 | 0 |
| 1 | 18909 | 2 | 1089 |
| 2 | 17547 | 2 | 2451 |
| 3 | 16168 | 2 | 3830 |
| 4 | 14749 | 2 | 5249 |
| 5 | 13345 | 2 | 6653 |
| 6 | 11952 | 2 | 8046 |
| 7 | 10536 | 2 | 9462 |
| 8 | 9140 | 2 | 10858 |
| 9 | 7729 | 2 | 12269 |
| 10 | 6342 | 2 | 13656 |
| 11 | 4934 | 2 | 15064 |
| 12 | 3561 | 2 | 16437 |
| 13 | 2166 | 2 | 17832 |
| 14 | 739 | 2 | 19259 |
| 15 | 0 | 0 | 20000 |
