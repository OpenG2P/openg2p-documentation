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

# 📔 Import CSV File to Registry Module

This document provides instructions to import .csv File to Registry Module.

## Prerequisites

* The user must have access to the Registry module in OpenG2P systems.

## Procedure

1. Click the main menu icon ![](../../../../../.gitbook/assets/main-menu.png) and select _**Registry**_.

<figure><img src="../../../../../.gitbook/assets/main-menu-registry.png" alt=""><figcaption></figcaption></figure>

_**Registry**_ screen is displayed.

<figure><img src="../../../../../.gitbook/assets/registry-import-records.png" alt=""><figcaption></figcaption></figure>

2. In the menu bar, click the _**Individual**_ tab.

_**Individual**_ screen is displayed.

3. Click the _**Action**_ icon and then select _**Import records**_.

_**Individuals Import a File**_ screen is displayed.

<figure><img src="../../../../../.gitbook/assets/import-file-screen.png" alt=""><figcaption></figcaption></figure>

4. Click the _**Upload File**_ button.
5. Browse for the file location and upload the file.

Below the File Column, the name of the fields are populated from the .csv file. You need to map the field names from CSV file with the associated Odoo Field name.

For example, the mapping of the few fields are given below. &#x20;

| Field name in .csv file | Mapped to Odoo Field Name |
| ----------------------- | ------------------------- |
| language                | Language                  |
| id\_type                | Registrant IDs / ID Type  |
| id\_number              | Registrant IDs / Value    |
| given\_name             | Given Name                |

Similarly, you must map the rest of the fields.

6. Click the _**Test**_ button to validate the mapping.&#x20;

A pop up message _**Everything seems valid**_ implies that the mapping of the field is successfully validated.&#x20;

7. Click the _**Load File**_ button to upload another csv file for validation
8. Click the _**Cancel**_ button to exit from the screen.
9. Click the _**Import**_ button to import the csv file after successful validation.

The files are imported to the individual registry dashboard.

<figure><img src="../../../../../.gitbook/assets/individual-dashboard.png" alt=""><figcaption></figcaption></figure>

This completes the process of importing .csv file into the individual registry.
