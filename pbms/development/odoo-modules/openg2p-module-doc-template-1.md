---
description: The title should have the exact module name, e.g. g2p_notifications_voucher
---

# G2P Registry: Individual

### Module name

g2p\_registry\_individual

### Module title

G2P Registry: Individual

### Technology base

Odoo

### Functionality

* **Create and Manage Individual Records:**
  * Users can create detailed records for individuals participating in G2P programs.
  * Efficiently manage and update individual information through customizable forms.
* **Access Control:**
  * Implements fine-grained access control using the "security/ir.model.access.csv" file.
  * Defines specific access rules to safeguard individual records and related data.
* **Tailored User Interface:**
  * Utilizes the "views/individuals\_view.xml" file to provide custom views for displaying individual records.
  * Enhances the user interface for a more intuitive and streamlined experience.
* **Representation of Gender Information:**
  * Introduces specialized views for managing gender-related information.
  * Improves the visualization and management of gender-specific data.

### Design notes

* NA

### Relationships with other entities

**Dependencies**

* Module dependencies
  * base
  * mail
  * contacts
  * g2p\_registry\_base

### User interface

* NA

### Configuration

* Configure individual record settings based on program requirements.
* Review and adjust security settings to align with organizational policies.

### Source code

[https://github.com/OpenG2P/openg2p-registry/tree/15.0-develop/g2p\_registry\_individual](https://github.com/OpenG2P/openg2p-registry/tree/15.0-develop/g2p\_registry\_individual)

### Installation

* Ensure that the module dependencies ("base," "mail," "contacts," "g2p\_registry\_base") are installed.
* Install the "G2P Registry: Individual" module from the Odoo Apps interface.



###
