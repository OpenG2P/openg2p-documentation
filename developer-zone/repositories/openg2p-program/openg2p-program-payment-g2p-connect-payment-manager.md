---
description: '! working Inprogress'
layout:
  title:
    visible: true
  description:
    visible: true
  tableOfContents:
    visible: true
  outline:
    visible: true
  pagination:
    visible: true
---

# OpenG2P Program Payment: G2P Connect Payment Manager

### Module name

g2p\_payment\_g2p\_connect

### Module title

OpenG2P Program Payment: G2P Connect Payment Manager

### Technology base

Odoo and G2P Connect API (RESTful API)

### Functionality

The "`g2p_payment_g2p_connect`" module is an integral component of Odoo 15, integrated to streamline payment processes within the G2P Connect API.. It simplifies payment processing for each cycle.

* **Integration with G2P Connect API:** This module seamlessly integrates with the G2P Connect API, allowing for secure and efficient payment transactions.
* **Cycle-Based Payments:** Users can make payments for each cycle, ensuring timely and accurate disbursements.

### Design notes

* The G2P Connect module follows a modular and extensible design, making it easy to integrate with various payment systems and government-to-person (G2P) programs.

### Relationships with other entities

None

### Dependencies

* g2p\_registry\_base
* g2p\_programs

### User interface

**Submenu**: Program --> Configuration -->G2P Connect Payment Managers

**G2P Connect Payment Managers**: Configuration views for setting up G2P Connect .

### Configuration

To utilize the **g2p\_payment\_g2p\_connect** module, configure the following settings within **G2P Connect Payment Manager**s (Configuration Views):

**Payment Endpoint URL:** Specify the URL for payment disbursement.

**API Timeout:** Set the maximum time (in seconds) for the API request to complete.

**Payer Financial Address:** Enter the financial address of the payer.

**Payer Name:** Provide the payer's name.

**Payee ID Field:** Choose the field used as the payee's identification.

**ID Type for Payee ID:** Define the type of ID used for payees.

**Payee Prefix:** (Required only for All Options) Add a prefix to payee information.

**Payee Suffix:** (Required only for REG\_ID) Add a suffix to payee information.

**Locale:** Set the locale for language and formatting preferences.

### Error codes

N/A

### Source code

[https://github.com/OpenG2P/openg2p-program/tree/15.0-develop/g2p\_payment\_g2p\_connect](https://github.com/OpenG2P/openg2p-program/tree/15.0-develop/g2p\_payment\_g2p\_connect)

### Installation

Installation of the g2p\_payment\_g2p\_connect module follows standard Odoo package installation procedures.
