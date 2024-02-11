# Admin Guide to Update ID with Financial Address information

## Introduction

This document contains step-by-step instructions for administrator to update the .csv file with beneficiary data  and run the script to map the national ID with the FA of the beneficiary. The updated data can be retrieved from currently linked FA list in the self service portal.&#x20;

## Prerequisite

* The user must have knowledge to access [SPAR](../../../deployment/openg2p-modules-deployment/spar-deployment/) via internet which is available in public portal
* The user must have administrator role
* A sample .csv file
* A script to map the national ID with the FA of the beneficiary which are listed in the .csv file by administrator
* The administrator system must have python and its modules cryptography, requests installed

## Procedure

The administrator must follow the following sequence process:

1. [Update the csv file](admin-guide-to-update-id-with-financial-address-information.md#update-the-csv-file) with the beneficiary details
2. [Run the python script](admin-guide-to-update-id-with-financial-address-information.md#run-the-script) to link the National ID with the FA
3. [Response](admin-guide-to-update-id-with-financial-address-information.md#response-triggered-in-cmd) is displayed in cmd file
4. [Retrieve](admin-guide-to-update-id-with-financial-address-information.md#retrieve-the-updated-data) the data in the portal

### Update the csv file

The administrator must follow the below steps to run the script.

1. The administrator must clone the repository [https://github.com/OpenG2P/social-payments-account-registry/tree/develop/scripts](https://github.com/OpenG2P/social-payments-account-registry/tree/develop/scripts)
2. Download the _**sample\_data.csv**_ file and update the data of the beneficiaries in the respective columns

Note:

The administrator must update the columns _**National ID**_ and _**Account number**_, while columns _**Name**_ and _**phone**_ are optional.

<figure><img src="../../../.gitbook/assets/sample-csv-file.png" alt=""><figcaption><p>sample-csv-file.</p></figcaption></figure>

### Run the Script

3. Click the python script file _**link\_mapper.py**_. The script is displayed.

<figure><img src="../../../.gitbook/assets/python-script.png" alt=""><figcaption><p>Python script.</p></figcaption></figure>

3. The mapper\_link\_api\_url  and the csv\_path must be verified and updated.&#x20;
4. Save and download the script file _**link\_mapper.py**_.
5. Double click the script link\_mapper.py from the downloaded path.

<figure><img src="../../../.gitbook/assets/python-script-file.png" alt=""><figcaption><p>Python script file.</p></figcaption></figure>

### Response triggered in cmd

6. After the administrator runs the script, the response is triggered in a cmd file which shows that the National ID is linked to the FA of the beneficiaries.

<figure><img src="../../../.gitbook/assets/Sample-response-message .png" alt=""><figcaption><p>Sample response message.</p></figcaption></figure>

6. &#x20;Press Enter to exit from the cmd prompt.&#x20;

### Retrieve the updated data

7. Open the SPAR URL on your browser,  for example, https://spar.openg2p.sandbox.net
8. \<Geo-specific portal> page is displayed.

<figure><img src="../../../.gitbook/assets/login-page (1).png" alt=""><figcaption><p>Name of the portal.</p></figcaption></figure>

There are two options available to login self-service portal.

* Login with your email or phone number&#x20;
* [Login with your National ID](admin-guide-to-update-id-with-financial-address-information.md#login-with-national-id)

### Login with National ID

9. Click the _**SIGNIN WITH NATIONAL ID**_ button.
10. Login with eSignet page is displayed.

<figure><img src="../../../.gitbook/assets/e-signet-login.png" alt=""><figcaption><p>eSignet login page.</p></figcaption></figure>

You can select your preferred mode of login

* [Login with OTP](admin-guide-to-update-id-with-financial-address-information.md#login-with-otp)
* Login with Biometrics
* Login with Inji Mobile App
* Login with Inji Mobile App1

#### Login with OTP

11. Click the _**Login with OTP**_ button.
12. _**Login with OTP**_ page pops up.

<figure><img src="../../../.gitbook/assets/login-otp.png" alt=""><figcaption><p>Login with OTP.</p></figcaption></figure>

####

13. Enter the _**VID**_ number and click the _**Get OTP**_ button.

You receive the OTP number in your registered phone number.

14. Enter the OTP number and click the _**Verify**_ button.

<figure><img src="../../../.gitbook/assets/login-otp-verify.png" alt=""><figcaption><p>OTP verification.</p></figcaption></figure>

It redirects to the \<Geo-specific portal> Home page_**.**_

<figure><img src="../../../.gitbook/assets/NSPAP - Home page (1).png" alt=""><figcaption><p>Home page.</p></figcaption></figure>

In _**Home**_ page, the features and their descriptions are:

| Feature                                                                         | Description                                                                                                             |
| ------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| <img src="../../../.gitbook/assets/image (12).png" alt="" data-size="original"> | It displays your name.                                                                                                  |
| Update your Linked Financial Address                                            | This tab is used to update the bank details/wallet/mpesa and map your national ID with your bank/wallet/mpesa account.  |
| Currently Linked Financial Address                                              | This tab populates the current list of linked financial address.                                                        |

## Currently Linked Financial Address

In _**Currently Linked Financial Address**_ tab,

15. Click the button _**GET CURRENT FINANCIAL ADDRESS.**_
16. The administrator mapped beneficiary data iusing script is displayed in the currently linked FA.

