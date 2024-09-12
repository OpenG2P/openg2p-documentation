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

# 📔 Import Specific ODK Forms using Instance ID



This document provides instructions for importing specific applicants/registrants' ODK forms hosted in ODK Central. It uses the unique [**Instance ID**](import-specific-odk-forms-using-instance-id.md#instance-id) of the ODK forms to import them into the PBMS modules' relevant individual/group registries.

## Prerequisites

* A user must have an Administrator role to access ODK Central in OpenG2P systems.

## Procedure

1. Click the main icon ![](../../../../.gitbook/assets/menu-icon.png) and select _**Settings**_.

<figure><img src="../../../../.gitbook/assets/pbms-settings (1).png" alt=""><figcaption></figcaption></figure>

_**Settings**_ screen is displayed.&#x20;

<figure><img src="../../../../.gitbook/assets/pbms-settings-screen.png" alt=""><figcaption></figcaption></figure>

2. Select the _**General Settings**_ tab.
3. Select the  _**ODK Import Settings**_ from the menu.
4. Check the _**Enable ODK Import InstanceID**_ box.

### Occurrence of Instance ID field

4. Use the main menu icon ![](../../../../.gitbook/assets/menu-icon.png) to navigate to ODK -> ODK Import.&#x20;
5. Select the ODK Import from the current list.
6. Find an additional field labeled _**InstanceID**_ that appears at the bottom of the displayed screen.

<figure><img src="../../../../.gitbook/assets/odkimport-fetchrecord.png" alt=""><figcaption></figcaption></figure>

7. Enter the _**Instance ID**_.
8. Fill in the remaining fields following the [import record configuration](../../../features/odk-importer/user-guides/customize-the-odk-importer-configuration-based-on-the-odk-form-fields.md) procedure.
9. Click the _**Fetch Record**_ to import the specific applicants/registrants' ODK form relevant to the entered Instance ID.

{% hint style="danger" %}
The PBMS module may be able to import duplicate applicant/registrants' ODK forms if the same Instance ID is used more than once.
{% endhint %}

## Instance ID

1. Log into the _**ODK central**_ with the valid credentials.
2. Select a form below the _**Projects**_ section.

For example, here Group sample form is selected.

<figure><img src="../../../../.gitbook/assets/odk-central-form.png" alt=""><figcaption></figcaption></figure>

3. Select the Group Sample form in the _**Group Sample form**_ screen.

<figure><img src="../../../../.gitbook/assets/odkform.png" alt=""><figcaption></figcaption></figure>

4. Click the _**Submission**_ tab.

<figure><img src="../../../../.gitbook/assets/odkform-submissiontab.png" alt=""><figcaption></figcaption></figure>

5. Find the Instance ID in the current list of submitted ODK forms.

<figure><img src="../../../../.gitbook/assets/odkform-instanceid.png" alt=""><figcaption></figcaption></figure>
