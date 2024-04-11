# G2P Program Payment Manager: Payment Interoperability Layer

### Module name

g2p\_payment\_interop\_layer

### Module title

G2P Program Payment Manager: Payment Interoperability Layer

### Technology base

[Odoo](https://www.odoo.com/)

### Functionality

This module extends the core G2P Payment Manager functionality to integrate with an external payment interoperability layer.&#x20;

* Sends payment information for designated payment batches to the interoperability layer API.
* Supports automatic batch creation based on program cycles and configurations.
* Maps beneficiary information (payee IDs) to the interoperability layer format using configurable rules.
* Handles successful disbursements, updating payment statuses and reconciling records.
* Provides information on completed payment processes through notifications.

### Design notes

* Built upon the existing `g2p.program.payment.manager` class, inheriting its core functionalities.
* Utilizes the Odoo inheritance pattern for modularity and maintainability.
* Relies on configurable settings for payee ID mapping and automatic batch creation.
* Integrates with the external interoperability layer through its configured API endpoint URL.

### Relationships with other entities

* **Internal Interactions:** Collaborates with the `g2p.program.payment.manager` class for overall payment coordination and batch management.
* **External Integration:** Connects to the external payment interoperability layer API for secure and efficient disbursement execution.

### Dependencies

Relies on the `base`, `g2p_registry_base`, and `g2p_programs` modules for core functionalities and data models.

### User interface

Menu Added

* **Submenu**: Program -> Configuration -> Payment Interoperability Layer Payment Managers
* **Payment Interoperability Layer**: Configuration views for setting up API URL

### Configuration

To configure the Payment Interoperability Layer module with the specified settings, please follow the given instructions:

1. **Payment Endpoint URL:**
   * Open the Payment Interoperability Layer module configuration.
   * Locate the "Payment Endpoint URL" field.
   * Update the field with the desired Payment Endpoint URL.
2. **Payee ID Field:**
   * Within the Payment Interoperability Layer module configuration, find the "Payee ID Field."
   * Modify the configuration to set the Payee ID field as required.

### Error codes

NA

### Source code

[https://github.com/OpenG2P/openg2p-program/tree/15.0-develop/g2p\_payment\_interop\_layer](https://github.com/OpenG2P/openg2p-program/tree/15.0-develop/g2p\_payment\_interop\_layer)

### Installation

Standard odoo package installation

###
