---
cover: ../../.gitbook/assets/SPAR banner-on-light-background.png
coverY: 0
---

# SPAR Post Installation Configuration

## Post-installation

Onboard SPAR on eSignet:

* Create OIDC Client for SPAR in eSignet. Follow the method suggested by the ID Provider.
  * If using mock eSignet, use this API to create OIDC client [https://esignet.dev.openg2p.net/v1/esignet/swagger-ui/index.html#/client-management-controller/createOAuthClient](https://esignet.dev.openg2p.net/v1/esignet/swagger-ui/index.html#/client-management-controller/createOAuthClient).
* During OIDC client creation, you will be asked for (or given) a client ID and private key JWK as client secret.
* Edit the SPAR DB, `login_provider` table and modify the `authorization_parameters` row of the first entry, with:
  * appropriate URLs for `authorize_endpoint` , `token_endpoint` , `validate_endpoint`, `jwks_endpoint`, and `redirect_uri` fields.
  * above client ID under the `client_id` field.
  * and above private key jwk under the `client_assertion_jwk` field.
* Seed/edit metadata of banks, wallets, branches, etc for the SPAR self-service portal in database. TODO: Elaborate.
