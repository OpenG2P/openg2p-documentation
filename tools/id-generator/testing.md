---
description: >-
  Test plan for the ID Generator service — test categories, execution,
  and reporting.
---

# Testing

## Approach

All tests are **API-level integration tests** executed against a running instance of the ID Generator service. The service can be local (`http://localhost:8000`) or a remote deployment.

No unit tests or mocking — the tests exercise the real service end-to-end through its HTTP API.

## Test categories

Tests are organized into 5 categories, executed in order:

| Phase | Category       | Marker          | Description                                                |
| ----- | -------------- | --------------- | ---------------------------------------------------------- |
| 1     | API Contract   | `api_contract`  | Response envelope, HTTP status codes, error codes, OpenAPI |
| 2     | Filters        | `filters`       | Validate API correctly accepts/rejects IDs per filter rules|
| 3     | Exhaustive     | `exhaustive`    | Drain all IDs from small ID types, verify uniqueness       |
| 4     | Exhaustion     | `exhaustion`    | Verify correct IDG-002 errors after space is consumed      |
| 5     | Performance    | `performance`   | Response time percentiles (p50, p95, p99)                  |

## Test cases

A complete, human-readable list of all test cases is maintained in [`tests/test_cases.yaml`](https://github.com/OpenG2P/id-generator/blob/main/tests/test_cases.yaml). Each entry includes the test ID, name, category, file, and description. This file serves as a reviewable inventory of what is tested.

## Running tests

### Prerequisites

```bash
pip install -r requirements-test.txt
```

### Commands

```bash
cd tests

# Fast tests — API contract + filters (~2 seconds)
pytest -m "api_contract or filters" --base-url=http://localhost:8000 -v

# All tests in order
pytest --base-url=http://localhost:8000 -v

# With HTML report
pytest --base-url=http://localhost:8000 --html=report.html --self-contained-html -v

# Against a remote service
pytest --base-url=https://idgen.staging.example.com -v

# Individual categories
pytest -m api_contract --base-url=http://localhost:8000 -v
pytest -m filters --base-url=http://localhost:8000 -v
pytest -m performance --base-url=http://localhost:8000 -v
pytest -m exhaustive --base-url=http://localhost:8000 -v
pytest -m exhaustion --base-url=http://localhost:8000 -v
```

{% hint style="warning" %}
**Exhaustive tests** drain all IDs from the two smallest-ID-length types. After running them, those ID types are fully consumed. Drop their tables and restart the service to re-run.
{% endhint %}

## Test auto-discovery

Tests **auto-discover** ID type names and ID lengths from the running service via `GET /v1/idgenerator/config`. No ID type names are hardcoded in test code.

The test framework:

1. Fetches config from the service at session start
2. Sorts ID types by `id_length`
3. Uses the two smallest for exhaustive/exhaustion tests
4. Uses the largest for performance tests

## HTML report

The test report includes:

* **Service version** — fetched from `GET /v1/idgenerator/version`
* **Git commit** and **build time**
* **Target URL** — which service instance was tested
* **Test run time** — UTC timestamp
* Per-test results with pass/fail/skip status

## Technology stack

| Component         | Choice            | License      |
| ----------------- | ----------------- | ------------ |
| Framework         | pytest            | MIT          |
| HTTP Client       | httpx (async)     | BSD-3-Clause |
| Async support     | pytest-asyncio    | Apache 2.0   |
| Reporting         | pytest-html       | MPL 2.0      |
| Test ordering     | pytest-ordering   | MIT          |
| Report metadata   | pytest-metadata   | MPL 2.0      |
