---
description: Intake forms for Register
---

# Intake Forms

***

### 1. Overview

This document details the architectural changes to decouple sections from tabs, restructure intake form handling, and implement deduplication logic. The changes enable sections to be reusable across tabs and intake forms, while establishing a complete intake form lifecycle separate from change requests.

***

### 2. Model Changes

#### 2.1 Register UI Structure Changes

| Model Name                     | Current State                                                  | Proposed State                                        | Change Type  |
| ------------------------------ | -------------------------------------------------------------- | ----------------------------------------------------- | ------------ |
| `g2p_register_ui_tabs`         | Tab definition table                                           | Remains unchanged (tab definitions)                   | No Change    |
| `g2p_register_sections`        | Sections coupled with tabs; Section definition + Tab reference | Sections decoupled from tabs; Section definition only | Major Change |
| `g2p_register_ui_tab_sections` | **Does not exist**                                             | New junction table: Tab ID ↔ Section ID mapping       | New Table    |

#### 2.2 Register Sections Model Details

**Table:** `g2p_register_section`

| Field                | Type      | Constraint       | Notes                                     |
| -------------------- | --------- | ---------------- | ----------------------------------------- |
| section\_id          | UUID      | PRIMARY KEY      | Unique section identifier                 |
| register\_id         | UUID      | NON UNIQUE INDEX | Register reference                        |
| section\_mnemonic    | STRING    | UNIQUE           | Section identifier name                   |
| section\_label       | STRING    | -                | Display label                             |
| section\_description | STRING    | -                | Description                               |
| is\_list             | BOOLEAN   | -                | Whether section contains multiple records |
| created\_at          | TIMESTAMP | -                | Creation timestamp                        |
| updated\_at          | TIMESTAMP | -                | Last update timestamp                     |

**Changes from current model:**

* Remove `tab_id` foreign key
* Add `section_mnemonic` as unique identifier
* Section now exists independently of any tab

#### 2.3 Register UI Tab Sections Model (New)

**Table:** `g2p_register_ui_tab_sections`

| Field            | Type      | Constraint       | Notes                                |
| ---------------- | --------- | ---------------- | ------------------------------------ |
| tab\_section\_id | UUID      | PRIMARY KEY      | Junction record ID                   |
| tab\_id          | UUID      | NON UNIQUE INDEX | Reference to g2p\_register\_ui\_tabs |
| section\_id      | UUID      | NON UNIQUE INDEX | Reference to g2p\_register\_section  |
| section\_order   | INTEGER   | -                | Display order within tab             |
| created\_at      | TIMESTAMP | -                | Creation timestamp                   |
| updated\_at      | TIMESTAMP | -                | Last update timestamp                |

**Purpose:** Explicit many-to-many mapping between tabs and sections, allowing sections to be reused across tabs.

***

### 3. Intake Form Models

#### 3.1 Intake Form Metadata Models

**Table:** `g2p_intake_form_definitions`

| Field                                | Type      | Constraint       | Notes                                                  |
| ------------------------------------ | --------- | ---------------- | ------------------------------------------------------ |
| form\_id                             | UUID      | PRIMARY KEY      | Unique form identifier                                 |
| register\_id                         | UUID      | NON UNIQUE INDEX | Associated register                                    |
| form\_mnemonic                       | STRING    | UNIQUE           | Form identifier name                                   |
| form\_description                    | STRING    | -                | Form description                                       |
| number\_of\_verifications            | INTEGER   | -                | Required verification count                            |
| used\_only\_for\_ingestion\_pipeline | BOOLEAN   | -                | TRUE: ingestion only; FALSE: manual submission allowed |
| created\_at                          | TIMESTAMP | -                | Creation timestamp                                     |
| updated\_at                          | TIMESTAMP | -                | Last update timestamp                                  |

**Table:** `g2p_intake_form_ui_tabs`

| Field       | Type      | Constraint       | Notes                  |
| ----------- | --------- | ---------------- | ---------------------- |
| tab\_id     | UUID      | PRIMARY KEY      | Unique tab identifier  |
| form\_id    | UUID      | NON UNIQUE INDEX | Associated intake form |
| tab\_label  | STRING    | -                | Tab display label      |
| tab\_order  | INTEGER   | -                | Display order          |
| created\_at | TIMESTAMP | -                | Creation timestamp     |
| updated\_at | TIMESTAMP | -                | Last update timestamp  |

**Table:** `g2p_intake_form_ui_tab_sections`

| Field            | Type      | Constraint       | Notes                                    |
| ---------------- | --------- | ---------------- | ---------------------------------------- |
| tab\_section\_id | UUID      | PRIMARY KEY      | Junction record ID                       |
| tab\_id          | UUID      | NON UNIQUE INDEX | Reference to g2p\_intake\_form\_ui\_tabs |
| section\_id      | UUID      | NON UNIQUE INDEX | Reference to g2p\_register\_section      |
| section\_order   | INTEGER   | -                | Display order within tab                 |
| created\_at      | TIMESTAMP | -                | Creation timestamp                       |
| updated\_at      | TIMESTAMP | -                | Last update timestamp                    |

**Relationship:** Intake form tabs use the same sections (`g2p_register_section`) as register tabs, enabling section reuse.

#### 3.2 Intake Form Submission Model

**Table:** `g2p_intake_form_submission`

| Field                                            | Type      | Constraint       | Notes                                               |
| ------------------------------------------------ | --------- | ---------------- | --------------------------------------------------- |
| submission\_id                                   | UUID      | PRIMARY KEY      | Unique submission identifier                        |
| form\_id                                         | UUID      | NON UNIQUE INDEX | Associated form                                     |
| register\_id                                     | UUID      | NON UNIQUE INDEX | Associated register                                 |
| draft\_status                                    | ENUM      | -                | DRAFT, FINAL                                        |
| approval\_status                                 | ENUM      | -                | PENDING, APPROVED, REJECTED                         |
| approved\_by                                     | UUID      | -                | User who approved                                   |
| approved\_at                                     | TIMESTAMP | -                | Approval timestamp                                  |
| finalized\_at                                    | TIMESTAMP | -                | Finalization timestamp                              |
| first\_created\_at                               | TIMESTAMP | -                | Initial creation timestamp                          |
| last\_updated\_at                                | TIMESTAMP | -                | Last update timestamp                               |
| created\_by                                      | UUID      | -                | User who created                                    |
| submission\_source                               | ENUM      | -                | BENE\_PORTAL, AGENT\_PORTAL, STAFF\_PORTAL, PARTNER |
| partner\_id                                      | UUID      | NON UNIQUE INDEX | Partner reference (if applicable)                   |
| register\_ingest\_process\_status                | ENUM      | -                | PENDING, PROCESSED, NOT\_APPLICABLE                 |
| register\_ingest\_processed\_timestamp           | TIMESTAMP | -                | Ingest completion timestamp                         |
| register\_ingest\_process\_attempts              | INTEGER   | -                | Ingest attempt count                                |
| register\_ingest\_process\_last\_error\_code     | STRING    | -                | Last ingest error                                   |
| number\_of\_verifications\_required              | INTEGER   | -                | Required verification count                         |
| number\_of\_verifications\_done                  | INTEGER   | -                | Completed verifications                             |
| deduplication\_status\_vs\_intake\_forms         | ENUM      | -                | PENDING, PROCESSED, FAILED                          |
| deduplication\_intake\_forms\_process\_timestamp | TIMESTAMP | -                | Dedup completion                                    |
| deduplication\_intake\_forms\_attempts           | INTEGER   | -                | Dedup attempt count                                 |
| deduplication\_intake\_forms\_error              | STRING    | -                | Dedup error message                                 |
| deduplication\_status\_vs\_register              | ENUM      | -                | PENDING, PROCESSED, FAILED                          |
| deduplication\_register\_process\_timestamp      | TIMESTAMP | -                | Register dedup completion                           |
| deduplication\_register\_attempts                | INTEGER   | -                | Register dedup attempt count                        |
| deduplication\_register\_error                   | STRING    | -                | Register dedup error message                        |

#### 3.3 Deduplication Results Models (New)

**Table:** `g2p_dedup_results_intake_forms_vs_intake_forms`

| Field                     | Type      | Constraint       | Notes                          |
| ------------------------- | --------- | ---------------- | ------------------------------ |
| dedup\_result\_id         | UUID      | PRIMARY KEY      | Result identifier              |
| submission\_id            | UUID      | NON UNIQUE INDEX | Submission being deduplicated  |
| duplicate\_submission\_id | UUID      | NON UNIQUE INDEX | Potential duplicate submission |
| match\_score              | DECIMAL   | -                | Match confidence (0.0-1.0)     |
| match\_fields             | JSONB     | -                | Fields that matched            |
| created\_at               | TIMESTAMP | -                | Creation timestamp             |

**Table:** `g2p_dedup_results_intake_forms_vs_register`

| Field                   | Type      | Constraint       | Notes                           |
| ----------------------- | --------- | ---------------- | ------------------------------- |
| dedup\_result\_id       | UUID      | PRIMARY KEY      | Result identifier               |
| submission\_id          | UUID      | NON UNIQUE INDEX | Submission being deduplicated   |
| register\_record\_id    | UUID      | NON UNIQUE INDEX | Potential duplicate in register |
| register\_section\_name | STRING    | -                | Register section name           |
| match\_score            | DECIMAL   | -                | Match confidence (0.0-1.0)      |
| match\_fields           | JSONB     | -                | Fields that matched             |
| created\_at             | TIMESTAMP | -                | Creation timestamp              |

***

### 4. Extension Model Hierarchy

#### 4.1 Domain-Specific Classes

All domain manifestations (e.g., Farmer Registry) follow this pattern:

**Base Structure (Core Repository):**

```
g2p_register_{domain}
g2p_register_history_{domain}
```

**Extension Structure (Extensions Repository):**

```
G2PRegister{Domain} extends SQLAlchemy Base
G2PRegisterHistory{Domain} extends SQLAlchemy Base
G2PIntakeForm{Domain} extends G2PRegister{Domain} and G2PIntakeForm
```

**Example - Farmer Domain:**

* Location: `farmer_extension.register_domain.farmer.py`
* Classes:
  * `G2PRegisterFarmer` (table: `g2p_register_farmer`)
  * `G2PRegisterHistoryFarmer` (table: `g2p_register_history_farmer`)
  * `G2PIntakeFormFarmer` (extends both `G2PRegisterFarmer` and `G2PIntakeForm`)

**Applied to all domain registers and tables.**

***

### 5. Existing Code Flow

#### 5.1 Register Tabs and Sections Retrieval

**Current Flow:**

```
API Request: GET /register/{register_id}/tabs
├─ Retrieve g2p_register_ui_tabs where register_id = {register_id}
├─ For each tab:
│  └─ Retrieve g2p_register_sections where tab_id = tab_id
│     (Sections are coupled with tabs; cannot exist separately)
└─ Return: Tabs with nested section definitions
```

#### 5.2 Intake Form Submission - Current

**Current Flow:**

```
API Request: POST /intake-form/submit
├─ Create g2p_intake_form_submission
├─ For each section in form:
│  └─ Save section data using dynamic class resolution:
│     G2PIntakeForm{register_mnemonic}
└─ Draft saved; awaiting approval
```

#### 5.3 Intake Form Approval - Current

**Current Flow:**

```
API Request: POST /intake-form/{submission_id}/approve
├─ Set approval_status = APPROVED
├─ Set register_ingest_process_status = PENDING
└─ Emit to Celery Worker for register ingestion
```

***

### 6. Proposed Code Flow

#### 6.1 Register Tabs and Sections Retrieval

**Proposed Flow:**

```
API Request: GET /register/{register_id}/tabs
├─ Retrieve g2p_register_ui_tabs where register_id = {register_id}
├─ For each tab:
│  └─ Retrieve g2p_register_ui_tab_sections where tab_id = tab_id
│     ├─ For each tab_section:
│     │  └─ Resolve g2p_register_section where section_id = section_id
│     │     (Sections retrieved via junction table; decoupled from tabs)
│     └─ Return section definition with tab-specific order
├─ Return: Tabs with referenceable sections
└─ Sections can now be reused across multiple tabs
```

#### 6.2 Intake Form Submission - Proposed

**Proposed Flow:**

```
API Request: POST /intake-form/submit
├─ Create g2p_intake_form_submission record
│  └─ submission_id: unique identifier
│  └─ draft_status: DRAFT
│  └─ approval_status: PENDING
│  └─ register_ingest_process_status: NOT_APPLICABLE
│  └─ deduplication_status_vs_intake_forms: PENDING
│  └─ deduplication_status_vs_register: PENDING
│
├─ For each section in intake_form_definition:
│  ├─ Retrieve section_register_id from form section mapping
│  ├─ Resolve dynamic class: G2PIntakeForm{register_mnemonic}
│  ├─ If internal_record_id exists in section payload:
│  │  └─ UPDATE existing section_register record
│  ├─ Else:
│  │  └─ INSERT new section_register record
│  └─ Link to submission_id
│
└─ Return: submission_id (DRAFT saved)
```

#### 6.3 Intake Form Finalization - Proposed

**Proposed Flow:**

```
API Request: POST /intake-form/{submission_id}/finalize
├─ Set draft_status = FINAL
├─ Set finalized_at = NOW()
└─ Return: submission_id
```

#### 6.4 Intake Form Approval - Proposed

**Proposed Flow:**

```
API Request: POST /intake-form/{submission_id}/approve
├─ Set approval_status = APPROVED
├─ Set register_ingest_process_status = PENDING
├─ Set deduplication_status_vs_intake_forms = PENDING
├─ Set deduplication_status_vs_register = PENDING
├─ approved_by = current_user_id
├─ approved_at = NOW()
├─ Emit submission_id to Register-Ingest-Beat
├─ Emit submission_id to Deduplication-Intake-Forms-Beat
├─ Emit submission_id to Deduplication-Register-Beat
└─ Return: submission_id
```

#### 6.5 Intake Form Deletion - Proposed

**Proposed Flow:**

```
API Request: DELETE /intake-form/{submission_id}
├─ Retrieve form_id from submission_id
├─ Retrieve all sections for form_id from g2p_intake_form_definitions
├─ For each section:
│  ├─ Resolve section_register_id
│  ├─ Resolve dynamic class: G2PIntakeForm{register_mnemonic}
│  ├─ DELETE all records where submission_id matches
│  └─ Delete from G2PIntakeForm{register_mnemonic}
│
├─ DELETE from g2p_intake_form_submission
└─ Return: Empty response
```

#### 6.6 Intake Form Rejection - Proposed

**Proposed Flow:**

```
API Request: POST /intake-form/{submission_id}/reject
├─ Set approval_status = REJECTED
├─ Do NOT trigger ingest or deduplication processes
└─ Return: submission_id
```

#### 6.7 Intake Form Search - Proposed

**Proposed Flow:**

```
API Request: GET /intake-forms/search
├─ Input: register_id, search_text, filter_schema, pagination
├─ Resolve dynamic class: G2PIntakeForm{register_mnemonic}
├─ Execute search across all G2PIntakeForm{register_mnemonic} records
│  └─ Apply filter_schema (same as register search)
│  └─ Apply pagination
│
├─ Return: List of matching submissions
│  ├─ record_name (from G2PIntakeForm{register_mnemonic})
│  ├─ submission_id
│  ├─ form_id
│  ├─ draft_status
│  ├─ approval_status
│  ├─ register_ingest_process_status
│  └─ Deduplication status fields
│
└─ Results include metadata from g2p_intake_form_submission
```

***

### 7. Ingest Pipeline Changes

#### 7.1 Current Ingest Process

**Current State:**

```
Incoming Message
├─ Parsed with IncomingModelSemanticPattern
├─ Resolved to: REGISTER → SECTION via semantic_expression
└─ Routed to: Change Request (for edits) or Direct Register insertion (for new records)
```

#### 7.2 Proposed Ingest Process

**Proposed State:**

```
Incoming Message
├─ Parsed with IncomingModelSemanticPattern
│  └─ section_id replaced with: intake_form_id
├─ Resolved to: INTAKE_FORM via semantic_expression
│
├─ Retrieve intake_form_definition where intake_form_id = resolved_form_id
│  └─ Check: used_only_for_ingestion_pipeline = TRUE
│     (Ensures form is available only for ingest, not manual submission)
│
└─ Routed to: Intake Form Submission (marked with PARTNER source)
   ├─ submission_source = PARTNER
   ├─ register_ingest_process_status = PENDING
   └─ Created without approval (auto-approved for ingestion)
```

#### 7.3 Ingest Configuration Changes

**Table:** `IncomingModelSemanticPattern` (metadata)

| Current Field         | Proposed Field        | Change                            |
| --------------------- | --------------------- | --------------------------------- |
| `section_id`          | `intake_form_id`      | Rename and repoint to intake form |
| `register_id`         | `register_id`         | Remains unchanged                 |
| `semantic_expression` | `semantic_expression` | Unchanged logic                   |

***

### 8. Register Ingest Process (Celery)

#### 8.1 Register-Ingest-Beat

**Purpose:** Trigger register ingest for approved intake form submissions

**Schedule:** Periodic (configurable interval)

**Process:**

```
1. Query g2p_intake_form_submission:
   └─ WHERE register_ingest_process_status = PENDING
   └─ AND approval_status = APPROVED
   └─ ORDER BY approved_at ASC

2. For each submission:
   └─ Emit message to Register-Ingest-Worker
      └─ Payload: { submission_id, form_id, register_id }

3. Return: Count of submissions emitted
```

#### 8.2 Register-Ingest-Worker

**Purpose:** Insert intake form data into register tables

**Process:**

```
1. Receive submission_id

2. Retrieve g2p_intake_form_submission
   └─ Extract: form_id, register_id

3. Retrieve all sections for form_id:
   └─ Query g2p_intake_form_definitions
   └─ Get all section references (via join to section definitions)

4. For each section:
   a. Resolve section_register_id
   
   b. Resolve dynamic classes:
      ├─ G2PIntakeForm{register_mnemonic} (source)
      ├─ G2PRegister{register_mnemonic} (destination)
      └─ G2PRegisterHistory{register_mnemonic} (audit)
   
   c. Retrieve intake form records:
      └─ SELECT * FROM G2PIntakeForm{register_mnemonic}
         WHERE submission_id = {submission_id}
   
   d. For each record:
      ├─ Transform data (if needed)
      ├─ INSERT into G2PRegister{register_mnemonic}
      │  └─ Set version = V0 (initial version)
      ├─ INSERT into G2PRegisterHistory{register_mnemonic}
      │  └─ Record as creation event
      └─ Track internal_record_id mapping

5. Update submission status:
   └─ SET register_ingest_process_status = PROCESSED
   └─ SET register_ingest_processed_timestamp = NOW()
   └─ SET register_ingest_process_attempts = register_ingest_process_attempts + 1

6. On error:
   └─ SET register_ingest_process_status = PENDING (retry)
   └─ SET register_ingest_process_last_error_code = {error_code}
   └─ SET register_ingest_process_attempts = register_ingest_process_attempts + 1
   └─ If attempts > max_retries:
      └─ SET register_ingest_process_status = FAILED
```

***

### 9. Deduplication Process (Celery)

#### 9.1 Deduplication Overview

Two deduplication processes run in parallel:

1. **Intake-Forms-vs-Intake-Forms:** Check new submission against existing submissions
2. **Intake-Forms-vs-Register:** Check new submission against existing register records

#### 9.2 Deduplication-Intake-Forms-Beat

**Purpose:** Trigger deduplication of intake form submissions against other intake form submissions

**Schedule:** Periodic (configurable interval)

**Process:**

```
1. Query g2p_intake_form_submission:
   └─ WHERE deduplication_status_vs_intake_forms = PENDING
   └─ AND approval_status = APPROVED
   └─ ORDER BY approved_at ASC

2. For each submission:
   └─ Emit message to Deduplication-Intake-Forms-Worker
      └─ Payload: { submission_id, form_id, register_id }

3. Return: Count of submissions emitted
```

#### 9.3 Deduplication-Intake-Forms-Worker

**Purpose:** Find potential duplicates in other approved intake form submissions

**Process:**

```
1. Receive submission_id

2. Retrieve submission record:
   └─ Extract: register_id, form_id

3. Resolve dynamic class:
   └─ G2PIntakeForm{register_mnemonic}

4. Retrieve current submission data:
   └─ SELECT * FROM G2PIntakeForm{register_mnemonic}
      WHERE submission_id = {submission_id}

5. Define deduplication keys (configurable by domain):
   └─ Example: name, date_of_birth, phone_number

6. Query other submissions:
   └─ SELECT submission_id, * FROM G2PIntakeForm{register_mnemonic}
      WHERE register_id = {register_id}
      AND submission_id != {submission_id}
      AND approval_status = APPROVED
      AND draft_status = FINAL

7. For each other submission:
   a. Calculate match score (0.0-1.0):
      └─ Based on dedup key field matches
   
   b. If match_score >= threshold (configurable):
      └─ INSERT into g2p_dedup_results_intake_forms_vs_intake_forms
         ├─ submission_id
         ├─ duplicate_submission_id
         ├─ match_score
         ├─ match_fields (JSONB array of matched field names)
         └─ created_at

8. Update submission status:
   └─ SET deduplication_status_vs_intake_forms = PROCESSED
   └─ SET deduplication_intake_forms_process_timestamp = NOW()
   └─ SET deduplication_intake_forms_attempts = deduplication_intake_forms_attempts + 1

9. On error:
   └─ SET deduplication_status_vs_intake_forms = PENDING (retry)
   └─ SET deduplication_intake_forms_error = {error_message}
   └─ SET deduplication_intake_forms_attempts = deduplication_intake_forms_attempts + 1
   └─ If attempts > max_retries:
      └─ SET deduplication_status_vs_intake_forms = FAILED
```

#### 9.4 Deduplication-Register-Beat

**Purpose:** Trigger deduplication of intake form submissions against existing register records

**Schedule:** Periodic (configurable interval)

**Process:**

```
1. Query g2p_intake_form_submission:
   └─ WHERE deduplication_status_vs_register = PENDING
   └─ AND register_ingest_process_status = PROCESSED
   └─ ORDER BY register_ingest_processed_timestamp ASC

2. For each submission:
   └─ Emit message to Deduplication-Register-Worker
      └─ Payload: { submission_id, form_id, register_id }

3. Return: Count of submissions emitted
```

#### 9.5 Deduplication-Register-Worker

**Purpose:** Find potential duplicates in existing register records

**Process:**

```
1. Receive submission_id

2. Retrieve submission record:
   └─ Extract: register_id, form_id

3. Retrieve all sections for form_id:
   └─ Get section_register_ids

4. For each section_register_id:
   
   a. Resolve dynamic classes:
      ├─ G2PRegister{register_mnemonic} (destination for dedup)
      └─ G2PIntakeForm{register_mnemonic} (source data)
   
   b. Define deduplication keys (per section/domain):
      └─ Example: name, date_of_birth, phone_number
   
   c. Retrieve submission data:
      └─ SELECT * FROM G2PIntakeForm{register_mnemonic}
         WHERE submission_id = {submission_id}
   
   d. Retrieve register records for comparison:
      └─ SELECT * FROM G2PRegister{register_mnemonic}
         WHERE register_id = {register_id}
         AND is_deleted = FALSE
   
   e. For each register record:
      i.   Calculate match score (0.0-1.0)
      ii.  If match_score >= threshold:
           └─ INSERT into g2p_dedup_results_intake_forms_vs_register
              ├─ submission_id
              ├─ register_record_id
              ├─ register_section_name (for context)
              ├─ match_score
              ├─ match_fields (JSONB)
              └─ created_at

5. Update submission status:
   └─ SET deduplication_status_vs_register = PROCESSED
   └─ SET deduplication_register_process_timestamp = NOW()
   └─ SET deduplication_register_attempts = deduplication_register_attempts + 1

6. On error:
   └─ SET deduplication_status_vs_register = PENDING (retry)
   └─ SET deduplication_register_error = {error_message}
   └─ SET deduplication_register_attempts = deduplication_register_attempts + 1
   └─ If attempts > max_retries:
      └─ SET deduplication_status_vs_register = FAILED
```

***

### 10. Controller Changes

#### 10.1 G2PIntakeFormMetadataController

**Endpoint Base:** `/intake-form-metadata/`

| Method | Endpoint                | Input                               | Output                   | Process                                                    |
| ------ | ----------------------- | ----------------------------------- | ------------------------ | ---------------------------------------------------------- |
| POST   | `/create_intake_form`   | form fields (excluding form\_id)    | form\_id                 | Insert into g2p\_intake\_form\_definitions                 |
| PUT    | `/update_intake_form`   | form\_id, update fields             | form\_id                 | Update specific fields (form\_mnemonic, form\_description) |
| DELETE | `/delete_intake_form`   | form\_id                            | Empty                    | Delete intake form definition                              |
| GET    | `/get_all_intake_forms` | register\_id (optional), pagination | list\[form\_definitions] | Retrieve forms for register or all forms                   |
| GET    | `/get_intake_form`      | form\_id                            | form\_definition         | Retrieve single form                                       |
| POST   | `/create_tab`           | tab fields (excluding tab\_id)      | tab\_id                  | Insert into g2p\_intake\_form\_ui\_tabs                    |
| DELETE | `/delete_tab`           | tab\_id                             | Empty                    | Delete tab from form                                       |
| POST   | `/toggle_tab_status`    | tab\_id                             | tab\_id                  | Toggle active/inactive status                              |
| GET    | `/get_tab`              | tab\_id                             | tab\_definition          | Retrieve tab definition                                    |
| GET    | `/get_all_tabs`         | form\_id                            | list\[tabs]              | Retrieve all tabs for form                                 |
| POST   | `/add_section`          | tab\_id, section\_id                | tab\_section\_id         | Create mapping in g2p\_intake\_form\_ui\_tab\_sections     |
| DELETE | `/remove_section`       | tab\_section\_id                    | Empty                    | Remove section from tab                                    |
| POST   | `/update_section`       | tab\_section\_id, section\_order    | tab\_section\_id         | Update section order within tab                            |
| GET    | `/get_all_sections`     | tab\_id                             | list\[sections]          | Retrieve sections for tab with metadata                    |

#### 10.2 G2PIntakeFormDataController

**Endpoint Base:** `/intake-form-data/`

| Method | Endpoint                             | Input                                                    | Output             | Process                                                   |
| ------ | ------------------------------------ | -------------------------------------------------------- | ------------------ | --------------------------------------------------------- |
| POST   | `/save_intake_form_submission`       | form\_id, section\_payload\[], submission\_id (optional) | submission\_id     | Save form data in DRAFT status                            |
| POST   | `/finalize_intake_form_submission`   | submission\_id                                           | Empty              | Set draft\_status = FINAL                                 |
| DELETE | `/delete_intake_form_submission`     | submission\_id                                           | Empty              | Delete submission and all section data                    |
| POST   | `/approve_intake_form_submission`    | submission\_id                                           | Empty              | Set approval\_status = APPROVED, trigger ingest and dedup |
| POST   | `/reject_intake_form_submission`     | submission\_id                                           | Empty              | Set approval\_status = REJECTED                           |
| GET    | `/get_intake_form_submission`        | submission\_id, section\_register\_id                    | submission data    | Retrieve submission records                               |
| GET    | `/search_in_intake_form_submissions` | register\_id, search\_text, filter\_schema, pagination   | list\[submissions] | Search across all submissions                             |

#### 10.3 Verification Controller Updates

**Endpoint:** `/verification/`

**Changes:**

* Update submission model references when retrieving verification data
* Ensure verification records link to submission\_id
* Update response model to include deduplication status fields

***

### 11. New Celery Jobs

#### 11.1 Register Ingest Jobs

| Job Name                 | Type   | Schedule  | Input          | Output                |
| ------------------------ | ------ | --------- | -------------- | --------------------- |
| `register_ingest_beat`   | Beat   | Periodic  | None           | Emits submission\_ids |
| `register_ingest_worker` | Worker | On-demand | submission\_id | Processed submissions |

#### 11.2 Deduplication Jobs

| Job Name                            | Type   | Schedule  | Input          | Output                |
| ----------------------------------- | ------ | --------- | -------------- | --------------------- |
| `deduplication_intake_forms_beat`   | Beat   | Periodic  | None           | Emits submission\_ids |
| `deduplication_intake_forms_worker` | Worker | On-demand | submission\_id | Dedup results         |
| `deduplication_register_beat`       | Beat   | Periodic  | None           | Emits submission\_ids |
| `deduplication_register_worker`     | Worker | On-demand | submission\_id | Dedup results         |

***

### 12. Change Request vs Intake Form Workflow

#### 12.1 Intake Form Workflow (New Records)

```
User submits via Intake Form (Manual or Partner)
    ↓
Set approval_status = PENDING
    ↓
Staff approves: approval_status = APPROVED
    ↓
Trigger: register_ingest_beat
    ↓
Worker inserts into Register (Version = V0)
    ↓
Trigger: deduplication processes
    ↓
Submission lifecycle complete
```

#### 12.2 Change Request Workflow (Edits)

```
User submits Change Request (Bene, Agent, Staff, Partner)
    ↓
Change Request processing (existing flow)
    ↓
Register updated with version increment
    ↓
No intake form involvement
```

#### 12.3 Key Distinction

| Aspect          | Intake Form                  | Change Request               |
| --------------- | ---------------------------- | ---------------------------- |
| Purpose         | New record creation          | Record modifications         |
| Submission      | Form submission              | Change request submission    |
| Approval        | Staff approval before ingest | Standard CR approval process |
| Register Update | Via ingest process           | Direct CR process            |
| Versioning      | Created as V0                | Version increments           |
| Deduplication   | Yes (on approval)            | No                           |

***

### 13. Functional Changes Summary

#### 13.1 Section Decoupling

**Before:**

* Sections tightly coupled to tabs
* Sections cannot be reused across tabs
* Tab is required to define a section

**After:**

* Sections defined independently
* Sections mapped to tabs via junction table
* Sections reusable across multiple tabs in register and intake forms
* Section exists regardless of tab association

#### 13.2 Intake Form Independence

**Before:**

* Intake form submission could modify existing records
* Changes submitted as change requests

**After:**

* Intake form ONLY for new record creation
* No modifications through intake form
* All edits via change request process
* Intake form with approval = direct register insertion

#### 13.3 Ingest Pipeline

**Before:**

* Incoming messages routed to change requests
* Section resolution via semantic expression

**After:**

* Incoming messages routed to intake forms
* Form must be marked as `used_only_for_ingestion_pipeline = TRUE`
* Form resolution via updated semantic expression
* Partner-sourced submissions auto-processed

#### 13.4 Deduplication

**Before:**

* No built-in deduplication

**After:**

* Two parallel deduplication processes
* Results stored for UI display
* Configurable match thresholds
* Tracks dedup status across submission lifecycle

***

### 14. Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Intake Form Submission                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ↓
          ┌───────────────────────────────────┐
          │  Save (DRAFT) + Section Data      │
          │  g2p_intake_form_submission       │
          └───────────────────────────────────┘
                              │
                              ↓
          ┌───────────────────────────────────┐
          │   Finalize (FINAL)                │
          │   + Approve (APPROVED)            │
          └───────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ↓               ↓               ↓
        ┌──────────┐  ┌──────────────┐  ┌──────────────┐
        │Register  │  │Intake-Forms  │  │Register      │
        │Ingest    │  │Dedup         │  │Dedup         │
        │Beat      │  │Beat          │  │Beat          │
        └────┬─────┘  └──────┬───────┘  └──────┬───────┘
             │               │                 │
             ↓               ↓                 ↓
        ┌──────────┐  ┌──────────────┐  ┌──────────────┐
        │Register  │  │Intake-Forms  │  │Register      │
        │Ingest    │  │Dedup         │  │Dedup         │
        │Worker    │  │Worker        │  │Worker        │
        └────┬─────┘  └──────┬───────┘  └──────┬───────┘
             │               │                 │
             ↓               ↓                 ↓
        ┌──────────┐  ┌──────────────────────────────────┐
        │Insert    │  │g2p_dedup_results_*               │
        │into      │  │├─ intake_forms_vs_intake_forms   │
        │Register  │  │└─ intake_forms_vs_register       │
        └──────────┘  └──────────────────────────────────┘
```

***

### 15. Implementation Notes

* All dynamic class resolution follows pattern: `{module}.{register_mnemonic}`
* Section reuse enabled through junction tables for both register and intake form tabs
* Deduplication configurable per domain via configuration
* Ingest process idempotent; can safely retry failed submissions
* Submission model tracks multiple asynchronous processes (ingest, dedup intake, dedup register)
* Abstract base class pattern allows domain-specific intake form extensions
