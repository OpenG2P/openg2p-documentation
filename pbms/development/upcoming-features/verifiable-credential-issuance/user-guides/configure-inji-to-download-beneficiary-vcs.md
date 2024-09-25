# 📔 Configure Inji to download Beneficiary VCs

This guide contains the procedure to install and set up the backend required for the Inji App to download PBMS Beneficiary VCs.

## Prerequisites

* eSignet is available with the National ID system and is ready for authentication. If not available, a mock eSignet can be installed with PBMS.
* [G2P OpenID VCI: Base](../../../odoo-modules/g2p-openid-vci-base.md), [G2P OpenID VCI: Programs](../../../odoo-modules/g2p-openid-vci-programs.md), [G2P OpenID VCI: Rest API](../../../odoo-modules/g2p-openid-vci-rest-api.md) odoo modules are installed on PBMS.

## Procedure

### 1. Create Mimoto OIDC client

(Only required for testing. Not required for production.)

1. Create an [eSignet OIDC client](../../../../../social-registry/features/id-authentication/user-guides/esignet-client-creation.md) with the following parameters:
   * clientId: mimoto-oidc
   * clientName: Inji Wallet
   * logoUrl:[https://raw.githubusercontent.com/mosip/mosip-file-server/master/mosip-file-server/inji-model/inji-home-logo.png](https://raw.githubusercontent.com/mosip/mosip-file-server/master/mosip-file-server/inji-model/inji-home-logo.png)
   * redirectUris: `io.mosip.residentapp.inji://oauthredirect` .
   * relyingPartyId: `mpartner-default-mimoto` .

### 2. Create OpenG2P Mimoto OIDC Client

1. Create an [eSignet OIDC client](../../../../../social-registry/features/id-authentication/user-guides/esignet-client-creation.md) with the following parameters:
   * clientId: `openg2p-mimoto-oidc`
   * clientName: `Inji Wallet`
   * logoUrl: [https://raw.githubusercontent.com/mosip/mosip-file-server/master/mosip-file-server/inji-model/inji-home-logo.png](https://raw.githubusercontent.com/mosip/mosip-file-server/master/mosip-file-server/inji-model/inji-home-logo.png)
   * redirectUris: `io.mosip.residentapp.inji://oauthredirect` .
   * relyingPartyId: `openg2p-auth-partner` .

### 3. Setup Mimoto Issuers Config

1. Fork this repository [https://github.com/OpenG2P/mosip-config](https://github.com/OpenG2P/mosip-config).
2. Edit [mimoto-issuers-config.json](https://github.com/OpenG2P/mosip-config/blob/master/mimoto-issuers-config.json) with appropriate names and URLs.

### 4. Install Mimoto

(Only required for testing. Not required for production.)

1. Collect public-key-private-key pairs from both the OIDC clients created above.
2. Create a P12 file using [KeyStore Explorer](configure-inji-to-download-beneficiary-vcs.md#prerequisites).&#x20;
   * Import the Mimoto OIDC client key pair with the name `mpartner-default-mimotooidc` and an appropriate password (The rest of this guide assumes this password is `openg2p123` ).
   * Import the OpenG2P Mimoto OIDC client key pair with the name `openg2p-mimotooidc` with the same password as the one for the above key pair, `openg2p123`.
   * Set keystore password. The password should be the same as the above, `openg2p123`.
3.  Create a K8s secret with the name `mimoto-oidc-secret`, for the above P12 file:

    ```bash
    kubectl -n <namespace> create secret generic mimoto-oidc-secret \
        --from-file=oidckeystore.p12=<path to above p12 file>
    ```
4. Install Mimoto in your OpenG2P namespace using Rancher:
   * Go to Rancher -> Apps -> Repositories. Add a repository with this URL if it doesn't exist [https://openg2p.github.io/openg2p-helm](https://openg2p.github.io/openg2p-helm/rancher) (name can be given as `openg2p-extras`).
   * Select the namespace in the Rancher namespace filter.
   * Go to Rancher -> Apps -> Charts. Refresh all charts. Search and select Mimoto. Choose version 0.13.0 or higher. On the config page, give the name of the Kubernetes secret containing the OIDC keystore, the keystore password, URL of the mosip-config repo from step 3.1, along with any other details asked. Finish installation.

### 5. Set up PBMS for VC Issuance

1. Go to PBMS -> Settings -> VCI Issuers. Create one VC Issuer for each program for which VC download should be supported. Configure VC Issuer with the following parameters:
   * Name: Name to identify the VC Issuer and to be displayed on the Inji App when downloading.&#x20;
   * Scope: Scope should be one of the entries present in the `scopes_supported` field in [mimoto-issuers-config.json](https://github.com/OpenG2P/mosip-config/blob/master/mimoto-issuers-config.json).
   * Issuer Type: Beneficiary
   * Program: Choose the relevant program
   * Auth Subject ID Type: NATIONAL ID TOKEN.
   * Auth Allowed Issuers: eSignet Issuer URL (Example: https://esignet.explore.openg2p.org.)
   * Leave the rest of the fields with default values and save. Upon saving all the other fields will get auto-populated.

### 6. Setup Inji App

1. Download Inji App version 0.13.0 or higher.
2. Go to Inji -> Settings -> Credential Registry. Edit :
   * Credential Registry: Mimoto Base URL given in step 4.4. (Example: https://mimoto.explore.openg2p.org)
   * Esignet Host: eSignet Base URL (Example: https://esignet.explore.openg2p.org)

Now the Inji App should be ready to download Beneficiary credentials. (Beneficiary should be enrolled in the program and should be an active beneficiary to be able to download the card.)
