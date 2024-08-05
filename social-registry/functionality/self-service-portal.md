---
description: Work in Progress
---

# Self Service Portal

A self-service portal for a social registry is a digital platform designed to streamline and simplify the process of accessing and managing social services. It empowers citizens to interact with social services independently, reducing administrative burdens and improving service delivery.

### Key features

* **OpenID Connect integration:** The Self Service Portal allows integration with any OpenID Connect (OIDC) client. The portal has an existing integration with [eSignet](https://docs.esignet.io/).
* **User Portal Access:** Users can log in and independently manage various aspects of their social registry profile.
* **Form Design and Management:** Administrators can design multiple forms tailored to different social programs, enabling streamlined data collection and processing.
* **Profile and Contact Management:** Users can directly update their profile information and contact details, ensuring accuracy and timeliness.
* **Household and Family Management:** Users can add and update household and family details, facilitating comprehensive data management.
* **Periodic Liveliness Check:** Users can perform periodic liveliness checks through ID integration options, maintaining up-to-date records.
* **Document Upload:** Users can upload important documents as required by various departments, simplifying application processes.
* **User Profile Management:** Users can view and update their personal information, ensuring their data is current and accurate.
* **Notifications and Alerts:** Send automated notifications and alerts to users regarding application status, deadlines, and important updates.

### Benefits of Self Service Portal in Social Registry

1. **Enhanced Accessibility**
   * **24/7 Availability:** Users can access the portal at any time, from anywhere, making social services more accessible.
   * **Reduced Waiting Times:** By enabling self-service, the portal reduces the need for in-person visits and long waiting times.
2. **Increased Efficiency**
   * **Streamlined Processes:** Automated workflows and digital forms expedite application processing and reduce administrative overhead.
   * **Data Accuracy:** Direct user input minimises errors associated with manual data entry.
3. **Cost-Effectiveness**
   * **Lower Operational Costs:** Reduced reliance on physical offices and staff leads to significant cost savings.
   * **Scalability:** The API-based design facilitates easy scaling to accommodate growing numbers of users and services.
4. **Empowered Citizens**
   * **Self-Reliance:** Users gain greater control over their interactions with social services, fostering independence.
   * **Transparency:** Real-time updates and status tracking enhance transparency in service delivery.

### Design Strategy

* **API Based design**
* **Form.IO for managing form and rendering**

&#x20;

In the Social Registry (SR), data are gathered and updated using various mechanisms.  SR has an external web portal or Self Service portal, independent of the Odoo-based platform that empowers applicants/registrants and beneficiaries the ability to log in, edit, and submit their information.

## Significance of a Self Service portal

* Self Service portal's user-friendly design makes it simple for registrants and beneficiaries to navigate and use.
* It facilitates the registration process for applicants.
* It makes it simple for applicants and beneficiaries to sign up and carry out their activities on their own.
* It enables applicants and beneficiaries to register and manage their information.
* It complies with all security regulations to protect the information of applicants and beneficiaries.

## High-level workflow

{% embed url="https://miro.com/app/board/uXjVKtyyeYg=/" %}

## Benefits of the Self Service portal

* Self Service portal reduces dependency on government initiatives to gather data.
* It improves the accuracy and efficiency of the data in the Social Registry module.
* It aims to provide beneficiaries with more control over their data and seeks to expand their data collection mechanisms.
* It maintains a dynamic, up-to-date, realistic, and helpful Social Registry.
* Additionally, this feature offers an alternate method to create the nation's registry by allowing beneficiaries to update their information whenever they choose. This eliminates the need for them to wait for government to collect their data.

## Feature and functionality

<table><thead><tr><th width="231">Feature</th><th>Functionality</th></tr></thead><tbody><tr><td>Login <br></td><td>Applicants can use the Self Service portal to safely log in with any of their government authorized IDs, such as National IDs, Functional IDs, OTPs, or biometric verification.<br>(Need confirmation)</td></tr><tr><td>Submit Details</td><td>An Individuals can self-register, providing socioeconomic information about themselves and their family members.</td></tr><tr><td>Upload Documents</td><td>An Individuals can provide the required proof of identity or support documents. </td></tr><tr><td>Update Data</td><td>Applicants can use the Self Service portal to log in and directly update or edit their current information.</td></tr><tr><td>Updated Forms</td><td>Periodically, new forms and changes might be posted on the Self Service portal to reflect the most recent modifications</td></tr></tbody></table>

## Business process flow

* **Login**
* **Submit Details**
* **Validation and Verification**
* **Support System**







The feature aims to empower beneficiaries by allowing them to submit and update their information directly through a secure web portal. This feature enables registrants to log in to an external web portal, independent of the Odoo based system, to register themselves and manage their information.

\
This approach reduces dependency on government data collection efforts, enhances the accuracy and currency of data in the social registry, and grants beneficiaries control over their own data usage and seeks to expand their data collection mechanisms and maintain a dynamic and realistic social registry.\


Additionally, this feature offers an alternative method for building the country's registry by allowing beneficiaries to update their information at any time,without having to wait for government to collect their data\


## Feature Overview:

1\. Login: Registrants can access a web-based portal where they can securely log in using national IDs, functional IDs, OTPs, or bio-metric authentication. \
(Need confirmation)\
\
2\. Submit Details: The Individuals can register themselves and their family members, provide socio-economic details, and submit.\
\
3\. Upload Documents: The Individuals can submit necessary supporting or  identification documents. \
\
4\. Update Data: The registrants can login and update or edit their existing information directly through the portal.\
\
5\. Updated Forms: New forms and updates can be periodically hosted on the portal to accommodate the latest changes.

## Business process flow

* **Login**
* **Submit Details**
* **Validation and Verification**
* **Support System**
