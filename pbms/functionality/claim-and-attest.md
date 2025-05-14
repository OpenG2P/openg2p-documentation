---
description: Work in progress
---

# Claim and Attest

## Introduction

Claim and Attest is a key module in the OpenG2P Social Registry, designed to facilitate structured updates and corrections to registry data. It allows individuals (or field agents on their behalf) to raise claims—such as correcting personal information, adding missing household members, or changing socioeconomic details. These claims go through a formal verification and attestation process before the core registry is updated.

This helps maintain a balance between community-sourced data corrections and governance-driven data validation.

***

### 1. Key Concepts

* **Claim**: A request raised by a user to change or add to the registry data.
* **Attestation**: The official validation of a claim by an authorized attestor (usually a government official).
* **Evidence**: Supporting documents or attachments uploaded with a claim to support its validity.
* **Trust level**: A qualitative marker assigned to a claim after attestation, indicating the reliability of the data.
* **Re-attestation**: Revalidation of data that has a limited validity or expired trust window.
* **Revocation**: The ability to retract or invalidate previously attested claims if they are found incorrect.
* **Appeals**: Mechanism for claimants to challenge a rejected or revoked claim.

***

### 2. Actors and Roles

| Role                    | Description                                                                                                                                        |
| ----------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Claimant**            | The person who initiates the claim. This could be the individual themselves, a member of their household, or an enumerator acting on their behalf. |
| **Attestor**            | The user or official responsible for reviewing, validating, and approving or rejecting the claim.                                                  |
| **Administrator**       | Manages claim types, trust level settings, and user access control.                                                                                |
| **Verifier (optional)** | A system or external body responsible for checking evidence or integrating external validations.                                                   |

***

### 3. Claim Lifecycle

A claim typically progresses through the following stages:

1. **Draft** – Initial stage where the claim is being prepared.
2. **Submitted** – Claim is submitted for review.
3. **Under review** – Claim is picked up by an attestor or routed automatically.
4. **Approved** – Claim is validated and applied to the registry.
5. **Rejected** – Claim is invalidated due to insufficient evidence, incorrect data, or policy violations.
6. **Expired** – Claims with time-bound trust levels may require re-attestation after expiry.
7. **Revoked** – Approved claims may be later revoked upon audit, appeal, or further investigation.

***

### 4. Supported Features

#### Evidence attachment support

Users can upload documents, photos, or scanned IDs to support their claim. This may be mandatory or optional based on the claim type.

#### Trust level assignment&#x20;

After attestation, a trust level like _Low_, _Medium_, or _High_ can be assigned to the claim to reflect its credibility.

#### Claim expiry and re-attestation

Some claims may have expiry durations (e.g., temporary disability status). These claims must be re-attested after their validity period ends.

#### Appeals and feedback workflow

Claimants can raise an appeal or submit feedback on a rejected claim. The appeal goes through a secondary review process.

#### Claim revocation registry

All revoked claims are stored in a separate registry for audit and governance purposes. The reason for revocation and who performed the action is logged.

***

### 5. Permissions and access control

Permissions are defined per role. Key access controls include:

* Claimants can create and view the status of their own claims.
* Attestors can view, review, and change the status of assigned claims.
* Admins can manage claim types, expiry configurations, trust level options, and revocation rules.

***

### 6. Configurations and extensions

* **Claim types**: Configurable per registry entity (individual, household, etc.) with optional fields for attachments and expected verification steps.
* **Trust levels**: Configured as labels (e.g., "Community Verified", "Digitally Verified") and do not use numerical scoring.
* **Claim expiry durations**: Defined per claim type (e.g., 180 days).
* **Re-attestation rules**: Allow automatic alerts or assignment after expiry.
* **Appeals workflow**: Optional and can be enabled per deployment.
* **Audit logs**: Maintained for each claim and its transitions.

***

### 7. Integration with registry

Approved claims trigger updates to the Social Registry models (`individual`, `household`, etc.) based on configured mappings. All claims are logged with references to:

* The entity being updated
* The claim data
* The attestation result and metadata
* Any documents attached

Rejections and revocations are non-destructive to registry data, but are logged for governance.

***

