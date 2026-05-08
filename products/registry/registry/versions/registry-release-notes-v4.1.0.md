# Registry Release Notes - v4.1.0

Major Features introduced in 4.1.0

[Intake Form](../design/intake-forms/) is now treated as a separate route (INSERT) into a register. Change Requests is reserved for the EDIT route. All new records into a REGISTER will now be routed through Intake Forms. Intake Forms and Change Requests are now parallel routes into a REGISTER.

[Registrant Authentication ](../design/registrant-authentication-oidc-widget/)- A new widget has been introduced to facilitated Registrant Authentication. This widget will interact with IAM-Service to facilitate authentication against an Identity Provider.

[Completion Score ](../design/completion-score.md)- allows you to specify whether a register needs completion score to be tracked. Allows specification of weightage for each section and computes a completion score for each section of the register and also the overall completion score of the register
