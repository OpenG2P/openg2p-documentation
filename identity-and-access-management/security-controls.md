---
description: Token Handling, Headers, CORS & CSRF Protection
---

# Security Controls

***

## **1. Token Strategy**

OpenG2P uses **OIDC-compliant tokens** issued by the Identity Provider (Keycloak).

***

### **1.1 Token Types**

<table><thead><tr><th width="147.16754150390625">Token</th><th width="283.7911376953125">Purpose</th><th>Usage in OpenG2P</th></tr></thead><tbody><tr><td><strong>ID Token</strong></td><td>Represents authenticated user identity</td><td>Used by frontend / IAM layer (not for API authorization)</td></tr><tr><td><strong>Access Token</strong></td><td>Grants access to APIs</td><td>Used by backend APIs for authentication &#x26; RBAC</td></tr></tbody></table>

***

### **1.2 ID Token Handling**

The **ID Token** contains user identity claims such as:

* `sub` (user id)
* `email`
* `name`
* `preferred_username`

#### **Usage Guidelines**

* Used **only during authentication phase**
* Used by IAM API for session/user context
* **NOT used for API authorization**

> **Important:** Authorization decisions must always be based on the **Access Token**, not the ID Token.

***

### **1.3 Access Token Handling (Primary Security Token)**

The **Access Token** is the authoritative token for:

* API authentication
* Role extraction
* RBAC enforcement

***

### **1.4 Token Storage (Cookie-Based Approach)**

The Access Token is stored in a **secure HTTP-only cookie**.

#### **Cookie Configuration**

```
Set-Cookie: access_token=abc123;
  Domain=.dev.openg2p.org;
  HttpOnly;
  Secure;
  SameSite=Lax;
  Path=/api;
  Max-Age=900
```

***

### **1.5 Attribute Explanation**

<table><thead><tr><th width="249.09393310546875">Attribute</th><th>Purpose</th></tr></thead><tbody><tr><td><code>HttpOnly</code></td><td>Prevents JavaScript access (protects against XSS)</td></tr><tr><td><code>Secure</code></td><td>Ensures transmission only over HTTPS</td></tr><tr><td><code>SameSite=Lax</code></td><td>Protects against CSRF</td></tr><tr><td><code>Domain=.dev.openg2p.org</code></td><td>Enables sharing across subdomains, within the same environment. <br><br>openg2p.org - represents the domain<br>dev - represents the environment (within the domain)</td></tr><tr><td><code>Path=/api</code></td><td>Restricts usage to API endpoints</td></tr><tr><td><code>Max-Age=900</code></td><td>Token lifetime (15 minutes)</td></tr></tbody></table>

***

***

### **1.7 Design Rationale**

<table><thead><tr><th width="288.44683837890625">Decision</th><th>Reason</th></tr></thead><tbody><tr><td>Use cookies for Access Token</td><td>Protects against XSS</td></tr><tr><td>HttpOnly flag</td><td>Prevents token theft via JS</td></tr><tr><td>Separate ID &#x26; Access usage</td><td>Aligns with OIDC best practices</td></tr><tr><td>Avoid ID token for APIs</td><td>Prevents misuse of identity token</td></tr></tbody></table>

***

## **2. Security Headers**

IAM APIs enforce security headers:

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
```

***

### **2.1 Header Purpose**

<table><thead><tr><th width="211.06317138671875">Header</th><th>Description</th></tr></thead><tbody><tr><td><code>nosniff</code></td><td>Prevents MIME-type sniffing</td></tr><tr><td><code>DENY</code></td><td>Blocks iframe embedding (clickjacking protection)</td></tr><tr><td><code>X-XSS-Protection</code></td><td>Legacy browser protection</td></tr></tbody></table>

***

## **3. CORS Configuration**

### **3.1 Allowed Origins**

```
allow_origins = [
    "https://staff-portal.openg2p.org",
    "https://registry-staff-portal.openg2p.org",
    "https://pbms-staff-portal.openg2p.org",
]
```

***

### **3.2 Credentials Support**

```
allow_credentials = True
```

#### **Implications**

* Cookies (including access token) are sent automatically
* Requires strict origin whitelisting

***

## **4. CSRF Protection Mechanism**

Since authentication is **cookie-based**, CSRF protection is mandatory.

***

### **4.1 CSRF Token Cookie**

```
Set-Cookie: csrf_token=UUID;
  Domain=.dev.openg2p.org;
  Secure;
  SameSite=Lax;
  Path=/api;
  Max-Age=900
```

***

### **4.2 Cookie Comparison**

<table><thead><tr><th width="164.73065185546875">Cookie</th><th width="156.89056396484375">HttpOnly</th><th>Purpose</th></tr></thead><tbody><tr><td>access_token</td><td>✅ Yes</td><td>Authentication</td></tr><tr><td>csrf_token</td><td>❌ No</td><td>CSRF validation</td></tr></tbody></table>

***

### **4.3 Frontend Implementation**

```
fetch("/api/update", {
  method: "POST",
  credentials: "include",
  headers: {
    "X-CSRF-Token": getCookie("csrf_token")
  }
})
```

***

### **4.4 Backend Validation (in all APIs)**

```
if request.headers.get("X-CSRF-Token") != request.cookies.get("csrf_token"):
    raise Exception("CSRF validation failed")
```

***

### **4.5 Security Model**

This implements the **Double Submit Cookie Pattern**.

* Browser sends cookies automatically
* Only your frontend can read `csrf_token`
* Attackers cannot forge matching header + cookie

***

## **5. End-to-End Flow (With Both Tokens)**

#### **Step-by-Step**

1. User authenticates via IdP
2. IAM API receives:
   * ID Token (identity)
   * Access Token (authorization)
3. IAM API:
   * Stores **access\_token** in HttpOnly cookie
   * Issues **csrf\_token** cookie
   * Processes ID token for user context
4. Frontend:
   * Uses session (no direct access to access\_token)
   * Reads csrf\_token
5. API Request:
   * Browser sends access\_token automatically
   * Frontend adds CSRF header
6. Backend:
   * Validates Access Token
   * Validates CSRF token
   * Processes request

***

## **6. Security Guarantees**

<table><thead><tr><th width="177.54425048828125">Threat</th><th>Protection</th></tr></thead><tbody><tr><td>XSS</td><td>HttpOnly cookies</td></tr><tr><td>CSRF</td><td>Double submit cookie</td></tr><tr><td>Token misuse</td><td>Access vs ID token separation</td></tr><tr><td>Clickjacking</td><td>X-Frame-Options</td></tr><tr><td>MIME attacks</td><td>nosniff</td></tr></tbody></table>

***
