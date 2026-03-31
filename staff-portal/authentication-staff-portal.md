# Authentication - Staff Portal

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

### Authentication Flow – Staff Portal Login

#### Overview

The **Staff Portal delegates authentication to the IAM service**.

Instead of directly interacting with Keycloak or handling OAuth flows, the portal:

* Calls an **IAM endpoint**
* Receives a **redirect URL**
* Redirects the user to continue authentication

This ensures that **all authentication logic, token exchange, and session handling are centralized in IAM**.

#### Step-by-Step

**1. User Accesses Staff Portal**

*   User opens:

    ```
    http://staff-portal.openg2p.my
    ```

**2. Staff Portal Initiates Authentication**

The portal calls its internal API:

```
GET /api/auth/login?redirect_uri=<target>
```

This triggers:

```
POST {IAM_URL}/auth/start_authentication_transaction
```

With:

* `id` → Login provider ID (e.g., Keycloak)
* `redirect_uri` → Where user should return after login

**3. IAM**&#x20;

IAM responds with:

```
{
  "redirectUrl": "https://keycloak2.openg2p.org/realms/master/protocol/openid-connect/auth?response_type=code&client_id=staff-portal&redirect_uri=http%3A%2F%2Fiam.openg2p.my%2Fauth%2Fcallback&scope=openid+profile+email&state=AyXhPtEhy7FcUU3aURkEibsGuMHeUTpVWKkc1n0Ap-Q&nonce=X9RsIJUCIDXf0WasjlCBQXKSNE3Otgoa_-vC3-oPlsQ&code_challenge=vmSaByvORbUTY52Ur2KOJA7RZbxXErb-7eLdzw9FZ-k&code_challenge_method=S256",
  "state": "AyXhPtEhy7FcUU3aURkEibsGuMHeUTpVWKkc1n0Ap-Q"
}
```

**4. Redirect to Keycloak**

*   Staff Portal redirects user to:

    ```
    redirectUrl
    ```
* User authenticates on Keycloak UI

**5. Full OAuth Flow Happens Inside IAM**

After login:

* Keycloak → returns authorization code to IAM
* IAM → exchanges code for tokens:
  * Access Token
  * ID Token

**6. Redirect Back to Staff Portal**

IAM redirects user back to:

```
REDIRECT_URL = http://staff-portal.openg2p.my
```

With session/cookies already established.

**7. User Gets Access**

* Staff Portal now detects valid session
* Displays application cards
