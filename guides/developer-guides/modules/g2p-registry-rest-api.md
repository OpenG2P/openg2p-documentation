# G2P Registry: Rest API

### Module name

g2p\_registry\_rest\_api

### Module title

G2P Registry: Rest API

### Technology base

[Odoo](https://www.odoo.com/es\_ES), RestAPI

### Functionality

The `g2p_registry_rest_api` module is a crucial component of the G2P Registry system, offering robust functionality through a Restful API. This module empowers users to interact with the system by providing endpoints for creating and retrieving records efficiently. With the help of this API, users can seamlessly create new records and retrieve existing ones, streamlining data management processes within the G2P Registry. The REST API design ensures accessibility and ease of integration, allowing developers and applications to interact with the registry seamlessly. However, it's important to note that the module does not support file uploads, a limitation worth considering when utilising the API for data operations.

### Design notes

* What are salient design features?
* Why were certain design decisions taken in a particular way?
* Design patterns used.
* Algorithms used.
* Anything a developer should know about the design of this module.
* Any scope for improvement and further design work that is pending.



### Relationships with other entities

None

### Dependencies

Module Dependencies

* component
* base\_rest
* pydantic
* base\_rest\_pydantic
* extendable
* g2p\_registry\_individual
* g2p\_registry\_group
* base\_rest\_auth\_user\_service

External dependencies

* pydantic==1.10.10
* extendable-pydantic

### User interface

Menu Added

* REST API



### Configuration

NA

### Error codes



| Error Code    | Error Message           |
| ------------- | ----------------------- |
| G2P\_REQ\_001 | Invalid kind field      |
| G2P\_REQ\_002 | Field is mandatory      |
| G2P\_REQ\_003 | Group type not Found    |
| G2P\_REQ\_004 | Member's kind not found |
| G2P\_REQ\_005 | Invalid ID field        |
| G2P\_REQ\_006 | Invalid phone number    |
| G2P\_REQ\_007 | Invalid email address   |
| G2P\_REQ\_008 | Invalid gender          |
| G2P\_REQ\_009 | Invalid account number  |

### Source code

[https://github.com/OpenG2P/openg2p-registry/tree/15.0-develop/g2p\_registry\_rest\_api](https://github.com/OpenG2P/openg2p-registry/tree/15.0-develop/g2p\_registry\_rest\_api)

### Installation

###
