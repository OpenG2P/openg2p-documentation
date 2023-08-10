# Reimbursement to Service Provider

## Introduction

Many programs disburse cash and other benefits through service providers. These providers provide cash at the counter, medical assistance, and other such assistance. They need proof from the beneficiary about their entitlement amount and issuing authority.

OpenG2P facilitates generating an [entitlement voucher](../../beneficiary-management/entitlement.md#entitlement-voucher) for the beneficiary. This voucher includes a QR code to make it a tamper-proof document. The beneficiary shows the entitlement voucher to the service provider, who scans the voucher for the authenticity of the voucher, beneficiary details, entitlement amount, validity time of entitlement, and supporting documents using the SmartScanner App. To learn about the SmartScanning App, click [here](../../guides/user-guides/install-smartscanner-app.md).

## Service provider portal

OpenG2P provides a reference implementation for a [Service Provider Portal](../../guides/user-guides/submit-reimbursement-using-the-service-provider-portal.md) that can be used by the service providers to submit reimbursements for their services. The service provider can log in, search for the beneficiary, and scan and fill in beneficiary details. After serving the beneficiary, the service provider uses the portal to apply for reimbursement.

The portal allows a service provider to perform the following functions:

* View a list of beneficiary
* Fill in the details scanned from the entitlement voucher
* Upload supporting documents
* Apply for reimbursement
* Track reimbursement status

## Reimbursing Service Provider

After serving the beneficiary, the service provider will raise a reimbursement request. These requests are listed in the reimbursements view of the OpenG2P platform under reimbursements. Program administrators can view these requests, validate them, and issue the payment to the service providers. To understand the steps for reimbursements, click [here](../../guides/user-guides/reimburse-service-provider.md).

## How-To Guides

[Install SmartScanner App](../../guides/user-guides/install-smartscanner-app.md)

[Submit Reimbursement Using the Service Provider Portal](../../guides/user-guides/submit-reimbursement-using-the-service-provider-portal.md)

[Reimburse Service Provider](../../guides/user-guides/reimburse-service-provider.md)
