---
description: Envelope encryption approach for column-level encryption of sensitive registry data at rest.
---

# Encryption at Rest

## Overview

OpenG2P Registry uses an **envelope encryption** approach to protect sensitive data stored in PostgreSQL. Rather than encrypting entire database files, the registry performs column-level encryption on fields that contain personally identifiable information. This provides fine-grained confidentiality while keeping non-sensitive columns available for indexing and querying.

## Envelope encryption

The envelope encryption model separates the encryption of data from the protection of the encryption key itself. The flow operates as follows:

1. **DEK generation** -- at initial setup, the registry generates a cleartext Data Encryption Key (DEK).
2. **DEK protection** -- the DEK is signed (wrapped) using an asymmetric key managed by the PKI / Key Management Service (KMS). This produces a ciphertext-DEK.
3. **DEK storage** -- the ciphertext-DEK is persisted in Kubernetes Secrets.
4. **Startup retrieval** -- during application startup, the registry calls the KMS to unwrap the ciphertext-DEK and obtains the cleartext DEK, which is held in memory for the lifetime of the process.
5. **Column encryption** -- individual database columns are encrypted and decrypted using AES symmetric encryption with the in-memory cleartext DEK.
6. **No KMS latency on read/write** -- because the cleartext DEK is held in memory, every encrypt and decrypt operation is a local AES operation. The KMS is only contacted at startup, eliminating per-request latency.

{% hint style="info" %}
The asymmetric KMS key is used solely to protect the DEK. All data-path encryption uses the symmetric AES DEK, ensuring that read and write performance is not affected by KMS availability or round-trip latency.
{% endhint %}

## Implementation

Domain models determine which columns require encryption. The implementation follows a consistent pattern across all register models.

### Storage format

Encrypted columns are stored as `LargeBinary` in PostgreSQL. The binary value contains the AES initialisation vector (IV) prepended to the ciphertext, allowing each value to be encrypted with a unique IV.

### Transparent access via hybrid properties

ORM models use SQLAlchemy `hybrid_property` decorators to provide transparent encryption and decryption. Application code reads and writes plaintext values; the ORM layer handles the encryption boundary automatically.

The pattern works as follows:

* The abstract `G2PRegister` base class provides two utility methods: `encrypt_value(plaintext)` and `decrypt_value(blob)`. These methods use AES symmetric encryption with the in-memory cleartext DEK.
* Each domain register model (e.g. `FarmerRegister`) declares encrypted columns as `LargeBinary` and exposes them through `@hybrid_property` getters and setters. The getter calls `decrypt_value`, and the setter calls `encrypt_value`.

This means that a domain model like `FarmerRegister` can declare a `full_name` column that is stored encrypted in the database but accessed as a plain string in application code. The encryption and decryption are fully transparent to service and controller layers.

{% content-ref url="../features/data-integrity-security-and-encryption.md" %}
data-integrity-security-and-encryption.md
{% endcontent-ref %}
