# Partner API

Performance-testing plan, execution, and results for the partner-api service — DCI-compliant farmer search (sync and async) and the partner ingest endpoint.

## Test Scenarios

The test plan: the DCI query types under test, sync vs. async pass criteria, pod and database configuration, search-term provenance, the ramp/SLO shape, and the execution runbook.

{% content-ref url="test-scenarios.md" %}
[test-scenarios.md](test-scenarios.md)
{% endcontent-ref %}

## Raw Report

Every measurement Locust actually recorded, verbatim — auto-generated, no interpretation.

{% content-ref url="raw-report.md" %}
[raw-report.md](raw-report.md)
{% endcontent-ref %}

## Final Report

The interpretation layer, organized around the four DCI-compliant query types (Single Farmer Search using ID, `expression` range, `graphql` range, `predicate` range) plus the Ingest API — sync vs. async throughput comparison, scaling behavior, and CPU/Memory findings, built from the raw report.

{% content-ref url="final-report.md" %}
[final-report.md](final-report.md)
{% endcontent-ref %}

## Final Report Summary

A condensed version of the final report: methodology, test environment, and per-query-type headline results.

{% content-ref url="final-report-summary.md" %}
[final-report-summary.md](final-report-summary.md)
{% endcontent-ref %}
