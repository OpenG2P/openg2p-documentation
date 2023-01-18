# Secure Registry

## Introduction

OpenG2P offers a secure registry that stores person details that have been collected across multiple programs.  Deduplication of person's data is avoided by deduplicating using the unique ID associated with the person (like MOSIP) or by running demographic deduplication heuristics such that the same person is not added multiple times to the same registry. To avoid duplication of fields like age, date of birth, city etc.,  the fields are "codified" with [schemas](../secure-registry/schema-for-fields.md).&#x20;

The data in the registry is encrypted at rest. &#x20;

The registry is queried by various programs to create beneficiary list.  See [Program Management](../beneficiary-management.md). The queried data is **anonymised** such that Personally Identifying Information (PII) is not exposed in a human readable form or provided to downstream systems.&#x20;







