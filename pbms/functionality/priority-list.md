---
description: Work In Progress
---

# Priority List

## Overview

In the context of OpenG2P, prioritization is a critical feature designed to ensure that the most eligible or vulnerable beneficiaries are addressed during disbursement cycles. Given the diverse socioeconomic and demographic contexts in which OpenG2P operates, the priority list serves as a dynamic tool that allows program managers to target beneficiaries based on predefined rules or ranking criteria.

The priority list functionality is integrated into the program and cycle management process, enabling flexibility while maintaining transparency and auditability. This document outlines the purpose, configuration, and workflow of the priority list feature, detailing its role in streamlining disbursement processes and ensuring efficient resource allocation.



## Key concepts and definitions

• **Priority list**: A ranked or filtered list of beneficiaries.

• **Rank-based criteria**: Ranking on scoring mechanisms like PMT, FSS, etc.

• **Inclusion limits**: Fixed rules for restricting beneficiaries in a priority list.



## Key Features

**Program-level default configuration**

* Define default priority rules at the program level to ensure consistency across disbursement cycles.
* Configure ranking methods, inclusion limits, and approval requirements as part of the program setup.

**Cycle-specific overrides**

* Modify the default priority configuration during cycle creation to address specific disbursement requirements.
* Ensure flexibility while maintaining a clear audit trail of adjustments.

**Rank-based prioritization**

* Automatically rank beneficiaries based on predefined criteria such as PMT scores, vulnerability indices, or multi-criteria evaluations.
* Supports weighted scoring for multi-dimensional prioritization.

**Configurable inclusion limits**

* Limit the number of beneficiaries included in a cycle based on:
* Fixed numbers.
* Specific rank thresholds.
* Financial caps for the cycle.

**Approval workflow**

* Enable optional manual approval of priority lists before beneficiaries are finalized for entitlement preparation.
* Provides an additional layer of governance to ensure the correctness of the prioritization process.

**Dynamic configuration during cycle creation**

* Provide users with a popup interface during cycle creation to review and update priority configurations.
* Allow for real-time adjustments to accommodate specific disbursement needs.

**Transparency and traceability**

* Store cycle-specific priority configurations and beneficiary ranks for auditability



## Work flow

### Program creation

Purpose: Set up foundational configurations for the program, including whether priority lists are used.

#### Steps:

1. **Define priority list usage:**

* Is disbursement through a priority list enabled for this program? (Yes/No).

2. **Configure default priority rules:**

* Priority type:
  * _Condition-based_: E.g., Age above 65, geography, vulnerability index.
  * _Rank-based_: Assign ranks using PMT, FSS, or multi-criteria evaluation.
* Inclusion limit:
  * Fixed number of beneficiaries.
  * Financial cap.
  * Rank threshold.
* Approval requirement: Is manual approval of the priority list required before entitlements?

3. **Save program**  **configuration**:

* These settings act as defaults for all cycles within the program.

### Cycle process (from initiation to disbursement)

Purpose: Execute the recurring process of creating a cycle, applying priority rules, and completing disbursement.

**Steps**:

1. **Cycle initiation**

* Start a new cycle under the program.
* Present the user with the default program-level configuration for the priority list.
* Allow modifications specific to the cycle:
* Update priority criteria, scoring methods, or inclusion limits.
* Save as a cycle-specific configuration for auditability.

2. **Priority list creation**

* Apply the priority logic to generate a list of eligible beneficiaries:
* Condition-Based Priority: Filter based on static conditions (e.g., age, geography).
* Rank-Based Priority: Rank beneficiaries using the selected scoring methods or criteria.
* Apply inclusion limits:
* Select beneficiaries based on top N, financial cap, or rank threshold.

3. **Approval of priority list (if required)**

* Submit the priority list for review.
* Ensure manual approval is completed before proceeding.

4. **Beneficiary assignment to cycle**

* Copy approved beneficiaries to the cycle.
* These beneficiaries proceed to the entitlement preparation stage.

5. &#x20;**Entitlement preparation and approval**

* Generate entitlements for cycle beneficiaries.
* Approve entitlements as per program-specific workflows.

6. **Disbursement**

* Prepare payments for approved entitlements.
* Approve payments manually.
* Disburse payments to beneficiaries.\


{% embed url="https://miro.com/app/board/uXjVLwhMvMU=/?share_link_id=131444890620" %}

