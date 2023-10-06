# Payment Modes

## Introduction

Payment mode is the way in which the benefits are paid to the beneficiaries. Program administrators must consider several factors before deciding on the payment mode. Some of these considerations are:

* Do the beneficiaries have to travel a long distance or stand in long queues to get the benefits?
* Do the beneficiaries have a choice in how they want to receive the benefit, i.e. cash, account, or mobile wallet?
* Can the beneficiaries use the pre-loaded cash cards to purchase groceries and daily provisions at local stores or keep the cash for later use?
* How will the beneficiary authenticate themselves for receiving benefits?
* What are the safety and security facilities at the benefits payout location where beneficiaries receive in-hand cash?

Most of these challenges can be easily solved by transferring payments digitally to the beneficiary bank accounts and mobile wallets. OpenG2P platform supports a variety of digital payments along with beneficiary authentication mechanisms to enable speedy, safe, and secure disbursements.

## OpenG2P cash disbursement methods

Cash benefits can be disbursed through various means in the OpenG2P platform:

#### Cash in hand at banks/cash counters

While the OpenG2P platform supports accounting and payment status updates for this method of disbursement, it is not recommended due to the manual intervention required in the process.

#### Payment using prepaid cards

The program's payment system (outside the purview of OpenG2P) loads a prepaid card usable at ATMs, stores, point of sale (POS) kiosks, etc. OpenG2P supports accounting and payment status updates for this type of payment.

#### Cash disbursement in account through direct account transfer

OpenG2P integrates with Mojaloop to provide this facility. To learn more about Mojaloop integration, click [here](../integrations/mojaloop-integration.md).

#### Cash disbursement in mobile wallets

OpenG2P integrates with [GSMA Mobile Money](https://www.gsma.com/mobilefordevelopment/mobile-money/) to provide this facility. This option is very lucrative for the unbanked beneficiaries.

## OpenG2P entitlement vouchers

OpenG2P platform facilitates program administrators to print/send [entitlement vouchers](../beneficiary-management/entitlement.md#entitlement-voucher) with customized QR codes. The QR code provides a digital signature that makes the voucher tamper-proof and authorizes the intended beneficiary to claim the benefits at the payment service provider facility. Vouchers may be issued in several forms:

1. Paper-based letter with QR code
2. Verifiable Credential (VC) on a smartphone

### Voucher code

A **voucher code** is a random code associated with a voucher that the beneficiary needs to share with the service provider. The voucher code is required to claim the reimbursement. The idea is to reduce the chances of fraud arising by a service provider claiming reimbursement without any connection with the beneficiary.

### Voucher reimbursement

Entitlement vouchers are versatile and can be used to disburse benefits other than cash such as medical assistance. These are some of the well-known uses of entitlement vouchers:

* encash at banks/counters
* account/wallet transfer at banks/counters
* guarantee letter for medical/service assistance

To understand an example workflow for entitlement vouchers, click [here](../workflows/on-demand-assistance.md).

###
