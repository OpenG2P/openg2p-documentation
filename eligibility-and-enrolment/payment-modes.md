# Payment Modes

## Introduction

Program administrators must consider several factors before deciding on the payment mode. Some of these considerations are:

* How will the beneficiary authenticate themselves for receiving benefits?
* Do the beneficiaries have to travel a long distance or stand in long queues to get the benefits?
* Do the beneficiaries have a choice in spending the cash benefits for purchasing groceries and daily provisions at local stores?
* What is the form of the benefit - medical assistance, job assistance, in-kind relief, nutritional supplements, etc.?
* What are the safety and security facilities at the benefit payout location?

Most of these challenges can be easily solved by transferring payments digitally to the beneficiary bank accounts and mobile wallets. OpenG2P platform supports a variety of digital payments along with beneficiary authentication mechanisms to enable speedy, safe, and secure disbursements.

## OpenG2P cash disbursement methods

Cash benefits can be disbursed through various means in the OpenG2P platform:

#### Cash in hand at banks/cash counters

While the OpenG2P platform supports accounting and payment status updates for this method of disbursement, it is not recommended due to the manual intervention required in the process.

#### Payment using smart cards

The program's payment system (outside the purview of OpenG2P) loads a smart card usable at ATMs, stores, point of sale (POS) kiosks, etc. OpenG2P supports accounting and payment status updates for this type of payment.

#### Cash disbursement in account through direct account transfer

OpenG2P integrates with Mojaloop to provide this facility. To learn more about Mojaloop integration, click [here](../integrations/mojaloop-integration.md).

#### Cash disbursement in mobile wallets

OpenG2P integrates with [GSMA Mobile Money](https://www.gsma.com/mobilefordevelopment/mobile-money/) to provide this facility. This option is very lucrative for the unbanked beneficiaries.

## OpenG2P entitlement vouchers

OpenG2P platform facilitates program administrators to print/send [entitlement vouchers](../beneficiary-management/entitlement.md#entitlement-voucher) with customized QR codes. The QR code provides a digital signature that makes the voucher tamper-proof and authorizes the intended beneficiary to claim the benefits at the payment service provider facility.

Entitlement vouchers are versatile and can be used to disburse benefits other than cash such as medical assistance. These are some of the well-known uses of entitlement vouchers:

* encash at banks/counters
* account/wallet transfer at banks/counters
* guarantee letter for medical/service assistance

To understand an example workflow for entitlement vouchers, click [here](../workflows/on-demand-assistance.md).
