# Authentication OIDC: Reg ID

### Module name

g2p\_auth\_id\_oidc

### Description

This module inherits from the [OIDC Authentication](authentication-oidc-base.md) module and adds functionality that allows registrants to log in to Portals (Odoo-based) and get the respective IDs filled (without this module only Odoo Application Users, like Admins, Managers, and Registrars, can log in).

### Features

* Allow new Registrants to log in, same as OIDC Authentication, but additionally marks the user as a Registrant (and not a system user). Also allows associates an ID to the newly created Registry entry, and the value of the ID can be mapped from the Userinfo response of the auth provider.
* Allows for existing Registrants to log in.
  * Will check for existing registrants by searching the registry for any entry with an ID value equal to the ID received in the Userinfo response.
* Supports authentication of Registry IDs. Allows to configure an auth provider against an ID Type.
  * Upon successful authentication of an ID, the user (registrar/system user authenticating the ID), will get an option to update the existing user data on the registry.

### Guides

* [Configure eSignet Auth Provider for ID Authentication](../../functionality/id-verification/user-guides/configure-esignet-auth-provider-for-id-authentication.md)

### Configuration

OAuth Provider Field Reference (exclusive of the fields from [OIDC base](authentication-oidc-base.md) module).

<table><thead><tr><th width="146">Field name</th><th width="137">Field Title</th><th width="334">Description</th><th>Default Value</th></tr></thead><tbody><tr><td>g2p_id_type</td><td>G2P ID Type</td><td>ID Type of registrant that this auth provider should fill</td><td></td></tr></tbody></table>

G2P ID Type Field Reference (exclusive of the basic field in ID Type configuration)&#x20;

<table><thead><tr><th width="146">Field name</th><th width="137">Field Title</th><th width="334">Description</th><th>Default Value</th></tr></thead><tbody><tr><td>auth_oauth_provider_id</td><td>Auth Oauth Provider ID</td><td>Auth provider which should be used to authenticate this ID</td><td></td></tr></tbody></table>

### Source code

[https://github.com/OpenG2P/openg2p-auth/tree/17.0-develop/g2p\_auth\_id\_oidc](https://github.com/OpenG2P/openg2p-auth/tree/17.0-develop/g2p\_auth\_id\_oidc)
