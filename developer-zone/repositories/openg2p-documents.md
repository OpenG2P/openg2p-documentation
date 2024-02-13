# openg2p-documents

### Module name

g2p\_documents

### Module title

G2P Documents Store

### Technology base

[Odoo](https://www.odoo.com/)

### Functionality

1. The G2P Documents Store is a module developed by OpenG2P for managing and storing documents in the G2P system. This module provides functionalities for handling document storage, categorization, and tagging within the G2P application. It is designed to enhance document management capabilities and improve user experience.
2.  #### Document Storage -

    The G2P Documents Store allows users to store various types of documents within the G2P application. It provides a structured and organized approach to managing documents.

### Dependencies

The G2P Documents Store module depends on the following modules:

* `storage_backend_s3`
* `storage_file`

#### External Python Dependencies

The module relies on the following external Python libraries:

* `boto3` (version <=1.15.18)
* `python_slugify`

### User interface

NA

### Configuration

Carefully structure the storage backend configuration (`data/storage_backend.xml`) to seamlessly integrate with the specified backends and to handle various document types.

### Error codes

NA

### Source cod

[https://github.com/openg2p/openg2p-documents](https://github.com/openg2p/openg2p-documents)

### Installation

Standard Odoo package installation
