---
description: OpenG2P uses eSignet to connect with MOSIP Id repository
---

# eSignet Login

[eSignet](https://docs.esignet.io) is a [OpenID Connect](https://openid.net/connect/) implementation which aims to offer a simple yet powerful mechanism for end users to identify themselves to avail of online services and also share their profile information.

OpenG2P integrates with MOSIP IdP over eSignet for the Self Service portal registration and login. This enables any MOSIP Id holders can easily use the service of OpenG2P through the secure bio-metric and other means of authentication.&#x20;

Following are the dependent modules in openG2P to integrate eSignet

## [server-auth](https://github.com/OpenG2P/server-auth/tree/15.0)

eSignet integration from OpenG2P uses the [auth\_oidc](https://github.com/OCA/server-auth/tree/15.0/auth\_oidc) package of odoo which is further extended to use [private\_key\_jwt ](https://openid.net/specs/openid-connect-core-1\_0-15.html#ClientAuthentication)assertion at the client side. To configure eSignet a new oAuth provider is added in OpenG2P. This can be done by entering into debug mode and going to "Settings" page and click on "OAuth Providers" under the menu "Users & Companies".  &#x20;

Following are the parameter setting for [server-auth](https://github.com/OpenG2P/server-auth/tree/15.0)

* **Provider name : A name for the configuration**
* **Auth Flow : "**OpenID Connect (authorization code flow)" can be used to connect OIDC IdP provider.
* **Token Map:** sub:user\_id&#x20;
* **Redirect Url :** URL where IdP would redirect to after successful login, where in the user sign in process inside OpenG2P will happen.
* **Client ID :** Client Id created at IdP against OpenG2P
* **Client Authentication :** The client authentication method for eSignet. eSignet uses "Private Key JWT"
* **Private Key :**  Private key pem file has to be uploaded here.
* **Grant Type :** Type of grant, which need to be "JWT Bearer" here.
* **Allowed ​:** Whether or not the login method is enabled in the login page
* **Login button label :** Button label visible in the login page.
* **CSS class :** CSS Class to get applied on the login button&#x20;
* **Authorization URL:** Authorization URL
* **Scope:** Provide the value "openid profile email"
* **UserInfo URL:** URL to fetch the User Info
* **Token URL :** Token end point to get the authorisation token&#x20;
* **JWKS URL :** The JSON Web Key Set (JWKS) endpoint
* **Data Endpoint :** Data end point

## [openg2p-auth](https://github.com/OpenG2P/openg2p-auth.git)

openg2p-auth is an extension to server-auth to setup further parameters  and facilitate further functionalities required for OpenG2P. The settings for openG2P-auth in included in the same page as server-auth.  Below are the parameters available for openg2p-auth

* **Allowed in Self Service Portal : Wether or not the login option will be visible for self service portal login page**&#x20;
* **Use G2P Reg ID Type :** What would be the Registry ID Type used to store the token received
* **Partner Creation Call Validate Url :**
* **Partner Creation Validate Response Mapping :** Mapping the fields for registry record creation ****&#x20;
* **Default Group User Creation :** Default user group to be created when the user log in to self service portal through eSignet for the first time. ****&#x20;
* **Login Attribute Mapping On User Creation : What would be the login attribute connected with the user after the user is created for first time**
