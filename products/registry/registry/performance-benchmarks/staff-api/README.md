# Staff API

Performance-testing plan, execution, and results for the staff-api (`staff-portal-api`) service — the highest-traffic surface in the registry.

## Test Scenarios

The test plan: objectives, scope, the Volume-Tier × Pod-Scale model, the 5 Locust scenarios, SLOs, and the execution runbook.

{% content-ref url="test-scenarios.md" %}
[test-scenarios.md](test-scenarios.md)
{% endcontent-ref %}

## Raw Report

Every measurement Locust actually recorded, verbatim — auto-generated, no interpretation.

{% content-ref url="raw-report.md" %}
[raw-report.md](raw-report.md)
{% endcontent-ref %}

## Final Report

The interpretation layer: capacity/sizing model, bottleneck findings, and pass/fail against the SLOs — built from the raw report.

{% content-ref url="final-report.md" %}
[final-report.md](final-report.md)
{% endcontent-ref %}
