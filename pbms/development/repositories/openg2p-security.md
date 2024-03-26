# openg2p-security

## Introduction <a href="#introduction" id="introduction"></a>

Source Code: [https://github.com/openg2p/openg2p-security](https://github.com/openg2p/openg2p-security)

This repository contains Odoo modules that help PBMS/Registry to perform cryptography operations like encrypt, decrypt, sign, verify, etc. and interface with external encryption modules like [Keymanager](https://github.com/mosip/keymanager). This also enables the registry to encrypt and store data or to decrypt the data on demand.

## Modules <a href="#modules" id="modules"></a>

This repository contains the following modules:

### G2P Encryption: Base <a href="#g2p-encryption-base" id="g2p-encryption-base"></a>

Module Name: g2p\_encryption

* This module contains the base model for `g2p.encryption.provider` .
* This base model exposes some basic cryptographic operations as Python functions so that subclasses can implement the functions. The `type` field drives which type of encryption provider to use.
  * This means custom encryption providers are supposed to extend this model, add their type, and implement the above crypto operations according to their type. Details are given [below](openg2p-security.md#creating-a-custom-encryption-provider).
* The cryptographic operations that are supported currently (that custom encryption providers can implement) are:
  * `encrypt`: encrypt given bytes.
  * `decrypt`: decrypt given bytes.
  * `jwt_sign`: Signs a given string/dictionary and returns a JWT.
  * `jwt_verify`: Verifies if the given JWT is valid.
  * `get_jwks`: get public keys/certificates of the encryption provider, which external parties should use to verify signatures, etc.
* This module also creates a default encryption provider instance (which can also be modified by the custom encryption providers), which will be used in all places if no purpose-specific encryption providers are created. This also enables users to just install the modules and use them directly without configuring anything.

### G2P Encryption: Keymanager <a href="#g2p-encryption-keymanager" id="g2p-encryption-keymanager"></a>

Module Name: g2p\_encryption\_keymanager

Installation Prerequisites: Keymanager and Keycloak.

* ​This module adds a new type called `keymanager` to the `g2p.encryption.provider` model.
* The module implements all the following functions by interacting with Keymanager APIs:
  * `encrypt`: runs `/v1/keymanager/encrypt` API call to encrypt given bytes.
  * `decrypt`: runs `/v1/keymanager/decrypt` API call to decrypt given bytes.
  * `jwt_sign`: runs `/v1/keymanager/jwtSign` API call to return signet JWT.
  * `jwt_verify`: runs `/v1/keymanager/jwtVerify` API call to verify given JWT.
  * `get_jwks`: gets certificates using  `/v1/keymanager/getAllCertificates`  and converts them to JWKs.

### G2P Encryption: Rest API <a href="#g2p-encryption-rest-api" id="g2p-encryption-rest-api"></a>

Module Name: g2p\_encryption\_rest\_api

* Exposes a `/.well-known/jwks.json` rest API. When called, this API will combine and return the JWKs returned by `get_jwks` function of all the encryption providers.

### G2P Registry Encryption <a href="#g2p-registry-encryption" id="g2p-registry-encryption"></a>

Module Name: g2p\_registry\_encryption

* This module uses an encryption provider (the type of provider doesn't matter, because it is abstracted out) to encrypt and decrypt Registry fields on demand.  Registry fields that should be encrypted can be configured on the encryption provider.
* This also adds the ability to turn registry encryption on or off in settings. This operation is only allowed for users with the Crypto Admin role.
* This also adds an ability where Crypto Admin users can decrypt the registry on demand to view the encrypted records.
* Whenever a new registry entry is added/updated, the to-be encrypted field data is collected into a JSON string, encrypted, and stored in one field. And vice-versa for decryption.

## Creating a custom Encryption Provider

*   Inherit `g2p.encryption.provider` model. Add a new type to the `type` Selection field using selection\_add. Example

    ```python
    type = fields.Selection(selection_add=[("mock", "Mock")])
    ```
* Implement the following functions:
  * `encrypt_data_{type}`
  * `decrypt_data_{type}`
  * `jwt_sign_{type}`
  * `jwt_verify_{type}`
  * `get_jwks_{type}`
*   Example:

    ```python
    def encrypt_data_mock(self, data: bytes, **kwargs) -> bytes:
        ...
    def decrypt_data_mock(self, data: bytes, **kwargs) -> bytes:
        ...
    def jwt_sign_mock(self, data, include_payload=True, include_certificate=True, include_cert_hash=True) -> str:
        ...
    def jwt_verify_mock(self, data: str, **kwargs):
        ...
    def get_jwks_mock(self, **kwargs):
        ...
    ```



## Configuration <a href="#configuration" id="configuration"></a>

* Encryption Providers' configs can be found under `Settings` Menu -> `Encryption Providers` Page. Configuration properties will vary depending on the encryption provider.
* If the encryption provider type is Keymanager, then the following config can be configured on the same Encryption Providers page:
  * If ENV Variable value is not empty against the config parameter below, it can be configured using the ENV var also.

<table><thead><tr><th width="200">Name</th><th width="151">Property name</th><th width="136">ENV Variable</th><th>Description</th></tr></thead><tbody><tr><td>Keymanager API Base URL</td><td>keymanager_api_base_url</td><td>KEYMANAGER_API_BASE_URL</td><td>Base URL to access Keymanager APIs. Defaults to k8s cluster local Keymanager URL, <code>http://keymanagar.keymanager/v1/keymanager</code>.</td></tr><tr><td>Keymanager Auth URL</td><td>keymanager_auth_url</td><td>KEYMANAGER_AUTH_URL</td><td>Auth URL to get auth for Keymanager APIs. Defaults to k8s local Keycloak token URL, <code>http://keycloak.keycloak/realms/openg2p/protocol/openid-connect/token</code>.</td></tr><tr><td>Keymanager Auth Client ID</td><td>keymanager_auth_client_id</td><td>KEYMANAGER_AUTH_CLIENT_ID</td><td>Keymanager Keycloak client ID. Defaults to <code>openg2p-admin-client</code>.</td></tr><tr><td>Keymanager Auth Client Secret</td><td>keymanager_auth_client_secret</td><td>KEYMANAGER_AUTH_CLIENT_SECRET</td><td>Keymanager Keycloak client secret.</td></tr><tr><td>Keymanager Auth Grant Type</td><td>keymanager_auth_grant_type</td><td>KEYMANAGER_AUTH_GRANT_TYPE</td><td>Defaults to <code>client_secret</code>.</td></tr><tr><td>Keymanager Encrypt Application ID</td><td>keymanager_encrypt_application_id</td><td></td><td>Defaults to <code>REGISTRATION</code>.</td></tr><tr><td>Keymanager Encrypt Reference ID</td><td>keymanager_encrypt_reference_id</td><td></td><td>Defaults to <code>ENCRYPT</code>.</td></tr><tr><td>Keymanager Sign Application ID</td><td>keymanager_sign_application_id</td><td></td><td>Defaults to <code>ID_REPO</code>.</td></tr><tr><td>Keymanager Sign Reference ID</td><td>keymanager_sign_reference_id</td><td></td><td></td></tr></tbody></table>

* For Registry Encryption, the following config can be configured on the Encryption Providers page:



| Name                                 | Property name                     | Description                                                                                                                                                                                                                                                                               |
| ------------------------------------ | --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Registry Fields to Encrypt           | registry\_fields\_to\_enc         | <p>Registry fields that are supposed to be considered for encryption-decryption. This should be given as a list. Defaults:</p><pre class="language-python"><code class="lang-python">["name","family_name","given_name","addl_name","display_name","address","birth_place"]
</code></pre> |
| Registry Encrypted Field Placeholder | registry\_enc\_field\_placeholder | String placeholder for an encrypted field in registry. Defaults to `encrypted`.                                                                                                                                                                                                           |

