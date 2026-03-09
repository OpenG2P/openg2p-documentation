# Authentication - Staff Portal

The OpenG2P Staff Portal provides a single, centralized login for staff and administrators to access all internal OpenG2P modules from one landing page after authentication.

This document defines:

* Authentication architecture
* Keycloak realm and client design
* Token lifecycle and reuse
* Single Sign-On (SSO) behavior
* Role-based authorization model
* End-to-end authentication flows

### Key Design Principles

* Single authentication, multiple modules
* No repeated logins
* Shared access token across modules
* Strong role-based authorization
* Realm isolation across portals
* Portal-specific theming

### Modules Accessed via Staff Portal

After login, users may access the following modules (based on roles):

* Registry
* PBMS
* G2PBridge
* SPAR
* Rancher
* Superset Dashboard
* Keycloak Admin Console
* MinIO
* ODK

### Identity Provider

#### Keycloak as IAM

Authentication and authorization are provided by Keycloak, implementing OpenID Connect (OIDC).

### Realm Strategy

Each OpenG2P portal is mapped to a separate Keycloak realm.

| **Portal**         | **Realm**           | **Authentication**                         |
| ------------------ | ------------------- | ------------------------------------------ |
| Staff Portal       | openg2p-staff       | Keycloak (username/password, MFA optional) |
| Agent Portal       | openg2p-agent       | Keycloak                                   |
| Beneficiary Portal | openg2p-beneficiary | National ID / External IdP                 |

#### Benefits of Realm Isolation

* User and credential separation
* Independent security policies
* Different authentication methods
* Custom UI themes per portal



### Staff Portal Realm Design

#### Realm: openg2p-staff

Within the Staff Portal realm:

* **Staff Portal UI** → OIDC client
* **Each module** → OIDC client
*   Centralized:

    * Users
    * Roles
    * Groups
    * Policies<br>

    All clients trust the same realm.



### Client Model

#### Client Types

| **Client**           | **Type**                  |
| -------------------- | ------------------------- |
| Staff Portal UI      | Public or Confidential    |
| Registry, PBMS, etc. | Confidential              |
| APIs                 | Bearer-only (recommended) |



### Role & Authorization Model

#### Role Types

**Realm Roles**

TBD

**Client Roles (Module-specific)**

Keycloak will only manage the high level roles

<table data-header-hidden><thead><tr><th>Client ID</th><th width="374">Roles</th></tr></thead><tbody><tr><td><strong>Client ID</strong></td><td><strong>Roles</strong></td></tr><tr><td>registry</td><td><ul><li>Registry View</li><li>Registry Edit</li></ul></td></tr><tr><td>pbms</td><td><ul><li>OpenG2P PBMS / Enrolment Operation</li><li>OpenG2P PBMS / Geography Operation</li><li>OpenG2P PBMS / Audit Operation</li><li>OpenG2P PBMS / Enrolment Approval</li><li>OpenG2P PBMS / Disbursement Approval</li><li> OpenG2P PBMS / Disbursement Operation</li><li>OpenG2P PBMS / Enrolment Verification</li><li>OpenG2P PBMS / Disbursement Verification</li></ul></td></tr><tr><td>rancher</td><td>Rancher View</td></tr><tr><td>odk</td><td>ODK View</td></tr><tr><td>minio</td><td><ul><li>consoleAdmin</li><li>readonly</li><li>readwrite</li><li>writeonly</li></ul></td></tr></tbody></table>

#### Authorization Enforcement

* Keycloak embeds roles in the access token
* Each module:
  * Validates token signature
  * Verifies token expiry
  * Enforces its own client roles



### Token Types & Responsibilities

| **Token**          | **Purpose**              | **Used By**            |
| ------------------ | ------------------------ | ---------------------- |
| Authorization Code | One-time login exchange  | Staff Portal only      |
| Access Token       | Access protected modules | Staff Portal + Modules |
| ID Token           | Identity information     | Staff Portal           |
| Refresh Token      | Renew access token       | Staff Portal only      |



### Authentication Flow – Staff Portal Login

#### Authorization Code Flow (OIDC)

TBD - Flow Diagram

#### Step-by-Step

1. User accesses Staff Portal URL
2. Staff Portal checks for valid session
3. If not authenticated:
   * Redirects to Keycloak login
4. User authenticates in Keycloak
5. Keycloak redirects back with authorization code
6. Staff Portal calls token endpoint using:
   * Authorization code
   * Client authentication / PKCE
7. Keycloak returns:
   * Access Token
   * ID Token
   * Refresh Token
8. User is logged in and sees Staff Portal dashboard



### Module Access Flow (Single Sign-On)

#### Shared Access Token Model

TBD - flow diagram

#### Flow Details

1. User clicks a module from Staff Portal
2. Browser navigates to module URL
3. Module:
   * Detects existing Keycloak session
   * Accepts the same access token
4. Module validates:
   * Token signature
   * Token expiry
   * Required client roles
5. User gains access without re-authentication



### Example Access Token Claims

```json
{
    "iss": "https://<auth-server>/realms/<realm>",
    "sub": "<user-id>",
    "aud": [
        "<service-a>",
        "<service-b>"
    ],
    "azp": "<client-application>",
    "exp": 1700000000,
    "iat": 1699996400,
    "typ": "Bearer",
    "preferred_username": "staff.user@example.com",
    "email": "staff.user@example.com",
    "name": "Staff User",
    "given_name": "Staff",
    "family_name": "User",
    "scope": "openid profile email",
    "realm_access": {
        "roles": [
            "create-realm"
        ]
    },
    "resource_access": {
        "<service-a>": {
            "roles": [
                "view",
                "edit"
            ]
        },
        "<service-b>": {
            "roles": [
                "admin"
            ]
        }
    },
    "user_type": "STAFF"
}
```

Each module checks only its own roles.



### Logout Flow (Single Logout)

1. User logs out from Staff Portal
2. Staff Portal calls Keycloak logout endpoint
3. Keycloak invalidates session
4. All module sessions become invalid



### Theming Strategy

* Each realm has its own Keycloak theme
*   Applied to:

    * Login pages
    * Error pages
    * Account console



    | **Realm**          | **Theme**                |
    | ------------------ | ------------------------ |
    | Staff Portal       | Admin / Enterprise theme |
    | Agent Portal       | Operational theme        |
    | Beneficiary Portal | Citizen-friendly theme   |



### High-Level Architecture Diagram

TBD
