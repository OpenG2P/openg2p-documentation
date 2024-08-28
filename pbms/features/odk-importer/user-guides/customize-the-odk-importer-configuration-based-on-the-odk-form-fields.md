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

# 📔 Customise the ODK Importer Configuration based on the ODK Form Fields

## Description

This document provides step-by-step instructions to customise the ODK Importer configuration based on the ODK form fields to cater to the needs of the stakeholders.

Note:

Every ODK form must have its own ODK importer.

## Prerequisites

* A user must have Administrator role to access ODK Central in OpenG2P systems.
* A user must know the pyjq syntax to customise the value in the JSON Formatter fields.

## Procedure

1. Login to _**OpenG2P**_ systems.

<figure><img src="../../../../.gitbook/assets/openg2p-application.png" alt=""><figcaption><p>OpenG2P application</p></figcaption></figure>

2. In the menu bar, click the icon ![](../../../../.gitbook/assets/menu-icon.png) and select ODK.

<figure><img src="../../../../.gitbook/assets/menu-odk-importer.png" alt=""><figcaption><p>ODK</p></figcaption></figure>

_**ODK configuration**_ screen is displayed.

<figure><img src="../../../../.gitbook/assets/ODK-configuration.png" alt=""><figcaption><p>ODK Configuration</p></figcaption></figure>

3. Click the **Create** button.

_**ODK Configuration/New**_ screen is displayed.

<figure><img src="../../../../.gitbook/assets/ODK-configuration-ODKnew.png" alt=""><figcaption><p>ODK Configuration/New</p></figcaption></figure>

4. Enter the valid values to access ODK Central in OpenG2P systems and customize the ODK Importer configuration based on the ODK Form Fields

| Field                                                                                                           | Description                                                                                                          |
| --------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| Start                                                                                                           | Click the _**Start**_ link to execute the schedule job to run periodically at fixed times, dates, or intervals.      |
| Restart                                                                                                         | Click the _**Restart**_ link to re-execute the schedule job to run periodically at fixed times, dates, or intervals. |
| Stop                                                                                                            | Click the **Stop** link to stop the execution of the  schedule job.                                                  |
| _**ODK Central**_                                                                                               |                                                                                                                      |
| Name                                                                                                            | Enter the name for the ODK importer.                                                                                 |
| Base URL                                                                                                        | Enter the URL of the ODK Central.                                                                                    |
| Username                                                                                                        | Enter the username which is used to login ODK Central                                                                |
| Password                                                                                                        | Enter the password which is used to login ODK Central                                                                |
| _**Project details**_                                                                                           |                                                                                                                      |
| \*[Project](customize-the-odk-importer-configuration-based-on-the-odk-form-fields.md#project)                   | <p>Enter the project number. </p><p>For example, 5</p>                                                               |
| \*\*[Form ID](customize-the-odk-importer-configuration-based-on-the-odk-form-fields.md#form-id)                 | <p>Enter the ID of the form.</p><p>For example, Household_data_collection </p>                                       |
| _**Target settings**_                                                                                           |                                                                                                                      |
| Target Registry                                                                                                 | <p>Select the appropriate option. The valid values are:</p><ul><li>Group</li><li>Individual</li></ul>                |
| \*\*\*[JSON Formatter](customize-the-odk-importer-configuration-based-on-the-odk-form-fields.md#json-formatter) | Use the pyjq library to manipulate JSON, based on the required fields in OpenG2P system.                             |
| _**Time interval**_                                                                                             |                                                                                                                      |
| Interval in hours                                                                                               | Enter the time duration in hours to run the job automatically.                                                       |
| _**Program details**_                                                                                           |                                                                                                                      |
| ODK Program ID                                                                                                  | Enter the program ID                                                                                                 |
| Save                                                                                                            | Click the _**Save**_ button to save the data                                                                         |
| Discard                                                                                                         | Click the _**Discard**_ to clear the data                                                                            |

### Test Connection

_**Test Connection**_ feature establishes the connection between _**ODK Central**_ and _**OpenG2P**_ systems.

5. Click the _**Test Connection**_ button.

If the _**Test Connection**_ feature connects the _**ODK Central**_ and _**OpenG2P**_ systems successfully, a successful message pop ups.

<figure><img src="../../../../.gitbook/assets/test-connection-successful.png" alt=""><figcaption><p>Test Connection - Successful</p></figcaption></figure>

If the _**Test Connection**_ feature unable to connect the _**ODK Central**_ and _**OpenG2P**_ systems, an error  message pop ups.&#x20;

6. Click the _**OK**_ button to exit the dialog box.

<figure><img src="../../../../.gitbook/assets/test-connection-failure.png" alt=""><figcaption><p>Test Connection - Failure</p></figcaption></figure>

### Import Records

_**Import Records**_ feature imports and stores the records in Social Registry.

7. Click the _**Import Records**_ button.

If the ODK form is imported successfully, a success message pops up.

<figure><img src="../../../../.gitbook/assets/import-success.png" alt=""><figcaption><p>Import Record - Successful</p></figcaption></figure>

If there is no new ODK form submitted, then ODK form records will not be imported.

<figure><img src="../../../../.gitbook/assets/import-record.png" alt=""><figcaption><p>Import Record - No new record found.</p></figcaption></figure>

A view of the ODK form recorded in Social Registry.

<figure><img src="../../../../.gitbook/assets/ODK-form-recorded.png" alt=""><figcaption><p>ODK Form recorded</p></figcaption></figure>

The below image shows the specific ODK form record.

<figure><img src="../../../../.gitbook/assets/ODK-form-specific-record.png" alt=""><figcaption><p>Specific ODK Form</p></figcaption></figure>

The Household Data tab shows only the fields which are configured using pyjq JSON formatter in ODK importer. The fields are populated while the ODK form is imported to the Social Registry.

<figure><img src="../../../../.gitbook/assets/populated-field.png" alt=""><figcaption><p>Populated fields</p></figcaption></figure>

<figure><img src="../../../../.gitbook/assets/populated-field (2).png" alt=""><figcaption><p>Populated fields</p></figcaption></figure>

You can find the created ODK form below the name column in _**ODK Configuration**_ screen.

<figure><img src="../../../../.gitbook/assets/ODK-configuration.png" alt=""><figcaption></figcaption></figure>

This completes process of importing a ODK form into Social registry by customizing the ODK Importer configuration based on the ODK Form Fields.

***

### Project

Follow the below steps to know the project ID taken from ODK Central.

1. Login to _**ODK Central**_.

_**ODK Central**_ home page is displayed.

<figure><img src="../../../../.gitbook/assets/ODK-central-home-page.png" alt=""><figcaption><p>ODK Central</p></figcaption></figure>

Here, for example, click the Household data collection form below the program Test.

The Household data collection form's  overview screen is displayed.

<figure><img src="../../../../.gitbook/assets/ODK-central-home-form-overview.png" alt=""><figcaption><p>ODK Central - Project number</p></figcaption></figure>

In the URL , the number which is after the project is the project Id (5) (highlighted in yellow).

### Form ID

Follow the below steps to know the form ID taken from ODK Central.

1. Login to _**ODK Central**_.

_**ODK Central**_ home page is displayed.

<figure><img src="../../../../.gitbook/assets/ODK-central-home-page.png" alt=""><figcaption><p>ODK Central</p></figcaption></figure>

Here, for example, click the Household data collection form below the program Test.

The Household data collection form's overview form is displayed.

<figure><img src="../../../../.gitbook/assets/ODK-central-home-form-overview-form.png" alt=""><figcaption><p>ODK Central - Form ID</p></figcaption></figure>

In the URL , the word which is after the forms is the form Id (Household\_data\_collection) (highlighted in yellow).

### JSON Formatter

Configure the required fields based on the ODK form field using pyjq JSON formatter.&#x20;

For example, ODK importer configures the required fields from Household data collection form present in ODK central in JSON Formatter box.

<figure><img src="../../../../.gitbook/assets/JSON-formatter-1.png" alt=""><figcaption><p>JSON Formatter</p></figcaption></figure>
