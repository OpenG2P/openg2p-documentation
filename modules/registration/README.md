# Secure Registry

## Introduction

OpenG2P offers a secure registry that stores person details that have been collected across multiple programs.  Duplication of person's data is avoided by deduplicating using the unique ID associated with the person (like MOSIP) or by running demographic deduplication heuristics such that the same person is not added multiple times to the same registry. To avoid duplication of fields like age, date of birth, city etc.,  the fields are "codified" with [schemas](../secure-registry/schema-for-fields.md).&#x20;

The data in the registry is encrypted at rest. &#x20;

The registry is queried by various programs to create beneficiary list.  See [Program Management](../beneficiary-management.md). The queried data is **anonymised** such that Personally Identifying Information (PII) is not exposed in a human readable form or provided to downstream systems.&#x20;

Registry supports the following functions\*\*:

1. CRUD operations
2. Attestation
3. Verifiable credentials
4. Anonymous profile
5. Complex queries

{% hint style="info" %}
\*\* Full implementations of these functions will be available in version 1.2.x of OpenG2P.
{% endhint %}







