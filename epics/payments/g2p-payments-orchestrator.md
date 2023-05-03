# G2P Payments Orchestrator

## Context

Enabling digital payments in a country requires several technology components, standards, legal frameworks and stakeholder agreements to come together. Countries across the globe stand at different maturity levels when it comes to digital payment infrastructure. In the context of social protection programs, the focus is more on the government-to-person payment channels for direct benefit transfer (DBT), emergency relief cash transfer, conditional cash transfer etc. It should be possible to connect these payment channels to systems like OpenG2P that can automatically trigger digital cash transfers.&#x20;

When it comes to G2P payments we face the following challenges:

* Interfacing with various non-standard payment interfaces and systems that are not interoperable with each other.&#x20;
* Handling bulk payment processing as typically social benefit transfers are done in bulk and the entire process needs to be done in a short period of time, esp. in emergency scenarios.

Mifos's Payment Hub is an open source project designed for this purpose. However, we see the following practical difficulties with the PH:

1. PH has been designed for several use cases including P2P, P2G, B2B etc. Hence the overall software is bulky for just the G2P use case.
2. PH uses the Zeebe orchestration engine whose license is not as permissive as Apache 2.0 or MPL 2.0. Zeebe prohibits free usage for commercial cloud deployments. See [Zeebe FAQ](https://camunda.com/legal/terms/cloud-terms-and-conditions/zeebe-license-overview-and-faq/).
3. Lack of responsive support from the PH contributors
4. No visible plan in the PH roadmap to make interfaces compliant with G2P Connect
5. According to engineers who have inspected the code and tried using PH, the impression is that the code is not very well written and modularized for making changes and enhancing the system

**G2P Payments Orchestrator (GPO)** is envisaged as an open source "interoperability layer" along with bulk payment orchestration that connects any upstream G2P system like OpenG2P to the specific payment rails of a country while addressing some of the issues mentioned above.

## High level view

<figure><img src="https://github.com/OpenG2P/openg2p-documentation/raw/develop/.gitbook/assets/g2p-payments-orchestrator.png" alt=""><figcaption></figcaption></figure>
