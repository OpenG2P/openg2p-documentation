# Social Account Registry

## Introduction



<figure><img src="https://raw.githubusercontent.com/OpenG2P/openg2p-documentation/1.1/.gitbook/assets/social-account-registry.png" alt=""><figcaption></figcaption></figure>

## Sunbird Registry

* Account mapper compliant to G2P Connect interface
* Database of ID Tokens and Account Numbers

## Token Mapper

* With user consent, map token SAR token to OpenG2P app
* Database table for token mapping
* Automatic deletion of records based on expiry set
* Notification to user via SMS/email
* Onboarding of consumer apps (like OpenG2P)

## SAR Account Validator

One suggested way to validate the user account number is to initiate a small cash transfer from the treasury account to the person's account. Upon successful transfer (as communicated by the bank) consider the account mapper entry valid. This could take several minutes to hours as it depends on the response from the bank.&#x20;

Configuration: Treasury account details

## Self Service Portal

* Authentication page leading to e-Signet interface.
* Consent page for users to map token for a time period specifically for an app (like OpenG2P)
* Display of current account number of the user.
* Option to add/update the account number and account details.
* Notification to users via email/sms
* Onboarding of authenticators like e-Signet.



##
