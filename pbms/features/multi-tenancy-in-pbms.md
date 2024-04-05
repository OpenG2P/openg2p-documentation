---
layout:
  title:
    visible: true
  description:
    visible: false
  tableOfContents:
    visible: true
  outline:
    visible: true
  pagination:
    visible: true
---

# Multi-tenancy

## Concept

To allow multiple departments/organisations to use the same instance of OpenG2P while maintaining separation of data, control and access, the multi-company feature in Odoo is being explored that allows users to manage and operate multiple companies within a single Odoo instance. A user can be logged in to multiple companies at once. This allows the user to access information from multiple companies and create or edit records in a multi-company environment.

## Multi-companies feature in Odoo

The companies feature in Odoo can be used by users to associate with multiple companies. This functionality allows users in OpenG2P to establish connections with and operate across multiple companies, providing a flexible and wide-ranging approach to managing various private matters within the system.

\
The purpose of incorporating multiple companies feature within a single platform is to facilitate the maintenance of distinct data sets. Users can segregate registry data by selecting a specific company from the drop-down menu. For instance, if the user selects the companies for any individual /group that particular individual/ group will be visible only in that particular company. If the user does not choose any specific company, the registry data will be reflected across all companies.

\
The program data can be organized in alignment with the registry by incorporating a "companies" field on the program creation page. In this field, users have the option to select a specific company from the drop-down menu, determining the visibility of the program within that chosen company. This feature enables users to associate programs with specific companies and manage program data according to company preferences.

## How to manage companies

Multiple companies can be created from the Settings menu. Users can create multiple companies, irrespective of the debug mode. The user can go to settings and under user and companies, select the companies option to create a new one.

<figure><img src="https://github.com/OpenG2P/openg2p-documentation/blob/1.2.1/developer-zone/upcoming-features/.gitbook/assets/image%20(45).png" alt=""><figcaption></figcaption></figure>

Once the company is created, all the newly created companies are visible on the upper bar. All the allowed companies to the user are available here. The user can access these companies by selecting any one of them from the drop-down menu located on the header.

<figure><img src="https://github.com/OpenG2P/openg2p-documentation/blob/1.2.1/developer-zone/upcoming-features/.gitbook/assets/image%20(50).png" alt=""><figcaption></figcaption></figure>

The user has the ability to designate allowed and default companies. Only the selected companies will be visible in the portal, and the user can toggle exclusively between those designated companies.

<figure><img src="https://github.com/OpenG2P/openg2p-documentation/blob/1.2.1/developer-zone/upcoming-features/.gitbook/assets/image%20(49).png" alt=""><figcaption></figcaption></figure>
