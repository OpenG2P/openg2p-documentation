# Service Provider Reimbursement

## Introduction

OpenG2P has a reference implementation for the Service Provider Portal. A service provider can submit the reimbursement application on this portal after assisting the beneficiary. Subsequently, the reimbursement request is inspected and approved by accountants and cash managers. Post reimbursement approval, the payment switch transfers the reimbursement amount to the service provider account.

## Process

1. The service provider logs into the Service Provider Portal and searches for the beneficiary record.
2. The QR code in the beneficiary entitlement voucher is scanned to verify the issuing authority's digital signature and read the beneficiary entitlement details.
3. If the scan is successful, the service provider provides cash/medical assistance to the beneficiary.&#x20;
4. The service provider uploads the supporting documents for assistance and submits the reimbursement application.
5. The accountant inspects the reimbursement application and approves the reimbursement amount.
6. The cash manager also inspects the application and approves it.&#x20;
7. Post approval, the system generates an account payable PDF file with the account details required for the payment transfer. A QR code is embedded in this PDF to establish the source of truth and make the PDF tamper-proof.
8. The cash manager sends the PDF digitally to the payment switch.
9. The payment switch transfers the reimbursement amount per service provider account details in the PDF.

## Reference scenario

<figure><img src="../.gitbook/assets/service-provider-reimbursement.drawio (2).png" alt=""><figcaption></figcaption></figure>

## Customizations

1. The program manager/administrator can custom-assign an approving officer for multiple approvals.
2. Though this example shows two approval stages, the number of stages can be customized.
3. The payment mode for reimbursement can be customized.
