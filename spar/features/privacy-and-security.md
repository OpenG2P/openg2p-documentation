---
description: SPAR Privacy & Security
layout:
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

# Privacy & Security

### Authentication & authorization

SPAR APIs are consumed by two categories of clients

1. Beneficiaries logging on to the Self-Service-Portal (through the Self-Service-Client) and consuming the APIs provided by openg2p-self-service-api
2. Partner systems consuming the Mapper APIs provided by openg2p-spar-mapper-api. These partner systems can be Banks, National Clearing, PBMS/MIS Systems - systems in the G2P chain, using the lookup (resolve) API of Mapper. \
   \
   The openg2p-spar-self-service-api (of point 1) which serves the self-service-ui, in turn has to consume the mapper APIs. In this context, the openg2p-spar-self-service-api will behave like a partner system&#x20;

### Transport security using a secure tunnel

Security of the payload during transmission (in both cases mentioned above) is handled using the https (SSL) implementation, using PKI.

<figure><img src="../../.gitbook/assets/Gitbook-OpenG2P-API-Security-L1.jpg" alt=""><figcaption><p>OpenG2P - SSL and TLS</p></figcaption></figure>

### Authentication

#### Case 1 - Authentication of Beneficiaries (Browser Client Application) consuming self-service-apis

This is handled by the Self Service API - integration with an OIDC - OAuth2.0 Login Provider. The beneficiary logs in, into the SPAR Self Service portal, using his/her National ID.

The Login Provider authorizes the beneficiary and provides the ID and Access tokens. The subsequent browser requests from the user, then carry these tokens to get access to the APIs.

There are two API paths, viz. <mark style="color:blue;">**auth**</mark> and <mark style="color:blue;">**oauth**</mark>, in the self-service-api, that fulfil these functionalities.

#### Case 2 - Authentication of Partner Systems consuming mapper-apis

(the self-service application that consumes mapper-apis - In this case, the self-service application is treated like a partner system consuming mapper apis)

### Partner authorization

#### Onboarding a Partner to consume an OpenG2P API

<figure><img src="../../.gitbook/assets/Gitbook-OpenG2P-API-Security-L2.jpg" alt=""><figcaption><p>Partner Onboarding for OpenG2P API</p></figcaption></figure>

#### API call by Partner

<figure><img src="../../.gitbook/assets/Gitbook-OpenG2P-API-Security-L3-01.jpg" alt=""><figcaption><p>OpenG2P API call from Partner Organization / Partner System</p></figcaption></figure>

#### JWT Schematic

<figure><img src="../../.gitbook/assets/Gitbook-OpenG2P-API-Security-L3-03.jpg" alt=""><figcaption><p>OpenG2P - JWT Schematic</p></figcaption></figure>

#### Validation of JWT using MOSIP Key Manager

<figure><img src="../../.gitbook/assets/Gitbook-OpenG2P-API-Security-L3-02.jpg" alt=""><figcaption><p>OpenG2P - Validation of JWT in MOSIP Key Manager</p></figcaption></figure>
