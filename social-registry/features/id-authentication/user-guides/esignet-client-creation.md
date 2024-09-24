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

There are two methods for creating an eSignet client.

* [Using PMS API](esignet-client-creation.md#using-pms-api)
* [Using eSignet API](esignet-client-creation.md#using-esignet-api)

## Using PMS API

This method is applicable if MOSIP Partner Management APIs are available. The MOSIP Partner Admin executes the below steps.

1. Create an eSignet OIDC client using PMS OIDC API.

{% swagger src="../../../../.gitbook/assets/pms-api-docs.json" path="/oidc/client" method="post" %}
[pms-api-docs.json](../../../../.gitbook/assets/pms-api-docs.json)
{% endswagger %}

* `authParnterId:` Partner ID in [this](esignet-client-creation.md#configure-openg2p-as-a-partner-on-mosip) step.
* `policyId` : Policy ID in [this](esignet-client-creation.md#configure-openg2p-as-a-partner-on-mosip) step.
* `publicKey:` Generate [JWK](https://openid.net/specs/draft-jones-json-web-key-03.html).
* `logoUri`: URL of your logo accessible publicly.
* `grantTypes` = `["authorization_code"]`
* `clientAuthMethods`= `["private_key_jwt"]`
* `redirectUris`: URLs of the form `https://<your web portal>/auth_oauth/signin`

Note down the Client ID as an output of the above step.

### Using eSignet API

This method is applicable if MOSIP Partner Management APIs are **not** available.

1. Create an eSignet OIDC client using the following API.

POST /client-mgmt/oidc

* `clientId:` Arbitrary string.
* `clientName:` Arbitrary string.
* `relyingParnterId:` Partner ID in [this](esignet-client-creation.md#configure-openg2p-as-a-partner-on-mosip) step.
* `publicKey:` Generated [JWK](https://openid.net/specs/draft-jones-json-web-key-03.html).
*   `authContextRefs`:&#x20;

    ```
    ["mosip:idp:acr:biometrics","mosip:idp:acr:generated-code"]
    ```
*   `userClaims`:&#x20;

    ```
    ["birthdate","address","gender","name","phone_number","email","picture"]
    ```
* `logoUri`: URL of your logo accessible publicly.
* `grantTypes` = `["authorization_code"]`
* `clientAuthMethods`= `["private_key_jwt"]`
* `redirectUris`: URLs of the form `https://<your web portal>/auth_oauth/signin`
