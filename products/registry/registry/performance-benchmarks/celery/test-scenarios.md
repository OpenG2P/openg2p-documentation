# Test Scenarios for celery

## 1. Objectives

Establish, with a minute-by-minute drain of a fixed backlog
([environment-topology.md](../environment-topology.md)):

1. **Drain time** — how many minutes one beat pod and N worker pods take to
  move a known backlog from pending to done.
2. **Worker scaling** — how that drain changes from 1 worker pod to 2 to 3,
  with beat held at 1 pod.
3. **Where the time goes** — beat sending tasks, the worker doing the task,
  Postgres, or an outside service such as the id-generator.

The unit is rows on one status column, counted every minute.

Staff-api calls such as `get_deduplication_register_results` only read
results this pipeline has already written. Those API numbers do not include
the cost of producing the results. That cost is what these scenarios measure.
See [../staff-api/test-scenarios.md](../staff-api/test-scenarios.md).

## 2. Scope

**In scope**

- The scenarios in §4, one at a time. `ingest_data` and `change_request_ingest` share one beat producer. The other scenarios each have their own. `outgest_topic_register` and `import_file_process` are not 1, 2, 3 worker runs.
- One beat pod. Worker pods at 1, then 2, then 3.
- A fixed backlog size, passed to `./k8s/run.sh`.
- The perftest namespace, image `vin0dkhichar/ofr-staff-celery:performance-test`.

**Out of scope**

- Staff-api and partner-api request latency.
- Soak, chaos, and a Postgres tuning sweep.



## 3. The model: backlog size × worker pods, beat fixed at 1

A run is one cell: one scenario, one backlog size, one worker count.


| Axis        | Values                                                               | What stays fixed                                                      |
| ----------- | -------------------------------------------------------------------- | --------------------------------------------------------------------- |
| Scenario    | one name from §4                                                     | Every other producer is parked                                        |
| Backlog     | the third argument of `./k8s/run.sh`, for example `10000` or `50000` | That many rows are left `PENDING`. The rest of that status are parked |
| Worker pods | `1`, then `2`, then `3`                                              | Beat is always 1 pod                                                  |


Beat claims pending rows on each tick and sends one Celery message per row to
`registry_worker_queue`. A set `REGISTRY_CELERY_BEAT_<PRODUCER>_NO_OF_TASKS`
is that producer's claim size. Otherwise the claim size is
`REGISTRY_CELERY_BEAT_NO_OF_TASKS_TO_PROCESS`. Each run enables only that
scenario's producer and worker and disables the others. A worker pod runs
`--concurrency=2`, so one pod has two processes. The clock starts after the
workers are ready, the backlog is pinned, and beat has logged that it
started. `./k8s/run.sh` then writes one CSV row per minute until `pending`
and `in_progress` are both 0, or until minute 30.

CSV path:

`locust/celery/results/pod-<workers>/<scenario>/<scenario>-workers-<workers>-size-<size>.csv`

Columns:


| Column        | Meaning                                                                           |
| ------------- | --------------------------------------------------------------------------------- |
| `mark_min`    | Minutes since beat logged `beat: Starting`. Minute 0 is the first count, taken at that moment. |
| `pending`     | Cohort rows still `PENDING` on this scenario's status column.                     |
| `in_progress` | Cohort rows in `PROCESSING` or `INPROGRESS` on that column.                        |
| `done`        | Cohort rows in `PROCESSED` or `COMPLETED` on that column. A scenario uses one of those two. |


`import_file_process` counts records inside the CSV, not queue rows. `pending`
is records not started, `in_progress` is the record the process is ingesting,
and `done` is rows already written to `import_file_process_log`.

Rows finished in that minute are `done` at this mark minus `done` at the
previous mark.

Put the beat CPU screenshot and the worker CPU screenshot in the same folder
as the CSV.

**Derived from the three worker counts, not a separate run:**

- **Finish minute** — the first `mark_min` where `pending` and `in_progress`
are both 0 and `done` equals the backlog.
- **Steady rows/min** — `done` gained per minute while `in_progress` stays
above zero.
- **Scaling** — finish minute at 2 workers and at 3 workers, compared with
1 worker on the same scenario and the same backlog. If 2 workers already
drain as fast as beat can send, a third worker does not shorten the run.



## 4. Test scenarios (`locust/celery/`)

Each scenario is one `./k8s/run.sh` case. Populate it with
`./k8s/populate.sh <scenario> <size>` while beat and workers are at 0
replicas, then run workers 1, 2, and 3. Populate again before the 2-worker
and 3-worker runs. `./k8s/run.sh` puts that cohort back to `PENDING` before
the next worker count. Dedup runs also delete that cohort's result rows.
Intake ingest gives the section rows new `internal_record_id` values so the
live register is left in place.

Beat sets the in-progress status before it sends the task, except
`intake_register_ingest`, where the worker sets `PROCESSING`. `done` in the
table below is the status the worker writes when the task succeeds.

### Partner ingest

Purpose: take a partner payload from raw file rows through classification,
transformation, and writing the register.


| Scenario                     | Table                      | Status column           | Done        | What the worker does                                                                  |
| ---------------------------- | -------------------------- | ----------------------- | ----------- | ------------------------------------------------------------------------------------- |
| `ingest_data_classification` | `incoming_raw_data`        | `classification_status` | `PROCESSED` | Classifies one raw ingest row.                                                        |
| `ingest_data_transformation` | `incoming_classified_data` | `transformation_status` | `PROCESSED` | Transforms one classified row. Shares its beat frequency with outgest transformation. |
| `ingest_data`                | `incoming_classified_data` | `ingestion_status`      | `PROCESSED` | Writes rows whose `pipeline_action` is not `UPDATE`.                                  |
| `change_request_ingest`      | `incoming_classified_data` | `ingestion_status`      | `PROCESSED` | Same table and status as `ingest_data`, limited to `pipeline_action = 'UPDATE'`.      |




### Outgest

Purpose: turn a register change into a payload, publish it, and register the WebSub topic.


| Scenario                      | Table               | Status column            | Done        | What the worker does                                                                   |
| ----------------------------- | ------------------- | ------------------------ | ----------- | -------------------------------------------------------------------------------------- |
| `outgest_data_transformation` | `outgoing_raw_data` | `transformation_status`  | `PROCESSED` | Transforms one outgest payload. Populate builds the rows. `publish_status` stays null. |
| `outgest_data_publish`        | `outgoing_raw_data` | `publish_status`         | `PROCESSED` | Publishes one payload that is already transformed. |
| `outgest_topic_register`      | `outgoing_topics`   | `websub_register_status` | `PROCESSED` | Registers one WebSub topic. Not run in the 1, 2, 3 worker series. |


Publish posts to `https://websub.perftest.openg2p.org`.

`outgest_topic_register` is left out of the worker-scaling runs. A topic is
unique on `(data_model_id, register_id)`. This database has one data model
and 9 registers, so 9 topics is the maximum. Each task is one register call,
and that count does not grow with the farmer backlog, so 1, 2, and 3 worker
pods do not show a drain.




### Deduplication

**To be added.** None of these four scenarios has a backlog or a 1, 2, 3
worker run yet.

Purpose: score one record against a candidate set and write match rows when the score is at or above the threshold. An empty match list is still `COMPLETED`.


| Scenario                   | Table                          | Status column                          | Done        | What the worker does                                                       |
| -------------------------- | ------------------------------ | -------------------------------------- | ----------- | -------------------------------------------------------------------------- |
| `dedup_register`           | `g2p_register_change_requests` | `deduplication_register_status`        | `COMPLETED` | Scores one change request against farmers on the parent register.          |
| `dedup_change_request`     | `g2p_register_change_requests` | `deduplication_change_request_status`  | `COMPLETED` | Scores one pending change request against other pending change requests.   |
| `dedup_intake_vs_register` | `g2p_intake_form_submissions`  | `deduplication_status_vs_register`     | `COMPLETED` | Scores one `FINAL` intake submission against the register.                 |
| `dedup_intake_vs_intake`   | `g2p_intake_form_submissions`  | `deduplication_status_vs_intake_forms` | `COMPLETED` | Scores one `FINAL` intake submission against other intake submissions.     |

### Intake ingest

Purpose: copy one approved, final intake submission into the live register.


| Scenario                 | Table                         | Status column                    | Done        | What the worker does                                                                                           |
| ------------------------ | ----------------------------- | -------------------------------- | ----------- | -------------------------------------------------------------------------------------------------------------- |
| `intake_register_ingest` | `g2p_intake_form_submissions` | `register_ingest_process_status` | `PROCESSED` | Inserts one register row for each section row on that submission. The submission must be `APPROVED` and `FINAL`. |


Each copied section row has its own `internal_record_id` and
`application_reference`. A rerun assigns new ids on the intake tables and
leaves the live farmer table in place.

### Functional ID

Purpose: give a register row a functional id, then record that the id was applied.


| Scenario                   | Table                                | Status column          | Done        | What the worker does                                                                                                                                    |
| -------------------------- | ------------------------------------ | ---------------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `functional_id_allocation` | `g2p_functional_id_generation_queue` | `id_allocation_status` | `COMPLETED` | `POST {functional_id_generation_url}/idgenerator/{register}/id`. The default base ends in `/v1`, so a farmer call is `/v1/idgenerator/farmer/id`. Writes `functional_record_id` on the farmer and sets `id_updation_status` to `PENDING`. |
| `functional_id_updation`   | `g2p_functional_id_generation_queue` | `id_updation_status`   | `COMPLETED` | Joins `resolved_prefix`, `resolved_id`, and `resolved_suffix` already stored on the queue row and marks that row completed. The populate script stores the farmer's existing `functional_record_id` in `resolved_id`. |


Allocation is the run that contacts the [id-generator](https://github.com/OpenG2P/id-generator).
`POST /{id_type}/id` marks the issued id `TAKEN`. That service has no update
route. The update worker only logs the URL it would have called
(`_notify_functional_id_used` in `functional_id_updation_worker.py`), so an
update run is a queue-status update and the id-generator log stays empty.

When an allocation row finishes, its `id_updation_status` becomes `PENDING`.
The updation producer then sends that same queue row. Those follow-on tasks
share the worker pods with the allocation run. The updation scenario itself
starts from rows whose allocation status is already `COMPLETED`.

### Scores

Purpose: write one score for a register record.


| Scenario           | Table                                    | Status column    | Done        | What the worker does                                                                                                      |
| ------------------ | ---------------------------------------- | ---------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------- |
| `score_compute`    | `g2p_score_compute_queue`                | `compute_status` | `COMPLETED` | Loads `G2PScoreComputeService` plus the queue row's score type, then upserts `g2p_register_scores`. Populate copies one existing queue row, including its score definition and attribute values. `POVERTY` uses the farmer extension class. |
| `completion_score` | `g2p_completion_score_computation_queue` | `compute_status` | `COMPLETED` | One queue row per farmer, on section `farmer_farmer_socio_economic_and_health_section_04`. Counts filled columns on that farmer row and writes `g2p_register_section_completion_score`. |


`score_compute` passes `contributing_attribute_config` into `compute_score`.
The Farmer poverty service must accept that argument. A service that still
takes `score_config` fails every task and `done` stays 0. Rebuild the celery
image after changing `farmer-extension/.../score_compute/services/poverty.py`.

`completion_score` does not read the poverty score-definition tables.

### Import file


| Scenario              | Table                       | Status column                  | Done        | What the worker does                                                                                                                               |
| --------------------- | --------------------------- | ------------------------------ | ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| `import_file_process` | `import_file_process_queue` | `intake_form_ingestion_status` | `PROCESSED` | Ingests every row of one CSV. One file is one Celery task. Not run at 2 or 3 worker pods. |


`./k8s/populate.sh import_file_process <records>` writes that many records
into each CSV, up to 50000. `IMPORT_FILES` is the number of files. The run
size is the number of files. The CSV counts records ingested, not queue rows.

One process keeps a file until that file is finished. Another pod cannot
take part of the same file, so 2 and 3 worker pods do not shorten the run.
The 1-pod run with two files is enough: finish time stays the length of one
file, and a second process only finishes a second file in that same time.

```bash
IMPORT_FILES=2 ./k8s/populate.sh import_file_process 10000
./k8s/run.sh 1 import_file_process 2
```

## 5. What a finished run shows

There is no latency SLO. Read the CSV and the two CPU screenshots.


| Reading                                                                       | What it means                                                                        |
| ----------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| `done` reaches the backlog and `pending` and `in_progress` hit 0              | The cohort finished. The finish minute is the drain time.                            |
| `pending` falls in steps equal to the beat batch, and `in_progress` stays low | Beat is not releasing work as fast as the workers can take it.                       |
| `in_progress` stays near the backlog until late in the run                    | Workers are busy. The drain time is worker time.                                     |
| `done` stays 0 while `in_progress` is high                                    | Tasks are failing and returning to `PENDING`. Read the worker log for that scenario. |
| 2 worker pods finish in about the same minute as 3                            | The single beat pod is the limit. The third pod is idle.                             |


A run is usable when `done` equals the backlog, the worker log is not a
repeating exception for that task, and the CPU screenshots sit beside the CSV.

## 6. Execution runbook

From `farmer-registry/performance-testing/locust/celery`, with
`KUBECONFIG` pointed at the perftest cluster.

1. Populate the scenario once. The script refuses to run unless beat and
   workers are already at 0 replicas.

   ```bash
   ./k8s/populate.sh outgest_data_transformation 10000
   ```

2. Run one worker count. This puts the previous cohort back to `PENDING`,
   parks every other producer, pins the backlog, starts the workers, starts
   beat, and writes the CSV.

   ```bash
   ./k8s/run.sh 1 outgest_data_transformation 10000
   ./k8s/run.sh 2 outgest_data_transformation 10000
   ./k8s/run.sh 3 outgest_data_transformation 10000
   ```

3. Leave the terminal open until the script prints `COLLECTOR_FINISHED`.
4. Save the beat CPU screenshot and the worker CPU screenshot next to that CSV.
5. Populate again before the 2-worker and 3-worker runs. Skip
   `outgest_topic_register` and `import_file_process`. The reasons are in
   those sections.

If `./k8s/run.sh` stops after the pods are already running, do not start it
again. Use `./k8s/collect.sh <workers> <scenario> <size>`. That command only
appends the CSV.