---
description: OpenG2P G2P Bridge Partner API Documentation
---

# Partner APIs

### Overview

The Partner API module (`openg2p-g2p-bridge-partner-api`) provides a comprehensive set of REST APIs for partner systems to interact with the G2P Bridge. The APIs handle disbursement operations, status inquiries, and account statement uploads, with all requests authenticated using JWT signature validation.

**Module Location**: `openg2p-g2p-bridge/openg2p-g2p-bridge-partner-api`

***

### Authentication

All API endpoints (except account statement upload) require JWT signature validation. The signature is validated using the `JWTSignatureValidator` dependency from `openg2p_fastapi_partner_auth`.

* **Validator**: `JWTSignatureValidator()`
* **Requirement**: All requests must include valid JWT signatures
* **Error Code on Invalid Signature**: Request validation error

***

### API Endpoints

#### 1. Disbursement Controller

**Base Tag**: `G2P Bridge Disbursement Envelope`

**1.1 Create Disbursements**

**Endpoint**: `POST /create_disbursements`

**Description**: Create new disbursements for a batch of beneficiaries.

**Request Body**:

* **Type**: `DisbursementRequest`
* **Authentication**: JWT Signature validation required

**Response**:

* **Type**: `DisbursementResponse`
* **HTTP Status**: 200 (OK)

**Process**:

1. Validates JWT signature
2. Validates disbursement request structure
3. Calls disbursement service to create disbursements
4. Returns list of created disbursement payloads with unique IDs
5. Returns error response if validation or creation fails

**Error Handling**:

* **RequestValidationException**: Returns error response with validation error code
* **DisbursementException**: Returns error response with disbursement error code and partial payloads

**Example**:

```
POST /create_disbursements
Content-Type: application/json

{
  "disbursement_request_data": {...}
}
```

***

**1.2 Cancel Disbursements**

**Endpoint**: `POST /cancel_disbursements`

**Description**: Cancel existing disbursements.

**Request Body**:

* **Type**: `DisbursementRequest`
* **Authentication**: JWT Signature validation required

**Response**:

* **Type**: `DisbursementResponse`
* **HTTP Status**: 200 (OK)

**Process**:

1. Validates JWT signature
2. Validates disbursement request structure
3. Calls disbursement service to cancel disbursements
4. Returns list of cancelled disbursement payloads
5. Returns error response if validation or cancellation fails

**Error Handling**:

* **RequestValidationException**: Returns error response with validation error code
* **DisbursementException**: Returns error response with disbursement error code and partial payloads

***

#### 2. Disbursement Envelope Controller

**Base Tag**: `G2P Bridge Disbursement Envelope`

**2.1 Create Disbursement Envelopes**

**Endpoint**: `POST /create_disbursement_envelopes`

**Description**: Bulk create disbursement envelopes. An envelope is a container for multiple disbursements.

**Request Body**:

* **Type**: `DisbursementEnvelopeRequest`
* **Authentication**: JWT Signature validation required

**Response**:

* **Type**: `DisbursementEnvelopeResponse`
* **HTTP Status**: 200 (OK)

**Process**:

1. Validates JWT signature
2. Validates disbursement envelope request structure
3. Calls disbursement envelope service to create envelopes
4. Returns list of created disbursement envelope payloads
5. Returns error response if validation or creation fails

**Error Handling**:

* **RequestValidationException**: Returns error response with validation error code
* **DisbursementEnvelopeException**: Returns error response with envelope creation error code

**Example**:

```
POST /create_disbursement_envelopes
Content-Type: application/json

{
  "envelopes": [...]
}
```

***

**2.2 Cancel Disbursement Envelope**

**Endpoint**: `POST /cancel_disbursement_envelope`

**Description**: Cancel an existing disbursement envelope. Cancelling an envelope cancels all disbursements within it.

**Request Body**:

* **Type**: `DisbursementEnvelopeRequest`
* **Authentication**: JWT Signature validation required

**Response**:

* **Type**: `DisbursementEnvelopeResponse`
* **HTTP Status**: 200 (OK)

**Process**:

1. Validates JWT signature
2. Validates disbursement envelope request structure
3. Calls disbursement envelope service to cancel envelope
4. Returns cancelled disbursement envelope payload
5. Returns error response if validation or cancellation fails

**Error Handling**:

* **RequestValidationException**: Returns error response with validation error code
* **DisbursementEnvelopeException**: Returns error response with envelope cancellation error code

***

**2.3 Amend Disbursement Envelope**

**Endpoint**: `POST /amend_disbursement_envelope`

**Description**: Amend/modify an existing disbursement envelope.

**Request Body**:

* **Type**: `DisbursementEnvelopeRequest`
* **Authentication**: JWT Signature validation required

**Response**:

* **Type**: `DisbursementEnvelopeResponse`
* **HTTP Status**: 200 (OK)

**Process**:

1. Validates JWT signature
2. Validates disbursement envelope request structure
3. Calls disbursement envelope service to amend envelope
4. Returns amended disbursement envelope payload
5. Returns error response if validation or amendment fails

**Error Handling**:

* **RequestValidationException**: Returns error response with validation error code
* **DisbursementEnvelopeException**: Returns error response with envelope amendment error code

***

#### 3. Disbursement Status Controller

**Base Tag**: `G2P Bridge Disbursement Status`

**3.1 Get Disbursement Status**

**Endpoint**: `POST /get_disbursement_status`

**Description**: Retrieve the current status of one or more disbursements.

**Request Body**:

* **Type**: `DisbursementStatusRequest`
* **Authentication**: JWT Signature validation required

**Response**:

* **Type**: `DisbursementStatusResponse`
* **HTTP Status**: 200 (OK)

**Process**:

1. Validates JWT signature
2. Validates disbursement status request structure
3. Calls disbursement status service to retrieve status payloads
4. Constructs success response with status information
5. Returns error response if validation or retrieval fails

**Error Handling**:

* **RequestValidationException**: Returns error response with validation error code
* **DisbursementException**: Returns error response with disbursement error code

**Response Data**:

* Returns list of `DisbursementStatusPayload` objects containing current status of requested disbursements

***

**3.2 Get Disbursement Batch Control**

**Endpoint**: `POST /get_disbursement_batch_control`

**Description**: Retrieve batch-level control information and status for a disbursement batch.

**Request Body**:

* **Type**: `DisbursementBatchControlRequest`
* **Authentication**: JWT Signature validation required

**Response**:

* **Type**: `DisbursementBatchControlResponse`
* **HTTP Status**: 200 (OK)

**Process**:

1. Validates JWT signature
2. Validates disbursement batch control request structure
3. Calls disbursement status service to retrieve batch control payload
4. Constructs success response with batch control information
5. Returns error response if validation or retrieval fails

**Error Handling**:

* **RequestValidationException**: Returns error response with validation error code
* **Generic Exception**: Returns error response with "internal\_error" code

**Response Data**:

* Returns `DisbursementBatchControlPayload` containing batch-level information (totals, counts, status)

***

#### 4. Disbursement Envelope Status Controller

**Base Tag**: `G2P Bridge Disbursement Envelope Status`

**4.1 Get Disbursement Envelope Status**

**Endpoint**: `POST /get_disbursement_envelope_status`

**Description**: Retrieve the current status of a disbursement envelope and its enclosed disbursements.

**Request Body**:

* **Type**: `DisbursementEnvelopeStatusRequest`
* **Authentication**: JWT Signature validation required

**Response**:

* **Type**: `DisbursementEnvelopeStatusResponse`
* **HTTP Status**: 200 (OK)

**Process**:

1. Validates JWT signature
2. Validates disbursement envelope status request structure
3. Calls disbursement envelope status service to retrieve status
4. Constructs success response with envelope status information
5. Returns error response if validation or retrieval fails

**Error Handling**:

* **RequestValidationException**: Returns error response with validation error code
* **DisbursementStatusException**: Returns error response with status retrieval error code

**Response Data**:

* Returns `DisbursementEnvelopeStatusPayload` containing envelope status and enclosed disbursement statuses

***

#### 5. Account Statement Controller

**Base Tag**: `G2P Bridge Account Statement`

**5.1 Upload MT940**

**Endpoint**: `POST /upload_mt940`

**Description**: Upload a bank account statement in MT940 format. MT940 is a standardized SWIFT format for bank statements.

**Request**:

* **Method**: POST (multipart/form-data)
* **Parameter**: `statement_file` (File upload, required)
* **Authentication**: NO JWT signature validation required

**Response**:

* **Type**: `AccountStatementResponse`
* **HTTP Status**: 200 (OK)

**Process**:

1. Validates uploaded file exists
2. Validates file format is valid MT940
3. Calls account statement service to process and store statement
4. Returns account statement ID and success response
5. Returns error response if validation or upload fails

**Error Handling**:

* **RequestValidationException**: Returns error response with REQUEST\_VALIDATION\_ERROR code
* **AccountStatementException**: Returns error response with STATEMENT\_UPLOAD\_ERROR code

**Response Data**:

* Returns success response containing the unique account statement ID assigned to the upload

**Example**:

```
POST /upload_mt940
Content-Type: multipart/form-data

statement_file: [MT940 file content]
```

***

### Request/Response Schema Overview

#### Common Response Structure

All API responses follow a standard structure:

**Success Response**:

```json
{
  "status": "success",
  "code": "200",
  "message": "Operation completed successfully",
  "data": {
    // Response-specific data
  }
}
```

**Error Response**:

```json
{
  "status": "error",
  "code": "ERROR_CODE",
  "message": "Error description",
  "data": null
}
```

#### Disbursement Request

**Type**: `DisbursementRequest`

Used for creating and cancelling disbursements.

**Key Fields**:

* Disbursement details (amount, currency, beneficiary info)
* Batch control information
* Payment method details

#### Disbursement Response

**Type**: `DisbursementResponse`

Returns list of disbursement payloads and status information.

#### Disbursement Envelope Request

**Type**: `DisbursementEnvelopeRequest`

Used for creating, cancelling, and amending disbursement envelopes.

#### Disbursement Envelope Response

**Type**: `DisbursementEnvelopeResponse`

Returns disbursement envelope payload(s) with status.

#### Disbursement Status Request

**Type**: `DisbursementStatusRequest`

Parameters to query disbursement status.

#### Disbursement Status Response

**Type**: `DisbursementStatusResponse`

Returns list of disbursement status payloads.

#### Disbursement Batch Control Request

**Type**: `DisbursementBatchControlRequest`

Parameters to query batch control information.

#### Disbursement Batch Control Response

**Type**: `DisbursementBatchControlResponse`

Returns batch control payload with aggregated information.

#### Disbursement Envelope Status Request

**Type**: `DisbursementEnvelopeStatusRequest`

Parameters to query envelope status.

#### Disbursement Envelope Status Response

**Type**: `DisbursementEnvelopeStatusResponse`

Returns envelope status payload.

#### Account Statement Response

**Type**: `AccountStatementResponse`

Returns account statement ID and upload status.

***

### Error Codes and Exceptions

The Partner API handles several types of errors:

#### Exception Types

1. **RequestValidationException**
   * Raised when request validation fails
   * Includes error code indicating validation failure
   * Returned in HTTP 200 with error status
2. **DisbursementException**
   * Raised during disbursement creation/cancellation
   * Includes error code and partially processed payloads
   * Allows caller to identify which disbursements failed
3. **DisbursementEnvelopeException**
   * Raised during envelope operations
   * Includes error code for envelope-specific failures
4. **DisbursementStatusException**
   * Raised during status retrieval operations
   * Includes error code for status-related errors
5. **AccountStatementException**
   * Raised during statement upload/processing
   * Includes error code for statement-specific failures

#### Error Code Usage

* All endpoints return HTTP 200 even for errors (consistent with G2P Bridge pattern)
* Error details are in the response body with appropriate error code
* Callers should check response status field (not HTTP status) to determine success/failure

***

### Request Validation

All endpoints perform validation through the `RequestValidation` service:

1. **Signature Validation** (Disbursement/Status/Envelope APIs):
   * Validates JWT signature using `JWTSignatureValidator`
   * Rejects requests with invalid signatures
2. **Request Structure Validation** (All endpoints):
   * Validates required fields are present
   * Validates data types and formats
   * May validate business rules (e.g., amounts, dates)
3. **File Validation** (Account Statement):
   * Validates file is present
   * Validates file format is valid MT940

***

### API Flow Examples

#### Example 1: Create Disbursements Workflow

```
1. Partner calls POST /create_disbursements
2. API validates JWT signature
3. API validates disbursement request structure
4. Service creates disbursements in database
5. Returns DisbursementResponse with created disbursement IDs
6. Partner receives response and processes results
```

#### Example 2: Check Disbursement Status Workflow

```
1. Partner calls POST /get_disbursement_status
2. API validates JWT signature
3. API validates status request parameters
4. Service queries database for disbursement status
5. Returns DisbursementStatusResponse with current status
6. Partner receives and displays status to user
```

#### Example 3: Upload Bank Statement Workflow

```
1. Partner calls POST /upload_mt940 with MT940 file
2. API validates file presence and format
3. Service parses and processes MT940 file
4. Service stores statement in database
5. Returns AccountStatementResponse with statement ID
6. Partner receives statement ID for future reference
```

***

### Service Components

The Partner API uses the following service components:

1. **DisbursementService**: Handles disbursement creation and cancellation
2. **DisbursementEnvelopeService**: Manages envelope lifecycle operations
3. **DisbursementStatusService**: Retrieves disbursement and batch status information
4. **DisbursementEnvelopeStatusService**: Retrieves envelope status
5. **AccountStatementService**: Processes and stores account statements
6. **RequestValidation**: Validates all incoming requests

***

### Configuration

Configuration is loaded from `Settings` class:

* Logging configuration: Uses `logging_default_logger_name` from settings
* Logger instances created with module-specific names

***

### Logging

All controllers log using the configured logger:

* **INFO**: Start of operations, successful completions
* **ERROR**: Validation failures, service errors
* **DEBUG**: Detailed request/response information

***

### Base Controller

All controllers extend `BaseController` from `openg2p_fastapi_common.controller`, providing:

* FastAPI router setup
* Tag management for API documentation
* Request/response handling
* Common patterns for API route registration

***

### Summary Table

| Endpoint                            | Method | Auth Required | Purpose                       |
| ----------------------------------- | ------ | ------------- | ----------------------------- |
| `/create_disbursements`             | POST   | Yes           | Create new disbursements      |
| `/cancel_disbursements`             | POST   | Yes           | Cancel disbursements          |
| `/create_disbursement_envelopes`    | POST   | Yes           | Create disbursement envelopes |
| `/cancel_disbursement_envelope`     | POST   | Yes           | Cancel disbursement envelope  |
| `/amend_disbursement_envelope`      | POST   | Yes           | Amend disbursement envelope   |
| `/get_disbursement_status`          | POST   | Yes           | Retrieve disbursement status  |
| `/get_disbursement_batch_control`   | POST   | Yes           | Retrieve batch control info   |
| `/get_disbursement_envelope_status` | POST   | Yes           | Retrieve envelope status      |
| `/upload_mt940`                     | POST   | No            | Upload bank statement file    |

***

### Notes

1. All endpoints use POST method for consistency (including GET-like operations)
2. HTTP status code is always 200; check response body for actual status
3. Responses are async (using `async def`)
4. All disbursement operations support partial failures with detailed error reporting
5. Account statement upload does not require JWT signature validation
6. All date/time values should follow ISO 8601 format
