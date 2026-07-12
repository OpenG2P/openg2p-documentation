---
description: OpenG2P Interoperability
---

# Interoperability

At the very onset OpenG2P team has been cognizant of the importance of working with DPGs and other external components with standard interfaces avoiding the need to develop proprietary and custom methods of connecting to other systems. Interoperability is a fundamental design principle in OpenG2P's thought process. We have been an active participant in interoperability efforts like G2P Connect, DCI, and GovStack. Specifically, the following **open standards** interfaces have been implemented:

| Open Standard                                                                                                   | Application                                                                                                          |
| --------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| [G2P Connect ID Mapper APIs](https://g2p-connect.github.io/specs/release/html/mapper_core_api_v1.0.0.html)      | [SPAR](https://github.com/OpenG2P/openg2p-documentation/blob/latest/social-payments-account-registry-spar/README.md) |
| [G2P Connect Disbursement APIs](https://g2p-connect.github.io/specs/release/html/disburse_core_api_v1.0.0.html) | [G2P Bridge](g2p-bridge/), [PBMS](pbms/)                                                                             |
| [G2P Connect Registry APIs](https://g2p-connect.github.io/specs/release/html/registry_core_api_v1.0.0.html)     | [PBMS](pbms/), [Social Registry](products/registry/registry/_archive/social-registry/)                               |
| [Verifiable Credentials](https://www.w3.org/TR/vc-data-model/)                                                  | [e-Voucher](products/pbms/_archive/previous-generation/functionality/disbursement-cycles/e-voucher.md) and e-Card    |
| [S3 APIs](https://docs.aws.amazon.com/AmazonS3/latest/API/Welcome.html)                                         | Document store                                                                                                       |
| [⁠CWT](https://datatracker.ietf.org/doc/html/rfc8392)                                                           | QR Code Scan of ID                                                                                                   |
| [⁠OpenID](https://auth0.com/docs/authenticate/protocols/openid-connect-protocol)                                | Authentication                                                                                                       |
