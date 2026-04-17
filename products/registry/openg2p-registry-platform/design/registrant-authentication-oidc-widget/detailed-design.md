# Detailed design

## Registrant Authentication — Feature Design Document

**Project:** OpenG2P Registry Gen2\
**Feature:** Registrant Authentication via OIDC/OAuth2.0\
**Status:** Design / Pre-implementation\
**Date:** 2026-04-10

***

### 1. Overview

Registrant Authentication is a feature that allows staff operating the registry to authenticate a registrant (farmer, disabled person, vehicle owner, etc.) using the same OIDC/OAuth2.0 infrastructure as user login, but designed for **in-portal authentication facilitation** rather than self-service login.

**Key Use Case:**

* Staff opens a registrant's record in the registry
* Staff clicks "Authenticate Registrant" widget
* Widget initiates authentication with the configured auth provider (Keycloak, eSignet, etc.)
* Auth provider performs authentication (password, OTP, biometric, face, voice, etc.)
* Registry verifies the returned token and stores authentication proof
* Audit trail is maintained; registrant is notified
* Authentication is valid for a configured period (e.g., 2 years)
* When approaching expiry, system notifies registrant to re-authenticate

**Architectural Key Insight:** This feature **reuses the IAM service's OIDC/OAuth2.0 core libraries** (imported as a dependency) but operates completely independently from user login. Registrant authentication is:

* Tied to a registrant record (`internal_record_id`), not a user session
* Initiated by staff, not self-service
* Stored in the registry database with full audit trail
* Managed with explicit expiry and re-authentication workflows

***

### 2. Design Principles

* **Reuse, Don't Duplicate:** Import IAM core libraries (OidcClient, token validation, adapters) as a dependency
* **Separation of Concerns:** Registrant auth is entirely separate from user authentication and authorization
* **Audit First:** Every authentication attempt (success/failure) is recorded with full context
* **Compliance Ready:** Stores proof (token hash, claims, method) for verification and audits
* **Extensible Providers:** Pluggable adapter pattern supports any OIDC/OAuth2.0 provider (Keycloak, eSignet, custom)
* **Graceful Expiry:** Clear workflow for re-authentication with user notifications

***

### 3. Data Model

#### 3.1 `G2PRegistrantAuthenticationProvider`

Configuration table for registrant authentication providers. Multiple providers can be active simultaneously, allowing registrants to choose their preferred authentication method.

**Location:** `openg2p-registry-gen2-core/.../models/g2p_registrant_authentication_provider.py`

```python
class G2PRegistrantAuthenticationProvider(BaseORMModel):
    __tablename__ = "g2p_registrant_authentication_providers"

    provider_id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    register_id: Mapped[str] = mapped_column(
        String, nullable=False, index=True
    )  # Which register(s) this provider is available for
    provider_name: Mapped[str] = mapped_column(String, nullable=False)
    # e.g. "Keycloak (Password)", "eSignet (Biometric)", "Custom OTP", etc.
    provider_description: Mapped[str] = mapped_column(String, nullable=True)
    # e.g. "Authenticate using password and OTP"
    
    # Provider type for adapter lookup
    adapter_name: Mapped[str] = mapped_column(String, nullable=False)
    # e.g. "keycloak", "esignet", "custom"

    # OIDC endpoints or server metadata URL
    server_metadata_url: Mapped[str] = mapped_column(String, nullable=True)
    authorization_endpoint: Mapped[str] = mapped_column(String, nullable=True)
    token_endpoint: Mapped[str] = mapped_column(String, nullable=True)
    userinfo_endpoint: Mapped[str] = mapped_column(String, nullable=True)
    jwks_endpoint: Mapped[str] = mapped_column(String, nullable=True)
    introspection_endpoint: Mapped[str] = mapped_column(String, nullable=True)

    # Client credentials
    client_id: Mapped[str] = mapped_column(String, nullable=False)
    client_secret: Mapped[str] = mapped_column(String, nullable=False)  # encrypted
    token_endpoint_auth_method: Mapped[str] = mapped_column(
        String, default="client_secret_basic"
    )

    # Optional: KeyManager integration for MOSIP e-Signet
    keymanager_sign_app_id: Mapped[str] = mapped_column(String, nullable=True)

    # Provider-specific config (e.g., realm for Keycloak, locale for eSignet)
    provider_config: Mapped[JSON] = mapped_column(JSON, nullable=True)

    # Display order in widget
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
```

**Multi-Provider Support:**

* Multiple providers can be active for the same register (e.g., Keycloak + eSignet)
* Registrant chooses which provider to use via widget dropdown
* `display_order` controls the order in the UI dropdown
* `register_id` allows different registers to have different available providers (or same providers)

***

#### 3.2 `G2PRegistrantAuthentication`

Audit trail table. Records every authentication attempt (success or failure) for every registrant.

**Location:** `openg2p-registry-gen2-core/.../models/g2p_registrant_authentication.py`

```python
class AuthenticationStatusEnum(str, enum.Enum):
    PENDING = "PENDING"        # User initiated, waiting for response
    COMPLETED = "COMPLETED"    # Token received and validated
    FAILED = "FAILED"          # Auth failed or token validation failed
    EXPIRED = "EXPIRED"        # Valid auth but now past expiry_at

class G2PRegistrantAuthentication(BaseORMModel):
    __tablename__ = "g2p_registrant_authentications"

    authentication_id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    
    # Record being authenticated
    register_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    internal_record_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    
    # Provider used
    provider_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    
    # Who initiated the authentication
    initiated_by_staff_id: Mapped[str] = mapped_column(String, nullable=False)
    initiated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Authentication status
    status: Mapped[AuthenticationStatusEnum] = mapped_column(
        String, nullable=False, default=AuthenticationStatusEnum.PENDING, index=True
    )
    
    # === SUCCESSFUL AUTHENTICATION ===
    # User claims from the auth provider (encrypted for privacy)
    user_claims: Mapped[str] = mapped_column(String, nullable=True)  # JSON, encrypted
    
    # Authentication method used by the provider
    # e.g. "password", "otp", "biometric_fingerprint", "face_recognition", "voice"
    authentication_method: Mapped[str] = mapped_column(String, nullable=True)
    
    # Claim verifications performed
    # e.g. {"email_verified": true, "phone_verified": true, "biometric_verified": true}
    claim_verifications: Mapped[JSON] = mapped_column(JSON, nullable=True)
    
    # Hash of the original token (for proof of authentication, not the token itself)
    token_hash: Mapped[str] = mapped_column(String, nullable=True)
    
    # Token expiry from the auth provider
    token_expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
    # When this authentication is no longer valid (e.g., 2 years from authenticated_at)
    expiry_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, index=True)
    
    # When user is notified to re-authenticate (e.g., 1.9 years from authenticated_at)
    notification_sent_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
    # === FAILED AUTHENTICATION ===
    # Error message if authentication failed
    failure_reason: Mapped[str] = mapped_column(String, nullable=True)
    
    # Timestamps
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
```

**Indexes:** `(register_id, internal_record_id)`, `(internal_record_id, status)`, `(expiry_at)` (for finding expired authentications).

***

#### 3.3 `G2PRegisterDefinition` Extension

Add authentication requirements to register metadata:

```python
class G2PRegisterDefinition(BaseORMModel):
    # ... existing fields ...
    
    # Authentication requirements
    requires_registrant_authentication: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    registrant_authentication_validity_days: Mapped[int] = mapped_column(
        Integer, nullable=True, default=730  # 2 years
    )
    registrant_re_auth_warning_days_before: Mapped[int] = mapped_column(
        Integer, nullable=True, default=30  # Notify 30 days before expiry
    )
```

***

#### 3.4 `G2PRegisterAuthentication` Mixin Base Class

Abstract base class for register types that support authentication. Domain registers opt-in to authentication by extending this mixin.

**Location:** `openg2p-registry-gen2-core/.../models/g2p_register_authentication.py`

```python
class G2PRegisterAuthentication(BaseORMModel):
    """
    Mixin class for registers that require registrant authentication.
    Domain-specific registers extend both G2PRegister and G2PRegisterAuthentication.
    """
    __abstract__ = True
    
    # Latest authentication reference
    last_authentication_id: Mapped[str] = mapped_column(
        String, nullable=True, index=True
    )
    last_authenticated_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    last_authentication_status: Mapped[AuthenticationStatusEnum] = mapped_column(
        String, nullable=True
    )
    
    # Authentication validity tracking
    authentication_expiry_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=True, index=True
    )
    
    # Notification tracking
    authentication_expiry_notified: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
```

#### 3.5 Domain Register Extension (Example: Farmer)

Domain registers that require authentication extend both base classes:

```python
# In openg2p-registry-farmer-extension
class G2PRegisterFarmer(G2PRegister, G2PRegisterAuthentication):
    __tablename__ = "g2p_register_farmers"
    
    # Core farmer-specific fields
    estimated_age: Mapped[int] = mapped_column(Integer, nullable=True)
    disability: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    income_source: Mapped[str] = mapped_column(String, nullable=True)
    education: Mapped[str] = mapped_column(String, nullable=True)
    
    # Inherits from G2PRegister:
    # - internal_record_id, functional_record_id, record_name, search_text, etc.
    
    # Inherits from G2PRegisterAuthentication (if enabled for this register):
    # - last_authentication_id, authentication_expiry_at, etc.
```

**Optional Feature:**

* If a domain register does **not** need authentication, it only extends `G2PRegister`
* If it needs authentication, it extends both `G2PRegister` and `G2PRegisterAuthentication`
* This separation keeps authentication optional and allows flexibility per domain

**Denormalized Fields:** These fields in the mixin enable fast queries like "which registrants need re-authentication notifications?" without joining to the `G2PRegistrantAuthentication` audit table.

***

### 4. Service Layer

#### 4.1 `G2PRegistrantAuthenticationService`

Orchestrates the registrant authentication flow with support for multiple providers.

**Location:** `openg2p-registry-gen2-core/.../services/g2p_registrant_authentication_service.py`

```python
class G2PRegistrantAuthenticationService(BaseService):
    
    async def get_available_providers(
        self,
        session,
        register_id: str,
    ) -> list[G2PRegistrantAuthenticationProvider]:
        """
        Fetch all active authentication providers for a register.
        Returns sorted by display_order.
        """
        ...
    
    async def get_provider(
        self,
        session,
        provider_id: str,
    ) -> G2PRegistrantAuthenticationProvider:
        """Fetch a specific provider by ID."""
        ...
    
    async def start_authentication(
        self,
        session,
        register_id: str,
        internal_record_id: str,
        provider_id: str,
        initiated_by_staff_id: str,
    ) -> tuple[AuthenticationSession, str]:
        """
        Initiate registrant authentication with specified provider.
        
        Args:
            provider_id: Which authentication provider to use
        
        Returns:
            (AuthenticationSession, authorization_url)
            - AuthenticationSession stores state/nonce/code_verifier, provider_id (TTL: 5 mins)
            - authorization_url to redirect to the chosen auth provider
        """
        ...
    
    async def complete_authentication(
        self,
        session,
        state: str,
        authorization_code: str,
    ) -> G2PRegistrantAuthentication:
        """
        Complete authentication after receiving callback from auth provider.
        
        1. Retrieve AuthenticationSession by state
        2. Exchange code for tokens via OidcClient
        3. Validate token (signature, nonce, at_hash)
        4. Extract and store user_claims
        5. Extract authentication_method and claim_verifications
        6. Compute token_hash (SHA-256 of token)
        7. Create G2PRegistrantAuthentication record
        8. Update domain register with last_authentication_id, last_authenticated_at, expiry_at
        9. Mark register for expiry notification if needed
        """
        ...
    
    async def get_authentication_status(
        self,
        session,
        internal_record_id: str,
    ) -> G2PRegistrantAuthentication | None:
        """Get the latest (most recent) authentication for a registrant."""
        ...
    
    async def get_authentication_history(
        self,
        session,
        internal_record_id: str,
    ) -> list[G2PRegistrantAuthentication]:
        """Get full authentication audit trail for a registrant (newest first)."""
        ...
    
    async def is_authentication_valid(
        self,
        session,
        internal_record_id: str,
    ) -> bool:
        """Check if registrant's authentication is currently valid (not expired)."""
        ...
    
    async def find_expiring_authentications(
        self,
        session,
        days_before: int = 30,
    ) -> list[tuple[str, str, datetime]]:
        """
        Find registrants whose authentication will expire in N days.
        Returns: [(register_id, internal_record_id, expiry_at), ...]
        """
        ...
```

#### 4.2 Reuse from IAM

Import and wrap IAM core services:

```python
from iam_core.user_auth.oidc_client import OidcClient
from iam_core.user_auth.services.token_validator_service import TokenValidatorService
from iam_core.user_auth.adapters.registry import AdapterFactory

class G2PRegistrantAuthenticationService:
    
    def __init__(self):
        self.oidc_client = OidcClient()
        self.token_validator = TokenValidatorService()
        self.adapter_factory = AdapterFactory()
    
    async def _exchange_code_for_token(self, provider, code, code_verifier):
        """Use IAM's OidcClient to exchange auth code for tokens."""
        return await self.oidc_client.exchange_code_for_token(
            provider.server_metadata_url,
            provider.token_endpoint,
            provider.client_id,
            provider.client_secret,
            code,
            code_verifier,
            token_endpoint_auth_method=provider.token_endpoint_auth_method,
        )
    
    async def _validate_token(self, provider, tokens):
        """Use IAM's token validation to verify the received token."""
        # Create a temporary LoginProvider-like object for validation
        login_provider = self._provider_to_login_provider(provider)
        return await self.token_validator.validate(tokens.id_token, login_provider)
```

***

### 5. Authentication Flow

#### 5.1 Staff Selects Provider and Initiates Authentication

**Step 1: Fetch Available Providers**

**Endpoint:** `GET /register-data/get-available-authentication-providers`

```
Request:
{
  "register_id": "FARMER"
}

Response:
{
  "providers": [
    {
      "provider_id": "prov-001",
      "provider_name": "Keycloak (Password + OTP)",
      "provider_description": "Authenticate using username and one-time password",
      "adapter_name": "keycloak",
      "display_order": 1
    },
    {
      "provider_id": "prov-002",
      "provider_name": "eSignet (Biometric)",
      "provider_description": "Authenticate using fingerprint or face biometric",
      "adapter_name": "esignet",
      "display_order": 2
    }
  ]
}
```

**Step 2: Initiate Authentication with Selected Provider**

**Endpoint:** `POST /register-data/authenticate-registrant`

```
Request:
{
  "register_id": "FARMER",
  "internal_record_id": "farm-12345",
  "provider_id": "prov-001",
  "initiated_by_staff_id": "staff-001"
}

Response:
{
  "authentication_session_id": "session-uuid",
  "authorization_url": "https://keycloak.example.com/oauth/authorize?client_id=...&state=...",
  "provider_name": "Keycloak (Password + OTP)"
}
```

**Flow:**

```
Staff opens registrant record and clicks "Authenticate"
  ↓
Widget calls GET /get-available-authentication-providers
  ↓
Widget displays dropdown of available providers
  ↓
Registrant selects provider (or default shown)
  ↓
Widget calls POST /register-data/authenticate-registrant with provider_id
  ↓
Service.start_authentication():
  - Fetch specified provider config
  - Create AuthenticationSession (state, nonce, code_verifier, provider_id, TTL=5min)
  - Build authorization URL with PKCE
  - Return auth URL + provider name
  ↓
Widget opens authorization URL in iframe/popup
  ↓
Auth provider shows authentication UI
```

#### 5.2 Auth Provider Callback

**Endpoint:** `GET /registrant-auth/callback?code=...&state=...`

```
Auth provider redirects to registry with authorization code
  ↓
Service.complete_authentication(state, code):
  - Retrieve AuthenticationSession by state
  - Exchange code for tokens via OidcClient
  - Validate token (signature, nonce, at_hash)
  - Extract user_claims from ID token
  - Extract authentication_method and claim_verifications (adapter-specific)
  - Compute token_hash = SHA-256(token)
  - CREATE G2PRegistrantAuthentication:
      status: COMPLETED
      user_claims: encrypted JSON
      authentication_method: "otp" (from provider)
      claim_verifications: {phone_verified: true}
      token_hash: "abc123..."
      expiry_at: now + 2 years
  - UPDATE G2PRegisterFarmer:
      last_authentication_id: auth.id
      last_authenticated_at: now
      authentication_expiry_at: now + 2 years
  ↓
Redirect back to staff portal with success message
```

***

### 6. Adapter Pattern

Registrant authentication adapters are **identical to user login adapters** in IAM, reused as-is.

#### 6.1 Keycloak Adapter

```python
class KeycloakAdapter(OIDCBase):
    name = "keycloak"
    
    def normalize_claims(self, claims, provider):
        # Extract verified_email, verified_phone from ID token
        return {
            "sub": claims.get("sub"),
            "email": claims.get("email"),
            "phone_number": claims.get("phone_number"),
            "verified_email": claims.get("email_verified", False),
            "verified_phone": claims.get("phone_number_verified", False),
            # ... etc
        }
    
    def get_authentication_method(self, claims, provider):
        # Extract from acr (Authentication Context Class Reference)
        acr = claims.get("acr", "")
        if "otp" in acr:
            return "otp"
        elif "password" in acr:
            return "password"
        return "unknown"
    
    def get_claim_verifications(self, claims, provider):
        return {
            "email_verified": claims.get("email_verified", False),
            "phone_verified": claims.get("phone_number_verified", False),
        }
```

#### 6.2 e-Signet Adapter

```python
class EsignetAdapter(OIDCBase):
    name = "esignet"
    
    def normalize_claims(self, claims, provider):
        # Extract verified_ flags from e-Signet's response
        verified_attrs = claims.get("verified_attributes", [])
        return {
            "sub": claims.get("sub"),
            "verified_attrs": verified_attrs,
        }
    
    def get_authentication_method(self, claims, provider):
        # e-Signet returns amr (Authentication Method Reference)
        amr = claims.get("amr", [])
        if "biometric" in amr:
            return "biometric_fingerprint"
        elif "face" in amr:
            return "face_recognition"
        elif "otp" in amr:
            return "otp"
        return "unknown"
    
    def get_claim_verifications(self, claims, provider):
        verified = claims.get("verified_attributes", [])
        return {attr: True for attr in verified}
```

**Key Point:** These adapters extract `authentication_method` and `claim_verifications` — data specific to registrant authentication that user login doesn't need.

***

### 7. Controller Service and API Endpoints

#### 7.1 Controller Service

**Location:** `openg2p-registry-gen2-core/.../controller_services/g2p_registrant_authentication_controller_service.py`

```python
class G2PRegistrantAuthenticationControllerService(BaseService):
    
    async def initiate_registrant_authentication(
        self,
        request: RegistrantAuthenticationInitiateRequest,
    ) -> RegistrantAuthenticationInitiateResponse:
        # Calls G2PRegistrantAuthenticationService.start_authentication()
        # Returns authorization URL for widget
        ...
    
    async def complete_registrant_authentication(
        self,
        request: RegistrantAuthenticationCompleteRequest,
    ) -> RegistrantAuthenticationCompleteResponse:
        # Calls G2PRegistrantAuthenticationService.complete_authentication()
        # Returns authentication result
        ...
    
    async def get_registrant_authentication_status(
        self,
        internal_record_id: str,
    ) -> RegistrantAuthenticationStatusResponse:
        # Returns latest auth status, expiry, etc.
        ...
    
    async def get_registrant_authentication_history(
        self,
        internal_record_id: str,
    ) -> list[RegistrantAuthenticationHistoryItem]:
        # Returns full audit trail
        ...
```

#### 7.2 Staff Portal API Endpoints

**Location:** `openg2p-registry-gen2-apis/openg2p-registry-staff-portal-api/.../g2p_registrant_authentication_controller.py`

```
GET /register-data/get-available-authentication-providers
    Request:  { register_id }
    Response: { providers: [{provider_id, provider_name, provider_description, display_order}] }
    Auth:     @require_permissions("registrantAuthentication:view")
    Purpose:  Fetch list of available auth providers for widget dropdown

POST /register-data/authenticate-registrant
    Request:  { register_id, internal_record_id, provider_id, initiated_by_staff_id }
    Response: { authorization_url, session_id, provider_name }
    Auth:     @require_permissions("registrantAuthentication:initiate")
    Purpose:  Initiate authentication with selected provider

GET /registrant-auth/callback
    Query:    code, state
    Response: Redirect to staff portal with result
    (No auth needed — OAuth callback)

POST /register-data/get-registrant-authentication-status
    Request:  { internal_record_id }
    Response: { 
      status, 
      last_authenticated_at, 
      expiry_at,
      authentication_method,
      claim_verifications,
      initiated_by_staff_id
    }
    Auth:     @require_permissions("registrantAuthentication:view")
    Purpose:  Get latest authentication status

POST /register-data/get-registrant-authentication-history
    Request:  { internal_record_id }
    Response: { authentications: [{
      authentication_id,
      initiated_at,
      status,
      authentication_method,
      initiated_by_staff_id,
      claim_verifications
    }] }
    Auth:     @require_permissions("registrantAuthentication:view")
    Purpose:  Get full audit trail of all authentication attempts
```

***

### 8. UI Widget

#### 8.1 Registrant Authentication Widget

**Location:** `openg2p-registry-gen2-ui-widgets/src/widgets/RegistrantAuthenticationWidget.tsx`

A new React widget for the staff portal with provider selection:

```tsx
interface RegistrantAuthenticationWidgetConfig extends BaseWidgetConfig {
  widget: 'registrant-authentication';
  'widget-id': string;
  'widget-label': string;
  'widget-data-path': string;  // internal_record_id from form
  'widget-register-id': string;  // register_id from form
  'widget-allow-provider-selection': boolean;  // default: true
}

component RegistrantAuthenticationWidget:
  Layout:
    1. Status Section (read-only):
       - ✓ Last authenticated: [date/time]
       - ⚠ Expires: [date/time]
       - Method: [password/OTP/biometric]
       - Claims verified: [list of verified attributes]
       - [View History link]
    
    2. Authentication Section (if not recently authenticated or needs re-auth):
       a. Provider Selector:
          - Dropdown with list of available providers
          - Each option shows: "Keycloak (Password + OTP)" + description
          - Sorted by display_order
       
       b. Authenticate Button
       
       c. Modal/Popup Flow:
          - On click: call GET /get-available-authentication-providers
          - Display dropdown
          - On selection: call POST /authenticate-registrant with provider_id
          - Open popup/iframe to authorization_url
          - Listen for callback (postMessage or URL)
          - Poll GET /get-registrant-authentication-status
          - Show success/failure message
          - Update status section
```

**UI Example:**

```
┌─ Registrant Authentication ─────────────────┐
│                                              │
│ Last authenticated:  Jan 15, 2024           │
│ Expires: Jan 15, 2026 (in 1 year 11 months)│
│ Method: Password + OTP                      │
│ Verified: email, phone                      │
│                                              │
│ [Authenticate Registrant ▼]  (dropdown)     │
│ ├─ Keycloak (Password + OTP)               │
│ └─ eSignet (Biometric)                     │
│                                              │
│ [Authenticate] [View History]              │
│                                              │
└──────────────────────────────────────────────┘
```

#### 8.2 Registrant Authentication Status Widget

Display current auth status:

```tsx
interface RegistrantAuthenticationStatusConfig extends BaseWidgetConfig {
  widget: 'registrant-authentication-status';
  'widget-data-path': string;  // internal_record_id
}

component RegistrantAuthenticationStatusWidget:
  - Shows: "Last authenticated: [date]"
  - Color: Green (valid), Yellow (expiring soon), Red (expired)
  - Click to view history
```

***

### 9. Notification and Re-authentication Workflow

#### 9.1 Periodic Re-authentication Check

**Celery Beat Producer:** `registrant_authentication_expiry_beat_producer`

Every hour, query for registrants approaching expiry:

```python
@celery_app.task(name="registrant_authentication_expiry_beat_producer")
def registrant_authentication_expiry_beat_producer():
    """
    Finds registrants whose authentication expires in N days (configurable).
    Marks them for notification.
    """
    with session_maker() as session:
        expiring = G2PRegistrantAuthenticationService.find_expiring_authentications(
            session, days_before=30
        )
        
        for register_id, internal_record_id, expiry_at in expiring:
            # Mark for notification
            domain_record = session.get(internal_record_id)
            domain_record.authentication_expiry_notified = False
            session.add(domain_record)
            
            # Queue notification task
            celery_app.send_task(
                "registrant_authentication_expiry_notifier",
                args=(internal_record_id,),
            )
        
        session.commit()
```

#### 9.2 Notification to Registrant

**Celery Worker:** `registrant_authentication_expiry_notifier`

Sends notification (SMS, email, push) to registrant:

```python
@celery_app.task(name="registrant_authentication_expiry_notifier")
def registrant_authentication_expiry_notifier(internal_record_id: str):
    """
    Notifies registrant that authentication will expire soon.
    Integrates with G2P notification service (SMS/email/push).
    """
    with session_maker() as session:
        auth = G2PRegistrantAuthenticationService.get_authentication_status(
            session, internal_record_id
        )
        
        if auth and auth.expiry_at:
            # Get registrant contact info (email, phone, etc.)
            register_record = session.get(internal_record_id)
            
            # Send notification via G2P NotificationService
            message = f"Your authentication for {register_record.record_name} "
                      f"will expire on {auth.expiry_at.strftime('%Y-%m-%d')}. "
                      f"Please re-authenticate here: [link]"
            
            NotificationService.send_notification(
                recipient_id=internal_record_id,
                message=message,
                channels=["sms", "email"],
            )
            
            # Mark as notified
            auth.notification_sent_at = datetime.utcnow()
            session.add(auth)
            session.commit()
```

***

### 10. Configuration

#### 10.1 Registry Configuration

Add to `G2PRegisterDefinition`:

```python
requires_registrant_authentication: bool = False
registrant_authentication_validity_days: int = 730  # 2 years
registrant_re_auth_warning_days_before: int = 30
```

#### 10.2 Provider Configuration

Set up multiple `G2PRegistrantAuthenticationProvider` records (one per authentication option):

**Example 1: Keycloak (Password + OTP)**

```
INSERT INTO g2p_registrant_authentication_providers (
  register_id,
  provider_name,
  provider_description,
  adapter_name,
  server_metadata_url,
  client_id,
  client_secret,
  token_endpoint_auth_method,
  display_order,
  is_active
) VALUES (
  'FARMER',
  'Keycloak (Password + OTP)',
  'Authenticate using username and one-time password',
  'keycloak',
  'https://keycloak.example.com/realms/registrants/.well-known/openid-configuration',
  'farmer-registrant-client',
  '[encrypted-secret]',
  'client_secret_basic',
  1,
  true
);
```

**Example 2: eSignet (Biometric)**

```
INSERT INTO g2p_registrant_authentication_providers (
  register_id,
  provider_name,
  provider_description,
  adapter_name,
  server_metadata_url,
  client_id,
  client_secret,
  token_endpoint_auth_method,
  keymanager_sign_app_id,
  display_order,
  is_active
) VALUES (
  'FARMER',
  'eSignet (Biometric)',
  'Authenticate using fingerprint or face biometric',
  'esignet',
  'https://esignet.example.com/.well-known/openid-configuration',
  'farmer-esignet-client',
  '[encrypted-secret]',
  'private_key_jwt_keymanager',
  'esignet-registrant-signing',
  2,
  true
);
```

**Multi-Provider Flexibility:**

* Different registers can have different available providers
* Registrants choose their preferred authentication method
* Providers are sorted by `display_order` in the UI
* Can enable/disable providers independently via `is_active` flag

#### 10.3 Environment Variables

```
REGISTRY_REGISTRANT_AUTH_ENABLED=true
REGISTRY_REGISTRANT_AUTH_CALLBACK_URL=https://registry.example.com/registrant-auth/callback
REGISTRY_REGISTRANT_AUTH_SESSION_TTL_SECONDS=300
REGISTRY_REGISTRANT_AUTH_SESSION_STORE_BACKEND=redis  # or memory
```

***

### 11. Encryption and Security

#### 11.1 User Claims Storage

User claims are **encrypted at rest**:

```python
# On write:
encrypted_claims = encrypt(json.dumps(user_claims), encryption_key)
auth.user_claims = encrypted_claims

# On read:
user_claims = json.loads(decrypt(auth.user_claims, encryption_key))
```

Uses a master encryption key managed via environment or KeyVault.

#### 11.2 Token Hash (Proof, Not Storage)

Instead of storing the actual token, store a SHA-256 hash:

```python
token_hash = hashlib.sha256(token.encode()).hexdigest()
auth.token_hash = token_hash
```

**Purpose:** Proof that authentication was performed, not for validation. Allows auditing without exposing the original token.

#### 11.3 Security Features Reused from IAM

* **PKCE**: Protects authorization code interception
* **Nonce**: Prevents ID token replay attacks
* **State Parameter**: Prevents CSRF
* **at\_hash**: Verifies access token integrity
* **HTTPS only**: Secure cookie transmission
* **Token validation**: Signature verification via JWKS

***

### 12. Audit Trail Features

The `G2PRegistrantAuthentication` table provides:

1. **Who**: `initiated_by_staff_id` (which staff initiated)
2. **When**: `initiated_at`, `completed_at`, `created_at`
3. **What**: `user_claims` (who was authenticated), `authentication_method` (how)
4. **Proof**: `token_hash` (hash of original token)
5. **Verification**: `claim_verifications` (what was verified)
6. **Status**: `status` (success/failure), `failure_reason`
7. **Validity**: `token_expires_at`, `expiry_at` (when auth is no longer valid)

**Compliance Benefits:**

* Non-repudiation: Staff can't deny initiating authentication
* Evidence: Token hash proves token was received and validated
* Auditability: Full timeline of every authentication attempt
* Traceability: Links staff, registrant, provider, method

***

### 13. Comparison: User Login vs. Registrant Authentication

| Aspect       | User Login (IAM)             | Registrant Auth (Registry)             |
| ------------ | ---------------------------- | -------------------------------------- |
| **Who**      | System user (staff, agent)   | Beneficiary/registrant                 |
| **Where**    | Login portal, self-service   | Initiated by staff in-app              |
| **Why**      | Access the system            | Prove identity for record              |
| **Storage**  | Secure HTTP-only cookie      | Database record + encrypted            |
| **Lifespan** | Session (hours)              | Long-term (2 years)                    |
| **Expiry**   | Implicit (session timeout)   | Explicit, with warnings                |
| **Audit**    | User access logs             | Authentication audit trail             |
| **Adapter**  | LoginProvider                | RegistrantAuthenticationProvider       |
| **Reuse**    | OidcClient, token validation | OidcClient, token validation, adapters |

***

### 13. Database Migrations

**New Tables (Alembic migrations):**

* \[ ] `g2p_registrant_authentication_providers` (provider configuration)
* \[ ] `g2p_registrant_authentications` (audit trail)

**Updated Tables:** For each domain register that supports authentication, add columns via migration:

* `last_authentication_id` (FK)
* `last_authenticated_at` (DateTime)
* `last_authentication_status` (String enum)
* `authentication_expiry_at` (DateTime, indexed)
* `authentication_expiry_notified` (Boolean)

Example: When `G2PRegisterFarmer` extends `G2PRegisterAuthentication`, the `g2p_register_farmers` table automatically includes these columns.

```python
# In CoreInitializer.migrate_database()
await G2PRegistrantAuthenticationProvider.create_migrate()
await G2PRegistrantAuthentication.create_migrate()

# In extension initializers (e.g., FarmerExtension)
# The mixin base class columns are automatically included
await G2PRegisterFarmer.create_migrate()
```

***

### 14. Implementation Checklist

**Core Service Layer:**

* \[ ] Create models:
  * \[ ] `G2PRegistrantAuthenticationProvider` (provider config)
  * \[ ] `G2PRegistrantAuthentication` (audit trail table)
  * \[ ] `G2PRegisterAuthentication` (mixin base class)
* \[ ] Create service: `G2PRegistrantAuthenticationService`
* \[ ] Create controller service: `G2PRegistrantAuthenticationControllerService`
* \[ ] Wrap IAM libraries: OidcClient, token validation, adapters
* \[ ] Implement AuthenticationSession (state/nonce/code\_verifier, TTL)
* \[ ] Encryption/decryption for user\_claims

**API Endpoints (Staff Portal):**

* \[ ] `POST /register-data/authenticate-registrant/initiate`
* \[ ] `GET /registrant-auth/callback`
* \[ ] `POST /register-data/get-registrant-authentication-status`
* \[ ] `POST /register-data/get-registrant-authentication-history`

**UI Widgets:**

* \[ ] `RegistrantAuthenticationWidget` (initiate button + popup)
* \[ ] `RegistrantAuthenticationStatusWidget` (display status)

**Celery Tasks:**

* \[ ] `registrant_authentication_expiry_beat_producer`
* \[ ] `registrant_authentication_expiry_notifier`

**Migrations:**

* \[ ] Alembic migrations for new tables (providers, authentications)
* \[ ] Add fields to `G2PRegisterDefinition` (authentication requirements)
* \[ ] Add columns to domain registers that extend `G2PRegisterAuthentication` mixin
  * Via inheritance, columns are auto-generated in extending tables

**Configuration:**

* \[ ] Setup `G2PRegistrantAuthenticationProvider` table
* \[ ] Create provider record (Keycloak/eSignet)
* \[ ] Configure register metadata (`requires_registrant_authentication`)
* \[ ] Environment variables for encryption key, callback URL

**Testing:**

* \[ ] Unit tests for authentication flows
* \[ ] Integration tests with mock auth provider
* \[ ] Encryption/decryption tests
* \[ ] Expiry notification logic

***

### 15. Architectural Highlights

#### Mixin-Based Design

The `G2PRegisterAuthentication` mixin base class embodies clean architecture principles:

```python
# Core register — no authentication fields
class G2PRegister(BaseORMModel):
    internal_record_id, functional_record_id, record_name, ...

# Authentication mixin — opt-in feature
class G2PRegisterAuthentication(BaseORMModel):
    last_authentication_id, last_authenticated_at, ...

# Domain register — extends both if authentication needed
class G2PRegisterFarmer(G2PRegister, G2PRegisterAuthentication):
    estimated_age, disability, income_source, ...
```

**Benefits:**

* **Single Responsibility:** `G2PRegister` stays focused on core functionality
* **Optional Feature:** Only registers that need authentication extend the mixin
* **Consistency:** Follows existing mixin pattern (G2PPerson, G2PGeo)
* **Flexibility:** Different domains can choose to support authentication or not
* **Clean Tables:** Database tables only include columns they actually use

***
