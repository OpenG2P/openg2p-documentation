---
description: Work In progress
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

# ODK Importer

The ODK Importer is a module built by OpenG2P. It is specifically designed to tailor, configure the required field based on the ODK (Open Data Kit) form, and import the relevant ODK form of the beneficiaries into OpenG2P Systems. The benefits of using ODK Importer are:

* Streamlines data transfer from ODK forms directly into OpenG2P Systems
* Eliminates manual data entry, improves data accuracy and efficiency in data management
* Provides data import for automatic updates using automated scheduler

## Feature and functionality

<table><thead><tr><th width="213">Feature </th><th>Functionality</th></tr></thead><tbody><tr><td><strong>Data Import</strong></td><td><ul><li>Allows users to import data from ODK forms into relevant fields within the OpenG2P Systems</li><li>Streamlines the process of transferring data, collected in the field using ODK forms into the OpenG2P Systems, ensuring accuracy and efficiency in data management</li></ul></td></tr><tr><td><strong>Test Connection</strong></td><td><ul><li>Verifies the established connection between the ODK Importer and ODK Central</li><li>Ensures that the ODK Importer can effectively communicate with ODK Central, the server hosting the ODK forms </li><li>Enables seamless data transfer between the two systems</li></ul></td></tr><tr><td><strong>Import Records</strong></td><td><ul><li>Tracks the progress of data import and identifies any errors that may occur during the process  </li><li>Provides users with real-time updates on the status of their data import, allowing them to quickly address any issues and ensure a smooth import process</li></ul></td></tr><tr><td><strong>Automated Data Processing</strong></td><td><ul><li>Removes the risk of manual error, ensuring higher accuracy in data records.</li><li>Streamlines task, saves time and resources while enhancing overall operational efficiency.</li></ul></td></tr><tr><td><strong>Automated Scheduler</strong></td><td><ul><li>Allows smooth updates that do not require operator intervention. This capability enables rapid and regular changes to data sets, improving data currency and relevancy</li><li>Automates the import process, improves workflow efficiency, and avoids delay in processing</li></ul></td></tr></tbody></table>

## Process workflow

{% embed url="https://miro.com/app/board/uXjVKcYGOyg=/" %}

## **Process & Data Flow**

1. **User initiates import:** User selects the desired ODK form and configures import options.
2. **Data Mapping:** User establishes a mapping between corresponding fields in the ODK form using JSON-formatter (PYJQ) and the OpenG2P system.
3. **Connection & Data Retrieval:** Module connects to ODK Central and retrieves data based on the selected form and import options.
4. **Data Import:** Extracted data is imported into the designated fields within the OpenG2P system.
5. **Import Status Update:** User receives notification of successful import completion or encounters any errors.

## Concepts

1. **ODK Form**: This is the source of data collection through the ODK. ODK forms are used to collect various types of data, such as beneficiary information in a structured format.
2. **Mapping**: Mapping defines the correspondence between fields in the ODK form and the OpenG2P system. It ensures that data collected in the ODK form is accurately mapped to the corresponding fields within the OpenG2P system.

## **Configuration**

The ODK Importer module requires configuration to establish a connection with ODK Central and define import parameters. Users can access the configuration settings through the **ODK** menu in the system.

### **Configuration parameters**

<table><thead><tr><th width="226">Parameters</th><th>Description</th></tr></thead><tbody><tr><td><strong>Base URL</strong></td><td>The base URL of the ODK Central instance from which data will be retrieved</td></tr><tr><td><strong>Username/Password</strong></td><td>Login credentials for accessing ODK Central</td></tr><tr><td><strong>Project ID</strong></td><td>The unique identifier of the ODK project containing the data to be imported</td></tr><tr><td><strong>Form ID</strong></td><td>The unique identifier of the specific ODK form within the chosen project that holds the data for import</td></tr><tr><td><strong>JSON Formatter</strong></td><td>Enables users to define a custom JSON formatter for transforming retrieved data before importing it into the OpenG2P system. Refer to relevant documentation for details on utilizing the JSON formatter using <a href="https://pypi.org/project/pyjq/">PYJQ library</a></td></tr><tr><td><strong>Target Registry</strong></td><td><p>Specifies whether imported records should be associated with individual or group registries within the OpenG2P system. </p><p>Available options are:</p><ul><li>Individual</li><li>Groups</li></ul></td></tr><tr><td><strong>Interval in Hours (Optional)</strong></td><td>Defines the interval (in hours) at which the import process should be automatically triggered. This allows for scheduled data updates.</td></tr><tr><td><strong>ODK Program (Optional)</strong></td><td>Map the registrant into the program using ODK Import</td></tr></tbody></table>

## **Source code**

[https://github.com/OpenG2P/openg2p-importers/tree/17.0-develop/g2p\_odk\_importer](https://github.com/OpenG2P/openg2p-importers/tree/17.0-develop/g2p\_odk\_importer)

## **Technical concepts**

* Utilizes APIs to communicate with ODK Central for data retrieval.
* Implements error handling mechanisms for robust import processes.

## API docs

* Documentation for APIs used in the ODK Importer module is available for reference.
* [https://docs.getodk.org/central-api-accounts-and-users/](https://docs.getodk.org/central-api-accounts-and-users/)

## Installation and deployment

Odoo installation

## User guides

[Customize the ODK Importer Configuration based on the ODK Form](https://app.gitbook.com/o/bnTr6Kp4z4CXR4QVIPSa/s/JZcdob2emEcLMvLyIxqT/\~/changes/54/pbms/features/odk-importer/user-guides/customize-the-odk-importer-configuration-based-on-the-odk-form-fields)
