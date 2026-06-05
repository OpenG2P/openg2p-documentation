# Testing

The G2P Bridge is tested at several complementary layers:

| Layer                                                     | Scope                                                                                                 | Where                   |
| --------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- | ----------------------- |
| Unit Testing                                              | White-box, mocked services/DB — fast, run in CI on every commit                                       | `core/**/tests/`        |
| [Functional Testing](functional-testing.md)               | Manual scenario testing driven from PBMS (UI flows, service-outage handling)                           | manual (PBMS)           |
| [Regression Sanity Suite](regression-sanity-suite.md)     | Black-box, point-at-a-deployed-system — every API + full end-to-end cash flow verified stage by stage, plus business-rule negatives and MT940 reconciliation errors | `test/sanity/`          |
| Performance Testing                                       | Load / throughput                                                                                     | `test/`                 |

Use the **unit tests** to catch code-logic regressions, the **regression sanity suite** to confirm an installed environment works end to end (it now also covers the API-level negative scenarios and MT940 reconciliation-error checks that were previously standalone Postman/script artefacts), and **functional** (manual PBMS) and **performance** testing for scenario coverage and scale.
