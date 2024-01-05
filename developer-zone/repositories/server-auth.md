# server-auth

Branch: [15.0](https://github.com/OpenG2P/server-auth/tree/15.0)

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

