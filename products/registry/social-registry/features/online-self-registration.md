# Online Self Registration

The Self Service Registration Portal for a Social Registry (SR-SSRP) is a digital platform designed to streamline and simplify the process of accessing and managing social services. It empowers citizens to interact with social services independently, reducing administrative burdens and improving service delivery.

## User Story

{% @jira/embed url="https://openg2p.atlassian.net/browse/SR-134" %}

## Feature and functionality

<table><thead><tr><th width="258">Feature</th><th>Functionality</th></tr></thead><tbody><tr><td><strong>OpenID Connect integration</strong></td><td><p></p><p>The SSRP allows integration with any OpenID Connect (OIDC) client. The portal has an existing integration with <a href="https://docs.esignet.io/">eSignet</a>.</p><p></p></td></tr><tr><td><strong>User Portal Access</strong></td><td>Users can log in and independently manage various aspects of their social registry profile.</td></tr><tr><td><strong>Form Design and Management</strong></td><td>Administrators can design multiple forms tailored to different social programs, enabling streamlined data collection, and processing.</td></tr><tr><td><strong>Profile and Contact Management</strong></td><td>Users can directly update their profile information and contact details, ensuring accuracy, and timeliness.</td></tr><tr><td><strong>Household and Family Management</strong></td><td>Users can add and update household and family details, facilitating comprehensive data management.</td></tr><tr><td><strong>Periodic Liveliness Check</strong></td><td> Users can perform periodic liveliness checks through ID integration options, maintaining up-to-date records.</td></tr><tr><td><strong>Document Upload</strong></td><td>Users can upload important documents as required by various departments, simplifying application processes.</td></tr><tr><td><strong>User Profile Management</strong></td><td>Users can view and update their personal information, ensuring their data is current and accurate.</td></tr><tr><td><strong>Notifications and Alerts</strong></td><td>Send automated notifications and alerts to users regarding application status, deadlines, and important updates.</td></tr></tbody></table>

## High-level workflow

{% embed url="https://miro.com/app/board/uXjVKtyyeYg=/" %}

## Benefits of SSRP

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
   * SSRP reduces dependency on government initiatives to gather data.
   * Additionally, this feature offers an alternate method to create the nation's registry by allowing beneficiaries to update their information whenever they choose. This eliminates the need for them to wait for government to collect their data.

## Design strategy

### **API Based design**

{% embed url="https://miro.com/app/board/uXjVKsL5Bfg=/" %}

This above chart outlines the redesigning of the PBMS Beneficiary Portal components to enhance re-usability and maintainability. The current architecture is being refined to separate a base set of components that can be effectively reused across both the Beneficiary Portal and the SR-SSRP.

#### **Initial architecture: Beneficiary Portal**

The Beneficiary Portal originally managed key services needed by users, including authentication, form submissions, and access to program-related functionalities.

**Services**

1. **Login Services:** Managed user authentication and session management.
2. **Form Services:** Facilitated the creation, submission, and management of forms.&#x20;
3. **Program Services:** Provided access to program-related information and functionality for beneficiaries.

#### **Redesign: separation of base components**

The redesigned architecture separates core components into a base that can be leveraged by both the Beneficiary Portal and the SR-SSRP, thereby increasing the overall reusability, maintainability, and flexibility of the system.

<table><thead><tr><th width="287">Portals</th><th>API Services</th></tr></thead><tbody><tr><td><strong>Base Portal</strong></td><td><ul><li><strong>Login Services:</strong> Centralised control over user authentication, session management, and reusable across both the portals.</li><li><strong>Form Services:</strong> Manages all form-related activities, including creation, and submission. </li></ul></td></tr><tr><td><strong>Beneficiary Portal</strong></td><td><strong>Program Services:</strong> Focuses specifically on program-related functionalities, ensuring dedicated support, and customisation for beneficiaries.</td></tr><tr><td><strong>Social Registry Self Service Registration Portal (SR-SSRP)</strong></td><td><ul><li><strong>Profile Services:</strong> Manages user profiles, enabling users to update, and maintain their personal information.</li><li><strong>Household Services:</strong> Manages household-related data and interactions, allowing the head of the household to update and maintain household information.</li></ul></td></tr></tbody></table>

#### Advantages of redesigning of Beneficiary Portal components

The redesign of the Beneficiary Portal components into a shared base architecture not only facilitate the reuse of essential services across different portals but also enhances the maintainability and adaptability of the entire system. By strategically separating these components, we are better equipped to satisfy the changing needs of our users and ensure a more effective, scalable solution.

### **Form.io for managing form and rendering**

Both the Beneficiary Portal and SR-SSRP will utilise Form.io to manage forms and display dynamic content. Using the features of Form.io, forms can be designed to collect and update socio-economic data from users, allowing them to add new household information or edit existing data directly through the portal.

### **OIDC for user login**

Secure and standardized user authentication is paramount. By implementing OIDC, the system can leverage a robust authentication framework. OIDC allows integration with various third-party identity providers, such as Keycloak or eSignet. This approach enables centralised user management, strengthens security, and simplifies the login process. With user credentials stored and managed by the chosen identity provider, the system benefits from enhanced security and reduced development complexity.

### **Common code base for Beneficiary Portal and SR-SSRP**

The redesigned architecture emphasises code reusability and maintainability by establishing a common code base. Core services like login and form management, originally part of the Beneficiary Portal, are now refactored into reusable components accessible by both the portals. This approach simplifies  development processes, guarantees a uniform user experience on both the platforms, and makes future maintenance and updates simpler.

## Development phase

The following deliverables for the SR-SSRP module are planned for development and release at the appropriate phases.

<table><thead><tr><th width="117">Phase</th><th>Deliverable</th><th>Status</th></tr></thead><tbody><tr><td>Phase 1</td><td><ul><li>Login with OIDC</li><li>Update Profile</li><li>Add/Update Household members</li><li>Reference UI</li></ul></td><td></td></tr><tr><td>Phase 2</td><td><ul><li>Survey and Program forms</li><li>Notifications and Alerts</li><li>Document management</li><li>Liveliness check</li></ul></td><td></td></tr><tr><td>Phase 3</td><td><ul><li>Discovery service</li></ul></td><td></td></tr></tbody></table>
