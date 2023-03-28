# Mojaloop Integration

## Introduction <a href="#introduction" id="introduction"></a>

This page describes the integration of OpenG2P with the [Mojaloop](https://mojaloop.io/) switch enabling cash transfer from one bank (treasury bank, for instance) to an individual's bank account. The connection to Mojaloop is achieved via an intermediate interoperability layer like the [Payment Hub](https://payments.mifos.org/) of Mifos.&#x20;

## Architecture

Below is the reference architecture of how the disbursements are triggered from OpenG2P.

<figure><img src="../.gitbook/assets/openg2p-payments-diagram-drawio.svg" alt=""><figcaption></figcaption></figure>

## Payment process

The beneficiary list is created on OpenG2P. After creating payment cycles and entitlements, payment batches are created for each cycle. A batch payment is triggered via the [Payment Manager](../modules/eligibility-and-enrolment/payment-manager.md). This batch is received by the Payment Hub and payments are orchestrated either in bulk or individually. The Payment Hub connects to the Mojaloop interface of DSFP1. DFSP1 takes the transaction forward with Mojaloop Switch.



## Interoperability layer <a href="#proof-of-concept-implementation-demo-1" id="proof-of-concept-implementation-demo-1"></a>

The payment architecture may vary from country to country. An interoperability layer like Payment Hub shields the downstream variations by offering a uniform payments API interface such that systems like OpenG2P do not have to modify the payments code, thus enabling interoperability with any payment system. Of course, customisation needs to be done on the Payment Hub, where a specific Payment Connector needs to be created specifically for the payment systems interface.&#x20;

<figure><img src="https://payments.mifos.org/wp-content/uploads/sites/20/2022/12/Screenshot-2022-12-27-at-10541-PM-transformed.png" alt=""><figcaption></figcaption></figure>

Payment Hub connects to Mojaloop via the Mojaloop Connector.&#x20;

{% hint style="info" %}
As part of the roadmap, OpenG2P is working towards supporting payments interfaces being defined as part of the [G2P Connect](https://g2pconnect.global/) initiative.&#x20;
{% endhint %}

## Payments demo <a href="#proof-of-concept-implementation-demo-1" id="proof-of-concept-implementation-demo-1"></a>

{% embed url="https://www.youtube.com/watch?v=O_CyoNZ2Mig" %}

