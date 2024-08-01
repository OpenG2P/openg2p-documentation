# Configure Keycloak Authentication Provider for User login

1. Create a Keycloak client for PBMS/SR as given in [Keycloak Client Creation](../../../../../deployment/deployment-guide/keycloak-client-creation.md) guide.
2. Install the [OIDC Authentication Base](../../../../development/odoo-modules/authentication-oidc-base.md) module.&#x20;
3. Create a new OAuth Provider in Odoo with the following values: (OAuth providers can be created from Odoo Settings (debug mode) -> Users & Companies -> OAuth Providers, or Odoo Settings -> General Settings -> Search for OAuth -> OAuth Providers)
   1. Provider name: Keycloak for PBMS Login
   2. Auth Flow: OIDC Authorization Code flow
   3. Token Map: Leave default except change `groups:groups` to `client_roles:groups` .
   4. Allowed: On
   5. Login Button Label: `Login with Keycloak`. (This text will be shown on the button on log in page, configure accordingly)
   6. Client Authenticate Method: _Client Secret (Post)_.
   7. Client Id: from Step 1.
   8. Client Secret: from Step 1.
   9. Auth URL, Token URL, Userinfo URL, JWKS URL: these are to be configured as available in the well-known config of Keycloak. (Keycloak OIDC well-known configuration can be found in Keycloak Admin Console -> Realm Settings -> (Bottom of Page) Endpoints -> OIDC Endpoint Configuration)
   10. Allow Signup: _Allows user signup_.
   11. Signup Default Groups: `User types/Portal`.
   12. Sync User Groups: _On every Login_.
   13. For the rest of the fields, leave default values.
4. Create client roles on Keycloak for the client created in Step 1. Example client role names:
   1. `Administrator/Settings` .
   2. `OpenG2P Module Access/Administrator` .
   3. `OpenG2P Module Access/Registrar` .
5. Create a Keycloak User and assign all the required client roles.
6. Proceed to the login page and use the "Login with Keycloak" button.
