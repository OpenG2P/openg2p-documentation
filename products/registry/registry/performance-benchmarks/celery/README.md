# Celery

Performance-testing plan, execution, and results for the Celery beat + worker backlog-drain pipelines (partner ingest, outgest, intake ingest, functional ID, scores, import file).

## Test Scenarios

The test plan: objectives, scope, the backlog-size × worker-pod model, the per-scenario producer/worker definitions, and the execution runbook.

{% content-ref url="test-scenarios.md" %}
[test-scenarios.md](test-scenarios.md)
{% endcontent-ref %}

## Raw Report

Every per-minute `pending`/`in_progress`/`done` count the collector actually recorded, verbatim — auto-generated, no interpretation.

{% content-ref url="raw-report.md" %}
[raw-report.md](raw-report.md)
{% endcontent-ref %}

## Final Report

The interpretation layer: per-scenario items-at-start, beat parameters, Tasks-vs-Time measurements, pod CPU/Memory, and bottleneck findings — built from the raw report.

{% content-ref url="final-report.md" %}
[final-report.md](final-report.md)
{% endcontent-ref %}

## Final Report Summary

A condensed version of the final report: methodology, data seeding, test environment, and per-scenario headline results.

{% content-ref url="final-report-summary.md" %}
[final-report-summary.md](final-report-summary.md)
{% endcontent-ref %}
