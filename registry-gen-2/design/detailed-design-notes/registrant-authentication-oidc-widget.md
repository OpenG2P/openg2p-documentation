---
layout:
  width: default
  title:
    visible: true
  description:
    visible: false
  tableOfContents:
    visible: true
  outline:
    visible: true
  pagination:
    visible: true
  metadata:
    visible: true
  tags:
    visible: true
---

# Registrant Authentication - OIDC Widget

<figure><img src="../../../.gitbook/assets/OIDC Widget for. Registrant Authentication.jpg" alt=""><figcaption></figcaption></figure>

**Step-1 (302 Redirect from OIDC Widget to IdP Authorization Endpoint)**

```
GET https://idp.example.org/authorize
?response_type=code
&client_id=FARMER_REGISTRY_DOA_SOME_PROVINCE
&redirect_uri=https://farmer_registry.doasp.org/oidc/callback
&scope=openid profile
&state=af0ifjsldkj
&code_challenge=E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM
&code_challenge_method=S256
&nonce=n-0S6_WzA2Mj
```

To support this, the following configurations are required from the Registry Backend

1. response\_type = code (tells that the exchange is based on an Authorization Code and not tokens) - This can be hardcoded in the Widget
2. client\_id = FARMER\_REGISTRY\_DOA\_SOME\_PROVINCE
3. redirect\_uri = https://farmer\_registry.doasp.org/oidc/callback
4. scope =&#x20;
5. state =&#x20;
6. code\_challenge =&#x20;
7. code\_challenge\_method =&#x20;
8. nonce =&#x20;

**Step - 2 (Navigate to IdP Authorization endpoint)**

This is handled by the Browser Engine

**Step - 3 (Authenticate Registrant)**

This is handled by the IdP depending on how the ID Authentication mechanism has been configured.

**Step - 4 (Redirect to redirect\_uri)**

This is handled by the IdP, once it establishes the result of Authentication

**Step - 5 (Handle the redirect into redirect\_uri)**

This is handled by the Browser Engine

**Step - 6 (Exchange the Authorization\_Code for Tokens)**

**Step - 7 (Validate ID Token and create Authorization Context)**

**Step - 8 (Return Success Response to Browser)**





