---
description: OpenG2P Interoperability
---

# Interoperability

At the very onset OpenG2P team has been cognizant of the importance of working with DPGs and other external components with standard interfaces avoiding the need to develop proprietary and custom methods of connecting to other systems. Interoperability is a fundamental design principle in OpenG2P's thought process. We have been an active participant in interoperability efforts like G2P Connect, DCI, and GovStack. Specifically, the following **open standards** interfaces have been implemented:

| Open Standard                                                                                                      | Application                                                             |
| ------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------- |
| [G2P Connect ID Mapper APIs](https://g2p-connect.github.io/specs/release/html/mapper\_core\_api\_v1.0.0.html)      | [SPAR](social-payments-account-registry-spar/)                          |
| [G2P Connect Disbursement APIs](https://g2p-connect.github.io/specs/release/html/disburse\_core\_api\_v1.0.0.html) |  [G2P Cash Transfer Bridge](g2p-cash-transfer-bridge/),  [PBMS ](pbms/) |
| [G2P Connect Registry APIs](https://g2p-connect.github.io/specs/release/html/registry\_core\_api\_v1.0.0.html)     |  [PBMS](pbms/), [Social Registry](social-registry/)                     |
| [Verifiable Credentials ](https://www.w3.org/TR/vc-data-model/)                                                    | [e-Voucher](pbms/features/disbursement-cycles/e-voucher.md) and e-Card  |
| [S3 APIs](https://docs.aws.amazon.com/AmazonS3/latest/API/Welcome.html)                                            | Document store                                                          |
| [⁠CWT](https://datatracker.ietf.org/doc/html/rfc8392)                                                              | QR Code Scan of ID                                                      |
| [⁠OpenID](https://auth0.com/docs/authenticate/protocols/openid-connect-protocol)                                   | Authentication                                                          |
