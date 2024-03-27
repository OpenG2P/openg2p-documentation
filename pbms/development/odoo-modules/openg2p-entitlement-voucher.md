# OpenG2P Entitlement Voucher

### Module name

g2p\_entitlement\_voucher

### Module title

OpenG2P Entitlement Voucher

### Technology base

Odoo

### Functionality

* The "OpenG2P Entitlement: Voucher" module is part of the OpenG2P project and extends the functionality related to entitlements within the G2P (Government-to-Person) category. This module focuses specifically on managing entitlements related to vouchers.
* Integration with "g2p\_programs" and "g2p\_payment\_files" modules.
* Enhanced management of entitlements with a focus on voucher-related processes.

### Design notes

*

### Relationships with other entities

None

### Dependencies

Module Dependencies

* g2p\_programs
* g2p\_payment\_files

### User interface

**Submenu**: Program --> configuration -->Entitlement Manager

### Configuration

#### Entitlement Manager Configuration

To utilize voucher functionality, configure the entitlement manager under the program configuration:

1. Navigate to the "Configuration" section of the desired G2P program.
2. Select an appropriate voucher option within the entitlement manager settings.

#### Voucher Generation

Once the entitlement is prepared and approved, the following options become available:

* **Generate Voucher Button:**
  * Configuration-Dependent: The availability of this button depends on the auto-generation setting in the entitlement manager configuration.
  * Auto-Generation: If configured to auto-generate vouchers, the voucher is automatically generated upon approval.
  * Manual Generation: If configured for manual generation, click this button to initiate voucher creation.
* **Print Voucher Button:**
  * Appears after the voucher is generated.
  * Click to print the voucher document.

### Source code

[https://github.com/OpenG2P/openg2p-program/tree/15.0-develop/g2p\_entitlement\_voucher](https://github.com/OpenG2P/openg2p-program/tree/15.0-develop/g2p\_entitlement\_voucher)

### Installation

1. Ensure that the dependencies are installed (g2p\_document) and configured in your Odoo instance.
2. Install the "OpenG2P Entitlement: Voucher" module through the Odoo Apps interface.
