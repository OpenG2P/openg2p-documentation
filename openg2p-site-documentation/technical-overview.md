# Technical Overview

## Implementing a Social Benefit Scheme

Each social benefits delivery scheme is implemented via a program in the OpenG2P platform. A program implements these key functions for benefits delivery:

#### Beneficiary Registration

Beneficiary information is collected and authenticated by a field registration officer, agent, or self-service portal. The beneficiary can be an individual, family, or group. The relevant beneficiary information fields are decided as part of the program configuration.&#x20;

#### Benefit Allocation

Registered beneficiaries are enrolled into a program after deduplicating the registered entries. Based on the eligibility criterion configured in the program such as age, gender, and income, the enrolled beneficiary is deemed entitled to the scheme benefits. Entitled beneficiaries are also notified through SMS/email based on the program's notification configuration.

#### Benefit Payment

The benefit can be disbursed as cash, voucher/coupon, in-account, or in-kind using an OpenG2P program. Further, accounting, reconciliation, and reports are facilitated by the program to allow the benefit issuing authorities to keep track of payouts, budgets, and other financials.

#### Monitoring and Reporting

OpenG2P platform integrates a [reporting framework](https://github.com/mosip/reporting) that lets benefit-issuing authorities create dashboards of their choice to visualize data related to the program(s).&#x20;

## Privacy and Security

OpenG2P stores Personal Identifiable Information (PII) in a secure manner at rest and in transit. The beneficiary signs a consent form before sharing the information with the field registration officer. PII or part of it is shared only after obtaining permission and establishing relevance for external parties.&#x20;

## Beneficiary Database

Beneficiary information is maintained in two databases:

#### PostgreSQL

This database has records of all the beneficiary information fields including registration, entitlements, and payments.&#x20;

#### MinIO Storage

This object storage stores supporting documents such as consent forms, ID proof, address proof, and other scans.

## Functional Architecture

OpenG2P has a flexible architecture that allows governments and social benefit delivery systems to choose functionalities per their needs. The platform is built to allow inclusion and has supporting features. For example, beneficiaries in remote areas without network connectivity can be registered offline. The platform enables bulk payments as well as on-demand assistance. The payment approval can involve multiple approvals including manual approvals. The platform can configure stages of approvals. Additionally, OpenG2P allows vendors to upload supporting documents&#x20;

<figure><img src="../.gitbook/assets/image.png" alt=""><figcaption></figcaption></figure>

{% hint style="info" %}
**External System Integrations**

Digital authentication can be facilitated using MOSIP or any other ID system as the platform is agnostic of ID systems.&#x20;

The platform can integrate with payment systems other than the three payment systems shown in the diagram. &#x20;
{% endhint %}

### Technical architecture <a href="#technical-architecture" id="technical-architecture"></a>

<figure><img src="../.gitbook/assets/image (2) (1).png" alt=""><figcaption></figcaption></figure>
