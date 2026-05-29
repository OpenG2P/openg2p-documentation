---
description: System Design Summary
---

# Design

### Summary

The **OpenG2P G2P Bridge** is a comprehensive, modular platform for managing and executing government-to-person (G2P) cash and commodity disbursements at scale. The system orchestrates complex multi-step workflows involving beneficiary identification, financial address resolution, fund management, allocation of delivery partners, and notification of all stakeholders.

The architecture follows a **plugin-based extension model** with **asynchronous task processing**, enabling partners to implement custom business logic while the core platform handles orchestration, state management, and integration coordination.

***

### System Context

#### Purpose

The G2P Bridge enables government agencies and development organizations to:

1. **Create and manage disbursement envelopes** (batches of beneficiary payments)
2. **Resolve beneficiary financial addresses** (bank accounts, mobile wallets, email wallets)
3. **Check and block funds** with sponsor banks
4. **Allocate delivery partners** (agencies for cash, warehouses for commodities)
5. **Execute disbursements** and reconcile with bank statements
6. **Notify all stakeholders** (warehouses, agencies, beneficiaries)
7. **Track status** at every step with retry capabilities

#### Key Stakeholders

* **Government Agencies**: Define programs, benefits, and disbursement schedules
* **Sponsor Banks**: Hold funds, validate balances, execute payments
* **Delivery Partners**: Agencies (for cash) and Warehouses (for commodities)
* **Beneficiaries**: Recipients of cash or commodities
* **Integration Partners**: External systems integrating via Partner API

***

### System Architecture

#### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      EXTERNAL SYSTEMS                            │
│  (Government Portal, Banking Systems, Partner Systems)           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    PARTNER API LAYER                             │
│  REST Endpoints for:                                             │
│  - Create/Cancel Disbursements & Envelopes                       │
│  - Query Disbursement Status                                     │
│  - Upload Bank Statements (MT940)                                │
│  - Amend Disbursement Envelopes                                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              ASYNCHRONOUS TASK PROCESSING LAYER                  │
│  Celery Beat Producers (Periodic Schedulers)                     │
│           ↓                                                       │
│  Message Queue (Redis)                                           │
│           ↓                                                       │
│  Celery Workers (Task Executors)                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│           EXTENSION MODULES (Plugin Architecture)                │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Allocation Modules                                       │   │
│  │ - Agency Allocator (Assign agencies to geo zones)        │   │
│  │ - Warehouse Allocator (Assign warehouses to zones)       │   │
│  │ - Geo Resolver (Resolve beneficiary locations)           │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Bank Integration Modules                                 │   │
│  │ - Bank Connectors (Fund checks, blocks, disbursements)   │   │
│  │ - Sponsor Bank Configuration                             │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Resolution Modules                                       │   │
│  │ - SPAR Mapper (Resolve financial addresses)              │   │
│  │ - MT940 Processor (Reconcile bank statements)            │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Notification Modules                                     │   │
│  │ - Notification Connectors (Send via Novu platform)       │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│               DATABASE LAYER                                     │
│  - G2P Bridge Database (Core state and transactions)             │
│  - PBMS Database (Programs, Benefits, Agencies, Warehouses)      │
└─────────────────────────────────────────────────────────────────┘
```

***

### Core Components Overview

#### 1. Partner API (`openg2p-g2p-bridge-partner-api`)

**Purpose**: Provides REST endpoints for external systems to interact with the G2P Bridge.

**Endpoints** (9 total):

* `POST /create_disbursements` - Create disbursements
* `POST /cancel_disbursements` - Cancel disbursements
* `POST /create_disbursement_envelopes` - Create envelope batches
* `POST /cancel_disbursement_envelope` - Cancel envelope
* `POST /amend_disbursement_envelope` - Modify envelope
* `POST /get_disbursement_status` - Query disbursement status
* `POST /get_disbursement_batch_control` - Query batch information
* `POST /get_disbursement_envelope_status` - Query envelope status
* `POST /upload_mt940` - Upload bank statement

**Key Features**:

* JWT signature validation (except statement upload)
* Consistent error handling
* All endpoints return HTTP 200 with status in response body

***

#### 2. Celery Task Processing (`openg2p-g2p-bridge-celery-beat-producers` & `openg2p-g2p-bridge-celery-workers`)

**Architecture**: Producer-Consumer pattern using Celery + Redis

**Beat Producers** (11 periodic tasks):

* Query database for pending work
* Limit throughput (default: 2 tasks per cycle)
* Update status to PROCESSING
* Dispatch to worker queue

**Workers** (11 corresponding tasks):

* Execute business logic
* Update database with results
* Handle errors with retry logic
* Max attempts configurable (default: 3)

**Task Pairs**:

1. Mapper Resolution → mapper\_resolution\_worker
2. Check Funds → check\_funds\_with\_bank\_worker
3. Block Funds → block\_funds\_with\_bank\_worker
4. Disburse Funds → disburse\_funds\_from\_bank\_worker
5. MT940 Processor → mt940\_processor\_worker
6. Geo Resolution → geo\_resolution\_worker
7. Warehouse Allocation → warehouse\_allocation\_worker
8. Agency Allocation → agency\_allocation\_worker
9. Warehouse Notification → warehouse\_notification\_worker
10. Agency Notification → agency\_notification\_worker
11. Beneficiary Notification → beneficiary\_notification\_worker

**Key Features**:

* Stale task recovery (automatic reset after timeout)
* Granular status tracking at batch and geo levels
* Integration with extension modules via factory pattern
* Comprehensive error handling and retry logic

***

#### 3. Extension Modules (Plugin Architecture)

**3.1 Agency Allocator (`openg2p-g2p-bridge-agency-allocator`)**

**Purpose**: Allocate agencies to geographic zones for final payment delivery.

**Algorithm**: Set intersection

* Authorized agencies (from G2PAgencyProgramBenefitCode)
* Geographic agencies (from G2PAdministrativeAreaSmallAgencyRel)
* Random selection from eligible agencies

**Called By**: agency\_allocation\_worker

***

**3.2 Warehouse Allocator (`openg2p-g2p-bridge-warehouse-allocator`)**

**Purpose**: Allocate warehouses to geographic zones for commodity distribution.

**Algorithm**: Set intersection (similar to agency allocator)

* Authorized warehouses (from G2PWarehouseProgramBenefitCode)
* Geographic warehouses (from G2PAdministrativeAreaLargeWarehouseRel)
* Random selection from eligible warehouses
* Logs and continues on missing warehouse (doesn't raise exception)

**Called By**: warehouse\_allocation\_worker

***

**3.3 Geo Resolver (`openg2p-g2p-bridge-geo-resolver`)**

**Purpose**: Resolve geographic zones for beneficiaries.

**Algorithm**: Direct lookup in farmer registry

* Query G2PFarmerRegistry by link\_registry\_id
* Silently skip missing beneficiaries
* Maps both large and small geographic zones

**Called By**: geo\_resolution\_worker

***

**3.4 Bank Connectors (`openg2p-g2p-bridge-bank-connectors`)**

**Purpose**: Interface with sponsor banks for fund management.

**Key Methods**:

* `check_funds(account, currency, amount)` → CheckFundsResponse
* `block_funds(account, currency, amount)` → BlockFundsResponse
* `initiate_payment(List[DisbursementPaymentPayload])` → PaymentResponse
* `retrieve_reconciliation_id()` - Extract transaction ID from response
* `retrieve_beneficiary_name()` - Extract name from response
* `retrieve_reversal_reason()` - Extract reversal reason from response

**Supported Payment Methods**:

* Bank account transfer (IFSC/BIC code)
* Mobile wallet (phone + provider)
* Email wallet (email + provider)

**Implementation**: HTTP-based using httpx with configurable endpoints

**Called By**:

* check\_funds\_with\_bank\_worker
* block\_funds\_with\_bank\_worker
* disburse\_funds\_from\_bank\_worker

***

**3.5 SPAR Mapper (`openg2p-g2p-bridge-mapper-connectors`)**

**Purpose**: Resolve financial addresses for beneficiaries using standardized SPAR protocol.

**Process**:

1. Accepts ResolveRequest with beneficiary IDs
2. Converts to SPAR format (SparResolveRequest)
3. Sends async HTTP POST to SPAR Mapper API
4. Receives ResolveResponse with resolved FAs
5. Extracts: account number, bank code, branch code, mobile, email, provider info

**Features**:

* Async/await pattern for non-blocking I/O
* JWT signature support (configurable)
* Comprehensive error handling
* Per-request HTTP client (avoids Celery fork issues)

**Called By**: mapper\_resolution\_worker

***

**3.6 Notification Connectors (`openg2p-g2p-bridge-notification-connectors`)**

**Purpose**: Send notifications to warehouses, agencies, and beneficiaries.

**Notification Types**:

* WAREHOUSE\_NOTIFICATION (warehouse\_workflow\_id)
* AGENCY\_NOTIFICATION (agency\_workflow\_id)
* BENEFICIARY\_NOTIFICATION (beneficiary\_workflow\_id)

**Implementation**: Novu platform integration

* Uses novu\_py library
* Configurable workflow IDs per notification type
* Sends to recipient email addresses
* Returns NotificationResponse with status (SUCCESS/FAILURE)

**Called By**:

* warehouse\_notification\_worker
* agency\_notification\_worker
* beneficiary\_notification\_worker

***

### End-to-End Data Flow

#### Complete Disbursement Lifecycle

```
1. INITIATION
   ↓
   Partner API: create_disbursement_envelopes()
   ├─ Creates DisbursementEnvelope
   ├─ Creates DisbursementBatchControl (one per program/benefit combo)
   └─ Sets initial statuses to PENDING
   
2. MAPPER RESOLUTION (Financial Address Resolution)
   ↓
   Beat Producer: mapper_resolution_beat_producer
   ├─ Queries PENDING batches
   ├─ Updates to PROCESSING
   └─ Dispatches to queue
   
   Worker: mapper_resolution_worker
   ├─ Gets all disbursements in batch
   ├─ Calls SPAR Mapper async
   ├─ Stores resolved FAs in DisbursementResolutionFinancialAddress
   └─ Updates status to PROCESSED
   
3. FUND MANAGEMENT
   ↓
   a) Check Funds
      Beat: check_funds_with_bank_beat_producer → Worker: check_funds_with_bank_worker
      └─ Calls bank_connector.check_funds() → Updates funds_available_with_bank
   
   b) Block Funds
      Beat: block_funds_with_bank_beat_producer → Worker: block_funds_with_bank_worker
      └─ Calls bank_connector.block_funds() → Stores block reference
   
4. GEOGRAPHIC RESOLUTION
   ↓
   Beat: geo_resolution_beat_producer → Worker: geo_resolution_worker
   ├─ Queries beneficiaries
   ├─ Calls GeoResolver.resolve_geo()
   ├─ Creates DisbursementBatchControlGeo records
   └─ Updates status to PROCESSED
   
5. PARTNER ALLOCATION
   ↓
   a) Warehouse Allocation (for commodities)
      Beat: warehouse_allocation_beat_producer → Worker: warehouse_allocation_worker
      ├─ Groups by large geographic zones
      ├─ Calls WarehouseAllocator.allocate_warehouse()
      └─ Stores warehouse assignments
   
   b) Agency Allocation (for cash payment delivery)
      Beat: agency_allocation_beat_producer → Worker: agency_allocation_worker
      ├─ Groups by small geographic zones
      ├─ Calls AgencyAllocator.allocate_agency()
      ├─ Stores agency assignments in multiple tables
      └─ Sets notification statuses to PENDING (unless suppressed)
   
6. NOTIFICATIONS (if not suppressed)
   ↓
   a) Warehouse Notifications
      Beat: warehouse_notification_beat_producer → Worker: warehouse_notification_worker
      └─ Sends WAREHOUSE_NOTIFICATION via Novu
   
   b) Agency Notifications
      Beat: agency_notification_beat_producer → Worker: agency_notification_worker
      └─ Sends AGENCY_NOTIFICATION via Novu
   
   c) Beneficiary Notifications
      Beat: beneficiary_notification_beat_producer → Worker: beneficiary_notification_worker
      └─ Sends BENEFICIARY_NOTIFICATION via Novu
   
7. DISBURSEMENT EXECUTION
   ↓
   Beat: disburse_funds_from_bank_beat_producer → Worker: disburse_funds_from_bank_worker
   ├─ Groups disbursements by payment method
   ├─ Calls bank_connector.initiate_payment()
   ├─ Stores transaction IDs and payment status
   └─ Updates status to PROCESSED
   
8. RECONCILIATION
   ↓
   Partner uploads MT940 statement: POST /upload_mt940
   ├─ Creates AccountStatement record
   ├─ Sets status to PENDING
   
   Beat: mt940_processor_beat_producer → Worker: mt940_processor_worker
   ├─ Parses MT940 file
   ├─ Extracts transactions and balances
   ├─ Reconciles with disbursement records
   └─ Updates transaction records with bank confirmation
   
9. COMPLETION
   └─ All processing complete, status records available via Partner API
```

***

### Processing Pipeline Architecture

#### State Diagram

```
           PENDING
             ↓
        ┌────────────┐
        │ Validation │
        └────┬───────┘
             ↓
          PROCESSING
             ↓
        ┌────────────┐
        │  Business  │
        │   Logic    │
        └────┬───────┘
             ↓
        ┌────────────┐
        │   Success? │
        └────┬───┬───┘
            yes   no
             │     └──────────────────┐
             ↓                        ↓
          PROCESSED             Increment Attempts
             ↓                        ↓
        Continue Pipeline      ┌──────────────┐
                               │ Max Exceeded?│
                               └──┬──────┬───┘
                                yes    no
                                 │      │
                                 ↓      ↓
                               ERROR  PENDING
                                       (retry)
```

***

### Key Design Patterns

#### 1. Factory Pattern

All extension modules use factory pattern for implementation selection:

```python
# Example: Agency Allocator
allocator = AgencyAllocatorFactory.get_agency_allocator()
allocations = allocator.allocate_agency(small_geo_list, benefit_code, program)
```

This allows custom implementations to be substituted without code changes.

#### 2. Producer-Consumer Pattern

Beat producers and workers follow the producer-consumer pattern:

```
Beat Producer:
  for each pending task:
    update status to PROCESSING
    send_task(worker_name, args=[task_id], queue=...)

Worker:
  fetch task by ID
  execute business logic
  update database with results
```

This decouples task discovery from execution and enables horizontal scaling.

#### 3. Status State Machine

All tasks follow a consistent state machine:

```
PENDING → PROCESSING → PROCESSED (success) or ERROR (max retries exceeded)
                    ↓ (failure, not max retries)
                    PENDING (retry)
```

#### 4. Async Task Execution

SPAR mapper uses async/await for non-blocking I/O:

```python
@celery_app.task(name="mapper_resolution_worker")
def mapper_resolution_worker(batch_id):
    loop = asyncio.new_event_loop()
    try:
        resolve_response = loop.run_until_complete(
            mapper.resolve(request)
        )
    finally:
        loop.close()
```

***

### Configuration and Customization

#### Extension Points

1. **Agency Allocator**: Implement custom agency selection logic
2. **Warehouse Allocator**: Implement custom warehouse selection logic
3. **Bank Connectors**: Implement connectors for specific banks
4. **Notification Connectors**: Implement notification channels (beyond Novu)
5. **Geo Resolver**: Implement custom geographic resolution

#### Configuration Parameters

**Beat Producers**:

* Task frequencies (default: 3600 seconds)
* Number of tasks per cycle (default: 2)
* Stale task threshold (default: 60 minutes)
* Future disbursement processing (default: false)

**Workers**:

* Max retry attempts per task (default: 3)
* Bank connector configurations
* SPAR mapper settings
* Notification settings
* OAuth and key management settings

***

### Security Considerations

#### API Security

* JWT signature validation on all Partner API endpoints (except file upload)
* Request validation framework
* Error code abstraction (no internal details exposed)

#### Data Security

* Database credentials from environment variables
* Separate PBMS database for sensitive program data
* Transaction-based updates with rollback on errors

#### Bank Integration

* API signature support for SPAR mapper
* OAuth integration for bank connectors
* Configurable timeout and retry settings

***

### Scalability and Performance

#### Horizontal Scaling

* **Stateless Workers**: Workers are stateless and can be scaled horizontally
* **Message Queue**: Redis-based queue with consumer groups
* **Database**: Single G2P Bridge DB + PBMS DB (schema supports concurrent access)

#### Performance Optimizations

* **Batch Processing**: Beat producers process limited number of tasks per cycle
* **Configurable Frequencies**: Tune task scheduling based on load
* **Async I/O**: Mapper uses async calls for better concurrency
* **Stale Task Recovery**: Prevents queue overflow from stuck tasks
* **Database Connection Pooling**: SQLAlchemy connection pooling

#### Monitoring Points

* Task queue depth (pending count by status)
* Worker throughput (tasks/minute by type)
* Error rates (failures by task type)
* Processing latency (P50, P95, P99)
* Retry rates (stale task recovery frequency)

***

### Error Handling Strategy

#### Multi-Level Error Handling

1. **Request Validation**: Pre-execution validation in Partner API
2. **Task Execution**: Try-catch in worker tasks
3. **Retry Logic**: Configurable max attempts per task type
4. **Stale Task Recovery**: Automatic recovery of stuck tasks
5. **Error Tracking**: Error codes and messages in database

#### Error Propagation

* Database updates capture error details
* Status field indicates processing state
* Attempt counter tracks retry history
* Error code field stores failure reason

***

### Integration Architecture

#### External System Integration Points

1. **Partner API**: REST interface for external systems
2. **Bank Integration**: Direct connection via bank connectors
3. **SPAR Mapper**: HTTP API for financial address resolution
4. **Notification Service**: Novu platform for message delivery
5. **Statement Upload**: MT940 file upload for reconciliation

#### Internal Module Integration

* **Allocators**: Called by workers via factory pattern
* **Resolvers**: Called by workers for geographic and FA resolution
* **Bank Connectors**: Called by fund-related workers
* **Notification Connectors**: Called by notification workers

***

### Deployment Architecture

#### Components to Deploy

1. **API Server**: Partner API (FastAPI)
2. **Celery Beat**: Beat scheduler (single instance)
3. **Celery Workers**: Worker pool (multiple instances)
4. **Message Queue**: Redis (high availability recommended)
5. **Databases**: G2P Bridge DB + PBMS DB

#### Recommended Topology

```
Load Balancer
    ↓
API Instances (multiple, stateless)
    ↓
Redis Queue (cluster mode recommended)
    ↓
Worker Instances (multiple, auto-scaling)
    ↓
G2P Bridge DB (replicated)
PBMS DB (read replica recommended)
```

***

### Data Models Overview

#### Core Models

* **DisbursementEnvelope**: Container for disbursements
* **DisbursementBatchControl**: Batch-level processing control and status
* **DisbursementBatchControlGeo**: Geographic allocation details
* **Disbursement**: Individual disbursement record
* **DisbursementResolutionGeoAddress**: Geographic resolution results
* **DisbursementResolutionFinancialAddress**: Resolved financial addresses

#### Status Tracking Models

* **EnvelopeBatchStatusForCash**: Cash-specific status (funds available, blocked)
* **DisbursementStatusTracking**: Individual disbursement status
* **AccountStatement**: MT940 file uploads and reconciliation

#### Configuration Models

* **SponsorBankConfiguration**: Bank account and connector settings
* **DisbursementSchedule**: Payment schedule definitions
* **G2PAgency / G2PWarehouse**: Agency and warehouse master data (in PBMS)

***

### Summary of Key Features

#### 1. Multi-Step Processing

* 11 orchestrated task types ensure complete workflow execution
* Configurable sequencing based on benefit type (cash vs. commodity)

#### 2. Flexible Delivery Methods

* Cash disbursements to bank accounts
* Commodity distribution via warehouses
* Agency-based delivery models
* Multiple payment methods (bank, mobile wallet, email wallet)

#### 3. Robust Error Handling

* Automatic retry with configurable attempts
* Stale task detection and recovery
* Granular error tracking per task
* Partial failure support (continue with successful disbursements)

#### 4. Scalability

* Stateless worker design for horizontal scaling
* Message queue-based distribution
* Batch processing to control throughput
* Configurable processing frequencies

#### 5. Extensibility

* Plugin architecture for custom implementations
* Factory pattern for component substitution
* Support for custom allocators, resolvers, and connectors
* Clear interface definitions

#### 6. Observability

* Comprehensive status tracking
* Attempt counts and timestamps
* Error codes and messages
* Queryable state via Partner API

***

### Document Cross-References

For detailed information on specific components, refer to:

1. **01\_AGENCY\_ALLOCATION\_DESIGN.md**: Agency allocator implementation
2. **02\_WAREHOUSE\_ALLOCATION\_DESIGN.md**: Warehouse allocator implementation
3. **03\_GEO\_RESOLUTION\_DESIGN.md**: Geographic zone resolution
4. **04\_SPONSOR\_BANK\_CONNECTION\_DESIGN.md**: Bank connector implementation
5. **05\_NOTIFICATION\_CONNECTION\_DESIGN.md**: Notification service integration
6. **06\_SPAR\_RESOLUTION\_DESIGN.md**: Financial address resolution (SPAR mapper)
7. **PARTNER\_API\_DOCUMENTATION.md**: REST API endpoints and schemas
8. **CELERY\_MODULES\_DESIGN.md**: Detailed task processing architecture

***

### Implementation Roadmap

#### Phase 1: Core Infrastructure

* Set up G2P Bridge database
* Deploy Partner API
* Configure Celery (beat + workers)
* Set up Redis message queue

#### Phase 2: Basic Processing Pipeline

* Implement geo resolution
* Implement agency allocation
* Implement basic fund checks and disbursements
* Set up error handling and retry logic

#### Phase 3: Advanced Features

* Implement SPAR mapper integration
* Implement warehouse allocation
* Implement notification service
* Set up MT940 reconciliation

#### Phase 4: Scaling and Optimization

* Scale worker pool based on throughput requirements
* Optimize database queries
* Implement monitoring and alerting
* Performance tuning

***

### Conclusion

The OpenG2P G2P Bridge is a sophisticated, modular platform designed to manage complex disbursement workflows at scale. The system's architecture emphasizes:

* **Scalability**: Horizontal scaling through stateless workers and message queues
* **Reliability**: Multi-level error handling, retry logic, and stale task recovery
* **Flexibility**: Plugin architecture enabling custom implementations
* **Observability**: Comprehensive status tracking and error reporting
* **Maintainability**: Clear separation of concerns and factory pattern abstractions

By combining a REST API for synchronous operations with Celery-based asynchronous processing, the G2P Bridge can handle the full lifecycle of government-to-person disbursements from initiation through reconciliation.

***

### Glossary

| Term                           | Definition                                                                          |
| ------------------------------ | ----------------------------------------------------------------------------------- |
| **Disbursement Envelope**      | Container for a batch of disbursements, typically for a specific program/benefit    |
| **Disbursement Batch Control** | Control record tracking status and metadata for a batch of disbursements            |
| **Beneficiary**                | Individual recipient of cash or commodity disbursement                              |
| **Sponsor Bank**               | Bank holding government funds for disbursement                                      |
| **Agency**                     | Organization responsible for final delivery of cash to beneficiaries                |
| **Warehouse**                  | Physical distribution center for commodity disbursements                            |
| **Financial Address (FA)**     | Recipient's bank account, mobile wallet, or email wallet details                    |
| **SPAR**                       | Standardized Platform for Address Resolution (financial address resolution service) |
| **Beat Producer**              | Celery task that periodically queries database for work and dispatches to workers   |
| **Worker**                     | Celery task that executes business logic and updates database                       |
| **Process Status**             | State of a task (PENDING, PROCESSING, PROCESSED, ERROR)                             |
| **MT940**                      | SWIFT standard format for bank statement files                                      |
