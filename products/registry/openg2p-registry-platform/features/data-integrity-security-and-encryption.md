# Data Integrity, Security, and Encryption

The Base Registry provides secure data storage mechanisms that protect sensitive fields through encryption at rest. Individual columns in the registry database can be encrypted using pgcrypto, with encryption keys managed via a dedicated Key Management Service. This approach ensures a high level of confidentiality for personally identifiable information while keeping cryptographic operations transparent to the registry application. The platform ensures secure access to registry data through authenticated and authorized APIs.

#### De-Duplication and Record Matching

To prevent duplicate registry records, the platform includes a built-in deduplication engine. Whenever a new change request is created, the registry performs similarity matching against existing records using SQL trigram-based matching. Possible duplicates are flagged in the change request workflow, allowing verifiers and approvers to take informed decisions before approving the proposed change. Deduplication runs asynchronously, ensuring that user interaction remains responsive while still providing timely alerting.
