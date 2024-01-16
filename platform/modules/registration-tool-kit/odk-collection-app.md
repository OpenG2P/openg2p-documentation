# ODK Collection App

## Introduction

OpenG2P platform uses the ODK Collect App to collect and manage the registrant information. The app can be used offline to carry out field registrations in areas without Internet connectivity. The registrant details are uploaded to ODK Central once the agent moves to an area with internet connectivity.

The app also has an integrated QR code scanning application to scan the ID card of the registrant. The scanning application automatically populates the KYC data of the registrant in the ODK form and verifies the digital signature to establish the card's authenticity.

## ODK

ODK is an open-source toolkit that uses offline forms to collect data. ODK Collect is the client-side app, and ODK Central is the server-side app.

Learn more about ODK [here](https://docs.getodk.org/).

## Registration process

The three steps involved in the registration process using the ODK Collect App are:

* ODK Central Configuration
* Field Registration
* Create ODK MTS Connector

#### ODK Central Configuration

A program administrator/manager performs the configuration.  The program administrator/manager must perform these necessary configurations to enable the field registration agent to collect information on the ODK Collect App.

* Program creation - To learn the steps, click [here](../../../guides/user-guides/create-a-program.md).
* Create ODK form in ODK Central - To learn the steps, click [here](../../../guides/user-guides/create-odk-form.md).
* Provide ODK form access to the field registration agent- To learn the steps, click [here](../../../guides/user-guides/provide-form-access-to-field-agent.md).

#### Field registration

The field registration agent downloads the ODK form using the ODK Collect App. To learn the steps, click [here](../../../guides/user-guides/download-form-on-odk-collect.md).

After downloading the app, the agent visits the field and follows these steps for registration:

* Captures the registrant's consent and records it
* Scans the ID card of the registrant to populate his/her KYC data
* Records further information such as household size, income, and home size
* Submits the registrant's information

The submitted forms are uploaded to ODK Central once the agent moves to an area with internet connectivity.

#### Create ODK MTS Connector

Based on the business scenario, a program administrator must create an [ODK MTS Connector](broken-reference) for individual/group to map the ODK forms available in the  ODK Central to the OpenG2P registry.&#x20;

**Business Scenario 1:** The verification process is not required on the individual/group information captured using ODK forms.

**Business Scenario 2:** The verification process is required on the individual/group information captured using ODK forms.

**Business Scenario 1:**

1. A program administrator creates an ODK MTS Connector for individual/group to map the ODK forms available in the ODK Central.
2. The ODK MTS Connector regularly queries the ODK Central for the submitted forms. Whenever forms are available, the MTS Connector maps the individual/group KYC data from them.
3. The ODK MTS Connector then calls OpenG2P Rest APIs to populate the OpenG2P registry with the individual/group KYC data.&#x20;

&#x20;      _Note: The OpenG2P registry accepts the individual/group KYC data only in JSON format._

**Business Scenario 2:**

1. A program administrator creates an ODK MTS Connector for individual/group to map the ODK forms available in the ODK Central.
2. The ODK MTS Connector regularly queries the ODK Central for submitted forms. Whenever forms are available, the MTS Connector maps the individual/group KYC data from them and sent to MTS (MOSIP Token Seeder).
3. MTS outputs an authentication token for each individual/group KYC data after performing ID verification. The authentication token is the proof of the registrant's authentication by the MOSIP ID Authentication system.
4. Post authentication, the MTS Connector maps the registrant information from the submitted form and the authentication token in the JSON format accepted by OpenG2P. The ODK MTS connector then calls OpenG2P Rest APIs to populate the OpenG2P registry with the registrant’s information in JSON object.&#x20;

&#x20;      _Note: The OpenG2P registry accepts the individual/group KYC data only in JSON format._

To learn the steps to create an ODK MTS Connector, click [here](../../../guides/user-guides/create-mts-connector/create-odk-mts-connector.md).

## Demo video

{% embed url="https://youtu.be/0jjkq4SoONM" %}

## Related links

* [Create Program](../../../guides/user-guides/create-a-program.md)
* [Create ODK Form](../../../guides/user-guides/create-odk-form.md)
* [Provide ODK Form Access to Field Agent](../../../guides/user-guides/provide-form-access-to-field-agent.md)
* [Download Form on ODK Collect](../../../guides/user-guides/download-form-on-odk-collect.md)
* [Create ODK MTS Connector](../../../guides/user-guides/create-mts-connector/create-odk-mts-connector.md)
