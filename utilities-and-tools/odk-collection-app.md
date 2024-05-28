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

# ODK

ODK (Open Data Kit) is an open-source toolkit that helps organizations collect, manage, and use data, particularly in areas with limited internet connectivity. It enables users to create custom data collection forms on mobile devices and collect data offline. ODK Collect is the client-side app, and ODK Central is the server-side app.

To learn more about ODK, click [here](https://docs.getodk.org/).

OpenG2P uses the ODK Collect App to collect and manage registrant information. The app works offline, allowing field registrations in areas without internet connectivity. The details are uploaded to ODK Central when the agent has internet access.

The app also has an integrated QR code scanning application to scan the ID card of the registrant. The scanning application automatically populates the KYC data of the registrant in the ODK form and verifies the digital signature to establish the card's authenticity.\


### Feature and functionality

<table><thead><tr><th width="283">Feature</th><th>Functionality</th></tr></thead><tbody><tr><td><strong>Offline Data Collection</strong></td><td>ODK Collect allows users to collect data offline, which is crucial for field registrations in areas without internet connectivity.</td></tr><tr><td><strong>Custom Forms</strong></td><td>Users can create custom data collection forms tailored to their specific needs, enhancing the flexibility and adaptability of the platform.</td></tr><tr><td><strong>Integration with ODK Central</strong></td><td>The data collected using ODK Collect is stored and managed on ODK Central and allows organizations to access and analyze the data easily, even if it was collected offline.</td></tr><tr><td><strong>QR Code Scanning</strong></td><td>QR code scanning in ODK Collect allows users to quickly capture information from ID cards or other sources by scanning QR codes.</td></tr><tr><td><strong>Digital Signature Verification</strong></td><td>ODK Collect verifies the digital signature of scanned ID cards, ensuring the authenticity of the information provided.</td></tr><tr><td><strong>Language Support</strong></td><td></td></tr><tr><td><strong>Calendar</strong></td><td></td></tr><tr><td><strong>Capture the Location Details</strong></td><td></td></tr></tbody></table>

## Registration process

The three steps involved in the registration process using the ODK Collect App are:

* ODK Central Configuration
* Field Registration
* Use [**ODK Importer**](../pbms/features/odk-importer/) or [**MTS Connector**](../pbms/development/odoo-modules/mts-connector.md)

### ODK Central Configuration

A program administrator/manager performs the configuration.  The program administrator/manager must perform these necessary configurations to enable the field registration agent to collect information on the ODK Collect App.

* Program creation - To learn the steps, click [here](../pbms/features/program-management/user-guides/create-a-program.md).
* Create ODK form in ODK Central - To learn the steps, click [here](odk-collection-app/user-guides/create-a-form.md).
* Provide ODK form access to the field registration agent - To learn the steps, click [here](odk-collection-app/user-guides/provide-form-access-to-field-agent.md).

### Field registration

The field registration agent downloads the ODK form using the ODK Collect App. To learn the steps, click [here](odk-collection-app/user-guides/download-form-on-odk-collect.md).

After downloading the app, the agent visits the field and follows these steps for registration:

* Captures the registrant's consent and records it.
* Scans the ID card of the registrant to populate his/her KYC data.
* Record further information such as household size, income, and home size.
* Submits the registrant's information.

The submitted forms are uploaded to ODK Central once the agent moves to an area with internet connectivity.

### Create ODK MTS Connector

### ODK Importer

ODK  and OpenG2P are connected through the ODK Importer module, which is specifically designed to import ODK forms of beneficiaries into OpenG2P Systems. The ODK Importer streamlines data transfer from ODK forms directly into OpenG2P Systems, eliminating manual data entry and improving data accuracy and efficiency in data management.

The ODK Importer module acts as a bridge between ODK forms and OpenG2P Systems, facilitating the integration and efficient management of data collected through ODK in the OpenG2P platform.

Based on the business scenario, a program administrator must create an ODK [MTS Connector](https://docs.mosip.io/1.2.0/integrations/mosip-token-seeder/mts-odk-importer) for each individual /group to map the ODK forms available in the  ODK Central to the OpenG2P registry.&#x20;

A program administrator must create an ODK MTS Connector to map the ODK forms in ODK Central to the OpenG2P registry. MTS Connector is the glue that holds ODK Central, MTS, and OpenG2P Registry together.&#x20;

<table><thead><tr><th width="373">No Verification </th><th> Verification </th></tr></thead><tbody><tr><td>A program administrator creates an ODK MTS Connector for individual/group to map the ODK forms available in the ODK Central.</td><td>A program administrator creates an ODK MTS Connector for individual/group to map the ODK forms available in the ODK Central.</td></tr><tr><td>The ODK MTS Connector regularly queries the ODK Central for the submitted forms. Whenever forms are available, the MTS Connector maps the individual/group KYC data from them.</td><td>The ODK MTS Connector regularly queries the ODK Central for the submitted forms. Whenever forms are available, the MTS Connector maps the individual/group KYC data from them and sends to MTS (MOSIP Token Seeder).</td></tr><tr><td> </td><td>MTS outputs an authentication token for each individual/ group's KYC data after performing ID verification. The authentication token is the proof of the registrant's authentication by the MOSIP ID Authentication system.</td></tr><tr><td>The ODK MTS Connector then calls OpenG2P Rest APIs to populate the OpenG2P registry with the individual/group KYC data.</td><td>Post-authentication, the MTS Connector maps the registrant information from the submitted form and the authentication token in the JSON format accepted by OpenG2P. The ODK MTS connector then calls OpenG2P Rest APIs to populate the OpenG2P registry with the registrant’s information in JSON object.</td></tr></tbody></table>

&#x20;_Note: The OpenG2P registry accepts the individual or group KYC data only in JSON format._

To learn the steps to create an ODK MTS Connector, click [here](../pbms/user-guides/eligibility-and-program-enrollment/mts-connector/create-mts-connector/create-odk-mts-connector.md).

## ODK language support

## ODK geographic

## Demo video

{% embed url="https://youtu.be/0jjkq4SoONM" %}

## Related user guides

:notebook\_with\_decorative\_cover:[Create Program](../pbms/features/program-management/user-guides/create-a-program.md)

:notebook\_with\_decorative\_cover:[Create ODK Form](odk-collection-app/user-guides/create-a-form.md)

:notebook\_with\_decorative\_cover:[Provide ODK Form Access to Field Agent](odk-collection-app/user-guides/provide-form-access-to-field-agent.md)

:notebook\_with\_decorative\_cover:[Download Form on ODK Collect](odk-collection-app/user-guides/download-form-on-odk-collect.md)

:notebook\_with\_decorative\_cover:[Create ODK MTS Connector](../pbms/user-guides/eligibility-and-program-enrollment/mts-connector/create-mts-connector/create-odk-mts-connector.md)
