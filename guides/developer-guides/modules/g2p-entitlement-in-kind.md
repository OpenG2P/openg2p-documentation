# G2P Entitlement In-kind

### Module name

g2p\_entitlement\_in\_kind

### Module title

OpenG2P Entitlement In-kind

### Technology base

Odoo

### Functionality

* This module is overriding the existing module spp\_entitlement\_in\_kind.
* OpenSPP supports the in-kind distribution of food and nonfood items, such as shelter materials, hygiene kits, and cooking items.
* The platform utilizes its ERP (Enterprise Resource Planning) backend to facilitate the entire distribution process, covering everything from planning to execution.
* It has the ability to handle the entire distribution process, from start to finish (from A to Z).
* It can also integrate with other ERP systems if needed, allowing for seamless data exchange and cooperation between systems.

### Design notes

* Stock management: OpenSPP is planning to include stock management features, which will likely enhance its ability to manage inventory effectively.
* Supply chain: Upcoming features may include improvements to supply chain management, which is crucial for ensuring a smooth flow of goods and materials.
* Warehouse and distribution point management: Upcoming enhancements may provide tools to better manage warehouses and distribution points, improving logistics and efficiency.
* Point of Sales (POS) integration: OpenSPP may include integration with POS systems, which can be useful for sales and transaction processing.

### Relationships with other entities

None

### Dependencies

Module Dependencies

* spp\_programs
* spp\_entitlement\_in\_kind

<figure><img src="../../../.gitbook/assets/Inkind_flowchart.drawio (4).png" alt=""><figcaption></figcaption></figure>

### User interface

**Submenu**: Program --> In-kind -->Entitlements

### Configuration

To set up In-kind Entitlement Managers, navigate to the "Programs" submenu and then access "Configuration". Within the "In-Kind Entitlement Manager", you can configure the following fields:

**Fields available inside the entitlement manager:**

1. **Name:** This field is used to specify the name of the manager.
2. **Program:** Choose a specific program from the available options.
3. **Items:** Select the product(s) that should be allocated to beneficiaries within the chosen program.

### Source code

[https://github.com/OpenG2P/openg2p-program/tree/15.0-develop/g2p\_entitlement\_in\_kind](https://github.com/OpenG2P/openg2p-program/tree/15.0-develop/g2p\_entitlement\_in\_kind)

### Installation
