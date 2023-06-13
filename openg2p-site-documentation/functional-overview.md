# Functional Overview

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

## Participants in a Program

A program is managed and executed by multiple participants. These participants play one or more of these key roles:

#### Administrator

An administrator configures role-based access to the OpenG2P portal for other participants as per their roles and may configure default parameters in the portal.

#### Program Manager

A program manager creates a program and configures deduplication and eligibility parameters in the OpenG2P portal. A program usually has multiple disbursement cycles with a start and end date that are configured by the program manager. In brief, a program manager handles benefit allocation functions during the lifecycle of a program.

#### Field Registration Officer

A field registration officer collects beneficiary information using a mobile registration application. This officer typically goes door-to-door to collect information. The beneficiary information fields are defined by the program manager.

#### Registration Agent

A registration agent collects beneficiary information in the same way as a field registration officer. However, the agent is likely to sit in a central location to be visited by the beneficiaries.

#### Payment Manager

A payment manager is responsible for configuring and managing the cycles, batches, and modes of benefit for the entitled beneficiaries in the OpenG2P portal. This manager also takes care of accounting, reconciliation, and reports related to the benefit payments. In brief, a payment manager handles benefit payment functions during the lifecycle of a program.

## Privacy and Security

OpenG2P stores Personal Identifiable Information (PII) in a secure manner at rest and in transit. The beneficiary signs a consent form before sharing the information with the field registration officer. PII or part of it is shared after obtaining permission and establishing relevance with external parties.&#x20;

## Beneficiary Database

Beneficiary information is maintained in two databases:

#### PostgreSQL

This database has records of all the beneficiary information fields including registration, entitlements, and payments.&#x20;

#### MinIO Storage

This object storage stores supporting documents such as consent forms, ID proof, address proof, and other scans.

## Functional Architecture

OpenG2P has a flexible architecture that allows governments and social benefit delivery systems to choose functionalities per their needs. The platform is built to allow inclusion and has supporting features. For example, beneficiaries in remote areas without any network connectivity can be registered offline. The platform enables bulk payments as well as on-demand payments. The payment approval can involve digital approval, multiple approvals, and manual interventions and the platform can support such disparate benefit disbursements.

<figure><img src="../.gitbook/assets/image.png" alt=""><figcaption></figcaption></figure>

{% hint style="info" %}
**External System Integrations**

Digital authentication can be facilitated using MOSIP or any other ID system as the platform is agnostic of ID systems.&#x20;

The platform can integrate with payment systems other than the three payment systems shown in the diagram. &#x20;
{% endhint %}

### Technical architecture <a href="#technical-architecture" id="technical-architecture"></a>

<figure><img src="../.gitbook/assets/image (2) (1).png" alt=""><figcaption></figcaption></figure>
