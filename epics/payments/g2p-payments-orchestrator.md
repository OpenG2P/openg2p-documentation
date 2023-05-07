# G2P Payments Orchestrator

## Context

Enabling digital payments in a country requires several technology components, standards, legal frameworks and stakeholder agreements to come together. Countries across the globe stand at different maturity levels with respect to digital payment infrastructure. In the context of social protection programs, the focus is more on the government-to-person payment channels for direct benefit transfer (DBT), emergency relief cash transfer, conditional cash transfer etc. It should be possible to trigger automatic digital cash transfers by systems like OpenG2P via the payment channels.

With regard to G2P payments, the following are some of the challenges encountered:

* Interfacing with various non-standard payment interfaces and systems that are not interoperable with each other.&#x20;
* Handling bulk payment processing as typically social benefit transfers are done in bulk and the entire process needs to be done in a short period of time, esp. in emergency scenarios.
* Reconciliation of all payments.

[Mifos's Payment Hub](https://payments.mifos.org/) (PH) is an open source project designed for this purpose. However, we see the following practical difficulties with the PH:

1. PH has been designed for several use cases including P2P, P2G, B2B etc. Hence the overall software is bulky for just the G2P use case.
2. PH uses the Zeebe orchestration engine whose license is not as permissive as Apache 2.0 or MPL 2.0. Zeebe prohibits free usage for commercial cloud deployments. See [Zeebe FAQ](https://camunda.com/legal/terms/cloud-terms-and-conditions/zeebe-license-overview-and-faq/).
3. Lack of responsive support from the PH contributors.
4. No visible plan in the PH roadmap to make interfaces compliant with G2P Connect and other emerging interoperable standards.
5. According to engineers who have inspected the code and tried using PH, the impression is that the code is not very well written and modularized for making changes and enhancing the system

**G2P Payments Orchestrator (GPO)** is envisaged as an open source module comprising of "interoperability layer" along with bulk payment orchestration that connects any upstream G2P system like OpenG2P to the specific payment rails of a country while addressing some of the issues mentioned above. The focus of GPO's functionality and design is G2P payments. The GPO is proposed to be developed as part of the OpenG2P project available under MPL 2.0 license.

## High level view

<figure><img src="https://github.com/OpenG2P/openg2p-documentation/raw/develop/.gitbook/assets/g2p-payments-orchestrator.png" alt=""><figcaption></figcaption></figure>

As depicted above, GPO sits between a G2P system and payment channels. The goal is to have a standard interface at **A** while **B,** **C**, **D** etc. may be custom interfaces and API calls specific to the payment system.&#x20;

## Technical architecture

<figure><img src="https://github.com/OpenG2P/openg2p-documentation/raw/develop/.gitbook/assets/gpo-tech-architecture.png" alt=""><figcaption></figcaption></figure>

The GPO consists of the following major components:

1. [Kafka](https://kafka.apache.org/) for event streaming
2. [Nussknacker](https://github.com/TouK/nussknacker) for real-time stream processing
3. Payment Connectors (PCs) specific to payment rails

Upstream G2P systems send the payment transfer requests to Kafka topics as JSON messages. Nussknacker can be visually programmed (no-code) to filter (and even transform) these requests and direct them to appropriate Kafka topics for the consumers. The input requests published in the _Request_ topic from the G2P system are checked for basic sanity and forwarded to the _Filtered Requests_ topic to be picked by PCs who in turn interface with specific payment systems like a payment gateway, core banking API or Mobile Money APIs. The response from these systems is received by the PCs, converted to JSON and published to the _Response_ topic. These response messages are filtered for cases of retries and failure by Nussknacker and published in corresponding Kafka topics. The "retry" messages are sent back to _Filtered Requests_ topic. G2P systems pick messages from Malformed Input, Success, and Failure topics for further actions.

Several different responses from the downstream payment rails may need to be filtered and directed to Kafka topics. More such topics may be defined along with the addition of logic in Nussknacker.

## Scalability&#x20;

Kafka and Nussknacker are highly scalable systems while Payment Connectors need to be designed and written supporting high scalability (for e.g. stateless micros services architecture)

## Bulk processing

## JSON message structure

The JSON messages flowing through the system need to be standardised for processing.&#x20;

## Open source technologies

The GPO uses open source technologies with very permissible license terms:

| Tool                                               | License    | Comments        |
| -------------------------------------------------- | ---------- | --------------- |
| [Nussknacker](https://github.com/TouK/nussknacker) | Apache 2.0 |                 |
| Apache Kafka                                       | Apache 2.0 |                 |
| Payment Connectors                                 | GPLv2      | If Java is used |
