# OpenG2P Program Payments: In Files

Module name

g2p\_payment\_files

### Module title

OpenG2P Program Payments: In Files

### Technology base

[Odoo](https://www.odoo.com/)

### Functionality

1. **Payment File Configuration**:
   * Configuration for payment files, possibly specifying file formats, fields, etc.
2. **Batch Tagging**:
   * Allows tagging batches of payments for easy identification and processing.
3. **Payment Management**:
   * A central view for managing payments, batches, and configurations.
4. **FastAPI Endpoint**:
   * This module integrates with FastAPI to expose endpoints for programmatic interaction. One notable endpoint is the `/jwks.json` API, which dynamically generates a pair of JSON Web Keys (JWKs) – a public key and a private key – when vouchers are created.

### Design notes

1. **Security Model**:
   * The `ir.model.access.csv` file suggests access control considerations. Ensure proper permissions are set for the views and functionalities exposed.
2. **API Integration**:
   * Leverage FastAPI for creating robust APIs. The `data/fastapi_endpoint.xml` file suggests the presence of API endpoints. Define API routes and handlers in accordance with your module's requirements.
3. **Payment File Handling**:
   * Design how payment files are processed. Consider supporting multiple file formats, validation checks, and error handling.

### Relationships with other entities

* **Internal Interactions:** Collaborates with the `g2p.program.payment.manager` class for overall payment coordination and batch management.
* **External Integration:** Connects to the external payment interoperability layer API for secure and efficient disbursement execution.

### Dependencies

1. **Internal Dependencies**:
   * Ensure that the listed dependencies (`g2p_programs`, `g2p_program_documents`, `fastapi`, `mail`) are properly installed and configured in your OpenG2P environment.
2. **External Dependencies**:
   * Install the specified Python libraries (`base45`, `cryptography`, `cose`, `python-jose`, `python-barcode`, `pdfkit`, `qrcode`, `wkhtmltopdf`). Use a virtual environment to manage dependencies.

### User interface

NA

### Configuration



### Error codes

NA

### Source cod

[https://github.com/OpenG2P/openg2p-program/tree/15.0-develop/g2p\_payment\_files](https://github.com/OpenG2P/openg2p-program/tree/15.0-develop/g2p\_payment\_files)

### Installation

Standard odoo package installation
