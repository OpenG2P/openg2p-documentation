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

# G2P ODK Importer

### Module name

g2p\_odk\_importer

### Module title

G2P ODK Importer

### Technology base

[Odoo](https://www.odoo.com/)

### Functionality

The **ODK Importer** module facilitates the import of records from Open Data Kit (ODK) into the OpenG2P system. It provides seamless integration with ODK Central, allowing users to import data submitted through ODK forms directly into the system.

### Features

* **Record Import**: Enables the import of records from ODK forms into the OpenG2P system.
* **Scheduled Import**: Supports scheduled imports based on configurable intervals.
* **Connection Testing**: Provides functionality to test the connection with ODK Central.
* **Import Status Monitoring**: Allows monitoring of import job status and logs.

### Design notes

* The module is designed to integrate smoothly with ODK Central for efficient data transfer.
* Emphasis is placed on robust error handling and status monitoring to ensure reliable import processes.

### Dependencies

* **Pyjq**: Python library for JSON querying.
* **Base**: Core module providing fundamental functionality.
* **Web**: Module for web interface components.
* **Queue Job**: Dependency for managing asynchronous jobs.

### User interface

Menu added

* **Submenu**: ODK -> Configuration.&#x20;

### Configuration

The module requires configuration of the following parameters:

* **Base URL**: The base URL of the ODK Central instance.
* **Username/Password**: Credentials for authentication with ODK Central.
* **Project ID**: The ID of the ODK project from which data will be imported.
* **Form ID**: The ID of the ODK form containing the data to be imported.
* **JSON Formatter**: Optional JSON formatter for customizing data mapping.
* **Target Registry**: Specifies whether imported records will be associated with individual or group registries.
* **Interval in Hours**: Configurable interval for scheduled imports.

### Usage

1. Configure the ODK connection settings in the **ODK Configuration** menu.
2. Test the connection to ODK Central to ensure successful authentication.
3. Schedule imports or manually trigger imports using the provided actions.
4. Monitor import job status and logs for any errors or warnings.

### **Handling JSON formatter using Pyjq**

#### **Explanation**

* Each key in the JSON formatter script corresponds to a database column name.
* Pyjq expressions are utilized to query and manipulate JSON data extracted from ODK forms.
* ODK form field keys are mapped to database column names, ensuring accurate data mapping.
* Optional fields are denoted with a question mark (?), indicating potential null or undefined values.

#### **Usage guidelines**

**Understanding database schema**

* Familiarize yourself with the database schema of the OpenG2P system to identify appropriate database column names.

**Mapping ODK form fields**

* Map each ODK form field to the corresponding database column by specifying key-value pairs in the JSON formatter script.

**Usage**

* Technical users can configure the JSON formatter script by defining mappings between Excel sheet columns and ODK form fields using Pyjq expressions.

**Example JSON formatter script**

```json
{
    "name": .vc_details.full_name,
    "gender": .vc_details.gender,
    "age": .vc_details.age,
    "address": .vc_details.address,
    "email": .personal_details.email
}
```

**Explanation**

* `"name": .vc_details.full_name`: Extracts the full name of the individual from the "vc\_details" section of the ODK form.
* `"gender": .vc_details.gender`: Extracts the gender of the individual from the same section.
* `"age": .vc_details.age`: Extracts the age of the individual from the same section.
* `"address": .vc_details.address`: Extracts the address of the individual from the same section.
* "email": .personal\_details.email: Extracts the email address of the individual from the "personal\_details" section.

**Accessing nested fields**

When navigating through nested structures, the dot (.) allows traversal from one level to another. For example:

* `.vc_details.full_name`: Accesses the full\_name field within the vc\_details section of the JSON data.
* `.vc_details.address.city`: Accesses the city field within the address subfield of the vc\_details section.

### Error codes

NA

### Source code

[https://github.com/OpenG2P/openg2p-importers/tree/17.0-develop/g2p\_odk\_importer](https://github.com/OpenG2P/openg2p-importers/tree/17.0-develop/g2p\_odk\_importer)

### Installation

Standard Odoo package installation
