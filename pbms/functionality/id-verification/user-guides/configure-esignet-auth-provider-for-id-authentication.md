# 📔 Configure eSignet Auth Provider for ID Authentication

1. Create an eSignet Client for PBMS/SR, if it doesn't exist.
   1. Create a public key private key JWKS pair and use the public key JWK during eSignet client creation and keep the private key JWK.
   2. Allowed redirect uris of the client should contain `https://socialregistry.your.org/auth_oauth/g2p_registry_id/confirm` .
2. Create two ID Types on the Registry: `NATIONAL ID` and `NATIONAL ID TOKEN`.
3. Install the [Authentication OIDC: Base](../../../development/odoo-modules/openid-connect-authentication.md), and [Authentication OIDC: Reg ID](../../../development/odoo-modules/authentication-oidc-reg-id.md) module.
4. Create a new OAuth Provider in Odoo with the following values: (OAuth providers can be created from Odoo Settings (debug mode) -> Users & Companies -> OAuth Providers, or Odoo Settings -> General Settings -> Search for OAuth -> OAuth Providers)
   1. Provider name: eSignet for ID Auth
   2. Auth Flow: OIDC Authorization Code flow
   3. Token Map: Leave the default and remove `groups:groups` .
   4. Allowed: Off
      1. If you want this provider to appear on any Portal but not on Odoo install the "G2P Portal Auth" module and allow this provider on the relevant portal from the same page.
   5. Login Button Label: `Login with eSignet`.
   6. Client Authenticate Method: _Private Key JWT_.
   7. Client Id: from Step 1.
   8. Client Private Key: Private key file in JWK Json format/PEM key format from Step 1.
   9. Auth URL, Token URL, Userinfo URL, JWKS URL: these are to be configured as available in the well-known config of eSignet.
   10. Allow Signup: _Allows user signup_.
   11. Signup Default Groups: `User types/Portal`.
   12. Sync User Groups: _When user groups are reset_.
   13. G2P ID Type: `NATIONAL ID TOKEN`.
   14. For the rest of the fields, leave default values.
5. Navigate to Registry -> Configuration -> ID Types: against the `NATIONAL ID` id type, configure the _Auth OAuth Provider_ as the one created in Step 4.
6. Navigate to Registry and open a record that contains `NATIONAL ID` ID and the authentication status is "Not authenticated". Click on the "Authenticate" button. Wait for the popup to open, and proceed with eSignet auth.
