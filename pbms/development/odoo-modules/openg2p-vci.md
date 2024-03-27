# openg2p-vci

## Introduction

Source Code: [https://github.com/openg2p/openg2p-vci](https://github.com/openg2p/openg2p-vci)

This repository contains Odoo modules that help PBMS/Registry to issue [Verifiable Credentials](https://www.w3.org/TR/vc-data-model/) (VC). This repo also provides default VC templates for both Registry and PBMS. This repo also adds [OpenID for VCI](https://openid.net/specs/openid-4-verifiable-credential-issuance-1\_0.html) APIs to both Registry and PBMS.

## Odoo modules

This repository contains  the following modules:

### G2P OpenID VCI

Module Name: g2p\_openid\_vci

* This module adds `g2p.openid.vci.issuers` model, called "VC Issuer". Following are the main fields in this VC Issuer model.
  * `issuer_type` selection field decides the functionality of this VC Issuer. If issuer\_type is `Registry` , it is issuing Registry Credentials.
  * `credential_format` is a [Jq](https://jqlang.github.io/jq/manual/) expression, which is supposed to define the format/template of the final verifiable credential.
  * `credential_type` is nothing but a name given to VC of this format. Example "FarmerIDVerifiableCredential", "StudentVerifiableCredential", or something generic like "OpenG2PRegistryVerifiableCredential" etc.
  * `issuer_metadata_text` is a [Jq](https://jqlang.github.io/jq/manual/) expression, which is supposed give out metadata of this issuer, and metadata of the fields in the credential.
  * `context_json` is the [JSON-LD context](https://www.w3.org/TR/json-ld11/#the-context) of this VerifiableCredential.
  * `scope` is OIDC authentication scope. In other words this issuer will only respond to requests for which the auth scope matches the scope configured here. Example scopes; `farmer_id_vc_ldp` , etc.
  * Further this also adds parameters to configure authentication. Like allowed auth token issuers, allowed auth token audience, which Registrant ID is present in the auth token subject, etc.
  * Refer to [Configuration](openg2p-vci.md#configuration) for complete configuration reference.
* Any number of issuers can be created with different combinations of scope, credential\_type, credential\_format, issuer\_metadata.
* Say you want to issue two types of credentials from your registry, each of which needs different fields to be placed in the credential, then follow this:
  * Create two issuers, both issuer\_types are `Registry` .
  * Configure different credential types and scopes for both issuers.
  * Configure the credential format of both the issuers with the relevant fields to be placed.
  * Modify the issuer metadata of both the issuers along with relevant metadata for the fields.&#x20;
  * Modify contexts json with different fields and different credential type for both issuers.
* When a credential request is received, it will select the issuer based on the combination of scope (from auth JWT), credential type (from credential request body) (and `supported_format` which defaults to `ldp_vc` for now).
* This module also uses `g2p.encryption.provider` (of any type) to sign the final VC. If encryption provider is not configured on the issuer, it will use the default encryption provider.
* A credential will only be issued if the sub from auth JWT exists as one of IDs in registry against a registry entry.

### G2P OpenID VCI: Programs

Module Name: g2p\_openid\_vci\_programs

* This extends the "G2P OpenID VCI" module, by adding a new issuer type called `Beneficiary`. This effectively adds ability to issue VC for beneficiaries that are part of a program in PBMS.
* This adds a parameter to attach a Program to an Issuer. With this each Program in PBMS is an issuer.
* For example, if three programs are running on PBMS, 3 different issuers can be created with issuer\_type as "Beneficiary" and different programs.
  * Configure 3 different scopes for the three issuers. Example:
    * IssuerName: "SafetyNetIssuer", scope: "safety\_net\_program\_vc\_ldp", Program: "Safety Net Program".
    * IssuerName: "HumAidIssuer", scope: "hum\_aid\_program\_vc\_ldp", Program: "Humanitarian Aid Program", etc.
  * If the content of the credential is the same for all the 3 programs, then use a generic credential\_type and format across all three issuers, like "OpenG2PBeneficiaryVerifiableCredential". If the content is different in all programs, use different credential types.
* Unlike a Registry VC, a Beneficiary may contain additional data, like name of Program, duration for which this beneficiary is part of the program, last date till which this beneficiary is part of program, etc. All these are supported by this module.
* A credential will only be issued if the sub from auth JWT exists as one of IDs in registry against a registry entry, and that registrant is also an enrolled beneficiary of the said program.
* Rest of the functionality from the base module remains the same.

### G2P OpenID VCI: Rest API

Module Name: g2p\_openid\_vci\_rest\_api

* This module exposes the following [OpenID for VCI](https://openid.net/specs/openid-4-verifiable-credential-issuance-1\_0.html) REST APIs.
  * `/api/v1/vci/credential` API - the main credential request API. This first gets the issuer based on scope, credential type, and supported format. Then verifies verifies and validates auth JWT based on issuer config. Then retrieves registrant data based on issuer config and auth JWT sub. And then issues credential based on credential format.
  * `/api/v1/vci/.well-known/openid-credential-issuer` API - Issuer metadata API. This will collate the `issuer_metadata` of all issuers and return.
    * It is also possible to get individual metadata of each issuer by suffixing the above API with Issuer Name. Example `/api/v1/vci/.well-known/openid-credential-issuer/SafetyNetIssuer` .
  * `/api/v1/vci/.well-known/contexts.json` API - All the contexts from all the Issuers are collated and returned on this API. This path will be included in as context path within the VC.

## Create a custom VC Issuer

This section describes procedure for developing custom VC Issuers with custom functionality that is different from the above Registry Credential Issuer and Beneficiary Credential Issuer.

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

## Configuration

* VCI Issuers' configs can be found under `Settings` Menu -> `VCI Issuers`  Page.
* VC Issuer general config properties:

<table><thead><tr><th width="221">Name</th><th width="174">Property name</th><th>Description</th></tr></thead><tbody><tr><td>Name</td><td>name</td><td>Name of this issuer.</td></tr><tr><td>Scope</td><td>scope</td><td>Scope that is to be accepted in authentication.</td></tr><tr><td>Issuer Type</td><td>issuer_type</td><td>Type of Issuer</td></tr><tr><td>Supported Format</td><td>supported_format</td><td>VC Format supported. Defaults to <code>ldp_vc</code> .</td></tr><tr><td>Unique Issuer ID</td><td>unique_issuer_id</td><td>A unique id (string) assigned to this issuer. Defaults to <code>did:example:12345678abcdefgh</code> .</td></tr><tr><td>Encryption Provider</td><td>encryption_provider_id</td><td>Encryption Provider. If left blank, it will choose default encryption provider.</td></tr><tr><td>Auth Subject ID Type</td><td>auth_sub_id_type_id</td><td>Type of ID which is present in Subject of Authentication.</td></tr><tr><td>Auth Allowed Audiences</td><td>auth_allowed_auds</td><td><p>Only authentications with "aud" from this list will be allowed.</p><p>Seperated by space/newline.</p><p>If left blank, audience in auth will be ignored.</p></td></tr><tr><td>Auth Allowed Issuers</td><td>auth_allowed_issuers</td><td><p>Only authentications with "iss" from this list will be allowed.</p><p>Seperated by space/newline.</p></td></tr><tr><td>Auth Issuer Jwks Mapping</td><td>auth_issuer_jwks_mapping</td><td>JWKs Url of each issuer from "Auth Allowed Issuers".<br>If there are 3 entries in "Auth Allowed Issuers", then there should 3 Jwks urls in this too, one for each iss.<br>Seperated by space/newline.</td></tr><tr><td>Auth Allowed Client IDs</td><td>auth_allowed_client_ids</td><td><p>Only authentications with "client_id" from this list will be allowed.<br>Seperated by space/newline.</p><p>If left blank, client_id in auth will be ignored.</p></td></tr><tr><td>Credential Type</td><td>credential_type</td><td>Type of the VC. Leave it blank to take the default value, according to Issuer Type. </td></tr><tr><td>Credential Format</td><td>credential_format</td><td>Credential format as Jq expression. Leave it blank to take the default value, according to Issuer Type.</td></tr><tr><td>Issuer Metadata Text</td><td>issuer_metadata_text</td><td>Issuer Metadata as Jq expression. Leave it blank to take the default value, according to Issuer Type.</td></tr><tr><td>Contexts Json</td><td>contexts_json</td><td>Contexts Json for this credential Type. Leave it blank to take the default value, according to Issuer Type.</td></tr></tbody></table>

* VC Issuer Program/Beneficiary specific configs:

<table><thead><tr><th width="224">Name</th><th width="175">Property Name</th><th>Description</th></tr></thead><tbody><tr><td>Program</td><td>program_id</td><td>Program for which we are issuing the Beneficiary VC.</td></tr></tbody></table>
