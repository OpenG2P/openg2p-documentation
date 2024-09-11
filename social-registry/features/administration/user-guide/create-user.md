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

# 📔 Create User

This document provides instructions to create user in the _**Social Registry**_ module.

## Prerequisites

* The user must have access to the Social Registry module.
* The user must have Registrar and Administrator role.

## Procedure

1. Click the main menu icon ![](../../../../.gitbook/assets/main-menu.png) and select _**Settings**_.

<figure><img src="../../../../.gitbook/assets/menu-settings.png" alt=""><figcaption></figcaption></figure>

The _**Settings**_ screen is displayed.

<figure><img src="../../../../.gitbook/assets/settings-screen.png" alt=""><figcaption></figcaption></figure>

2. In the menu bar, click the _**Users & Companies**_ and then select Users.

<figure><img src="../../../../.gitbook/assets/users-companies-social-registry.png" alt=""><figcaption></figcaption></figure>

_**Users**_ screen is displayed. It is a dashboard which lists the details of all the available Users Name, Login, Language, Latest authentication and their status.

<figure><img src="../../../../.gitbook/assets/users-screen-sr.png" alt=""><figcaption></figcaption></figure>

3. Click the _**New**_ button.

_**User New**_ screen is displayed.

<figure><img src="../../../../.gitbook/assets/users-new-screen-sr.png" alt=""><figcaption></figcaption></figure>

In _**Users New**_ screen, the available features and their descriptions are:

<table><thead><tr><th width="166">Feature</th><th>Description</th></tr></thead><tbody><tr><td>Name</td><td>Enter the new user name</td></tr><tr><td>Email Address</td><td>Enter the valid email Id. of the user. The invitation email will be sent to this email address.</td></tr><tr><td><img src="../../../../.gitbook/assets/photo-camera-icon.png" alt="" data-size="original"></td><td><ul><li>Select the icon, click the edit icon and then navigate to the user photo where it is stored</li><li>Export the user photo</li><li>Click the delete icon to delete the user photo</li></ul></td></tr></tbody></table>

4. Click the _**Access Rights**_ tab.

The fields and their descriptions are given below:

| Field          | Description                                                                                                                                                                                                                                                                                                                                   |
| -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Accounting     | <p><em><strong>Invoicing</strong></em></p><p>Select the appropriate value from the drop-down. The available values are</p><ul><li>Billing </li><li>Billing Administrator</li></ul><p><em><strong>Bank</strong></em></p><p>Select the appropriate value from the drop-down, The available value is </p><ul><li>Validate bank account</li></ul> |
| Website        | <p>Select the appropriate value from the drop-down. The available values are </p><ul><li>Restricted Editor</li><li>Editor and Designer</li></ul>                                                                                                                                                                                              |
| Administration | <p>Select the appropriate value from the drop-down. The available values are </p><ul><li>Access Rights</li><li>Settings</li></ul>                                                                                                                                                                                                             |
| Other          | <p><em><strong>Job Queue</strong></em></p><p>Select the appropriate value from the drop-down. The available value is</p><ul><li>Job Queue Manager</li></ul><p><em><strong>Dashboard</strong></em></p><p>Select the appropriate value from the drop-down. The available value is</p><ul><li>Admin</li></ul>                                    |

5. Click the _**Preferences**_ tab.

<figure><img src="../../../../.gitbook/assets/user-preference-sr.png" alt=""><figcaption></figcaption></figure>

The fields and their descriptions are given below:

| Field           | Description                                                                                                           |
| --------------- | --------------------------------------------------------------------------------------------------------------------- |
| Language        | Select the preferred language from the drop-down.                                                                     |
| Timezone        | Select the timezone from the drop-down list.                                                                          |
| Notification    | <p>Select the appropriate radio button. The values are: </p><ul><li>Handle by Emails</li><li>Handle in Odoo</li></ul> |
| Email Signature | Enter the valid Email ID.                                                                                             |

<figure><img src="../../../../.gitbook/assets/user-new-filled-screen-sr.png" alt=""><figcaption></figcaption></figure>

6. Click the _**Oauth**_ tab.

<figure><img src="../../../../.gitbook/assets/oauth-tab-sr.png" alt=""><figcaption></figcaption></figure>

The fields and their descriptions are given below:

| Field              | Description                                                                                                                                                                     |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| OAuth Provider     | <ul><li>Select the appropriate value from the drop-down. </li></ul><p>(or)</p><ul><li>Search for the OAuth Provider using the Search more option from the drop-down. </li></ul> |
| OAuth User ID      | Enter the OAuth user ID.                                                                                                                                                        |
| OAuth Access Token | Check the _**OIDC Groups Rest**_ box or _**OIDC Userinfo Reset**_ box as per the requirement                                                                                    |

7. Click the _**Account Security**_ tab.

<figure><img src="../../../../.gitbook/assets/account-security-tab.png" alt=""><figcaption></figcaption></figure>

8. Click the _**Invite to use 2FA**_ button to enable 2FA for a user.

| Icon                                                                                         | Click to                                                                                                                                                                                                                                     |
| -------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| <img src="../../../../.gitbook/assets/Actions.png" alt="" data-size="original">              | <p>Select the appropriate value. The available values are: </p><ul><li>Archive</li><li>Duplicate</li><li>Change Password</li><li>Disable two-factor authentication</li><li>Send Password Reset Instructions</li><li>Privacy Lookup</li></ul> |
| <img src="../../../../.gitbook/assets/icon-save-manually.png" alt="" data-size="original">   | Save manually the individual data and exit from the screen.                                                                                                                                                                                  |
| <img src="../../../../.gitbook/assets/discard-changes-icon.png" alt="" data-size="original"> | Discard changes and exit from the screen.                                                                                                                                                                                                    |

The newly created user is added to the user list.

<figure><img src="../../../../.gitbook/assets/user-list-sr.png" alt=""><figcaption></figcaption></figure>

Assign user role
