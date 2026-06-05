# Testing

The G2P Bridge is tested at several complementary layers:

| Layer                                                     | Scope                                                                                                 | Where                   |
| --------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- | ----------------------- |
| [Unit Testing](/broken/pages/Is61pElpvendTzOxEKb4)        | White-box, mocked services/DB — fast, run in CI on every commit                                       | `core/**/tests/`        |
| [Functional Testing](functional-testing.md)               | Scenario / manual + Postman flows (from PBMS and standalone)                                          | `test/functional-test/` |
| [Regression Sanity Suite](regression-sanity-suite.md)     | Black-box, point-at-a-deployed-system — every API + full end-to-end cash flow verified stage by stage | `test/sanity/`          |
| [Performance Testing](/broken/pages/AYM3TbNAi8E6y9lm2TMR) | Load / throughput                                                                                     | `test/`                 |

Use the **unit tests** to catch code-logic regressions, the **regression sanity suite** to confirm an installed environment works end to end, and **functional** and **performance** testing for scenario coverage and scale.
