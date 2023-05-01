# Voucher

## Introduction

A voucher is a digitally signed document (say, with a QR code) or letter of guarantee against which a beneficiary can avail a service without having to pay for it, or is entitled to withdraw cash.

Vouchers may be issued in several forms:

1. Paper-based letter and QR code
2. Verifiable Credential (VC) on a smartphone

## Voucher code

A **voucher code** is a random code associated with a voucher that the beneficiary needs to share with the service provider. The voucher code is required to claim the reimbursement. The idea is to reduce the chances of fraud arising by a service provider claiming reimbursement without any connection with the beneficiary.

## Design

* Entitlement Id == Voucher Id
* &#x20;voucher code = random string. The string should not be too long as it will be manually entered into the Claims portal.

## Sample

A voucher sample with a QR code is shown below:

{% file src="../.gitbook/assets/OpenG2P Generated Voucher Sample (1).pdf" %}
