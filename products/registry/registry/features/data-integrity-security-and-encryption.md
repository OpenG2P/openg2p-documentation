# Data Integrity, Security, and Encryption

The Base Registry provides secure data storage mechanisms that protect sensitive fields through encryption at rest. Individual columns in the registry database can be encrypted using pgcrypto, with encryption keys managed via a dedicated Key Management Service. This approach ensures a high level of confidentiality for personally identifiable information while keeping cryptographic operations transparent to the registry application. The platform ensures secure access to registry data through authenticated and authorized APIs.

#### Partner Signature Verification

External callers reach the registry through the **Partner API**, which does not use
Keycloak — callers prove identity by **signing** their request. The registry verifies
that signature against the partner's **public key**, and deliberately **stores no
partner keys of its own**: it fetches them at verification time from
[Partner Management](../../../../platform/platform-services/partner-management/README.md),
the platform's central registry of partner keys, and caches them briefly in-process.
Keys are looked up by the partner reference `PARTNER_<sender_id>` — the same
convention used across the platform — so onboarding, approval and key rotation are
handled once, centrally, rather than per registry. A partner that is unknown or has
been disabled in Partner Management yields no key and the request is rejected
(fail-closed).

Signature verification is an **independent switch** from consent enforcement (see
[Consent-Aware data sharing](consent-aware-data-sharing.md)); the Helm values ship it
off, so it is opt-in per deployment. Design detail, configuration and the current
per-endpoint status are in
[Partner APIs → Authentication and signature verification](../design/partner-apis.md#authentication-and-signature-verification).

#### De-Duplication and Record Matching

To prevent duplicate registry records, the platform includes a built-in deduplication engine. Whenever a new change request is created, the registry performs similarity matching against existing records using SQL trigram-based matching. Possible duplicates are flagged in the change request workflow, allowing verifiers and approvers to take informed decisions before approving the proposed change. Deduplication runs asynchronously, ensuring that user interaction remains responsive while still providing timely alerting.
