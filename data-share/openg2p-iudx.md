---
description: Data Share
---

# OpenG2P - IUDX

Data sharing across systems is a foundational pillar of any robust digital public infrastructure (DPI). An effective data sharing mechanism typically includes these key capabilities:

* Precise sharing of only the relevant and requested data segments
* Enforceable data access policies that govern both the data and its consumers
* Strong authentication and authorization controls
* Multiple data sharing channels such as events, APIs, and file transfers
* End-to-end security to protect data in transit
* Scalability to support numerous consumers and deliver data in real-time

While various approaches can achieve these goals, OpenG2P has integrated with [IUDX](https://iudx.org.in/)—an advanced urban data sharing platform that connects data producers and consumers under clearly defined access policies. We offer a ready-to-use implementation to demonstrate this powerful integration.

## Conceptual overview

{% embed url="https://miro.com/app/board/uXjVIE8imj8=/" %}

### Data sharing hierarchy

<figure><img src="../.gitbook/assets/image (17).png" alt=""><figcaption></figcaption></figure>

## Demo setup

{% embed url="https://miro.com/app/board/uXjVIDngMAk=/" %}

## Configuration and customization

Steps to configure IUDX:

1. Create Admin User and normal user on keycloak.
2. On-board Resource Server.
3. Assign roles (provider/ consumer) to the users.
4. Add access policy domain
5. Upload catalogue items.
6. Define policies for resources for an users.
7. Register Adaptor at dataset level.
8. Ingest data at resource level using adaptor.

{% hint style="info" %}
The adapter component is a customization step that providers write to share data from SR or PBMS.
{% endhint %}

The adaptor acts as a bridge between data sources (SR/PBMS) and the IUDX platform. It is responsible for fetching data from the specified data sources, transforming it into a format suitable for sharing, and then seamlessly pushing this transformed data into the IUDX platform. The process ensures that data is consistently and accurately delivered to consumers, tailored to their needs.

Key features of the adaptor include:

* **Data Fetching**: Collects data from specified sources, ensuring all relevant information is acquired.
* **Data Transformation**: Converts the data into a structured format that aligns with IUDX requirements, ensuring compatibility and ease of use.
* **Data Pushing**: Transmits the transformed data into the IUDX platform, facilitating immediate use or further processing.

The custom design and code of these adaptors ensure they are tailored to specific data sets and operational requirements, enhancing the overall efficiency of data handling within the IUDX framework.

## Deployment

Follow the IUDX-provided instructions on [deployment](https://github.com/datakaveri/iudx-deployment/).

{% hint style="info" %}
The UI is not open source. It's deployed by IUDX.
{% endhint %}

## Developer guide

* [Social Registry Connector](https://app.gitbook.com/o/bnTr6Kp4z4CXR4QVIPSa/s/JZcdob2emEcLMvLyIxqT/~/changes/1370/social-registry/developer-zone/odoo-modules/g2p-registry-datashare-rabbitmq)
* [PBMS Connector](https://app.gitbook.com/o/bnTr6Kp4z4CXR4QVIPSa/s/JZcdob2emEcLMvLyIxqT/~/changes/1370/pbms/developer-zone/odoo-modules/g2p-program-datashare-rabbitmq)

## Source code

* [IUDX](https://github.com/datakaveri/)
* [OpenG2P Social Registry Adapter](https://github.com/OpenG2P/openg2p-registry/)
* [OpenG2P PBMS Adapter](https://github.com/OpenG2P/openg2p-program/)
