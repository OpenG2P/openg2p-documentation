# Registry Release Notes - v4.1.0

|                        |                           |
| ---------------------- | ------------------------- |
| **Version**            | 4.1.0                     |
| **Helm Chart Version** | 4.1.0                     |
| **Release Date**       | 08-May-2026               |
| **Description**        | <p></p><ul><li></li></ul> |
| **Previous Version**   | 4.0.0                     |

Major Features introduced in 4.1.0

[Intake Form](../design/intake-forms/) is now treated as a separate route (INSERT) into a register. Change Requests is reserved for the EDIT route. All new records into a REGISTER will now be routed through Intake Forms. Intake Forms and Change Requests are now parallel routes into a REGISTER.

[Registrant Authentication ](../design/registrant-authentication-oidc-widget/)- A new widget has been introduced to facilitated Registrant Authentication. This widget will interact with IAM-Service to facilitate authentication against an Identity Provider.

[Completion Score ](../design/completion-score.md)- allows you to specify whether a register needs completion score to be tracked. Allows specification of weightage for each section and computes a completion score for each section of the register and also the overall completion score of the register

[Domain Scores for a Register](../design/score-computation-framework.md) - This feature allows you to specify the scores required to be computed for a register record. E.g. Poverty Score, PMT Score, Food security score.&#x20;

[Themes](../design/registry-themes.md) - This feature allows you to define themes for the UI. A theme defines primary colour scheme, secondary colour scheme and font family. You can switch a Registry instance from one theme to another theme.

[Dynamic Languages](../design/dynamic-languages.md) - This feature allows you to define a new language for the Registry and import a translation file (JSON format).

[Audit Log](../design/audit-trail-for-write-operations.md) - All API requests into the registry are now logged with non-blocking API call into a separate Audit Log Service. This logging has been enabled by introducing an intercepting middleware in the Registry API layer.





