# Audit trail for Write Operations

**Capture user\_id from JWT Access Token**

_April 2026_

***

### Table of Contents

1. [Executive Summary](https://claude.ai/local_sessions/local_6b9a08db-4fa7-4595-998a-cfa5a5aee039#executive-summary)
2. [Architecture Overview](https://claude.ai/local_sessions/local_6b9a08db-4fa7-4595-998a-cfa5a5aee039#architecture-overview)
3. [Implementation Strategy](https://claude.ai/local_sessions/local_6b9a08db-4fa7-4595-998a-cfa5a5aee039#implementation-strategy)
4. [Database Schema](https://claude.ai/local_sessions/local_6b9a08db-4fa7-4595-998a-cfa5a5aee039#database-schema)
5. [Security Considerations](https://claude.ai/local_sessions/local_6b9a08db-4fa7-4595-998a-cfa5a5aee039#security-considerations)
6. [Implementation Checklist](https://claude.ai/local_sessions/local_6b9a08db-4fa7-4595-998a-cfa5a5aee039#implementation-checklist)

***

### Executive Summary

This design document specifies a middleware approach to automatically capture the user\_id from JWT access tokens and inject it into all write operations across the OpenG2P Registry Gen2 system. The solution eliminates the need for UI clients to explicitly send user\_id, reduces code duplication, and maintains complete audit trails across all registry operations.

#### Key Benefits

* **Zero UI Changes Required** – The token is already being sent; user\_id is extracted server-side
* **Leverages Existing IAM Infrastructure** – Reuses established authentication and token validation
* **Single Point of Configuration** – All write operations use the same dependency; change once, affects everywhere
* **Maintains Backwards Compatibility** – Non-authenticated endpoints and existing reads are unaffected
* **Consistent with FastAPI Best Practices** – Follows standard dependency injection patterns

***

### Architecture Overview

#### The Core Idea

Extract the user\_id from the authenticated JWT token (already validated by existing IAM middleware) and store it in a request-scoped context that all write operations can access without explicit UI transmission. FastAPI's dependency injection system combined with request state provides the mechanism for this pattern.

The user\_id comes from the `subject` claim in the OIDC token, which is the unique identifier for the authenticated user and is guaranteed to be present in all validated tokens.

#### Existing Infrastructure

The registry already implements:

* **AuthMiddleware** that validates JWT tokens and populates `request.state.auth_principal`
* **IAM Service Integration** for OIDC/OAuth2.0 token generation and validation
* **Token Claims** with the subject claim containing the user's unique identifier
* **FastAPI Framework** with built-in dependency injection capabilities

This design builds on top of these existing components without requiring additional authentication infrastructure.

***

### Implementation Strategy

#### Layer 1: Enhance AuthMiddleware

Extend the existing AuthMiddleware to extract and store the user\_id in request state after token validation.

**Implementation Location:**

In the middleware's post-token-validation step, after `request.state.auth_principal` is populated:

```python
# Extract user_id from auth_principal
user_id = auth_principal.subject  # Standard OIDC subject claim
request.state.user_id = user_id
```

**Key Point:** The `subject` claim in OIDC tokens is the unique identifier for the authenticated user and is guaranteed to be present in all validated tokens by the OIDC specification.

***

#### Layer 2: Create User ID Dependency

Define a FastAPI dependency that retrieves the user\_id from request state and makes it available to all write operation handlers.

```python
from fastapi import Depends, HTTPException, Request

async def get_current_user_id(request: Request) -> str:
    """
    Extract user_id from request state (populated by AuthMiddleware).
    
    Returns:
        str: The authenticated user's ID from the JWT subject claim
        
    Raises:
        HTTPException: 401 if user_id is not found in request state
    """
    user_id = getattr(request.state, 'user_id', None)
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="User ID not found in token"
        )
    return user_id
```

**Purpose:** This dependency handles the defensive check that user\_id is present, raising an authentication error if the middleware didn't populate it correctly. In normal operation, all authenticated requests will have user\_id populated.

***

#### Layer 3: Add Dependency to Write Operations

Modify all write operation endpoints to include the user\_id dependency. The following operations require modification:

**Change Request Operations:**

* `POST /change-request` → `create_change_request()`
* `PATCH /change-request/{id}/verify` → `verify_change_request()`
* `PATCH /change-request/{id}/approve` → `approve_change_request()`

**Intake Form Operations:**

* `POST /intake-form` → `create_intake_form()`
* `PATCH /intake-form/{id}/verify` → `verify_intake_form()`
* `PATCH /intake-form/{id}/approve` → `approve_intake_form()`

**Verification Log Operations (CRITICAL - Fixes Existing TODO):**

* `POST /verifications/add_verification` → `add_verification()`
  * **Note:** Currently hardcodes `verified_by="system"` in the codebase (TODO comment present)
  * Our middleware will inject actual user\_id from JWT token
  * This will populate `verified_by` field correctly with authenticated user

**Example Endpoint Modification**

**Before:**

```python
@router.post("/change-request")
async def create_change_request(
    request_data: ChangeRequestCreate,
    db: Session = Depends(get_db)
):
    # user_id would have been in request_data (not recommended)
    return change_request_service.create(request_data, db=db)
```

**After:**

```python
@router.post("/change-request")
async def create_change_request(
    request_data: ChangeRequestCreate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    # user_id is automatically injected from the JWT token
    # The service receives user_id alongside the request data
    return change_request_service.create(
        request_data,
        user_id=user_id,
        db=db
    )
```

**Key Point**

The UI client **does not send user\_id**. The FastAPI framework automatically calls `get_current_user_id()` and passes the result to the handler. This is **zero additional work for the UI layer** – the token it already sends is sufficient.

**Benefits:**

* UI developers don't need to be aware of user\_id handling
* No opportunity for user ID spoofing at the UI level
* User\_id is always from a validated JWT token

***

#### Layer 4: Service Layer Implementation

Modify your service methods to accept and use the user\_id parameter. The service layer receives user\_id from the controller and stores it in the appropriate database field.

```python
from datetime import datetime
from sqlalchemy.orm import Session

class ChangeRequestService:
    def create(
        self,
        data: ChangeRequestCreate,
        user_id: str,
        db: Session
    ) -> G2PChangeRequest:
        """
        Create a new change request with audit trail.
        
        Args:
            data: The change request data from the request body
            user_id: User ID from the JWT subject claim (injected by dependency)
            db: Database session
            
        Returns:
            The created G2PChangeRequest instance
        """
        change_request = G2PChangeRequest(
            **data.dict(),
            created_by=user_id,
            created_at=datetime.utcnow()
        )
        db.add(change_request)
        db.commit()
        db.refresh(change_request)
        return change_request
    
    def verify(
        self,
        change_request_id: str,
        verification_data: dict,
        user_id: str,
        db: Session
    ) -> G2PChangeRequest:
        """Verify a change request and record who verified it."""
        cr = db.query(G2PChangeRequest).filter(
            G2PChangeRequest.id == change_request_id
        ).first()
        
        cr.verified_by = user_id
        cr.verified_at = datetime.utcnow()
        cr.verification_status = "VERIFIED"
        
        db.commit()
        db.refresh(cr)
        return cr
    
    def approve(
        self,
        change_request_id: str,
        user_id: str,
        db: Session
    ) -> G2PChangeRequest:
        """Approve a change request and record who approved it."""
        cr = db.query(G2PChangeRequest).filter(
            G2PChangeRequest.id == change_request_id
        ).first()
        
        cr.approved_by = user_id
        cr.approved_at = datetime.utcnow()
        cr.approval_status = "APPROVED"
        
        db.commit()
        db.refresh(cr)
        return cr
```

**Design Pattern:** The `created_by`, `verified_by`, and `approved_by` fields are already part of the audit trail design. The service layer simply fills them from the JWT token rather than relying on the UI to send them.

***

### Database Schema

#### Overview of Affected Tables

The middleware will inject user\_id into write operations affecting:

1. **G2PChangeRequest** – For create/verify/approve operations
2. **G2PIntakeForm** – For create/verify/approve operations
3. **G2PRegisterVerification** – **Verification log table (critical for this design)**

#### G2PRegisterVerification Table (Verification Log)

This existing table stores audit trail of all verifications performed on change requests and intake forms. **Multiple verifications can exist per change\_request or intake\_form.**

**Current Structure:**

| Field                       | Type          | Nullable | Purpose                                                              |
| --------------------------- | ------------- | -------- | -------------------------------------------------------------------- |
| `verification_id`           | String (UUID) | No       | Unique identifier for each verification record                       |
| `register_id`               | String        | No       | References the register being verified                               |
| `change_request_id`         | String        | Yes      | Links to G2PChangeRequest (mutually exclusive with submission\_id)   |
| `submission_id`             | String        | Yes      | Links to G2PIntakeForm (mutually exclusive with change\_request\_id) |
| `verified_by`               | String        | No       | **User ID who performed verification** ← Middleware injects this     |
| `verified_at`               | DateTime      | No       | Timestamp when verification occurred                                 |
| `verification_observations` | Text          | Yes      | Optional verification notes                                          |
| `is_approved`               | Boolean       | No       | Whether this verification is approved                                |

**Parent Entity Tracking:**

Both G2PChangeRequest and G2PIntakeForm track verification progress:

* `no_of_verifications_required` – How many verifications needed
* `no_of_verifications_done` – Incremented when new verification added

#### Critical: Resolving Existing TODO

**Current Codebase State:** The `add_verification()` service currently has a TODO comment:

```python
# TODO: verified_by should use authenticated user context instead of hardcoded "system"
verified_by = "system"  # Hardcoded value
```

**Our Solution:** The middleware will inject the actual authenticated user\_id from the JWT token into the `add_verification()` operation, replacing the hardcoded "system" string with the real user who performed the verification.

#### Service Operations Requiring user\_id

**G2PChangeRequest/G2PIntakeForm:**

```python
# Existing fields to be populated from middleware
created_by = Column(String(255), nullable=False)
created_at = Column(DateTime, nullable=False)
verified_by = Column(String(255), nullable=True)  # From latest verification
verified_at = Column(DateTime, nullable=True)     # From latest verification
approved_by = Column(String(255), nullable=True)
approved_at = Column(DateTime, nullable=True)
```

**G2PRegisterVerification (Add Verification):**

```python
class AddVerificationService:
    def add_verification(
        self,
        change_request_id: str | None,
        submission_id: str | None,
        verification_observations: str | None,
        is_approved: bool,
        user_id: str,  # ← Injected by middleware
        db: Session
    ) -> VerificationData:
        """Create verification log entry with authenticated user."""
        verification = G2PRegisterVerification(
            verification_id=uuid4(),
            register_id=register.id,
            change_request_id=change_request_id,
            submission_id=submission_id,
            verified_by=user_id,  # ← From JWT token
            verified_at=datetime.utcnow(),
            verification_observations=verification_observations,
            is_approved=is_approved
        )
        db.add(verification)
        # Also update parent counter
        if change_request_id:
            parent.no_of_verifications_done += 1
        else:
            parent.no_of_verifications_done += 1
        db.commit()
        return verification
```

***

### Security Considerations

#### 5.1 Token Validation

The user\_id is extracted from a validated JWT token signed by the IAM service. No additional validation is required because:

* **Signature Verified:** The token signature has already been verified by AuthMiddleware
* **Expiry Checked:** The token expiry has been checked during validation
* **Cannot Be Forged:** The subject claim (user\_id) cannot be forged without access to IAM's private key
* **Authentication Boundary Established:** The trust boundary is already established by the IAM service's token generation

The entire security model relies on the validity of the JWT signature, which is the standard for OAuth2.0 and OIDC implementations.

#### 5.2 Request Scope Isolation

Each HTTP request in FastAPI has its own request state object (`request.state`). This provides natural request-scoped isolation:

* **No Cross-Request Leakage:** User ID from Request A cannot leak into Request B
* **Concurrent Request Safety:** Concurrent requests maintain separate state objects
* **Automatic Cleanup:** State is automatically cleaned up after request completion

FastAPI's request handling is thread-safe and async-safe, so this isolation is guaranteed by the framework.

#### 5.3 Audit Trail Integrity

The user\_id stored in `created_by`, `verified_by`, and `approved_at` fields provides:

* **Immutable Audit Record:** Documents who performed each operation
* **Accountability:** All mutations to registrant data are attributable to a specific user
* **Compliance Ready:** Data for compliance and regulatory reporting
* **Operational Traceability:** Enables audits of who made what changes and when

The audit trail is created at the moment of operation, making it tamper-evident (if properly protected at the database level).

#### 5.4 Defensive Programming

The `get_current_user_id()` dependency includes defensive error handling:

```python
def get_current_user_id(request: Request) -> str:
    user_id = getattr(request.state, 'user_id', None)
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token")
    return user_id
```

**Defensive Benefits:**

* Returns 401 Unauthorized if user\_id is missing from request state
* Catches configuration errors or unexpected middleware failures
* Prevents silent failures that could corrupt audit records
* Fails fast with clear error messages

#### 5.5 No UI Transmission

By not requiring the UI to send user\_id, this design eliminates a vector for user ID spoofing or manipulation at the client level:

* **Server-Authoritative:** The user\_id comes solely from the authenticated token
* **Cryptographically Protected:** The token is signed by the IAM service's private key
* **No Client Manipulation:** The UI cannot forge or alter the user\_id
* **Standard Practice:** This is the recommended approach in OAuth2.0 and OIDC specifications

***

### Implementation Checklist

Use this checklist to ensure complete and systematic implementation:

#### Middleware Layer

* \[ ] Update AuthMiddleware to extract `user_id` from `auth_principal.subject`
* \[ ] Store extracted user\_id in `request.state.user_id`
* \[ ] Verify middleware populates user\_id for all authenticated requests

#### Dependency & Routing Layer

* \[ ] Create `get_current_user_id()` dependency function
* \[ ] Add user\_id dependency to `POST /change-request` endpoint
* \[ ] Add user\_id dependency to `PATCH /change-request/{id}/verify` endpoint
* \[ ] Add user\_id dependency to `PATCH /change-request/{id}/approve` endpoint
* \[ ] Add user\_id dependency to `POST /intake-form` endpoint
* \[ ] Add user\_id dependency to `PATCH /intake-form/{id}/verify` endpoint
* \[ ] Add user\_id dependency to `PATCH /intake-form/{id}/approve` endpoint
* \[ ] **Add user\_id dependency to `POST /verifications/add_verification` endpoint** (CRITICAL - fixes TODO)

#### Service Layer

* \[ ] Update `ChangeRequestService.create()` to accept and use `user_id` parameter
* \[ ] Update `ChangeRequestService.verify()` to accept and use `user_id` parameter
* \[ ] Update `ChangeRequestService.approve()` to accept and use `user_id` parameter
* \[ ] Update `IntakeFormService.create()` to accept and use `user_id` parameter
* \[ ] Update `IntakeFormService.verify()` to accept and use `user_id` parameter
* \[ ] Update `IntakeFormService.approve()` to accept and use `user_id` parameter
* \[ ] **Update `G2PRegisterVerificationService.add_verification()` to accept `user_id` parameter** (CRITICAL)
* \[ ] **Replace hardcoded `verified_by="system"` with `verified_by=user_id`** in add\_verification()

#### Database Schema

* \[ ] **Verify existing `G2PRegisterVerification` table has all required audit fields** (already exists)
  * \[ ] `verification_id` (UUID primary key)
  * \[ ] `change_request_id` (foreign reference)
  * \[ ] `submission_id` (foreign reference)
  * \[ ] `verified_by` (currently will be populated from JWT)
  * \[ ] `verified_at` (timestamp)
* \[ ] Add `created_by` and `created_at` fields to `G2PChangeRequest` model (if not already present)
* \[ ] Add `approved_by` and `approved_at` fields to `G2PChangeRequest` model (if not already present)
* \[ ] Add audit fields to `G2PIntakeForm` model (if not already present)
* \[ ] Create database migration for any new audit fields on `G2PChangeRequest`
* \[ ] Create database migration for any new audit fields on `G2PIntakeForm`
* \[ ] **No migration needed for G2PRegisterVerification** (table already exists with correct structure)
* \[ ] Apply migrations to development database
* \[ ] Apply migrations to staging database
* \[ ] Apply migrations to production database

#### Testing

* \[ ] Test authenticated request with valid JWT populates all audit fields correctly
* \[ ] Test unauthenticated requests are rejected with 401 status
* \[ ] Test multiple concurrent authenticated requests maintain separate audit trails
* \[ ] Test expired tokens are rejected
* \[ ] Test invalid tokens are rejected
* \[ ] Verify UI does NOT send user\_id in request payloads
* \[ ] Verify user\_id is always sourced from the JWT token
* \[ ] Load test: verify audit fields are populated under high concurrency

#### Documentation

* \[ ] Document API changes: user\_id is now always captured from JWT
* \[ ] Update API specification (OpenAPI/Swagger) if applicable
* \[ ] Document audit trail fields in database schema documentation
* \[ ] Update developer guide for new endpoints
* \[ ] Add examples showing user\_id is NOT required in client requests
* \[ ] Document the security model for user\_id capture

***

### Solving Existing Codebase TODO

This middleware design **directly addresses an existing TODO in the registry codebase:**

**Location:** `G2PRegisterVerificationService.add_verification()` method

**Current Code (TODO):**

```python
async def add_verification(self, payload: AddVerificationPayload) -> VerificationData:
    # TODO: verified_by should use authenticated user context instead of hardcoded "system"
    verification = G2PRegisterVerification(
        ...
        verified_by="system",  # ← HARDCODED - Problem
        verified_at=datetime.now(),
        ...
    )
```

**After Middleware Implementation:**

```python
async def add_verification(
    self, 
    payload: AddVerificationPayload,
    user_id: str = Depends(get_current_user_id),  # ← Injected from JWT
    db: Session = Depends(get_db)
) -> VerificationData:
    verification = G2PRegisterVerification(
        ...
        verified_by=user_id,  # ← From authenticated user's JWT token
        verified_at=datetime.utcnow(),
        ...
    )
```

**Impact:**

* Verification audit trail will now correctly attribute verifications to actual users
* Replaces generic "system" entries with real user identifiers
* Enables proper accountability for verification operations
* Completes the audit trail for change requests and intake forms

***
