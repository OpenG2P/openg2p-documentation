---
description: Design & architecture - Asynchronous background processes
---

# Celery

### Overview

The Celery modules provide an asynchronous task processing system for the G2P Bridge platform. The system is divided into two complementary modules:

1. **openg2p-g2p-bridge-celery-beat-producers**: Periodically checks the database for pending tasks and dispatches them to the message queue
2. **openg2p-g2p-bridge-celery-workers**: Executes the dispatched tasks by implementing business logic

This document provides a comprehensive overview of both modules and how they work together.

***

### Architecture Overview

```
Celery Beat Scheduler
       ↓
   Runs periodically
       ↓
Beat Producer Tasks (Query DB for pending work)
       ↓
   Send task to Celery Queue (Redis)
       ↓
Celery Worker Pool
       ↓
Worker Tasks (Execute actual business logic)
       ↓
   Update Database Status
```

***

### Module Locations

In the consolidated `g2p-bridge` monorepo:

* **Beat Producers**: `core/celery-beat-producers/`
* **Workers**: `core/celery-workers/`

Both ship as a **single** Docker image (`openg2p/openg2p-bridge-celery`), run as beat or worker by Helm configuration.

***

### Core Components

#### Celery Configuration

Both modules use:

* **Message Broker**: Redis (default: `redis://localhost:6379/0`)
* **Result Backend**: Redis (default: `redis://localhost:6379/0`)
* **Worker Queue**: `g2p_bridge_celery_worker_tasks`
* **Timezone**: UTC

#### Database Connections

**Beat Producers**:

* Single database connection to G2P Bridge database
* Configuration prefix: `g2p_bridge_celery_beat_`

**Workers**:

* Dual database connections:
  * **db\_engine\_pbms**: PBMS (PBMS database for agency/warehouse/program data)
  * **db\_engine\_bridge**: G2P Bridge database
* Configuration prefix: `g2p_bridge_celery_workers_`

***

### Task Scheduler Configuration

The Celery Beat scheduler runs the following producers on configurable intervals (all times in seconds):

```python
Beat Schedule = {
    "mapper_resolution_beat_producer": mapper_resolve_frequency,
    "check_funds_with_bank_beat_producer": funds_available_check_frequency,
    "block_funds_with_bank_beat_producer": funds_blocked_frequency,
    "disburse_funds_from_bank_beat_producer": funds_disbursement_frequency,
    "mt940_processor_beat_producer": mt940_processor_frequency,
    "geo_resolution_beat_producer": geo_resolution_frequency,
    "warehouse_allocation_beat_producer": warehouse_allocation_frequency,
    "agency_allocation_beat_producer": agency_allocation_frequency,
    "warehouse_notification_beat_producer": warehouse_notification_frequency,
    "agency_notification_beat_producer": agency_notification_frequency,
    "beneficiary_notification_beat_producer": beneficiary_notification_frequency,
}
```

Default: All frequencies are 3600 seconds (1 hour), configurable via environment variables.

***

### Task Pairs: Beat Producer → Worker

The system contains 11 task pairs, each following the same pattern:

#### Pattern Overview

**Beat Producer**:

1. Queries database for records with status = PENDING
2. Limits results to `no_of_tasks_to_process` (default: 2)
3. Updates status to PROCESSING
4. Sends task to worker queue with record ID

**Worker**:

1. Receives task from queue with record ID
2. Fetches record from database
3. Executes business logic
4. Updates database with results
5. Handles errors with retry logic

***

### Task Pair Details

#### 1. Mapper Resolution (Financial Address Resolution)

**Purpose**: Resolve financial addresses (bank accounts, mobile wallets, email wallets) for beneficiaries.

**Beat Producer**: `mapper_resolution_beat_producer`

* **Status Field**: `fa_resolution_status`
* **Database Model**: `DisbursementBatchControl`
* **Query Logic**:
  * Fetches batches where `fa_resolution_status == PENDING`
  * Resets stale tasks (PROCESSING > task\_stale\_threshold\_minutes)
  * Limits to `no_of_tasks_to_process`

**Worker**: `mapper_resolution_worker`

* **Input**: `disbursement_batch_control_id` (string)
* **Process**:
  1. Fetches disbursement batch control record
  2. Fetches all disbursements in batch without FA resolution
  3. Constructs `ResolveRequest` with beneficiary IDs
  4. Calls `MapperFactory.get_mapper().resolve()` (async)
  5. Processes resolution responses
  6. Stores financial address details in `DisbursementResolutionFinancialAddress` table
  7. Updates batch status to PROCESSED and triggers sponsor bank dispatch
* **Uses**:
  * `ResolveHelper` for request construction
  * `MapperFactory` for SPAR mapper integration
  * Async event loop for async mapper calls
* **Max Attempts**: `mapper_resolution_max_attempts` (default: 3)
* **FA Types Extracted**:
  * Account number, bank code, branch code (bank transfers)
  * Mobile number, mobile wallet provider (mobile wallet)
  * Email address, email wallet provider (email wallet)

***

#### 2. Check Funds with Bank

**Purpose**: Check if sponsor bank has sufficient funds for disbursement.

**Beat Producer**: `check_funds_with_bank_beat_producer`

* **Status Field**: `funds_available_with_bank` (EnvelopeBatchStatusForCash)
* **Database Models**: `DisbursementEnvelope`, `EnvelopeBatchStatusForCash`
* **Query Logic**:
  * Checks `disbursement_schedule_date` (current day or future based on config)
  * Filters: `cancellation_status == NOT_CANCELLED`
  * Filters: All disbursements received, all quantities received
  * Status: PENDING\_CHECK or FUNDS\_NOT\_AVAILABLE
  * Limits to `no_of_tasks_to_process`

**Worker**: `check_funds_with_bank_worker`

* **Input**: `disbursement_envelope_id` (string)
* **Process**:
  1. Fetches disbursement envelope
  2. Retrieves sponsor bank configuration (program account, bank code)
  3. Gets bank connector for sponsor bank
  4. Calls `bank_connector.check_funds()` with:
     * Account number
     * Currency (measurement unit)
     * Total amount needed
  5. Updates `EnvelopeBatchStatusForCash.funds_available_with_bank` status
  6. Records attempt count and timestamp
* **Status Values**:
  * FUNDS\_AVAILABLE: Funds are available
  * FUNDS\_NOT\_AVAILABLE: Funds are insufficient
  * ERROR: Max attempts exceeded
* **Max Attempts**: `check_funds_with_bank_max_attempts` (default: 3)

***

#### 3. Block Funds with Bank

**Purpose**: Block/reserve funds at the sponsor bank for the disbursement.

**Beat Producer**: `block_funds_with_bank_beat_producer`

* **Status Field**: `funds_blocked_with_bank` (EnvelopeBatchStatusForCash)
* **Database Models**: `DisbursementEnvelope`, `EnvelopeBatchStatusForCash`
* **Query Logic**:
  * Similar date filtering as check funds
  * Status: PENDING or FUNDS\_NOT\_AVAILABLE
  * Previous status: FUNDS\_AVAILABLE

**Worker**: `block_funds_with_bank_worker`

* **Input**: `disbursement_envelope_id` (string)
* **Process**:
  1. Fetches disbursement envelope and batch status
  2. Retrieves sponsor bank configuration
  3. Gets bank connector
  4. Calls `bank_connector.block_funds()` with account and amount
  5. Stores block reference number from bank
  6. Updates `funds_blocked_with_bank` status
  7. Records block reference for later payment initiation
* **Status Values**:
  * BLOCKED: Funds successfully blocked
  * FUNDS\_NOT\_AVAILABLE: Blocking failed
  * ERROR: Max attempts exceeded
* **Max Attempts**: `block_funds_with_bank_max_attempts` (default: 3)

***

#### 4. Disburse Funds from Bank

**Purpose**: Initiate actual payment disbursements from sponsor bank to beneficiaries.

**Beat Producer**: `disburse_funds_from_bank_beat_producer`

* **Status Field**: `sponsor_bank_dispatch_status` (DisbursementBatchControl)
* **Database Model**: `DisbursementBatchControl`
* **Query Logic**:
  * Fetches batches where status = PENDING
  * Checks all required predecessor statuses are PROCESSED
  * Limits to `no_of_tasks_to_process`

**Worker**: `disburse_funds_from_bank_worker`

* **Input**: `disbursement_batch_control_id` (string)
* **Process**:
  1. Fetches batch control and related disbursements
  2. Retrieves resolved financial addresses for beneficiaries
  3. Constructs payment payloads for each disbursement
  4. Groups by payment method (bank, mobile wallet, email wallet)
  5. Calls `bank_connector.initiate_payment()` with batch of payloads
  6. Stores transaction IDs and payment status
  7. Updates batch status and triggers status monitoring
* **Payment Methods Supported**:
  * Bank account transfer (IFSC/BIC)
  * Mobile wallet (phone + provider)
  * Email wallet (email + provider)
* **Max Attempts**: `disburse_funds_with_bank_max_attempts` (default: 3)

***

#### 5. MT940 Processor

**Purpose**: Process and parse bank statement files in MT940 format.

**Beat Producer**: `mt940_processor_beat_producer`

* **Status Field**: `mt940_status` (AccountStatement)
* **Database Model**: `AccountStatement`
* **Query Logic**:
  * Fetches statements where status = PENDING
  * Limits to `no_of_tasks_to_process`

**Worker**: `mt940_processor_worker`

* **Input**: `account_statement_id` (string)
* **Process**:
  1. Fetches account statement record
  2. Retrieves uploaded file from storage
  3. Parses MT940 format
  4. Extracts transactions and balances
  5. Validates transactions against disbursement records
  6. Reconciles transactions with disbursement statuses
  7. Updates transaction records with bank confirmation
* **Max Attempts**: `mt940_processor_max_attempts` (default: 3)

***

#### 6. Geo Resolution

**Purpose**: Resolve geographic zones (state/district) for beneficiaries.

**Beat Producer**: `geo_resolution_beat_producer`

* **Status Field**: `geo_resolution_status` (DisbursementBatchControl)
* **Database Model**: `DisbursementBatchControl`
* **Query Logic**:
  * Fetches batches where status = PENDING
  * Limits to `no_of_tasks_to_process`

**Worker**: `geo_resolution_worker`

* **Input**: `disbursement_batch_control_id` (string)
* **Process**:
  1. Fetches batch control and beneficiaries
  2. Calls `GeoResolverFactory.get_geo_resolver().resolve_geo()` with beneficiary IDs
  3. Receives geographic zone assignments (large and small areas)
  4. Stores geographic information in `DisbursementBatchControlGeo` table
  5. Updates batch status
* **Uses**: Farmer registry for geographic zone lookup
* **Max Attempts**: `geo_resolution_max_attempts` (default: 3)

***

#### 7. Warehouse Allocation

**Purpose**: Allocate warehouses to geographic zones for commodity distribution.

**Beat Producer**: `warehouse_allocation_beat_producer`

* **Status Field**: `warehouse_allocation_status` (DisbursementBatchControl)
* **Database Model**: `DisbursementBatchControl`
* **Query Logic**:
  * Fetches batches where status = PENDING
  * Verifies geo resolution is PROCESSED
  * Limits to `no_of_tasks_to_process`

**Worker**: `warehouse_allocation_worker`

* **Input**: `disbursement_batch_control_id` (string)
* **Process**:
  1. Fetches batch control and geo information
  2. Gets benefit code and program from envelope
  3. Calls `WarehouseAllocatorFactory.get_allocator().allocate_warehouse()` with:
     * Large geographic zones
     * Benefit code ID
     * Program ID
  4. Receives warehouse allocations
  5. Stores allocations in `DisbursementBatchControlGeo` table
  6. Updates batch status
* **Database Tables**: Intersects PBMS warehouse data with geographic coverage
* **Max Attempts**: `warehouse_allocation_max_attempts` (default: 3)

***

#### 8. Agency Allocation

**Purpose**: Allocate agencies for final payment delivery to beneficiaries.

**Beat Producer**: `agency_allocation_beat_producer`

* **Status Field**: `agency_allocation_status` (DisbursementBatchControl)
* **Database Model**: `DisbursementBatchControl`
* **Query Logic**:
  * Fetches batches where status = PENDING
  * Limits to `no_of_tasks_to_process`

**Worker**: `agency_allocation_worker`

* **Input**: `disbursement_batch_control_id` (string)
* **Process**:
  1. Fetches batch control and geo information
  2. Gets benefit code and program from envelope
  3. Calls `AgencyAllocatorFactory.get_allocator().allocate_agency()` with:
     * Small geographic zones
     * Benefit code (dict with id and mnemonic)
     * Program (dict with id and mnemonic)
  4. Receives agency allocations with:
     * Agency ID, name, mnemonic
     * Admin contact information
     * Additional attributes
  5. Updates multiple tables:
     * `DisbursementBatchControlGeo`: Agency details
     * `DisbursementResolutionGeoAddress`: Agency info and beneficiary notification status
     * `DisbursementBatchControlGeoAttributes`: Admin details
  6. Sets notification status flags (PENDING or PROCESSED based on suppress\_notifications config)
  7. For CASH\_PHYSICAL benefits: Sets sponsor\_bank\_dispatch\_status to PENDING
* **Max Attempts**: `agency_allocation_max_attempts` (default: 3)

***

#### 9. Warehouse Notification

**Purpose**: Send notifications to warehouses about commodity distribution tasks.

**Beat Producer**: `warehouse_notification_beat_producer`

* **Status Field**: `warehouse_notification_status` (DisbursementBatchControlGeo)
* **Query Logic**:
  * Fetches geo records where status = PENDING
  * Limits to `no_of_tasks_to_process`

**Worker**: `warehouse_notification_worker`

* **Input**: `batch_control_geo_id` (string)
* **Process**:
  1. Fetches batch control geo and related warehouse info
  2. Constructs notification payload with warehouse allocation details
  3. Calls notification service to send warehouse notification
  4. Updates notification status to PROCESSED
* **Notification Type**: `NotificationType.WAREHOUSE_NOTIFICATION`
* **Max Attempts**: `warehouse_notification_max_attempts` (default: 3)

***

#### 10. Agency Notification

**Purpose**: Send notifications to agencies about their payment delivery tasks.

**Beat Producer**: `agency_notification_beat_producer`

* **Status Field**: `agency_notification_status` (DisbursementBatchControlGeo)
* **Query Logic**:
  * Fetches geo records where status = PENDING
  * Limits to `no_of_tasks_to_process`

**Worker**: `agency_notification_worker`

* **Input**: `batch_control_geo_id` (string)
* **Process**:
  1. Fetches batch control geo and related agency info
  2. Constructs notification payload with agency allocation and beneficiary details
  3. Calls notification service to send agency notification
  4. Updates notification status to PROCESSED
* **Notification Type**: `NotificationType.AGENCY_NOTIFICATION`
* **Max Attempts**: `agency_notification_max_attempts` (default: 3)

***

#### 11. Beneficiary Notification

**Purpose**: Send notifications to beneficiaries about their disbursements.

**Beat Producer**: `beneficiary_notification_beat_producer`

* **Status Field**: `beneficiary_notification_status` (DisbursementResolutionGeoAddress)
* **Query Logic**:
  * Fetches resolution records where status = PENDING
  * Limits to `no_of_tasks_to_process`

**Worker**: `beneficiary_notification_worker`

* **Input**: `resolution_geo_address_id` (string)
* **Process**:
  1. Fetches resolution geo address with beneficiary details
  2. Constructs notification payload with disbursement information
  3. Calls notification service to send beneficiary notification
  4. Updates notification status to PROCESSED
* **Notification Type**: `NotificationType.BENEFICIARY_NOTIFICATION`
* **Max Attempts**: `beneficiary_notification_max_attempts` (default: 3)

***

### Data Flow and Processing Pipeline

```
1. Disbursement Envelope Created
         ↓
2. Mapper Resolution
   (Resolve financial addresses)
         ↓
3. Check Funds with Bank
   (Verify sponsor has funds)
         ↓
4. Block Funds with Bank
   (Reserve funds at sponsor bank)
         ↓
5. Geo Resolution
   (Determine beneficiary locations)
         ↓
6. Agency/Warehouse Allocation
   (Assign delivery partners)
         ↓
7. Notifications
   (Notify warehouse → agency → beneficiaries)
         ↓
8. Disburse Funds from Bank
   (Execute actual payments)
         ↓
9. MT940 Processing
   (Reconcile bank statements)
         ↓
Completion
```

***

### Error Handling and Retry Logic

#### Status Values

```python
class ProcessStatus(enum.Enum):
    PENDING = "PENDING"          # Task not yet started
    PROCESSING = "PROCESSING"    # Task in progress
    PROCESSED = "PROCESSED"      # Task completed successfully
    ERROR = "ERROR"              # Task failed after max attempts
    NOT_APPLICABLE = "NOT_APPLICABLE"  # Task not needed for this record
```

#### Retry Mechanism

**For Each Task**:

1. Beat producer checks status = PENDING
2. Updates status to PROCESSING
3. Dispatches to worker
4. Worker executes logic
5. On success: status = PROCESSED
6. On error:
   * Increments attempt counter
   * Stores error code/message
   * Updates timestamp
   * If attempts < max\_attempts: status = PENDING (will be retried)
   * If attempts >= max\_attempts: status = ERROR (stops retrying)

#### Stale Task Recovery

The mapper resolution producer includes special logic to recover stale tasks:

```python
stale_at = datetime.now() - timedelta(minutes=task_stale_threshold_minutes)
# Reset tasks stuck in PROCESSING for too long
update(DisbursementBatchControl)
  .where(fa_resolution_status == PROCESSING and updated_at > stale_at)
  .values(fa_resolution_status = PENDING)
```

This prevents tasks from getting stuck if a worker crashes while processing.

***

### Configuration Parameters

#### Beat Producer Configuration

```yaml
celery_broker_url: "redis://localhost:6379/0"
celery_backend_url: "redis://localhost:6379/0"

# Task Frequencies (in seconds, default: 3600 = 1 hour)
mapper_resolve_frequency: 3600
funds_available_check_frequency: 3600
funds_blocked_frequency: 3600
funds_disbursement_frequency: 3600
mt940_processor_frequency: 3600
geo_resolution_frequency: 3600
warehouse_allocation_frequency: 3600
agency_allocation_frequency: 3600
warehouse_notification_frequency: 3600
agency_notification_frequency: 3600
beneficiary_notification_frequency: 3600

# Processing Control
no_of_tasks_to_process: 2  # Tasks per beat cycle
task_stale_threshold_minutes: 60  # Stale task recovery threshold
process_future_disbursement_schedules: false  # Only process current day schedules

# Database
db_datasource: "postgresql://user:pass@host:5432/g2p_bridge_db"
```

#### Worker Configuration

```yaml
celery_broker_url: "redis://localhost:6379/0"
celery_backend_url: "redis://localhost:6379/0"

# Max Retry Attempts (all default to 3)
agency_allocation_max_attempts: 3
warehouse_allocation_max_attempts: 3
geo_resolution_max_attempts: 3
mapper_resolution_max_attempts: 3
check_funds_with_bank_max_attempts: 3
block_funds_with_bank_max_attempts: 3
disburse_funds_with_bank_max_attempts: 3
mt940_processor_max_attempts: 3
agency_notification_max_attempts: 3
warehouse_notification_max_attempts: 3
beneficiary_notification_max_attempts: 3

# Database Connections
db_datasource_bridge: "postgresql://user:pass@host:5432/g2p_bridge_db"
db_datasource_pbms: "postgresql://user:pass@host:5432/pbmsdb"

# Mapper Configuration (SPAR)
mapper_request_jwt_enabled: true
mapper_request_sender_id: "openg2p-g2p-bridge"

# Key Management
sign_key_keymanager_app_id: "G2PBRIDGE"
sign_key_keymanager_ref_id: ""
keymanager_api_timeout: 10
keymanager_api_base_url: ""

# OAuth Configuration
oauth_enabled: true
oauth_url: ""
oauth_client_id: "openg2p-g2p-bridge"

# Financial Address Parsing
bank_fa_deconstruct_strategy: "regex pattern for bank FA"
mobile_wallet_deconstruct_strategy: "regex pattern for mobile wallet"
email_wallet_deconstruct_strategy: "regex pattern for email wallet"

# Notification Control
suppress_notifications: false  # When true, sets notification status to PROCESSED
```

***

### Key Helpers (Workers)

#### Agency Helper

Provides utilities for agency-related operations:

* Retrieve agency information from PBMS database
* Get agency contact details
* Validate agency allocations

#### Warehouse Helper

Provides utilities for warehouse operations:

* Retrieve warehouse information
* Get sponsor bank configuration for programs/benefits
* Validate warehouse allocations

#### Resolve Helper

Provides utilities for address resolution:

* Construct resolve requests for SPAR mapper
* Parse financial address responses
* Extract FA components (account number, bank code, etc.)

***

### Database Models Used

#### Beat Producer Database Models

* `DisbursementBatchControl`: Batch-level processing status
* `DisbursementEnvelope`: Envelope container for disbursements
* `EnvelopeBatchStatusForCash`: Cash-specific batch status tracking
* `EnvelopeControl`: Envelope control and receipt tracking
* `AccountStatement`: MT940 file upload tracking

#### Worker Database Models

* `DisbursementBatchControl`: Batch processing and status updates
* `DisbursementBatchControlGeo`: Geographic allocation tracking
* `DisbursementBatchControlGeoAttributes`: Geo-specific attributes
* `DisbursementEnvelope`: Envelope information
* `DisbursementEnvelopeStatusForCash`: Envelope-specific status
* `Disbursement`: Individual disbursement records
* `DisbursementResolutionGeoAddress`: Geographic resolution data
* `DisbursementResolutionFinancialAddress`: Resolved financial addresses

***

### Integration with Extension Modules

The workers integrate with extension modules:

1. **Agency Allocator** (`openg2p-g2p-bridge-agency-allocator`):
   * Called by agency\_allocation\_worker
   * Allocates agencies using set intersection algorithm
2. **Warehouse Allocator** (`openg2p-g2p-bridge-warehouse-allocator`):
   * Called by warehouse\_allocation\_worker
   * Allocates warehouses for commodity distribution
3. **Geo Resolver** (`openg2p-g2p-bridge-geo-resolver`):
   * Called by geo\_resolution\_worker
   * Resolves beneficiary geographic zones
4. **Mapper Connectors** (`openg2p-g2p-bridge-mapper-connectors`):
   * Called by mapper\_resolution\_worker
   * Resolves financial addresses via SPAR integration
5. **Bank Connectors** (`openg2p-g2p-bridge-bank-connectors`):
   * Called by funds-related workers
   * Interfaces with sponsor banks
6. **Notification Connectors** (`openg2p-g2p-bridge-notification-connectors`):
   * Called by notification workers
   * Sends notifications via Novu platform

***

### Logging

Both modules use structured logging:

* **Beat Producers**: Log task dispatch events, status updates, database queries
* **Workers**: Log task execution, business logic progress, errors, and recovery

Logger names follow pattern:

* Beat: `{task_name}_beat_producer`
* Worker: `{task_name}_worker`

***

### Transaction Management

#### Beat Producers

* Use SQLAlchemy sessionmaker with `expire_on_commit=False`
* Commit status updates before dispatching task
* Ensures consistency between task dispatch and database state

#### Workers

* Use SQLAlchemy sessionmaker with `expire_on_commit=False`
* Wrap all logic in try-except blocks
* Rollback on error and update error status
* Commit all changes after processing or error handling

***

### Performance Considerations

1. **Batch Processing**: Each beat cycle processes `no_of_tasks_to_process` (default: 2) tasks to prevent queue congestion
2. **Frequency Control**: Task frequencies configurable (default: 1 hour) to balance real-time responsiveness and system load
3. **Stale Task Recovery**: Automatic recovery of stuck tasks after `task_stale_threshold_minutes` (default: 60)
4. **Async Operations**: Mapper resolution uses async/await for non-blocking I/O
5. **Database Connection Pooling**: SQLAlchemy connection pooling for efficient database access

***

### Monitoring and Observability

#### Key Metrics to Monitor

* Task queue depth (number of pending tasks)
* Worker throughput (tasks processed per minute)
* Error rates by task type
* Retry rates indicating systemic issues
* Stale task recovery frequency
* Task processing latency

#### Health Checks

* Monitor Redis broker connectivity
* Monitor database connectivity
* Monitor worker availability
* Track task completion rates vs. error rates

***

### Deployment Considerations

1. **Beat Scheduler**: Run single instance (ensure only one Celery Beat scheduler)
2. **Workers**: Scale horizontally (multiple worker instances with consumer groups)
3. **Queue**: Ensure Redis is highly available
4. **Database**: Ensure G2P Bridge and PBMS databases are accessible
5. **Notification Service**: Ensure Novu platform is accessible for notifications
6. **Bank Integration**: Ensure bank connectors are properly configured

***

### Summary

The Celery modules implement a robust, scalable asynchronous task processing system that:

* Separates task discovery (beat producers) from task execution (workers)
* Provides automatic retry logic with configurable max attempts
* Includes stale task recovery for fault tolerance
* Integrates with multiple extension modules for specialized operations
* Supports parallel processing through worker pool
* Provides comprehensive error tracking and status management
* Enables monitoring and observability of batch processing operations
