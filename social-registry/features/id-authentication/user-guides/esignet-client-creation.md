---
layout:
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
---

# 📔 eSignet Client Creation

This document provides instructions on eSignet client creation.

## Prerequisites

* Keycloak Client is created for eSignet. The `esignet_admin_access` client scope is assigned as a default scope. [More info>>](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/esignet#post-installation)

## Procedure

1. Create a private key public key JWK pair. (https://mkjwk.org can be used).
2.  Create an eSignet OIDC client using the following API. (Replace parameters with appropriate values in the below API)

    ```bash
    token=$(curl -s https://<keycloak hostname>/realms/master/protocol/openid-connect/token -d "client_id=<esignet keycloak client id>" -d "client_secret=<esignet keycloak client secret>" -d "grant_type=client_credentials" | jq -r '.access_token');
    curl -v -s -H "Authorization: Bearer ${token}" -H "content-type: application/json" https://<esignet hostname>/v1/esignet/client-mgmt/oauth-client -d '{
      "requestTime": "'$(date -u "+%Y-%m-%dT%T.%3NZ")'",
      "request": {
        "clientId": "<OIDC Client ID>",
        "clientName": "<OIDC Client Name>",
        "publicKey": <Public Key JWK>,
        "relyingPartyId": "<relying party id. (For OpenG2P related clients, give openg2p-auth-partner)>",
        "userClaims": [
          "birthdate","address","gender","name","phone_number","picture","email", "individual_id"
        ],
        "authContextRefs": [
          "mosip:idp:acr:biometrics","mosip:idp:acr:generated-code","mosip:idp:acr:linked-wallet"
        ],
        "logoUri": "<logo URL to be displayed on UI>",
        "redirectUris": [
          "<redirect URI List>"
        ],
        "grantTypes": [
          "authorization_code"
        ],
        "clientAuthMethods": [
          "private_key_jwt"
        ],
        "clientNameLangMap": {
          "eng": "<OIDC Client Name>"
        }
      }
    }'
    ```

