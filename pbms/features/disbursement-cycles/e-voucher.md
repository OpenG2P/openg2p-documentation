---
description: Digital vouchers for goods and services
---

# e-Voucher

A voucher is a method used to distribute benefits to individuals in a non-cash form. An e-voucher, or electronic voucher, serves as a digital replacement for traditional paper vouchers. In Open G2P, e-vouchers are utilized to distribute benefits to individuals through a third party.

Initially, a voucher entitlement is generated for the individual or group. This voucher is then scanned using an ID verification app by the service provider. After scanning the voucher, the service provider provides the benefits to the individual. The service provider is later reimbursed according to the services granted. It also streamlines the process of benefit distribution, making it more efficient and secure.

### Functions

* **Configure e-Voucher Manager:** This feature allows administrators to set up and configure the e-voucher management system according to the program's requirements.
* **Generate Voucher Entitlement:** Enables the generation of e-voucher entitlements for individuals or groups eligible for benefits.
* **Distribute e-Vouchers:** Facilitates the distribution of e-Vouchers to beneficiaries, ensuring they receive their entitlements promptly.
* **Scan e-Voucher:** The service provider uses an ID verification app to scan the e-voucher, confirming the entitlement and enabling the provision of benefits.
* **Provide Benefits:** After scanning the e-voucher, the service provider provides the benefits to the individual, ensuring they receive the intended support.
* **Reimbursement:** The service provider is later reimbursed for the benefits provided, based on the services granted and in compliance with program guidelines.

## Voucher verification app

The Smart Scanner app is a useful tool for scanning QR codes and managing voucher codes on your Android mobile device. This app is particularly useful for individuals or groups that need to process vouchers to avail themselves of the benefits.

### **Key features**

* **QR Code Scanning:** Smart Scanner allows users to scan QR codes quickly and accurately using their device's camera. This feature is essential for accessing information or redeeming vouchers linked to QR codes.
* **Voucher Code Management:** Users can manage voucher codes efficiently within the app. This includes generating new codes, organizing codes into categories, and tracking the redemption status of each code.
* **User-Friendly Interface: T**he Smart Scanner app offers a user-friendly interface that makes it easy for users to navigate and access its various functionalities.

## Voucher reimbursement&#x20;

OpenG2P provides a reference implementation for beneficiary registration, ensuring smooth access to entitlements. The registration process involves collecting beneficiary information, verifying eligibility, and issuing entitlement vouchers.

### Process

1. The service provider logs into the Service Provider Portal and searches for the beneficiary record.
2. The QR code in the beneficiary entitlement voucher is scanned to verify the issuing authority's digital signature and read the beneficiary entitlement details.
3. If the scan is successful, the service provider provides cash/medical assistance to the beneficiary.
4. The service provider uploads the supporting documents for assistance and submits the reimbursement application.
5. The accountant inspects the reimbursement application and approves the reimbursement amount.
6. The cash manager also inspects the application and approves it.
7. Post approval, the system generates an account payable PDF file with the account details required for the payment transfer. A QR code is embedded in this PDF to establish the source of truth and make the PDF tamper-proof.
8. The cash manager sends the PDF digitally to the payment switch.
9. The payment switch transfers the reimbursement amount per service provider account details in the PDF.

To follow the steps to create voucher [click here](../entitlement/user-guides/create-entitlement-manager-type/create-voucher-entitlement-manager.md)

&#x20;
