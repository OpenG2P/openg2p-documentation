---
description: '! working Inprogress'
cover: https://g2pconnect.global/images/Home/g2p-connect1.png
coverY: 0
layout:
  cover:
    visible: true
    size: hero
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

* The G2P Connect module follows a modular and extensible design, making it easy to integrate with various payment systems and government-to-person (G2P) programs.&#x20;

### Relationships with other entities

&#x20;None

### Dependencies

* g2p\_registry\_base
* g2p\_programs

### User interface

**Submenu**: <mark style="background-color:orange;">Program --> Configuration -->G2P Connect Payment Managers</mark>

**G2P Connect Payment Managers**: Configuration views for setting up G2P Connect .

### Configuration

To utilize the **g2p\_payment\_g2p\_connect** module, configure the following settings within **G2P Connect Payment Manager**s (Configuration Views):

<mark style="color:yellow;">**Payment Endpoint URL:**</mark> <mark style="color:yellow;"></mark><mark style="color:yellow;">Specify the URL for payment disbursement.</mark>

<mark style="color:yellow;">**API Timeout:**</mark> <mark style="color:yellow;"></mark><mark style="color:yellow;">Set the maximum time (in seconds) for the API request to complete.</mark>

<mark style="color:yellow;">**Payer Financial Address:**</mark> <mark style="color:yellow;"></mark><mark style="color:yellow;">Enter the financial address of the payer.</mark>

<mark style="color:yellow;">**Payer Name:**</mark> <mark style="color:yellow;"></mark><mark style="color:yellow;">Provide the payer's name.</mark>

<mark style="color:yellow;">**Payee ID Field:**</mark> <mark style="color:yellow;"></mark><mark style="color:yellow;">Choose the field used as the payee's identification.</mark>

<mark style="color:yellow;">**ID Type for Payee ID:**</mark> <mark style="color:yellow;"></mark><mark style="color:yellow;">Define the type of ID used for payees.</mark>

<mark style="color:yellow;">**Payee Prefix:**</mark> <mark style="color:yellow;"></mark><mark style="color:yellow;">(Required only for All Options) Add a prefix to payee information.</mark>

<mark style="color:yellow;">**Payee Suffix:**</mark> <mark style="color:yellow;"></mark><mark style="color:yellow;">(Required only for REG\_ID) Add a suffix to payee information.</mark>

<mark style="color:yellow;">**Locale:**</mark> <mark style="color:yellow;"></mark><mark style="color:yellow;">Set the locale for language and formatting preferences.</mark>

### Error codes

&#x20;   N/A

### Source code

[https://github.com/OpenG2P/openg2p-program/tree/15.0-develop/g2p\_payment\_g2p\_connect](https://github.com/OpenG2P/openg2p-program/tree/15.0-develop/g2p\_payment\_g2p\_connect)

### Installation

Installation of the g2p\_payment\_g2p\_connect module follows standard Odoo package installation procedures.
