---
description: Workflow for Enrolment & Disbursement Cycles
---

# Workflow design

## PBMS Workflow Design Document

Both Enrolment & Disbursement cycles have a Workflow definition attached to them. The Lists created under these cycles go through the workflow stages for seeking approvals from various stakeholders.

### Model Structures

#### g2p\_workflow\_stage\_definition

<table><thead><tr><th width="215.4854736328125">Field</th><th width="175.69677734375">Data Type</th><th width="201.2332763671875">Constraints</th><th>Description</th></tr></thead><tbody><tr><td>stage_id</td><td>String/UUID</td><td>Primary Key</td><td>Unique identifier for workflow stage</td></tr><tr><td>program_id</td><td>String/UUID</td><td>Index</td><td>References program</td></tr><tr><td>cycle_type</td><td>Enum</td><td>ENROLMENT, DISBURSEMENT</td><td>Type of cycle workflow</td></tr><tr><td>stage_number</td><td>Integer</td><td></td><td>Sequential stage number</td></tr><tr><td>stage_name</td><td>String</td><td></td><td>Name of the stage</td></tr><tr><td>is_final_stage</td><td>Boolean</td><td></td><td>True if highest stage_number for this program/cycle_type</td></tr><tr><td>group_id</td><td>Many2one (res.groups)</td><td></td><td>The Odoo security group authorized to act on this stage</td></tr><tr><td></td><td></td><td><strong>Unique</strong>: (program_id, cycle_type, stage_number)</td><td></td></tr></tbody></table>

#### g2p\_beneficiary\_list

<table><thead><tr><th width="212.14715576171875">Field</th><th width="178.47369384765625">Data Type</th><th width="201.919189453125">Constraints</th><th>Description</th></tr></thead><tbody><tr><td>list_id</td><td>String/UUID</td><td>Primary Key</td><td>Unique identifier for beneficiary list</td></tr><tr><td>cycle_id</td><td>String/UUID</td><td>Foreign Key</td><td>References cycle</td></tr><tr><td>list_number</td><td>Integer</td><td></td><td>Sequential integer for list versions (New field)</td></tr><tr><td>latest_stage_history_id</td><td>String/UUID</td><td>Foreign Key</td><td>References most recent stage_history record</td></tr><tr><td>number_of_beneficiaries</td><td>Integer</td><td></td><td>Total count of beneficiaries</td></tr><tr><td>disbursement_quantity</td><td>JSON</td><td></td><td>Disbursement details (Disbursement cycles only)</td></tr><tr><td></td><td></td><td><strong>Relationship</strong>: One cycle → one operating list at any time</td><td></td></tr></tbody></table>

#### g2p\_workflow\_stage\_history

<table><thead><tr><th width="211.00933837890625">Field</th><th width="178.3089599609375">Data Type</th><th width="207.4267578125">Constraints</th><th>Description</th></tr></thead><tbody><tr><td>stage_history_id</td><td>String/UUID</td><td>Primary Key</td><td>Unique identifier for stage history record</td></tr><tr><td>list_id</td><td>String/UUID</td><td>Index, Foreign Key</td><td>References beneficiary_list</td></tr><tr><td>list_type</td><td>Enum</td><td>ENROLMENT, DISBURSEMENT</td><td>Type of list</td></tr><tr><td>stage_id</td><td>String/UUID</td><td>Foreign Key</td><td>References workflow_definition stage</td></tr><tr><td>enqueued_at</td><td>Timestamp</td><td></td><td>When list was queued at this stage</td></tr><tr><td>status</td><td>Enum</td><td>PENDING, APPROVED, REJECTED</td><td>Current approval status</td></tr><tr><td>acted_by</td><td>String/UUID</td><td></td><td>User who performed the action</td></tr><tr><td>acted_at</td><td>Timestamp</td><td></td><td>When action was performed</td></tr><tr><td>Remarks</td><td>Text</td><td></td><td>Comments or rejection reason</td></tr><tr><td></td><td></td><td><strong>Unique</strong>: (list_id, stage_id)</td><td>Each list can only have one record per stage</td></tr></tbody></table>

#### g2p\_workflow\_pending\_stage

<table><thead><tr><th width="211.79998779296875">Field</th><th width="174.87646484375">Data Type</th><th width="214.070556640625">Constraints</th><th>Description</th></tr></thead><tbody><tr><td>list_id</td><td>String/UUID</td><td>Primary Key</td><td>References beneficiary_list</td></tr><tr><td>current_stage_id</td><td>String/UUID</td><td>Index, Foreign Key</td><td>References workflow_definition stage</td></tr><tr><td>enqueued_at</td><td>Timestamp</td><td></td><td>When list entered current stage</td></tr><tr><td>stage_status</td><td>Enum</td><td>PENDING</td><td>Status (always PENDING while in this table)</td></tr></tbody></table>

#### g2p\_enrolment\_cycle

<table><thead><tr><th width="210.400390625">Field</th><th width="177.8212890625">Data Type</th><th width="215.408203125">Constraints</th><th>Description</th></tr></thead><tbody><tr><td>cycle_id</td><td>String/UUID</td><td>Primary Key</td><td>Unique identifier for cycle</td></tr><tr><td>program_id</td><td>String/UUID</td><td>Foreign Key</td><td>References progra</td></tr><tr><td>cycle_number</td><td>Integer</td><td></td><td>Sequence number within program</td></tr><tr><td>created_on</td><td>Timestamp</td><td></td><td>When cycle was created</td></tr><tr><td>created_by</td><td>String/UUID</td><td></td><td>User who created the cycle</td></tr><tr><td>latest_list_id</td><td>String/UUID</td><td>Foreign Key</td><td>References latest beneficiary_list (New field)</td></tr><tr><td>number_of_lists</td><td>Integer</td><td></td><td>Count of all list versions</td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td></tr></tbody></table>

#### g2p\_disbursement\_cycle

<table><thead><tr><th width="210.400390625">Field</th><th width="177.8212890625">Data Type</th><th width="215.408203125">Constraints</th><th>Description</th></tr></thead><tbody><tr><td>cycle_id</td><td>String/UUID</td><td>Primary Key</td><td>Unique identifier for cycle</td></tr><tr><td>program_id</td><td>String/UUID</td><td>Foreign Key</td><td>References program</td></tr><tr><td>cycle_number</td><td>Integer</td><td></td><td>Sequence number within program</td></tr><tr><td>created_on</td><td>Timestamp</td><td></td><td>When cycle was created</td></tr><tr><td>created_by</td><td>String/UUID</td><td></td><td>User who created the cycle</td></tr><tr><td>latest_list_id</td><td>String/UUID</td><td>Foreign Key</td><td>References latest beneficiary_list (New field)</td></tr><tr><td>number_of_lists</td><td>Integer</td><td></td><td>Count of all list versions</td></tr></tbody></table>



#### g2p\_program\_metrics (New Model)

| Field                      | Data Type   | Constraints | Description                           |
| -------------------------- | ----------- | ----------- | ------------------------------------- |
| program\_id                | String/UUID | Primary Key | References program                    |
| enrolment\_cycle\_count    | Integer     |             | Total enrolment cycles for program    |
| disbursement\_cycle\_count | Integer     |             | Total disbursement cycles for program |

***

### Enrolment Workflow

#### Flow Overview

1. Create Cycle →&#x20;
2. Create 1 List that moves to Stage-1
3. List progresses through defined stages (Stage-1, Stage-2, ... Stage-N)
4. At each stage, list is queued for approval by role-based users
5. At each stage: PENDING → (APPROVED or REJECTED)
6. If APPROVED → moves to next stage
7. If REJECTED → user must create a new List version
8. Final stage approval = Cycle approved (no further actions allowed)

#### Stage Progression

* List has `latest_stage_history_id` stored within it
* Each stage creates a `beneficiary_list_stage_history` record
* Workflow is driven by stage definition and role-based approvals
* Once final stage is approved, the entire cycle is locked

#### Key Rules

* A cycle cannot be modified after approval
* Rejection at any stage requires new list creation
* List versions are tracked as versions in UI (only latest displayed)
* Previous versions accessible in separate tab

***

### Disbursement Workflow

#### Flow Overview

1. Create Cycle
2. Create 1 List that moves to Stage-1
3. List progresses through defined stages with disbursement-specific data
4. At each stage: PENDING → (APPROVED or REJECTED)
5. If APPROVED → moves to next stage with entitlement computation
6. If REJECTED → user must create a new List version
7. Final stage approval = Cycle approved with disbursement locked

#### Disbursement-Specific Fields

* `number_of_beneficiaries`
* `disbursement_quantity` (JSON format, first item displayed)
* `Total Entitlements` (computed at stage approval)

#### Bridge & Dispatch Elements (Final Approved List Only)

* Envelopes
* Batches
* Dispatch tracking

#### Key Rules

* Same stage progression model as Enrolment
* Entitlements computed during approval workflow
* Bridge and dispatch tables only appear for approved disbursement cycles
* Multiple batch control available for envelope distribution

***

### Enrolment Cycle View

#### List of Cycles Display

**Columns**: Cycle #, Created on, Stage, Status, # of Versions, # of Beneficiaries, Acted on

**Data Source**: cycle.latest\_list\_id → latest\_list\_id.latest\_stage\_history\_id

#### Cycle Detail View (Single Cycle)

**Cycle Section**:

* Enrolment (Cycle Type)
* Created on
* Created by

**Workflow Section**:

* Stage (Current)
* Status (PENDING, APPROVED, REJECTED)
* Queued date

**Beneficiaries Section**:

* Resolution status
* Number of Beneficiaries
* Search capability

#### Detail Tabs

1. **Statistics**: Key metrics
2. **Beneficiaries Tab**:
   * Search beneficiaries
   * View all beneficiaries in current list
3. **Approval History**:
   * Stage History of Current Latest List
4. **Previous Versions**:
   * List of Lists (excluding latest)
   * Stage History of each list (expanded view without context switching)

#### Status Logic

* If Approved & no further stages → Cycle is fully approved
* If Rejected → User must create new list
* If Pending → Awaiting action

***

### Disbursement Cycle View

#### List of Cycles Display

**Columns**: Cycle #, Created on, Stage, # of Versions, # of Beneficiaries, Disbursement Amount, Stage Status, Acted on

**Data Source**: cycle.latest\_list\_id → latest\_list\_id.latest\_stage\_history\_id

#### Cycle Detail View (Single Cycle)

**Cycle Section**:

* Disbursement (Cycle Type)
* Created on
* Created by

**Workflow Section**:

* Stage (Current)
* Status (PENDING, APPROVED, REJECTED)
* Queued date

**Beneficiaries Section**:

* Resolution status
* Number of Beneficiaries
* Search capability

**Entitlements Section**:

* Computation status
* Total Entitlements
* Product Code: Quantity, Unit

**Bridge Section** (Approved Cycle Only):

* Dispatch status
* Number of Envelopes
* Number of Batches

#### Detail Tabs

1. **Statistics**: Key metrics
2. **Beneficiaries Tab**:
   * Search beneficiaries
   * View all beneficiaries
3. **Approval Log**:
   * Stage History of Current Latest List
4. **Previous Versions**:
   * List of Lists (excluding latest)
   * Stage History of each list (expanded view)
5. **Envelopes** (Approved Cycle Only):
   * Envelope distribution details
6. **Batch Control** (Approved Cycle Only):
   * Batch management for approved disbursement

***

### Approval Queue View

#### Queue Filter Logic

1. Retrieve current user's roles
2. Get all workflow stage IDs for those roles
3. Display all `beneficiary_list_pending_stage` items matching those stage\_ids

#### List Display

**Columns**: Program Mnemonic, Cycle #, Enrolment/Disbursement, Current Stage, Current Version, Queued Date, # of Beneficiaries

#### Detail View (From Queue)

**Program Section**:

* Program Mnemonic
* Program Description

**Cycle Section**:

* Enrolment/Disbursement (Type)
* Cycle Number
* Created on
* Created by

**Workflow Section**:

* Version (Current)
* Stage (Current)
* Status (PENDING, APPROVED, REJECTED)

**Beneficiaries Section**:

* Number of Beneficiaries
* Search capability

**Entitlements Section** (Disbursement Only):

* Entitlements List
* Product Code: Quantity, Unit

#### Detail Tabs

1. **Statistics**: Custom view
2. **Beneficiaries**: Search and view
3. **Approval History**:
   * Stage History of Current Latest List
4. **Previous Versions**:
   * List of Lists (excluding latest)
   * Stage History of each list (expanded)

***

### Fundamental Concepts

* A cycle has only 1 operating list at any point in time
* Cycle workflow status is synonymous with the operating list's status
* Lists are treated as versions in the UI
* Only the current operating list is displayed prominently
* Previous lists (versions) are accessible in a separate tab
* Cycle → latest\_list\_id → List → latest\_stage\_history\_id → Stage History
* This chain allows complete cycle visibility across all states
