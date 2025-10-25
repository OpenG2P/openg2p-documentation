# OpenG2P Program Payment (Payment Hub EE)

### Module name

g2p\_payment\_phee

### Module title

OpenG2P Program Payment (Payment Hub EE)

### Technology base

Odoo

### Functionality

This module extends the capabilities of the G2P Program Payment Manager to integrate with Payment Hub EE. It provides functionalities related to preparing and sending payments through Payment Hub EE.

### Design notes

The module design emphasizes efficient integration with Payment Hub EE, enabling seamless payment processing within the G2P Programs system

### Relationships with other entities

* **G2P Program Payment Manager:** Extends the capabilities of the existing G2P Program Payment Manager to seamlessly integrate with Payment Hub EE, enhancing payment processing functionalities.
* **Payment Hub EE:** Establishes a connection and interaction with Payment Hub EE, enabling the module to prepare and send payments through this specific payment hub.

### Dependencies

* **`base`:** Fundamental module providing essential functionalities for Odoo.
* **`g2p_registry_base`:** Core module for the G2P Registry
* **`g2p_programs`:** Essential module for G2P Programs, laying the groundwork for program-specific features and functionalities.

### User interface

The module introduces additional configuration views accessible through the Odoo interface:

* **Menu:** `Settings -> Payment Hub EE Configuration`

### Configuration

The configuration options are available in the settings view&#x20;

(`Settings -> Payment Hub EE Configuration`). \
\
Key configuration parameters include authentication and endpoint URLs required for interaction with **Payment Hub EE**.

### Error codes

NA

### Source code

[https://github.com/OpenG2P/openg2p-program/tree/15.0-develop/g2p\_payment\_phee](https://github.com/OpenG2P/openg2p-program/tree/15.0-develop/g2p\_payment\_phee)

### Installation

Standard odoo package installation
