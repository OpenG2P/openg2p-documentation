# Mojaloop Integration

## Introduction <a href="#introduction" id="introduction"></a>

This page describes reference implementation for payment integration between OpenG2P and Mojaloop based Financial Systems. The architecture and implementation mentioned below is purely for demonstrations and is not intended for production deployments.ArchitectureBelow is the reference architecture of how the disbursements could be triggered from OpenG2P.

<figure><img src="../.gitbook/assets/openg2p-payment-manager-connections.svg" alt=""><figcaption></figcaption></figure>

## Proof of concept implementation - demo #1 <a href="#proof-of-concept-implementation-demo-1" id="proof-of-concept-implementation-demo-1"></a>

{% embed url="https://www.loom.com/share/29de864fd01a47dcbbdc9eee057b274b" %}

For the purposes of PoC Demonstration, we have chosen [SP Convergence Payment Interoperability Layer](https://sp-convergence.github.io/payments-interoperability-layer/documentation/pocs/G2P.html), as payment manager from OpenG2P.

* OpenG2P uses the configured Payment Manager and triggers payments in the way the payment manager understands.
* In the following implementation OpenG2P sends the list of Payments to be triggered to the [SP Convergence Payment Interoperability Layer](https://sp-convergence.github.io/payments-interoperability-layer/documentation/pocs/G2P.html), which in turn calls the pre-configured DFSP with relevant Payer and Payee details. (Payer being the Government/Department/Treasury)
* The following simulators and services (from the diagram) are used in place of real systems.

<figure><img src="../.gitbook/assets/openg2p-mojaloop-integration-setup.svg" alt=""><figcaption></figcaption></figure>

### Usage - payment cycle guide <a href="#usage-payment-cycle-guide" id="usage-payment-cycle-guide"></a>

(TODO: Elaborate)

#### **Prerequisites**

* The relevant registrant are registered into OpenG2P.
* The relevant Program is to be configured with the details of entitlement, eligibility etc.

#### **Procedure**

* Configure a new Payment manager on the Program, with all the required details.
* Enrol eligible registrants into the program.
* Create a new "Cycle" on the program.
* Create Entitlements.
* Approve Entitlements.
* Approve Cycle.
* Prepare Payments. Payment Batches are created based on the configurations.
* Send Payments. Payment Batches will be disbursed based on the configurations.
