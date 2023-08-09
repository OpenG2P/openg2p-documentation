# ODK Collect App

## Introduction

OpenG2P platform uses ODK Collect App to collect and manage the registrant information. The app can be used offline as well to carry out field registrations in areas where Internet connectivity may not be available. The registrant details are uploaded to ODK Central once the agent moves to an area with internet connectivity.

The app also has an integrated QR code scanning application to scan the ID card of the registrant. The scanning application automatically populates the KYC data of the registrant in the ODK form and verifies the digital signature to establish the card's authenticity.&#x20;

## ODK

ODK is an open-source toolkit that uses offline forms to collect data. ODK Collect is the client-side app while ODK Central is the server-side app. Learn more about ODK [here](https://docs.getodk.org/).

## Registration process

There are three key steps involved in registration using ODK Collect App.

#### ODK Central Configuration

This step is carried out by a program administrator/manager. To enable the field registration agent to collect information on the ODK Collect App, the administrator/manager has to do these necessary configurations:

* Program creation: To learn the steps, click [here](../../guides/user-guides/create-a-program.md).
* Create ODK form in ODK Central: To learn the steps, click [here](../../guides/user-guides/create-odk-form.md).
* Provide ODK form access to field agent: To learn the steps, click [here](../../guides/user-guides/provide-form-access-to-field-agent.md).

#### Field registration

The field registration agent downloads the ODK form using ODK Collect App. To learn the steps, click [here](../../guides/user-guides/download-form-on-odk-collect.md).

After downloading the app, the agent visits the field and follows these steps for registration:

* Captures the registrant's consent and records it
* Scans the ID card of the registrant to populate the KYC data of the registrant
* Fills in further information such as household size, income, and home size
* Submits the registrant's information&#x20;

The submitted forms are uploaded to ODK Central once the agent moves to an area with internet connectivity.&#x20;

#### Create ODK MTS Connector

A program administrator needs to create [ODK MTS Connector](../../integrations/integration-with-mosip/mts-connector.md) to map the ODK forms in ODK Central to the OpenG2P registry. MTS Connector is the glue that holds ODK Central, MTS, and OpenG2P Registry together.&#x20;

<figure><img src="https://github.com/OpenG2P/openg2p-documentation/raw/e9fdceeedd6e483eb45098b9a72f013a331451cf/.gitbook/assets/offline-registration-process.png" alt=""><figcaption></figcaption></figure>

The ODK MTS Connector regularly queries the ODK Central for submitted forms. Whenever forms are available, the MTS Connector maps the KYC data from the forms and sends them to MTS. MTS outputs an authentication token for each KYC data after performing [ID verification](../id-verification.md#registrant-authentication-using-mts). The authentication token is the proof of the registrant's authentication by the MOSIP ID Authentication system.

Post authentication, the MTS Connector maps the registrant information from the submitted form and the authentication token in the JSON format understood by OpenG2P. The connector then calls OpenG2P Rest APIs to populate the OpenG2P registry with the JSON object.

To learn the steps to create an ODK MTS Connector [here](../../guides/user-guides/create-mts-connector/create-odk-mts-connector.md).

## Demo video

{% embed url="https://youtu.be/0jjkq4SoONM" %}

## How-To Guides

* [Create Program](../../guides/user-guides/create-a-program.md)
* [Create ODK Form](../../guides/user-guides/create-odk-form.md)
* [Provide ODK Form Access to Field Agent](../../guides/user-guides/provide-form-access-to-field-agent.md)
* [Download Form on ODK Collect](../../guides/user-guides/download-form-on-odk-collect.md)
* [Create ODK MTS Connector](../../guides/user-guides/create-mts-connector/create-odk-mts-connector.md)
