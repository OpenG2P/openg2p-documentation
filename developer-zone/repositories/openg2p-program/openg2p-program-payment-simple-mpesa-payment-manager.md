# OpenG2P Program Payment Simple Mpesa Payment Manager

### Module name

g2p\_payment\_simple\_mpesa

### Module title

OpenG2P Program Payment: Simple Mpesa Payment Manager

### Technology base

Odoo

### Functionality

* This Module specifically designed to integrate with Simple Mpesa payment services.
* It enables users to create and manage payment batches for disbursements via Mpesa.
* **Authentication:** Acquires an access token from Simple Mpesa using provided credentials.
* **Payment Processing:** Iterates through payments within batches:
  * Constructs payment data for Simple Mpesa API calls.
  * Uses the access token for authentication.
  * Sends payment requests to the payment endpoint.
  * Handles responses, updating payment statuses accordingly.
  * Logs errors and sends notifications in case of failures.

### Dependencies

* base
* g2p\_registry\_base
* g2p\_programs

### &#x20;Design notes

*

### User interface

**menu** -> configuration -> Simple Mpesa Payment Managers

program -> configuration -> payment manager -> Simple Mpesa Payment Manager

### Configuration

* **`auth_endpoint_url`:** The URL for Simple Mpesa 's authentication endpoint.
* **`payment_endpoint_url`:** The URL for Simple Mpesa 's payment execution endpoint.
* **`api_timeout`:** The timeout duration (in seconds) for API calls.
* **`username`:** The Simple Mpesa account username.
* **`password`:** The Simple Mpesa account password.
* **`payee_id_type`:** Specifies the type of ID used for payee identification (bank account, phone, email, or registrant ID).
* **`customer_type`:** The customer type to be used in payment requests (defaults to "subscriber").

### Source code

[https://github.com/OpenG2P/openg2p-program/tree/15.0-develop/g2p\_payment\_simple\_mpesa](https://github.com/OpenG2P/openg2p-program/tree/15.0-develop/g2p\_payment\_simple\_mpesa)

### Installation

Standard odoo package installation
