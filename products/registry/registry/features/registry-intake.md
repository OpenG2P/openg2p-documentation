---
description: >-
  Registry Intake is a key mechanism for creating and onboarding records into
  the registry.
---

# Registry Intake

The intake layer is used a **JSON-configured form widgets** that dynamically assembles forms at runtime, eliminating the need for hardcoded forms for each register type.

### 1. Intake Overview & Process

Registry Intake defines the lifecycle through which a record is **created, verified, processed, and stored** in the system.

#### Intake Lifecycle

```mermaid
stateDiagram-v2
    [*] --> SelectRegister

    SelectRegister --> NewForm : Select Register for Intake

    NewForm --> SaveDraft : Fill Form & Save Draft
    SaveDraft --> SaveDraft : Edit & Save Draft
    SaveDraft --> Submit : Submit Form

    Submit --> Verification : Submission Created

    Verification --> Rejected : Reject Submission
    Verification --> Approved : Approve Submission

    Approved --> CR_Pending : Change Request Created (PENDING)

    CR_Pending --> CR_Processing : Start Processing
    CR_Processing --> CR_Processed : Processing Successful
    CR_Processing --> CR_Failed : Processing Failed

    CR_Failed --> CR_Processing : Retry (max 5 times)

    CR_Processed --> Completed_Success : Completed Successfully
    CR_Failed --> Completed_Failed : Failed after 5 retries

    Completed_Success --> Registry : Record Stored
```

***

### Key Stages in Intake Form Lifecycle

#### Draft Stage

* Form is created or edited
* Users can save and update multiple times
* Each submission is assigned an **Application Reference** and **Submission id**
* **Status:** `intake_form_status = DRAFT`

#### Submission Stage

* Form is finalized and submitted
* No further edits are allowed
* A submission record is created
* **Status:** `intake_form_status = FINAL`

#### Verification and Approval Stage

* Multiple verification steps can be performed based on configuration
* Final decision is made after all verifications
* **Status:** `approval_status`
  * `PENDING` → Awaiting review
  * `APPROVED` → Approved
  * `REJECTED` → Rejected (flow ends)

#### Change Request Stage

* Triggered after approval for backend processing
* **Status:** `change_request_submission_status`
  * `NOT_APPLICABLE` → Not submitted or not approved
  * `PENDING` → Ready for processing
  * `PROCESSING` → In progress
  * `PROCESSED` → Successfully processed
  * `FAILED` → Failed after retries

#### Completion Stage

* Final outcome of the process:
  * **Success** → Record stored in registry
  * **Failure** → Processing failed after retries

***

### After approval, and the dashboard

* **After the last approval** the record is created in the background, about a minute later (Celery), and a register with generated IDs gets the record's ID about a minute after that. Until then the record does not appear in its register, and then shows a temporary `TEMP-…` ID. A new record raises no change request: change requests are for edits to existing records.
* **The dashboard's Form Submissions card** counts all submissions, then drafts and finalized ones awaiting approval. An approved or rejected submission counts in the total only, so `1` with `0` pending and `0` draft means one submission, already decided.
* **The dashboard's register counts** (active records) are cached for 10 minutes, so a new record can take that long to show there. The register's own list is always current. The cache is there because the counts are a full count of every register's active records, cut down to each user's data policies, on every dashboard load: on a register of hundreds of thousands of records that takes seconds. Users with the same data policies share one cached result. To change the time, set `REGISTRY_STAFF_PORTAL_API_CACHE_SUMMARY_EXPIRES_IN_SECONDS` on the staff API (`registry.staffApi.envVars` in a values file), in seconds. A short time costs that count on more loads.

### 2. Configure Intake Form Using Configuration Page

#### Step 2.1: Select Register

* Select the target register for which the intake form will be configured

#### Step 2.2: Create Intake Form

* Add a new **Intake Form Tab**
* Provide form details such as name and description

#### Step 2.3: Create Sections within the Intake Form

* Add multiple sections under the intake form tab

**Important:**

* One section must be marked as the primary and core section
  * `is_core_section = true`
  * `is_primary = true`
* Remaining sections should be non-primary

#### Step 2.4: Configure UI Schema

* Define and update the [UI Schema](https://github.com/OpenG2P/registry-platform/tree/develop/ui/ui-widgets/UISchema.json) for each section

This controls:

* Field layout
* Input types
* Rendering behavior

#### Step 2.5: View and Fill Form

* Open the configured intake form
* Verify:
  * Sections render correctly
  * Fields behave as expected
* Fill and test the form end-to-end

***
