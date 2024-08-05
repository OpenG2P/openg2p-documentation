---
description: Work in Progress
---

# Self Service Portal

A Self Service portal for a Social Registry is a digital platform designed to streamline and simplify the process of accessing and managing social services. It empowers citizens to interact with social services independently, reducing administrative burdens and improving service delivery.

### Feature and functionality

<table><thead><tr><th width="258">Feature</th><th>Functionality</th></tr></thead><tbody><tr><td><strong>OpenID Connect integration</strong></td><td><p></p><p>The Self Service Portal allows integration with any OpenID Connect (OIDC) client. The portal has an existing integration with <a href="https://docs.esignet.io/">eSignet</a>.</p><p></p></td></tr><tr><td><strong>User Portal Access</strong></td><td>Users can log in and independently manage various aspects of their social registry profile.</td></tr><tr><td><strong>Form Design and Management</strong></td><td>Administrators can design multiple forms tailored to different social programs, enabling streamlined data collection and processing.</td></tr><tr><td><strong>Profile and Contact Management</strong></td><td>Users can directly update their profile information and contact details, ensuring accuracy and timeliness.</td></tr><tr><td><strong>Household and Family Management</strong></td><td>Users can add and update household and family details, facilitating comprehensive data management.</td></tr><tr><td><strong>Periodic Liveliness Check</strong></td><td> Users can perform periodic liveliness checks through ID integration options, maintaining up-to-date records.</td></tr><tr><td><strong>Document Upload</strong></td><td>Users can upload important documents as required by various departments, simplifying application processes.</td></tr><tr><td><strong>User Profile Management</strong></td><td>Users can view and update their personal information, ensuring their data is current and accurate.</td></tr><tr><td><strong>Notifications and Alerts</strong></td><td>Send automated notifications and alerts to users regarding application status, deadlines, and important updates.</td></tr></tbody></table>

## High-level workflow

{% embed url="https://miro.com/app/board/uXjVKtyyeYg=/" %}

### Benefits of Self Service Portal

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
   * **Transparency:** Real-time updates and status tracking enhance transparency in service delivery.&#x20;
5. **Reduces Dependency**
   * Self Service portal reduces dependency on government initiatives to gather data.
   * Additionally, this feature offers an alternate method to create the nation's registry by allowing beneficiaries to update their information whenever they choose. This eliminates the need for them to wait for government to collect their data.

## Design Strategy

* **API Based design**
* **Form.IO for managing form and rendering**

## Feature in upgraded version

The enhanced version of  Self Service portal for a Social Registry has the following feature.

<table><thead><tr><th width="201">Feature</th><th>Functionality</th><th>Process</th></tr></thead><tbody><tr><td><strong>Manage Financial Data</strong></td><td>In addition to giving beneficiaries access to social services, the Social Registry Self-Service Portal makes it easy to maintain and update their financial data, guaranteeing prompt and effective payment processing. SPAR plays a crucial role in processing payments that require accurate and current financial details for successful transfer of payments.</td><td>Beneficiary data is collected using ODK forms and imported into the Social Registry, where financial information becomes accessible for individuals to update at their convenience.</td></tr></tbody></table>
