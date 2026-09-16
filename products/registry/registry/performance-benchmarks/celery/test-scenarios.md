# Test Scenarios — celery (async pipelines)

**Status: deferred, undesigned.** `locust/celery/` is a bare scaffold
(`to-be-decided/` placeholder) — no tooling, no scenarios, no metrics
approach defined yet. See
[`../staff-api/test-scenarios.md`](../staff-api/test-scenarios.md) §1/§2:
*"Async pipeline throughput (Celery ingestion/outgestion/dedup) is explicitly
out of scope for this round — revisit once the Volume-Tier × Pod-Scale matrix
[for staff-api] is done."*

## What this will eventually cover

Async pipeline throughput — ingestion, outgestion, dedup, score-computation —
and Redis queue-depth / worker-throughput measurement. Unlike staff-api and
partner-api, this isn't request/response latency against Locust-driven load;
it's queue depth, task completion rate, and worker scaling, so it will need
its own measurement approach (not a Locust `User` class), not just a new set
of endpoint classes in the existing scheme.

`get_deduplication_register_results` / `get_deduplication_change_request_results`
in [`../staff-api/test-scenarios.md`](../staff-api/test-scenarios.md) are a
concrete link to this tier: those staff-api calls only *fetch* results this
pipeline already computed — this doc will eventually cover the cost of doing
that computation, which staff-api's Register-Read numbers deliberately don't
include.

## Reports

Once designed, this tier gets its own `raw-report.md`/`final-report.md`
under `documentation/celery/`, shaped around whatever this tier's actual unit
of measurement turns out to be (queue depth over time, task latency
percentiles, worker throughput) rather than the Ingress/Volume-Tier/
Pod-Scale/Step/Scenario shape that fits staff-api's synchronous-API load
tests.
