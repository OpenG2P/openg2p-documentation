---
description: Social Payments Account Registry
cover: ../.gitbook/assets/SPAR banner-on-light-background.png
coverY: 0
layout:
  cover:
    visible: true
    size: hero
  title:
    visible: true
  description:
    visible: true
  tableOfContents:
    visible: true
  outline:
    visible: true
  pagination:
    visible: true
---

# SPAR

The Social Payments Account Registry (SPAR) is an extension of the ID Account Mapper that maintains a mapping of a user ID and [Financial Address](https://docs.cdpi.dev/technical-notes/digital-payment-networks/financial-address) (FA) like bank code, account details, mobile wallet number, etc., primarily aimed at cash transfers in a social benefit delivery system. It is an independent module offered by OpenG2P. SPAR implements the functionality of an ID Account Mapper with the additional feature of offering a self-service portal for a beneficiary to add/update his/her FA. While in countries like India, the ID Account Mapper is updated by a bank (after authenticating a beneficiary), this may not be immediately feasible in many countries as all FSPs need to integrate with ID Account Mapper. In such situations, a department like the social welfare department can install SPAR and offer self-service updates, or via an agent. Of course, an important assumption is that an online ID authentication mechanism is available in the country via APIs. For example, in MOSIP adopting countries both biometric and OTP-based authentication is available.&#x20;

SPAR is a powerful **inclusion** tool as it gives end users the ability to choose how they would like to receive the benefits. &#x20;

SPAR may be housed centrally in a country as a building block of the Digital Public Infrastructure (DPI). Alternatively, a social welfare department can house it and enable other departments to use the same for cash disbursements.

The SPAR subsystem consists of 2 functional components

* SPAR Mapper (ID-Account Mapper)
* SPAR Self-Service

The SPAR Mapper contains the actual mapping between beneficiary IDs and their respective accounts.

The SPAR Self-Service  provides beneficiaries the ability to log in to SPAR and update their account information in the registry. The self-service portal facilitates an easy-to-use interface like searching for a beneficiary's bank, its branch, or a mobile service provider so that the beneficiary can provide the full financial address, where he/she wishes to receive the cash credits for the benefit programs.

## Functional Overview

The following figure provides a Functional Architecture of the SPAR Subsystem.

{% embed url="https://miro.com/app/board/uXjVNDnhJUg=/?share_link_id=24912538335" %}

## Technical Overview

The following picture provides a technical architecture of SPAR

<figure><img src="../.gitbook/assets/Gitbook-SPAR-Technical-Architecture.jpg" alt=""><figcaption><p>SPAR - Technical Architecture</p></figcaption></figure>

The SPAR subsystem consists of the following technology components

* **openg2p-spar-mapper-api** -- This is a FastAPI based python **microservice** that serves as the id-mapper registry service. This microservice provides G2P-Connect compliant APIs to update and retrieve financial address information.
* **openg2p-spar-self-service-ui** -- This is a ReactJS based **web-ui layer** that enables a beneficiary to log into the Self-Service System of SPAR and view and update his financial address.
* **openg2p-spar-self-service**
  * **openg2p-spar-self-service-api** -- This is a FastAPI based python **microservice** that provides REST APIs to the UI layer. This microservice facilitates maintenance of financial address to a beneficiary by providing search APIs for banks, branches and wallet providers so that a beneficiary can provide his/her complete financial address in the registry. This microservices uses a Postgresql persistence layer.
  * **openg2p-spar-mapper-interface-lib** -- This is Python **library** that specifies interface APIs to connect to an account-mapper service.
  * **openg2p-spar-mapper-connector-lib** -- This is a **library** that provides an OpenG2P implementation of the mapper interface. This connector library enables the self-service microservice to connect to the openg2p-spar-mapper-fastapi microservice using REST APIs.&#x20;
  * In an implementation, if there is a requirement to use some other account-mapper, we will need to provide another connector library. That new connector library also needs to implement the openg2p-spar-mapper-interface-lib, so that there is no change to be made in the openg2p-spar-self-service-api. The new connector library should be wired into the openg2p-spar-self-service-api in the application initializer.
