# OpenG2P Program: Documents

### Module name

g2p\_program\_documents

### Module title

OpenG2P Program: Documents

### Technology base

Odoo

### Functionality

The "OpenG2P Program: Documents" module enhances the document management capabilities within the OpenG2P system. It introduces functionalities related to associating documents with program memberships and entitlements. This module is designed to provide a streamlined approach to document handling, enabling easy access and management of supporting documents.

### Key Features

1. **Association with Program Memberships:**
   * Documents can be associated with specific program memberships.
2. **Association with Entitlements:**
   * Supports the association of documents with entitlements.
3. **Preview Functionality:**
   * The module introduces a preview feature for documents.

### Design notes

The module extends the `g2p.program.entitlement.manager.default` model for smooth document copying. No specific configuration is needed, utilizing options from the `g2p_documents` module. Dependencies on `g2p_documents` and `g2p_programs` enhance document management and integrate seamlessly with program-related functionalities.

### Relationships with other entities

* **G2P Documents Module:** Enhances document management by leveraging functionalities from `g2p_documents`.
* **G2P Programs Module:** Integrates with program-related functionalities provided by `g2p_programs`, ensuring a cohesive system for program management and document association.

### Dependencies

The module depends on the following Odoo modules:

* `g2p_documents`
* `g2p_programs`

### User interface

* **Entitlement Form View:** Supporting documents are displayed with the new section named "Supporting Documents."
* **Program Membership Form:** Includes a dedicated "Documents" page.
* **Program View:** Features a "Documents" menu.

### Configuration

No specific configuration is required for this module. Configuration options are available in the `g2p_documents` module.

### Error codes

NA

### Source code

[https://github.com/OpenG2P/openg2p-program/tree/15.0-develop/g2p\_program\_documents](https://github.com/OpenG2P/openg2p-program/tree/15.0-develop/g2p\_program\_documents)

### Installation

Standard odoo package installation
