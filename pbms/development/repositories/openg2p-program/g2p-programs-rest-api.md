# G2P Programs: REST API

### Module name

g2p\_programs\_rest\_api

### Module title

G2P Programs: REST API

### Technology base

Odoo, Rest API

### Functionality

The "G2P Programs: REST API" module facilitates the integration of RESTful API functionalities within the G2P (Government-to-Person) Programs system. This module extends existing capabilities related to group and individual memberships, providing a seamless integration for managing program-specific information through RESTful web services.

### Design notes

The design of this module emphasizes efficient integration with REST API functionalities, allowing for the smooth exchange of information between the G2P Programs system and external applications. It builds upon the Odoo platform, incorporating Rest API technology for enhanced interoperability.

### Relationships with other entities

This module establishes crucial relationships with two primary entities:

1. **g2p\_registry\_rest\_api**
   * Leverages existing REST API functionalities related to registry management.
   * Enhances interoperability by integrating seamlessly with the registry system through RESTful web services.
2. **g2p\_programs**
   * Builds upon the core functionalities of the g2p\_programs module.
   * Extends capabilities related to group and individual memberships with program-specific information managed by g2p\_programs.

### Dependencies

The module depends on the following Odoo modules:

* `g2p_registry_rest_api`
* `g2p_programs`

### User interface

The REST API functionalities provided by this module can be accessed through the Odoo menu.

Menu -> REST API

### Configuration

No specific configuration is required for this module. The REST API functionalities are directly accessible through the designated menu.

### Error codes

* What are the error codes/exceptions thrown by this module.

### Source code

[https://github.com/OpenG2P/openg2p-notifications/tree/15.0-1.1.0/g2p\_notifications\_voucher](https://github.com/OpenG2P/openg2p-notifications/tree/15.0-1.1.0/g2p\_notifications\_voucher)

### Installation
