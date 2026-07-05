# G2P Registry: Bank Details

### Module name

g2p\_bank

### Module title

G2P Registry: Bank Details

### Technology base

\<Odoo>

### Functionality

* **Secure Storage**
  * Provides a structured framework for storing and managing bank details.
  * Ensures the confidentiality and security of financial information.
* **Comprehensive Integration**
  * Integrates seamlessly with the "g2p\_registry\_individual" and "g2p\_registry\_group" modules.
  * Allows users to associate bank details with specific individuals and groups.
* **Python Library Integration**
  * Utilizes the "schwifty" Python library for enhanced functionality.
  * Enables the validation and processing of bank-related information.

### Design notes

NA

### Relationships with other entities

**Dependencies**

Module dependencies

* base
* mail
* contacts
* g2p\_registry\_group
* g2p\_registry\_individual

External Python Dependency

* schwifty

### User interface

NA

### Configuration

* No specific configuration steps are required. The module seamlessly integrates with individuals and groups.

### Source code

[https://github.com/OpenG2P/openg2p-registry/tree/15.0-develop/g2p\_registry\_membership](https://github.com/OpenG2P/openg2p-registry/tree/15.0-develop/g2p\_registry\_membership)

### Installation

* Ensure that all module dependencies are installed, including the external Python library "schwifty."
* Install the "G2P Registry: Bank Details" module from the Odoo Apps interface.
