---
description: Module name
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

# G2P OpenID VCI: Base

### Module name

g2p\_openid\_vci

### Module title&#x20;

G2P OpenID VCI: Base

### Technology base

[Odoo](https://www.odoo.com/)

This repository contains an Odoo module that helps PBMS/Social Registry (SR) to issue [Verifiable Credentials](https://www.w3.org/TR/vc-data-model/) (VC). It provides default VC templates for SR and PBMS and adds [OpenID for VCI](https://openid.net/specs/openid-4-verifiable-credential-issuance-1\_0.html) APIs to SR and PBMS.

### Functionality

This module adds `g2p.openid.vci.issuers` model called _**VC Issuer**_. The main fields in this VC Issuer model are given below.

<table><thead><tr><th width="256">Field</th><th>Description</th></tr></thead><tbody><tr><td><code>issuer_type</code></td><td> It is a selection field and decides the functionality of this VC Issuer. If issuer_type is <code>Registry</code>, it is issuing Registry credentials.</td></tr><tr><td><code>credential_format</code></td><td>It is a <a href="https://jqlang.github.io/jq/manual/">Jq</a> expression and it defines the format/template of the final VC.</td></tr><tr><td><code>credential_type</code></td><td><p>It is a name given to VC of this format.</p><p>For example: "FarmerIDVerifiableCredential", "StudentVerifiableCredential", or something generic like "OpenG2PRegistryVerifiableCredential" etc.</p></td></tr><tr><td><code>issuer_metadata_text</code></td><td> It is a <a href="https://jqlang.github.io/jq/manual/">Jq</a> expression to give out metadata of this issuer and metadata of the fields in the credential.</td></tr><tr><td><code>context_json</code></td><td>It is the <a href="https://www.w3.org/TR/json-ld11/#the-context">JSON-LD context</a> of this VC.</td></tr><tr><td><code>scope</code></td><td><p>It is an OIDC (OpenID Connect) authentication scope. In other words this issuer responds only to the requests for which the auth scope matches the scope configured here. </p><p>For example: scopes; <code>farmer_id_vc_ldp</code> , etc.</p></td></tr><tr><td><code>allowed auth token issuers, allowed auth token audience</code></td><td>These fields are added to configure authentication. Here  Registrant ID is present in the auth token subject, etc.</td></tr></tbody></table>

### Design notes

This module is designed to create any number of issuers with different combinations of parameters such as scope, credential\_type, credential\_format, issuer\_metadata, and so on.

For example: Follow the below steps if you want to issue two different types of credentials from your registry, each of which requires the credentials to have different fields.

1. Create two issuers, both issuer\_types are Registry.
2. Configure different credential types and scopes for both issuers.
3. Configure both issuers' credential formats with the necessary fields in place.
4. Modify the issuer metadata of both the issuers along with relevant metadata for the fields.
5. Modify contexts json with different fields and different credential type for both issuers.

When a credential request is received, it will select the issuer based on the combination of scope (from auth JWT), credential type (from credential request body) (and supported\_format which defaults to ldp\_vc for now).

This module also uses g2p.encryption.provider (of any type) to sign the final VC. If the encryption provider is not configured on the issuer, it will use the default encryption provider.

Note:

A credential will only be issued if the sub from auth JWT exists as one of IDs in registry against a registry entry.

### Guides

To learn more about _**Configuration**_, click [here](https://docs.openg2p.org/pbms/development/odoo-modules/openg2p-vci#configuration).

### Source code

[https://github.com/openg2p/openg2p-vci](https://github.com/openg2p/openg2p-vci)

### Create a custom VC Issuer

This section describes the procedure for developing custom VC Issuers with the custom functionality that differ from the above Registry Credential Issuer and Beneficiary Credential Issuer.

*   Inherit `g2p.openid.vci.issuers` model. Add a new type to the `issuer_type` Selection field using selection\_add. Example

    ```python
    issuer_type = fields.Selection(selection_add=[("Mock", "Mock")], ondelete={"Mock": "cascade"})
    ```
* Implement the following functions:
  * `issue_vc_{issuer_type}`&#x20;
  * `set_default_credential_type_{issuer_type}`&#x20;
  * `set_from_static_file_{issuer_type}`&#x20;
*   Example:

    ```python
    class BeneficiaryOpenIDVCIssuer(models.Model):
        _inherit = "g2p.openid.vci.issuers"

        issuer_type = fields.Selection(selection_add=[("Mock", "Mock")], ondelete={"Mock": "cascade"})
        
        def issue_vc_Mock(self, auth_claims, credential_request):
            ...    
        
        def set_default_credential_type_Mock(self):
            self.credential_type = "OpenG2PMockVerifiableCredential"

        def set_from_static_file_Mock(self, **kwargs):
            kwargs.setdefault("module_name", "g2p_openid_vci_mock")
            return self.set_from_static_file_Registry(**kwargs)
    ```

### Configuration

* VCI Issuers' configs can be found under `Settings` Menu -> `VCI Issuers`  page.
* VC Issuer general config properties:

<table><thead><tr><th width="221">Name</th><th width="174">Property name</th><th>Description</th></tr></thead><tbody><tr><td>Name</td><td>name</td><td>Name of the Issuer.</td></tr><tr><td>Scope</td><td>scope</td><td>Scope that is to be accepted in authentication.</td></tr><tr><td>Issuer Type</td><td>issuer_type</td><td>Type of Issuer</td></tr><tr><td>Supported Format</td><td>supported_format</td><td>VC format supported. Defaults to <code>ldp_vc</code> .</td></tr><tr><td>Unique Issuer ID</td><td>unique_issuer_id</td><td>A unique ID (string) assigned to this issuer. Defaults to <code>did:example:12345678abcdefgh</code> .</td></tr><tr><td>Encryption Provider</td><td>encryption_provider_id</td><td>Encryption Provider. If left blank, it will choose default encryption provider.</td></tr><tr><td>Auth Subject ID Type</td><td>auth_sub_id_type_id</td><td>Type of ID which is present in Subject of Authentication.</td></tr><tr><td>Auth Allowed Audiences</td><td>auth_allowed_auds</td><td><ul><li>Only authentications with "aud" from this list will be allowed.</li><li>Separated by space/newline.</li><li>If left blank, audience in auth will be ignored.</li></ul></td></tr><tr><td>Auth Allowed Issuers</td><td>auth_allowed_issuers</td><td><ul><li>Only authentications with "iss" from this list will be allowed.</li><li>Separated by space/newline.</li></ul></td></tr><tr><td>Auth Issuer JWKs Mapping</td><td>auth_issuer_jwks_mapping</td><td><ul><li>JWKs URL of each issuer from "Auth Allowed Issuers".</li><li>If there are 3 entries in "Auth Allowed Issuers", then there should be 3 JWKs URL in this too, one for each the issuer.</li><li>Separated by space/newline.</li></ul></td></tr><tr><td>Auth Allowed Client IDs</td><td>auth_allowed_client_ids</td><td><ul><li>Only authentications with "client_id" from this list will be allowed.</li><li>Separated by space/newline.</li><li>If left blank, client_id in the auth will be ignored.</li></ul></td></tr><tr><td>Credential Type</td><td>credential_type</td><td><ul><li>Type of the VC. </li><li>Leave it blank to take the default value, according to Issuer Type. </li></ul></td></tr><tr><td>Credential Format</td><td>credential_format</td><td><ul><li>Credential format as Jq expression. </li><li>Leave it blank to take the default value, according to Issuer Type.</li></ul></td></tr><tr><td>Issuer Metadata Text</td><td>issuer_metadata_text</td><td><ul><li>Issuer Metadata as Jq expression. </li><li>Leave it blank to take the default value, according to Issuer Type.</li></ul></td></tr><tr><td>Contexts JSON</td><td>contexts_json</td><td><ul><li>Contexts JSON for this credential Type</li><li>Leave it blank to take the default value, according to Issuer Type.</li></ul></td></tr></tbody></table>

* VC Issuer Program/Beneficiary specific configs:

<table><thead><tr><th width="224">Name</th><th width="175">Property name</th><th>Description</th></tr></thead><tbody><tr><td>Program</td><td>program_id</td><td>Program for which we are issuing the Beneficiary VC.</td></tr></tbody></table>
