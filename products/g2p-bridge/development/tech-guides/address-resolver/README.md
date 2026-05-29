---
description: Design & Implementation
---

# Financial address resolver

### Module Information

* **Module Name**: `openg2p-g2p-bridge-mapper-connectors`
* **Location**: `/openg2p-g2p-bridge-mapper-connectors/`
* **Primary Implementation**: `SPARMapper`

***

### Interface Definition

**File**: `interface/mapper_interface.py`

```python
class MapperInterface(BaseService):
    async def resolve(self, resolve_request: ResolveRequest) -> ResolveResponse | None:
        """
        Resolve the given request from Mapper and return the Response.
        """
        pass
```

#### Data Models

**File**: `schemas/resolve_schema.py`

```python
class ResolveRequest(BaseModel):
    beneficiary_ids: List[str]

class ResolveResult(BaseModel):
    id: Optional[str] = None
    fa: Optional[dict] = None
    name: Optional[str] = None
    status: Optional[str] = None
    status_reason_code: Optional[str] = None

class ResolveResponse(BaseModel):
    results: List[ResolveResult]
```

#### Method Parameters

* **resolve\_request** (ResolveRequest): Request object containing:
  * **beneficiary\_ids**: List of strings - IDs of beneficiaries to resolve (typically disbursement IDs)

#### Return Value

* **ResolveResponse | None**: Response containing list of ResolveResult objects, or None if request fails

#### Response Structure

```python
{
    "results": [
        {
            "id": str,                          # Beneficiary/disbursement ID
            "fa": dict,                         # Financial address (structure varies by provider)
            "name": str,                        # Account provider name / bank name
            "status": str,                      # Resolution status (e.g., "active", "inactive")
            "status_reason_code": str           # Reason code for status (e.g., error codes)
        },
        # ... more results
    ]
}
```

***

### Reference Implementation: SPARMapper

**File**: `implementations/spar_mapper.py`

#### Key Components

1. **SPARMapperClient**: HTTP async client for SPAR Mapper API communication
2. **Request Conversion**: Maps bridge format to SPAR format
3. **Response Conversion**: Maps SPAR format back to bridge format
4. **Async Processing**: Uses async/await for non-blocking I/O

#### Algorithm

```
1. Log incoming request
   - Log number of beneficiary IDs
   - Log the actual IDs for debugging

2. Convert ResolveRequest to SPAR ResolveRequest
   - Create SingleResolveRequest for each beneficiary_id
   - Build request header with sender app mnemonic and timestamp
   - Build request payload with transaction_id
   
3. Send SPAR request asynchronously
   - Call client.resolve_request(spar_request) with await
   - Block until response received
   
4. Log response
   - Log response status
   - Log transaction ID
   - Log count of results
   
5. Convert SPAR ResolveResponse to custom ResolveResponse
   - For each single_response in SPAR response:
     a. Extract: id, fa, status, status_reason_code
     b. Extract name from account_provider_info if available
     c. Build ResolveResult object
     d. Add to results list
   
6. Return ResolveResponse
   - Returns ResolveResponse with results list
   - Returns None if any exception occurs during processing
```

#### Request Conversion Detail

The `_convert_to_spar_request` method transforms the bridge ResolveRequest into SPAR format:

```
Input: ResolveRequest with beneficiary_ids: ["id1", "id2", "id3"]

For each beneficiary_id:
  Create SingleResolveRequest:
    - reference_id: beneficiary_id
    - timestamp: ISO format current datetime
    - id: beneficiary_id
    - fa: "" (empty string, will be filled by SPAR)
    - scope: ResolveScope.details
    - locale: "en"

Create ResolveRequestPayload:
  - transaction_id: f"txn_{timestamp_in_seconds}"
  - resolve_request: list of SingleResolveRequest objects

Create G2PRequestHeader:
  - sender_app_mnemonic: "g2p_bridge"
  - sender_app_url: "" (empty)
  - request_id: f"req_{timestamp_in_seconds}"
  - request_timestamp: current datetime

Create final SparResolveRequest:
  - request_header: G2PRequestHeader
  - request_body: ResolveRequestBody with payload
```

#### Response Conversion Detail

The `_convert_from_spar_response` method transforms SPAR response back to bridge format:

```
Input: SparResolveResponse with SPAR structure

For each single_response in response_body.response_payload.resolve_response:
  Extract fields:
    - id_value = single_response.id
    - fa_value = single_response.fa (dict structure from SPAR)
    - status = single_response.status
    - status_reason_code = single_response.status_reason_code
    - name_value = single_response.account_provider_info.name (if exists)
  
  Create ResolveResult:
    - id: id_value
    - fa: fa_value
    - name: name_value
    - status: status
    - status_reason_code: status_reason_code
  
  Add to results list
  Log debug info for each result

Return ResolveResponse:
  - results: List of ResolveResult objects
```

#### Key Characteristics

1. **Async/Await Pattern**: Uses `async def` and `await` for non-blocking I/O
2. **Format Translation**: Converts between bridge and SPAR data formats
3. **Transaction IDs**: Generates unique transaction and request IDs using timestamps
4. **Error Handling**: Returns None on any exception (logs error details)
5. **Graceful Degradation**: Exception returns None rather than raising
6. **Logging**: Uses logger name "spar\_mapper\_impl"
   * INFO: Request received, SPAR conversion details, response received
   * DEBUG: Per-result conversion details
   * ERROR: Exception with full stack trace

***

### SPARMapperClient

**File**: `client/spar_mapper_client.py`

#### Async HTTP Client

```python
class SPARMapperClient(BaseService):
    def __init__(self):
        self.url = _config.spar_mapper_url
        self.api_sign_enabled = _config.spar_mapper_api_sign_enabled
        self.timeout = 30.0

    async def resolve_request(
        self, 
        request: ResolveRequest, 
        headers: dict | None = None
    ) -> ResolveResponse:
        """Send async POST request to SPAR Mapper API"""
```

#### Algorithm

```
1. Serialize request
   - Call request.model_dump(mode="json")
   - Convert to JSON-serializable dict

2. Prepare headers
   - Set content-type to "application/json"
   
3. Add JWT signature if enabled
   - If api_sign_enabled is True:
     a. Call crypto_helper.create_jwt_token(payload) with await
     b. Add to headers["Signature"]

4. Log request
   - Log target URL
   - Log (debug) request payload

5. Create async HTTP client and send POST
   - Use httpx.AsyncClient with 30 second timeout
   - POST to spar_mapper_url
   - Send payload as JSON using orjson.dumps()
   - Include prepared headers
   - Call raise_for_status() for error checking

6. Parse response
   - Get JSON response data
   - Parse and validate as ResolveResponse

7. Log response
   - Log response status
   - Log count of results returned

8. Return ResolveResponse
   - Return parsed and validated response object

Error Handling:
  - HTTPStatusError: Raise BaseAppException with HTTP status code
  - Other exceptions: Raise BaseAppException with code "500"
  - Both log with full exception info
```

#### Configuration

**File**: `config.py`

Configuration uses Pydantic Settings with environment variable prefix `g2p_bridge_mapper_connectors_`:

```python
class Settings(BaseSettings):
    spar_mapper_url: str = "http://localhost:8080/mapper/resolve"
    spar_mapper_api_sign_enabled: bool = False
    spar_mapper_api_sign_crypto_helper_name: str = "spar_mapper_crypto"
```

#### Configuration Parameters

| Parameter                                 | Default Value                          | Purpose                              |
| ----------------------------------------- | -------------------------------------- | ------------------------------------ |
| `spar_mapper_url`                         | `http://localhost:8080/mapper/resolve` | SPAR Mapper API endpoint URL         |
| `spar_mapper_api_sign_enabled`            | `False`                                | Enable JWT signature verification    |
| `spar_mapper_api_sign_crypto_helper_name` | `spar_mapper_crypto`                   | Crypto helper component name for JWT |

#### HTTP Client Details

* **Library**: `httpx` (async HTTP client)
* **Timeout**: 30 seconds
* **Method**: POST
* **Serialization**: `orjson.dumps()` with sorted keys
* **Headers**: Content-Type application/json, optional Signature header
* **Error Handling**: `raise_for_status()` converts 4xx/5xx to HTTPStatusError
* **Context Manager**: Uses `async with httpx.AsyncClient(...)` for resource cleanup

***

### Factory Pattern

**File**: `factory/mapper_factory.py`

```python
class MapperFactory(BaseService):
    @staticmethod
    def get_mapper() -> MapperInterface:
        return SPARMapper.get_component()
```

***

### SPAR Models Integration

The implementation uses models from `openg2p_spar_models`:

#### SPAR Request Structure

* **SparResolveRequest**: Top-level request with request\_header and request\_body
* **G2PRequestHeader**: Sender information and request metadata
* **ResolveRequestBody**: Contains request payload
* **ResolveRequestPayload**: Contains list of SingleResolveRequest
* **SingleResolveRequest**: Individual beneficiary resolution request with id, fa, scope, locale
* **ResolveScope**: Enum with values like `details`

#### SPAR Response Structure

* **SparResolveResponse**: Top-level response with response\_header and response\_body
* **ResolveResponsePayload**: Contains list of SingleResolveResponse (results)
* **SingleResolveResponse**: Individual result with id, fa, status, status\_reason\_code, account\_provider\_info
* **AccountProviderInfo**: Contains name and other provider details

***

### Data Flow Diagram

```
Bridge Process
    |
    v
ResolveRequest (beneficiary_ids)
    |
    v
SPARMapper.resolve()
    |
    +---> _convert_to_spar_request()
    |     Creates SingleResolveRequest for each ID
    |     Builds request header and payload
    |     Returns SparResolveRequest
    |
    +---> SPARMapperClient.resolve_request() [ASYNC]
    |     Serializes request to JSON
    |     Adds JWT signature if enabled
    |     POSTs to spar_mapper_url
    |     Returns SparResolveResponse
    |
    +---> _convert_from_spar_response()
    |     Extracts results from SPAR response
    |     Maps to ResolveResult objects
    |     Returns ResolveResponse
    |
    v
ResolveResponse (with results)
     OR
    None (on error)
```

***

### Logging

All logging uses logger name: `spar_mapper_impl`

* INFO: Request received with count of IDs
* INFO: Disbursement IDs being processed
* INFO: SPAR request conversion details with transaction\_id
* INFO: Request completed successfully
* INFO: Response status and transaction ID
* INFO: Number of resolve results returned
* DEBUG: Per-result conversion details (id, fa, name, status, status\_reason)
* ERROR: Exception with full stack trace

SPARMapperClient uses logger: `spar_mapper_client`

* INFO: Request being sent to URL
* DEBUG: Request payload
* INFO: Response received with text
* INFO: Response status and result count
* EXCEPTION: HTTP and unknown errors

***

### Integration Pattern

```python
# Typical Celery worker usage - async context required
from ..factory.mapper_factory import MapperFactory

# In async function
mapper = MapperFactory.get_mapper()

resolve_request = ResolveRequest(
    beneficiary_ids=[
        "BENE-001",
        "BENE-002",
        "BENE-003"
    ]
)

resolve_response = await mapper.resolve(resolve_request)

if resolve_response:
    for result in resolve_response.results:
        print(f"ID: {result.id}")
        print(f"Name: {result.name}")
        print(f"FA: {result.fa}")
        print(f"Status: {result.status}")
        
        if result.status != "active":
            # Handle inactive accounts
            # Log status_reason_code for debugging
            log.warning(f"Inactive account {result.id}: {result.status_reason_code}")
else:
    # Handle resolution failure
    log.error("Failed to resolve beneficiaries")
```

***

### Error Handling

1. **HTTP Errors**: SPARMapperClient raises BaseAppException with HTTP status code
2. **JSON Parsing Errors**: SPARMapperClient raises BaseAppException with code "500"
3. **Request Conversion Errors**: SPARMapper catches and logs, returns None
4. **Response Conversion Errors**: SPARMapper catches and logs, returns None
5. **Any Exception**: SPARMapper returns None and logs full stack trace

No exceptions propagate from SPARMapper to caller; always check for None response.

***

### Key Implementation Notes

1. **Async-Required**: The resolve method is async; must be called with `await` and in async context
2. **Generator-Based IDs**: Uses current timestamp for transaction and request IDs (not cryptographically unique)
3. **Scope Fixed to Details**: Always requests ResolveScope.details; no parameter to change scope
4. **Empty FA on Request**: Sends empty string for `fa` in request; SPAR fills this in response
5. **Locale Fixed to English**: Always uses "en" locale; no parameter to change
6. **JWT Signing Optional**: API signature only added if `spar_mapper_api_sign_enabled` is True
7. **Per-Request Client**: Creates new httpx.AsyncClient for each request (avoids Celery fork worker issues)
8. **Crypto Helper**: Uses cached\_property to lazily initialize CryptoHelper component

***

### Performance Considerations

1. **Async I/O**: Non-blocking HTTP request allows concurrent execution of multiple mapper calls
2. **Single HTTP Request**: All beneficiary IDs resolved in one POST request (not batched separately)
3. **Response Parsing**: Uses Pydantic validation for type safety
4. **No Caching**: Every resolve call hits the SPAR Mapper API (no local cache)
5. **Timeout**: 30-second timeout prevents indefinite hangs

***

### Limitations/Considerations

1. Beneficiary IDs converted to strings; no validation of ID format
2. No batch size limits; large lists of IDs sent in single request
3. Scope and locale are hardcoded; no flexibility in request parameters
4. Returns None on any error; caller cannot distinguish different failure modes
5. No retry logic in mapper implementation; Celery task retries handle failures
6. FA structure varies by provider; no validation or transformation applied
7. Account provider info optional in response; name may be None
8. No support for multiple locales despite locale parameter
9. SPAR Mapper endpoint URL must be accessible; no fallback mechanisms
10. JWT signing uses crypto helper component; requires proper configuration if enabled
