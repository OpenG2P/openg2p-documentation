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

# G2P OpenID VCI: Rest API

### Module name

g2p\_openid\_vci\_rest\_api

### Module title

G2P OpenID VCI: Rest API

### Technology base

[Odoo](https://www.odoo.com/)

### Functionality

This module exposes the following [OpenID for VCI](https://openid.net/specs/openid-4-verifiable-credential-issuance-1\_0.html) REST APIs.

The endpoints and their descriptions are given below.

<table><thead><tr><th width="417">Endpoint</th><th>Description</th></tr></thead><tbody><tr><td><code>/api/v1/vci/credential</code> </td><td><p>The main credential request API. </p><ol><li>Gets the issuer based on scope, credential type, and supported format. </li><li>Verifies and validates auth JWT based on issuer config. </li><li>Retrieves registrant data based on issuer config and auth JWT sub. </li><li>Issues the credential based on credential format.</li></ol></td></tr><tr><td><code>/api/v1/vci/.well-known/openid-credential-issuer</code></td><td><p>Issuer metadata API.</p><ul><li>collates the <code>issuer_metadata</code> of all issuers and return</li></ul></td></tr><tr><td><code>/api/v1/vci/.well-known/openid-credential-issuer/</code><mark style="color:orange;"><code>{SafetyNetIssuer}</code></mark></td><td><p>Specific Issuer metadata API. </p><ul><li>Gets individual metadata of each issuer by suffixing the API with Issuer Name. </li></ul></td></tr><tr><td><code>/api/v1/vci/.well-known/contexts.json</code></td><td> All the contexts from all the Issuers are collated and returned on this API. This path will be included in as context path within the VC.</td></tr></tbody></table>

### Source code

&#x20;[https://github.com/openg2p/openg2p-vci](https://github.com/openg2p/openg2p-vci)
