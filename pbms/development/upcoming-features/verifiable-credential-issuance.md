---
description: WORK IN PROGRESS
---

# Verifiable Credential Issuance

PBMS Beneficiary Registry (BR) can issue beneficiary credentials (e-cards) in the form of [Verifiable Credentials](https://www.w3.org/TR/vc-data-model/) (VC). These can be downloaded into the beneficiary's digital wallet upon authentication. These credentials can signify that this person is part of this benefit program. Some example use-cases are  Safety Net Program Beneficiary e-Card, BPL Card, etc.



<figure><img src="../../../.gitbook/assets/beneficiary-e-card.jpg" alt="" width="188"><figcaption></figcaption></figure>

{% embed url="https://miro.com/app/board/uXjVKe3Q2Vo=/?share_link_id=906399345811" %}

## Feature and functionality

| Feature                                                                                                         | Description                                                         |
| --------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| Online ID authentication for download                                                                           | <ul><li>Using eSignet</li></ul>                                     |
| [OpenID for VCI API](https://openid.net/specs/openid-4-verifiable-credential-issuance-1\_0.html) implementation |                                                                     |
| Support for issuance of multiple credential types                                                               | <ul><li>Configuration of VC content without code change. </li></ul> |
| Tamper proof                                                                                                    | <ul><li>Digitally signed</li></ul>                                  |
| Download into Inji Wallet                                                                                       |                                                                     |
| Share e-card to avail services                                                                                  |                                                                     |

{% hint style="info" %}
Bulk VC issuance is not supported&#x20;
{% endhint %}

## Source code

## Configuration

\<All configuration concepts, and pointer to configuration guides>

## Technical documentation

VCI uses Odoo modules:

* \<module names>

## User guides
