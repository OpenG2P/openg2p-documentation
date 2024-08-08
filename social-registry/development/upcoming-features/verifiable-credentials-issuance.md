---
description: WORK IN PROGRESS
---

# Verifiable Credentials Issuance

Social Registry can issue credentials in the form of [Verifiable Credentials](https://www.w3.org/TR/vc-data-model/) (VC).  Upon authentication, these can be downloaded into the beneficiary's **digital wallet** or printed on paper as a **QR code.** These credentials indicate that the individual is the member of the Social Registry.  Credentials are sometimes also referred to as e-cards, Farmer Registry e-Card, etc.

## User story

{% @jira/embed url="https://openg2p.atlassian.net/browse/SR-13" %}

## Feature and functionality

* Social Registry exposes [OpenID for VCI](https://openid.net/specs/openid-4-verifiable-credential-issuance-1\_0.html) APIs. A wallet can use these APIs to retrieve the VCs.
* The content inside the VC can be configured without modifying the code.
* Any functional/foundational ID can be configured for authentication. For example, if the Registry contains National IDs (or National ID tokens) of individuals, and a valid eSignet authentication mechanism (or similar) exists against the given National ID, then the credential can be issued.
  * **Future possibilities**: If the Social Registry generates a unique ID, then that can be used to authenticate and retrieve the credential.

## High-level workflow

<figure><img src="../../../.gitbook/assets/Social Registry VC Issunace.jpg" alt="" width="563"><figcaption></figcaption></figure>

## Source code and configuration

Link to [Configuration and source code](../../../pbms/development/repositories/openg2p-vci.md).

