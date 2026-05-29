# Scaling for High Volumes

The G2P Bridge is designed to perform in high volume disbursement scenarios. To achieve this, all the processing in the G2P Bridge is done asynchronously.

The disbursement instructions from the upstream Program MIS / PBMS systems are received by the G2P Bridge via. a REST API. The "create\_disbursements" API is designed to receive multiple API invocations for a single "program-disbursement-cycle". Each invocation of the API brings a payload that contains a list of disbursements.

Refer to the tech [architecture section - asynchronous processing](../../platform/architecture/async-processes-tech-architecture.md) for detailed architecture and design.
