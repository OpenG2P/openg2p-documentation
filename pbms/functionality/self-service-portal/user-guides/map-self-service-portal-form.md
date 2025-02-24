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

# 📔 Configure Login Providers for Beneficiary Portal

## Description

This document provides step-by-step instructions for configuring **Login Providers** in **PBMS** to enable end-users to log in to the **Beneficiary Portal**.

## Prerequisites

1. A client must be successfully created on the respective login provider you want to configure.
2. Install the **G2P Portal Auth** module.

## Steps

1. Enable **Debug Mode.** (Settings --> General Settings --> Developer Tools --> Activate the developer mode).

<figure><img src="../../../../.gitbook/assets/image (20).png" alt=""><figcaption></figcaption></figure>

2. Go to the **OAuth Providers** section. (Settings --> Users & companies --> OAuth Providers)

<figure><img src="../../../../.gitbook/assets/image (21).png" alt=""><figcaption></figcaption></figure>

3. Create a new **Login Provider** and enter the required values in the respective fields.

<figure><img src="../../../../.gitbook/assets/image (22).png" alt=""><figcaption></figcaption></figure>

For example, the fields, their descriptions, and sample values are given below.

<table><thead><tr><th width="230">Feature</th><th width="281">Description</th><th>Value</th></tr></thead><tbody><tr><td>Provider name</td><td>Enter the provider name.</td><td>For example: Keycloak for Beneficiary Portal Login</td></tr><tr><td>Auth Flow</td><td>Select the option <em><strong>OpenID Connect Authorization Code Flow</strong></em> from the drop-down.</td><td></td></tr><tr><td>Client ID</td><td>The ID of the client.</td><td></td></tr><tr><td>Client Authentication Method</td><td>Select the Client Authentication method.</td><td></td></tr><tr><td>Allowed</td><td>check the box.</td><td></td></tr><tr><td>Allowed in Self Service Portal</td><td>Check the box to enable the option <em><strong>Allowed</strong></em>.</td><td></td></tr><tr><td>Allowed in Service Provider Portal</td><td>Uncheck the box.</td><td></td></tr><tr><td>G2P Portal Oauth Callback Url</td><td>Configure the beneficiary portal callback URL.</td><td>For example: <code>&#x3C;beneficiary-portal-url>/v1/selfservice/oauth2/callback</code></td></tr><tr><td>Login button label</td><td>Enter the label name for the Login button.</td><td><p>For example:  <code>Login with National ID.</code></p><p>Note: This text with the button name will appear on login page. </p></td></tr><tr><td>Image Icon URL</td><td>Enter the URL of an image for the Login button.</td><td></td></tr><tr><td>Authorization URL, Userinfo URL, Token Endpoint, JWKS URL</td><td>These are to be configured as available in the well-known config of Login Provider. </td><td></td></tr><tr><td>Extra Authorize Params</td><td>Depending upon the Provider, configure the extra parameters if needed.</td><td></td></tr><tr><td>Enable Pkce?</td><td>Check the box.</td><td></td></tr><tr><td>Verify Access Token Hash</td><td>Check the box to enable the option <em><strong>Verify Access Token</strong></em>.</td><td></td></tr><tr><td>Allow Signup</td><td>Select the option <em><strong>Denies user signup (invitation only)</strong></em> from the drop-down. </td><td></td></tr><tr><td>Sync User Groups</td><td>Select the option <em><strong>Never</strong></em> from the drop-down. </td><td></td></tr><tr><td>G2P Registrant ID Type</td><td>Configure the ID Type where the user token will be stored.</td><td></td></tr></tbody></table>

The rest of the fields have the default values.
