---
description: Input mechanisms into Intake Forms
---

# Input Mechanisms

## Input Mechanisms Convergence - Design Document

### Overview

This document outlines the consolidation of input mechanism handling across registry modules. The goal is to create a unified user interface experience for record submission and streamline the underlying API architecture to support multiple pathways for data entry into the system.

***

### Registry Staff Portal UI changes

#### Restructuring the Record Creation Flow

Currently, the Register Route allows users to add new records directly within the application. Under the proposed changes, this functionality will be removed from the Register Route and moved exclusively to the Submissions route. This separation of concerns ensures that the Register Route focuses solely on editing and managing existing records, while all new record creation flows through a centralized Submissions interface.

The Register Route will transition to an edit-only mode for existing records, simplifying its scope and preventing duplicate functionality across the application.

***

### Consolidated Input Mechanism in Submissions UI

#### Creating New Submissions

When a user initiates the creation of a new submission through the Submissions route, the system will call the `get_input_mechanisms(register_id)` API endpoint. This endpoint currently exists in the Register Route and will be migrated to the consolidated Input Mechanism interface.

The API returns three available input mechanisms that users can choose from:

* **INTAKE\_FORM** - Traditional form-based data entry
* **IMPORT\_FILE** - Bulk file import functionality
* **VERIFIABLE\_CREDENTIALS** - Digital credential verification

These three mechanisms form a nested, tiered menu structure in the UI, where each mechanism type represents a Level 1 menu item. Users select their desired input method, and the UI dynamically presents the relevant sub-options and workflows specific to that mechanism.

***

### INTAKE\_FORM Selection Flow

#### Form-Based Data Entry

When users select the INTAKE\_FORM mechanism, the UI calls the `get_intake_forms(register_id)` API endpoint, which returns all intake forms defined for the specific register. This functionality currently exists within the Submissions route and will now be consolidated as part of the unified Input Mechanism interface.

Upon receiving the list of available forms, the user selects the appropriate form for their submission. The existing form submission workflow continues unchanged, preserving the current user experience and validation logic for form-based data entry.

***

### IMPORT\_FILE Selection Flow

#### File-Based Bulk Import

The IMPORT\_FILE mechanism enables bulk data import capabilities. When users select this option, the system calls a new API endpoint: `get_import_file_definitions(register_id)`. This endpoint returns all available file definition templates configured for the register, allowing users to understand the expected file format and structure.

After selecting a file definition, users proceed with file upload functionality. The UI provides standard file browsing and selection capabilities. Once a file is selected and uploaded, the system receives a unique `document_store_id` from the file storage service.

The user then triggers the `enqueue_file_import_into_register` API call with three required parameters:

* `document_store_id` - The identifier pointing to the uploaded file in storage
* `register_id` - The target register for data import
* `intake_form_id` - The associated intake form for classification and processing

This queued approach decouples the file upload from processing, allowing asynchronous handling of bulk imports through a background worker system.

***

### VERIFIABLE\_CREDENTIALS Selection Flow

#### Digital Credential Verification

The VERIFIABLE\_CREDENTIALS mechanism leverages digital credentials for data submission. When users select this option, the system calls `get_vc_configuration(register_id)` to retrieve all verifiable credentials configured for the register. This API call and the overall VC workflow continue as currently implemented.

The proposed enhancement includes additional UI context. In addition to displaying the available credentials, the system now shows:

* The **INTAKE\_FORM Mnemonic** that is compatible with each credential
* The **Data Model Mnemonic** that the credential conforms to

Users make a three-part selection: the verifiable credential, the compatible intake form, and the associated data model. Following this selection, the system initiates the existing VC/VP (Verifiable Presentation) interaction flow with the Inji Verifier.

Once verification is complete, the Inji Verifier returns a signed payload. Previously, this payload was sent to `partner-api/ingest-data`. Under the new architecture, this payload is instead sent to `registry-staff-portal-api/ingest-data`, consolidating credential-based submissions within the staff portal API layer.

***

### Registry Core - Data Models

#### Enhanced Input Mechanism Model

The `G2PInputMechanism` model is being refined to use a structured enumeration for the `mechanism_type` field. Rather than accepting arbitrary string values, it now supports three explicit types:

* INTAKE\_FORM
* IMPORT\_FILE
* VERIFIABLE\_CREDENTIAL

This enum-based approach provides type safety and prevents invalid mechanism types from being created in the system.

#### VC Configuration Enhancement

The existing `G2PRegistryVcConfiguration` model is being extended with two new attributes:

* `intake_form_id` - Links the VC to a specific intake form for context and compatibility information
* `data_model_id` - Associates the credential with the data model it conforms to

These additions enable the UI to display compatibility information and ensure that ingested data from credentials is properly classified and routed.

#### New Import File Configuration Model

A new model, `G2PRegistryImportFileConfiguration`, has been introduced to manage file import templates and definitions. This model contains:

* `import_file_configuration_id` - Primary identifier
* `register_id` - The register to which this import applies
* `form_id` - The associated intake form
* `data_model_id` - The data model for the imported records
* `import_file_template_mnemonic` - A unique identifier for the file template
* `import_file_template_description` - Human-readable description of the file format

#### Consolidated Service Layer

All input mechanism-related operations are consolidated into two key services:

* **input\_mechanism\_metadata\_service** - Handles retrieval of mechanism definitions, form lists, and configuration details
* **input\_mechanism\_data\_service** - Manages the actual processing and ingestion of data from various mechanisms

#### Import File Processing Queue

A new model, `import_file_process_queue`, manages the asynchronous processing of file imports. This table maintains the state of each import job:

| Field                             | Type            | Purpose                                   |
| --------------------------------- | --------------- | ----------------------------------------- |
| `import_file_id`                  | UUID (PK)       | Unique identifier for the import file job |
| `document_store_id`               | String (Unique) | Reference to the stored file in Minio     |
| `data_model_id`                   | UUID            | The data model for classification         |
| `register_id`                     | UUID            | Target register for import                |
| `intake_form_id`                  | UUID            | Associated intake form                    |
| `queued_at`                       | Timestamp       | When the job was queued                   |
| `queued_by`                       | String          | User who initiated the import             |
| `intake_form_ingestion_status`    | ENUM            | Status: PENDING, PROCESSED, or FAILED     |
| `intake_form_ingestion_timestamp` | Timestamp       | When ingestion completed                  |
| `intake_form_ingestion_attempts`  | Integer         | Number of attempted ingestions            |
| `intake_form_ingestion_error`     | Text            | Error message if ingestion failed         |
| `number_of_records_present`       | Integer         | Total records in the file                 |
| `number_of_records_ingested`      | Integer         | Records successfully ingested             |

#### Import File Processing Log

The `import_file_process_log` model provides detailed record-level tracking for file imports:

| Field                   | Type                    | Purpose                           |
| ----------------------- | ----------------------- | --------------------------------- |
| `import_file_record_id` | UUID (PK)               | Unique identifier for each record |
| `import_file_id`        | UUID (Non-unique Index) | Links to the parent import job    |
| `document_store_id`     | String (Unique Index)   | Reference to the file in storage  |
| `record_number`         | Integer                 | Sequential position in the file   |
| `ingestion_timestamp`   | Timestamp               | When this record was processed    |

***

### Registry Staff API

#### New API Controllers

The Registry Staff API is being expanded with two new dedicated controllers to manage input mechanism operations.

**input-mechanism-metadata Controller**

This controller provides metadata and configuration retrieval for all input mechanism types. It includes the following methods, migrated from the existing ui-helper-controller:

* `get_input_mechanisms` - Returns the three available mechanism types
* `get_import_file_configuration` - Retrieves file definition templates
* `get_vc_configuration` - Returns configured verifiable credentials

Consolidating these endpoints in a dedicated metadata controller improves organization and makes it easier to extend mechanism capabilities in the future.

**input-mechanism-data Controller**

This controller handles the actual processing and ingestion of data from various input mechanisms. Key methods include:

* `enqueue_import_file` - Queues a file import job for asynchronous processing
* `ingest-data` - Accepts ingested data and routes it appropriately

#### Enhanced ingest-data Endpoint

The `ingest-data` endpoint is being made available in the Registry Staff API at the path `input-mechanism-data/ingest-data`. In addition to the existing payload parameter, this endpoint now accepts two new optional parameters:

* `register_id` - Identifies the target register for ingestion
* `intake_form_id` - Specifies which intake form the data conforms to

These parameters enable intelligent routing and classification of ingested data without requiring a separate classification processing step.

***

### Registry Partner API

#### ingest-data Enhancement

The existing `/ingest-data` endpoint in the Registry Partner API is being enhanced to accept the same two new optional parameters:

* `register_id` - Identifies the target register
* `intake_form_id` - Specifies the intake form

This ensures consistency across both the partner and staff API layers, allowing external partners and internal staff portals to use the same ingestion interface with optional classification context.

***

### Registry Celery - Asynchronous Processing

#### Import File Processing Pipeline

Two new components are being added to the Celery-based asynchronous processing system to handle file imports.

**import\_file\_process\_beat\_producer**

This beat producer is responsible for periodically checking the `import_file_process_queue` for pending import jobs. When jobs are found, it picks them up and emits the `import_file_id` to the worker, initiating the processing workflow.

**import\_file\_process\_worker**

The worker handles the actual processing of file imports. Its workflow operates as follows:

1. **Retrieve the file** from Minio storage using the `document_store_id`
2. **Process record by record** from the uploaded file
3. **Check for duplicates** by verifying whether each record already exists in the `import_file_process_log`
4. **Send to ingestion service** by calling `/ingest-data` with the record payload and metadata:
   * Payload (the actual record data)
   * `data_model_id`
   * `register_id`
   * `intake_form_id`
5. **Log the result** by persisting the outcome to `import_file_process_log`
6. **Commit granularly** - Each record is committed independently, ensuring that partial failures don't cause entire files to be rejected

This record-by-record processing approach provides fine-grained error handling and allows the system to continue processing despite individual record failures.

***

### Data Ingestion Logic Enhancement

#### Intelligent Ingestion Classification

The ingestion pipeline is being enhanced to intelligently classify data based on available context. The behavior changes as follows:

**When register\_id and intake\_form\_id are provided:**

* Write incoming data to `incoming_classified_data` (rather than raw data)
* Set the `Classification_status` to PROCESSED
* **Result:** The data is immediately routed to the TRANSFORMATION stage, bypassing the classification processing pipeline

This optimization recognizes that when classification context is already available (because the user selected a register and form), there is no need for the expensive classification step. The system can move directly to data transformation.

**When register\_id and intake\_form\_id are not provided:**

* Write incoming data to `incoming_raw_data` and `incoming_raw_data_payload` tables
* Set the `Classification_status` to UNPROCESSED
* **Result:** Data flows through the normal classification pipeline

This preserves backward compatibility for legacy ingestion flows or third-party integrations that cannot provide classification context. The system still properly processes this data through the full pipeline.

This dual-path approach balances optimization for classified ingestion while maintaining compatibility for unclassified submissions.
