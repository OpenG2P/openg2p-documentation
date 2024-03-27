# OpenG2P Entitlement: Differential

### Module name

g2p\_entitlement\_differential

### Module title

OpenG2P Entitlement: Differential

### Technology base

Odoo

### Functionality

The OpenG2P Entitlement: Differential module extends the existing cash entitlement manager in OpenG2P to support differential entitlements. Differential entitlements allow for the entitlement amount to vary based on certain criteria, such as the beneficiary's location or household size. The module enables inflation adjustments for cash entitlements and applies additional filtering criteria for beneficiaries eligible for entitlements.

**Key Features:**

1. **Inflation Adjustment:** Define an inflation rate and enable inflation adjustment for entitlement amounts during program cycles.
2. **Differential Entitlements:** Calculate entitlement amounts differentially for beneficiaries based on specified criteria.
3. **Approval and Management:** Ability to approve, view, and manage differential entitlements.

### Design notes

* The module is designed to be flexible and extensible. Administrators can easily configure differential entitlement rules to meet the specific needs of their program.
* The module is also designed to be user-friendly. Entitlement managers can easily calculate, approve, and manage differential entitlements.

### Relationships with other entities

* The `g2p.program.entitlement.manager.cash` model is extended to support differential entitlements.

### Dependencies

The module depends on the following modules:

* `g2p_entitlement_cash`

### User interface

Access the module through the submenu: `Program -> Configuration -> Cash Entitlement Managers`

### Configuration

1. Configure inflation rate and other settings in the Cash Entitlement Manager form.
2. Enter an Amount for the entitlement item.
3. (Optional) Enter a Condition for the entitlement item, determining eligible beneficiaries.
4. (Optional) Select a Multiplier Field for the entitlement item to calculate the multiplier.
5. (Optional) Enter a Maximum Multiplier for the entitlement item, specifying the maximum value.
6. In the Entitlement Validation Group field, select a validation group from the dropdown list for validation.

**Note:**

* The Maximum Amount field limits the total entitlement amount.
* The Evaluate One Item checkbox evaluates only one entitlement item at a time.

### Error codes

### Source code

[https://github.com/OpenG2P/openg2p-program/tree/15.0-develop/g2p\_entitlement\_differential](https://github.com/OpenG2P/openg2p-program/tree/15.0-develop/g2p\_entitlement\_differential)

### Installation

Standard odoo package installation
