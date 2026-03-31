---
description: IAM and RBAC concepts within OpenG2P
---

# Identity and Access Management

## **1. Introduction**

### **1.1 Purpose**

This document provides a detailed description of how **authentication, authorization, and identity management** are implemented within the OpenG2P platform.

It explains:

* Integration with external Identity Providers (IdP)
* Token lifecycle and authentication flows
* Role-Based Access Control (RBAC) architecture
* Interaction between IAM services and product APIs
* Multi-channel user isolation

***

### **1.2 Scope**

This document covers:

* Staff channel (fully implemented in v1.0.0)
* Foundational design for Agent and Beneficiary channels

***

### **1.3 Key Concepts**

<table data-full-width="true"><thead><tr><th width="150.3787841796875">Concept</th><th>Description</th></tr></thead><tbody><tr><td>IdP</td><td>External Identity Provider (Keycloak by default)</td></tr><tr><td>Realm</td><td>Logical isolation boundary for users</td></tr><tr><td>Client</td><td>Application registered with IdP</td></tr><tr><td>Token</td><td>JWT used for authentication and authorization</td></tr><tr><td>RBAC</td><td>Role-Based Access Control</td></tr><tr><td>IAM Service</td><td>Central service managing RBAC logic</td></tr></tbody></table>

***

## **2. System Overview**

OpenG2P follows a **decoupled IAM architecture**, where:

* **Authentication** is handled by an external IdP (Keycloak)
* **Authorization (RBAC)** is handled internally via IAM services
* **Business APIs** enforce permissions using IAM

***

### **2.1 User Channels**

OpenG2P supports three independent user channels:

<table><thead><tr><th width="155.789794921875">Channel</th><th>Description</th></tr></thead><tbody><tr><td>Staff</td><td>Internal users (administrators, operators)</td></tr><tr><td>Agents</td><td>Field agents interacting with beneficiaries</td></tr><tr><td>Beneficiaries</td><td>End users receiving benefits</td></tr></tbody></table>

Each channel is:

* Logically isolated
* Independently scalable
* Mapped to separate identity domains

***

## **3. Identity Provider Architecture**

### **3.1 Keycloak as Default IdP**

OpenG2P uses Keycloak for:

* User authentication
* Token issuance
* Identity federation (future-ready)

<mark style="color:blue;">Implementation teams can embrace other IdPs. OpenG2P supports use of multiple IdPs in a single installation. Example - Beneficiary Portal may use eSignet while Staff Portal may use Keycloak.</mark>

***

### **3.2 Realm Design**

Each user channel maps to a dedicated realm:

<table><thead><tr><th width="143.7193603515625">Realm</th><th>Purpose</th></tr></thead><tbody><tr><td>staff</td><td>Staff users and internal applications</td></tr><tr><td>agents</td><td>Agent users</td></tr><tr><td>beneficiaries</td><td>Beneficiary users</td></tr></tbody></table>

#### **Why separate realms?**

* Security isolation
* Independent lifecycle management
* Custom policies per user group

***

### **3.3 Client Configuration (Staff Realm)**

The following clients are registered:

<table><thead><tr><th width="202.9041748046875">Client</th><th width="191.546142578125">Type</th><th>Purpose</th></tr></thead><tbody><tr><td>openg2p-registry</td><td>Confidential</td><td>Core platform</td></tr><tr><td>Rancher</td><td>Third-party</td><td>Kubernetes management</td></tr><tr><td>Keycloak</td><td>Internal</td><td>Identity administration</td></tr><tr><td>MinIO</td><td>Third-party</td><td>Object storage</td></tr></tbody></table>

***

### **3.4 Token Structure**

Tokens issued by Keycloak follow OIDC standards and include:

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

#### **Important Claim: `resource_access`**

This is critical for OpenG2P:

* Contains application-specific roles
* Used for RBAC enforcement

***

## **4. IAM Service Architecture**

### **4.1 Overview**

The IAM service acts as the **central authority for authorization logic**.

#### **Repository**

[`openg2p-iam-service`](https://github.com/OpenG2P/openg2p-iam-service)

[`openg2p-iam-service-deployment`](https://github.com/OpenG2P/openg2p-iam-service-deployment)

***

### **4.2 API Components**

<table><thead><tr><th width="219.1722412109375">API</th><th width="197.50830078125">Purpose</th><th>Status</th></tr></thead><tbody><tr><td>openg2p-iam-staff-api</td><td>Staff RBAC</td><td>✅ Active</td></tr><tr><td>openg2p-iam-agent-api</td><td>Agent RBAC</td><td>⏳ Planned</td></tr><tr><td>openg2p-iam-bene-api</td><td>Beneficiary RBAC</td><td>⏳ Planned</td></tr></tbody></table>

***

### **4.3 Architectural Responsibilities**

#### **4.3.1 Authentication Orchestration**

* Ownership of Authentication transaction
* Handles login flow redirection
* Exchanges authorization codes for tokens
* Manages session lifecycle

#### **4.3.2 Token Mediation**

* Validates tokens from IdP
* Normalizes token structure for internal use

#### **4.3.3 RBAC Enforcement Support**

* Provides APIs/libraries for permission resolution

***

### **4.4 IAM API Runtime Design**

Each channel has:

* Independent FastAPI runtime
* Independent deployment
* Independent scaling

***

### **4.5 IAM Database Layer**

#### **Database Strategy**

* Separate database per channel
* Avoids cross-channel contamination

***

### **4.6 Data Model**

#### **4.6.1 Configuration Data (Staff Only)**

**Applications**

Defines accessible systems for Staff users

* Registry
* MinIO (3rd party)
* Rancher (3rd party)
* Keycloak (identity provider)

***

**Roles & Permissions**

Roles and Permissions for each Application is defined in the Staff IAM database.

While roles for 3rd party applications are managed by the 3rd party applications themselves, roles and their permissions for openg2p products are managed by the IAM service.

Roles and Permissions for the Registry platform is available [here](https://docs.openg2p.org/registry/design/detailed-design-notes/rbac-roles-and-permissions) within the Registry documentation.

***

**Identity Providers**

* Configurable login sources

***

#### **4.6.2 Transactional Data**

Stored for all channels:

<table><thead><tr><th width="147.792236328125">Data</th><th>Purpose</th></tr></thead><tbody><tr><td>Login logs</td><td>Audit</td></tr><tr><td>Logout logs</td><td>Session tracking</td></tr></tbody></table>

***

## **5. Product API Layer**

### **5.1 Overview**

Each business product exposes APIs per user channel.

***

### **5.2 API Structure**

Each product runs **three independent API runtimes**:

| Product  | Staff              | Agent              | Beneficiary       |
| -------- | ------------------ | ------------------ | ----------------- |
| Registry | registry-staff-api | registry-agent-api | registry-bene-api |
| PBMS     | pbms-staff-api     | pbms-agent-api     | pbms-bene-api     |
| Bridge   | bridge-staff-api   | bridge-agent-api   | bridge-bene-api   |
| SPAR     | spar-staff-api     | spar-agent-api     | spar-bene-api     |

***

### **5.3 Responsibilities of Product APIs**

* Validate JWT tokens
* Extract roles from token
* Fetch permissions from IAM
* Enforce authorization rules

***

## **6. End-to-End Authentication Flow**

### **6.1 Login Flow (OIDC Authorization Code Flow)**

#### **Step-by-Step**

1. User accesses application
2. Redirected to Keycloak login
3. User authenticates
4. Keycloak returns authorization code
5. IAM API exchanges code for token
6. Token returned to client

***

### **6.2 SSO Behavior**

For staff:

* One login → access multiple apps
* Shared session via Keycloak realm

***

## **7. Authorization Flow (RBAC Execution)**

### **7.1 Flow Description**

1. Client sends request with JWT
2. Product API validates token (using IAM library)
3. Extract roles from `resource_access`
4. IAM library resolves permissions
5. API checks required permission
6. Access granted/denied

***

### **7.2 Key Design Choice**

**RBAC is NOT embedded in product APIs**

Instead:

* Centralized in IAM service
* Accessed via shared library

***

### **7.3 IAM Library Usage**

Product APIs:

* Import IAM library
* Call permission validation methods
* Avoid duplicating RBAC logic

***

## **8. Integration with Third-Party Applications**

### **8.1 RBAC Model**

| Application Type | RBAC Ownership |
| ---------------- | -------------- |
| OpenG2P Products | IAM Service    |
| Third-party Apps | Self-managed   |

***

### **8.2 Examples**

| App      | RBAC     |
| -------- | -------- |
| Rancher  | Internal |
| Keycloak | Internal |
| MinIO    | Internal |

***

## **12. Design Principles**

* **Separation of Concerns**
  * Products isolated from Identity and RBAC logic
* **Centralized Authorization**
  * Access controls defined in IdP identity definitions
  * Access controls centrally by IAM services
* **Decoupled Authentication**
  * Authentication handled in decoupled IdPs
  * OIDC / OAuth2.0 protocols used for integration with IdPs
* **Channel Isolation**
  * Realm-level separation
  * Database-level separation
* **Scalability by Design**
  * IAM APIs scale independently for each channel
  * Product APIs scale independently for each channel
* Auditability
  * Centralized logs (per channel) for Login / Logouts
  * Future: API audit trails

***

