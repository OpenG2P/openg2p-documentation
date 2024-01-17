# OpenG2P Mojaloop Integration

## Introduction <a href="#introduction" id="introduction"></a>

This page describes the integration of OpenG2P with the [Mojaloop](https://mojaloop.io/) switch enabling cash transfer from one bank (treasury bank, for instance) to an individual's bank account. The connection to Mojaloop is achieved via an intermediate interoperability layer implemented by a Payment Hub (PH).

## Functional architecture

Below is the reference architecture of disbursements triggered from OpenG2P resulting in cash transfers.

<figure><img src="https://github.com/smita-g2p/openg2p-documentation/raw/c68b3e6da99fe077e2cbe5d5fc166b3e3487fbce/.gitbook/assets/openg2p-payments-diagram.png" alt=""><figcaption></figcaption></figure>

## Payment process

The beneficiary list is created on OpenG2P. After creating payment cycles and entitlements, payment batches are created for each cycle. A batch payment is triggered via the [Payment Manager](https://github.com/OpenG2P/openg2p-documentation/blob/1.2.1/platform/eligibility-and-enrolment/payment-manager.md). This batch is received by the interoperability layer implemented by a Payment Hub (PH) and payments are orchestrated either in bulk or individually. The Payment Hub connects to the Mojaloop interface of the Digital Financial Service Provider (DSFP). DFSP1 takes the transaction forward with Mojaloop Switch.

Reconciliation at the OpenG2P end is done via status API calls to Payment Hub which is responsible for gathering payment status information of all transactions from DFSPs and Switch.

In the current integration, the account id of the payee is available in the OpenG2P registry and passed on to Payment Hub (hence propagated to Mojaloop). The account id of the payer is configured in the[ Payment Manager](https://github.com/OpenG2P/openg2p-documentation/blob/1.2.1/platform/eligibility-and-enrolment/payment-manager.md).

{% hint style="info" %}
If [Account Mapper](https://g2pconnect.global/) is available as part of Digital Public Infrastructure, then the account id need not be stored in the OpenG2P registry.
{% endhint %}

## Payment Hub <a href="#proof-of-concept-implementation-demo-1" id="proof-of-concept-implementation-demo-1"></a>

The payment architecture may vary from country to country. An interoperability layer like Payment Hub shields the downstream variations by offering a uniform payments API interface such that systems like OpenG2P do not have to modify the payment code, thus enabling interoperability with any payment system. Of course, customisation needs to be done on the Payment Hub, where a specific Payment Connector needs to be created specifically for the payment systems interface.

<figure><img src="https://payments.mifos.org/wp-content/uploads/sites/20/2022/12/Screenshot-2022-12-27-at-10541-PM-transformed.png" alt=""><figcaption><p>Payment Hub</p></figcaption></figure>

Payment Hub connects to Mojaloop via the Mojaloop Connector.

{% hint style="info" %}
As part of the roadmap, OpenG2P is working towards supporting payment interfaces being defined as part of the [G2P Connect](https://g2pconnect.global/) initiative.
{% endhint %}

## Payments demo <a href="#proof-of-concept-implementation-demo-1" id="proof-of-concept-implementation-demo-1"></a>

{% embed url="https://www.youtube.com/watch?v=O_CyoNZ2Mig" %}

## Source code

The source code for OpenG2P - Payment Hub integration can be found [here](https://github.com/OpenG2P/openg2p-program/tree/15.0-develop/g2p\_payment\_phee).
