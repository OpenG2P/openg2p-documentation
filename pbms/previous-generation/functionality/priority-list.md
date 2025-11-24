---
description: Work In Progress
---

# Priority List

## Overview

In the context of OpenG2P, prioritization is a critical feature designed to ensure that the most eligible or vulnerable beneficiaries are addressed during disbursement cycles. Given the diverse socioeconomic and demographic contexts in which OpenG2P operates, the priority list serves as a dynamic tool that allows program managers to target beneficiaries based on predefined rules and ranking criteria.

The priority list functionality is integrated into the program and cycle management process, enabling flexibility while maintaining transparency and auditability. This document outlines the purpose, configuration, and workflow of the priority list feature, detailing its role in streamlining disbursement processes and ensuring efficient resource allocation.



## Key concepts and definitions

• **Priority list**: A filtered and ranked list of beneficiaries.

• **Eligibility and Ranking**:&#x20;

* Beneficiaries are filtered based on selected eligibility domain and then ranked according to selected sorting order criteria

• **Inclusion limits**: Fixed number of beneficiaries.

## Key Features

**Program-level default configuration**

* Define default priority rules at the program level to ensure consistency across disbursement cycles.
* Configure eligibility and ranking methods, inclusion limits as part of the program setup.

**Cycle-specific overrides**

* Modify the default priority configuration during cycle creation to address specific disbursement requirements.
* Ensure flexibility while maintaining a clear audit trail of adjustments.

**Eligibility and Ranking**

* Filter beneficiaries based on the cycle configuration, which includes conditions such as age, geography, and vulnerability index, then rank them using PMT, FSS, or multi-criteria evaluation.

**Configurable inclusion limits**

* Limit the number of beneficiaries included in a cycle based on:&#x20;
* Fixed numbers.

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

* Eligibility:
  * Beneficiaries are filtered based on conditions like age above 65, geography, and vulnerability index.
* Ranking
  * Assign ranks using PMT, FSS, or multi-criteria evaluation. Sorting can be applied in ascending or descending order, depending on program requirements.
* Inclusion limit:
  * Fixed number of beneficiaries.

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
* Eligibility: Filter based on static conditions (e.g., age, geography).
* Ranking: Rank beneficiaries using the selected scoring methods or criteria.
* Apply inclusion limits:
* Select beneficiaries based on top N.

3. **Beneficiary assignment to cycle**

* Copy approved beneficiaries to the cycle.
* These beneficiaries proceed to the entitlement preparation stage.

5. &#x20;**Entitlement preparation and approval**

* Generate entitlements for cycle beneficiaries.
* Approve entitlements as per program-specific workflows.

6. **Disbursement**

* Prepare payments for approved entitlements.
* Approve payments manually.
* Disburse payments to beneficiaries.<br>

{% embed url="https://miro.com/app/board/uXjVLwhMvMU=/?share_link_id=131444890620" %}

