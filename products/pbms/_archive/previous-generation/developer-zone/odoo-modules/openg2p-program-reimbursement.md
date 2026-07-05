# OpenG2P Programs: Reimbursement

### Module name

g2p\_program\_reimbursement

### Module title

OpenG2P Programs: Reimbursement

### Technology base

Odoo

### Functionality

The main functionality of this module is to redeem the voucher generate by any program.

#### 1. Reimbursement Program Management

* **Program View:** The module introduces a new program view (`program_view.xml`) that incorporates features specific to reimbursement programs.
* **Cycle View:** A customized cycle view (`cycle_view.xml`) tailored for reimbursement cycles is provided, allowing detailed management of each cycle.

#### 2. Entitlement Management

* **Entitlement View:** The module enhances the entitlement view (`entitlement_view.xml`) to accommodate reimbursement-specific information.
* **Service Provider View:** A dedicated view (`serviceprovider_view.xml`) enables efficient management of service providers associated with reimbursement programs.

#### 3. Wizards

* **Assign to Program Wizard:** The module includes an assignment wizard (`assign_to_program_wizard.xml`) to streamline the process of assigning beneficiaries to reimbursement programs.
* **Create Program Wizard:** A creation wizard (`create_program_wizard.xml`) facilitates the easy setup of new reimbursement programs.
* **Create Entitlement Wizard:** An entitlement creation wizard (`create_entitlement_wizard.xml`) simplifies the process of generating new entitlements within reimbursement cycles.

### Relationships with other entities

None

### Dependencies

Module Dependencies

* g2p\_programs
* g2p\_program\_assessment

### User interface

**Submenu** : Program --> reimbursement program

### Configuration

Create a reimbursement program and map it with any program.

### Source code

[https://github.com/OpenG2P/openg2p-program/tree/15.0-develop/g2p\_program\_reimbursement](https://github.com/OpenG2P/openg2p-program/tree/15.0-develop/g2p\_program\_reimbursement)

### Installation
