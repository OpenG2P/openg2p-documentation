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

# G2P Auth: OIDC - Reg ID

### Module name

g2p\_auth\_id\_oidc

### Module title

G2P Auth: OIDC - Reg ID

### Technology base

[Odoo](https://www.odoo.com/)

### Functionality

This module adds functionality that enables registrants to log in to Odoo-based portals and get the respective IDs filled. It is derived from the [OpenID Connect Authentication](openid-connect-authentication.md) module.

Note:

Only the Odoo Application Users, such as Administrators, Managers, and Registrars, are able to log in without this module.&#x20;

### Features

<table><thead><tr><th width="267">Feature</th><th>Description</th></tr></thead><tbody><tr><td>New Registrants log in </td><td>Allows new Registrants to log in, same as OIDC Authentication, but additionally marks the user as a Registrant (and not a system user). Also allows associates an ID to the newly created Registry entry, and the value of the ID can be mapped from the Userinfo response of the auth provider.</td></tr><tr><td>Existing Registrants log in</td><td>Checks for existing registrants by searching the registry for any entry with an ID value equal to the ID received in the Userinfo response.</td></tr><tr><td>Authentication</td><td><p>Supports authentication of Registry IDs. Allows to configure an auth provider against an ID Type.</p><ul><li>Upon successful authentication of an ID, the user (registrar/system user authenticating the ID), will get an option to update the existing user data on the registry.</li></ul></td></tr></tbody></table>

### Guides

To learn more on _**Configure eSignet Auth Provider for ID Authentication**_, click [here](https://docs.openg2p.org/pbms/functionality/id-verification/user-guides/configure-esignet-auth-provider-for-id-authentication).

### Configuration

OAuth Provider field reference (exclusive of the fields from [OIDC base](openid-connect-authentication.md) module).

<table><thead><tr><th width="146">Field name</th><th width="137">Field title</th><th width="334">Description</th><th>Default value</th></tr></thead><tbody><tr><td>g2p_id_type</td><td>G2P ID Type</td><td>ID Type of registrant that this auth provider should fill</td><td></td></tr></tbody></table>

G2P ID Type field reference (exclusive of the basic field in ID Type configuration)&#x20;

<table><thead><tr><th width="146">Field name</th><th width="137">Field title</th><th width="334">Description</th><th>Default value</th></tr></thead><tbody><tr><td>auth_oauth_provider_id</td><td>Auth Oauth Provider ID</td><td>Auth provider which should be used to authenticate this ID</td><td></td></tr></tbody></table>

### Source code

[https://github.com/OpenG2P/openg2p-auth/tree/17.0-develop/g2p\_auth\_id\_oidc](https://github.com/OpenG2P/openg2p-auth/tree/17.0-develop/g2p\_auth\_id\_oidc)
