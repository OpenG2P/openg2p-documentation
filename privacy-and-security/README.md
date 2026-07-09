# Privacy & Security

OpenG2P is a robust and versatile platform, providing governments and organisations with a comprehensive solution for delivering benefits efficiently. As OpenG2P handles sensitive beneficiary information including personally identifiable information (PII), maintaining the highest standards of security is paramount.



1. Applicability&#x20;

This privacy policy applies to the users of the OpenG2P platform which collects, stores and transfers data at various levels during the course of implementation of government-to-person benefits delivery by various Government departments in the country where the platform is being deployed.&#x20;



2. Information collected and why&#x20;

Information is collected for benefits delivery and varies per department, on whose request OpenG2P platform is adopted by a country. OpenG2P uses the data which is collected by the social registry, at this stage consent is taken by the registry. For collection of data offline, OpenG2P takes consent via a consent form while using ODK. Scanned consent documents are also collected and stored while collecting data from the field. If OpenG2P platform’s self service portal is used or if the registry data is imported from 3rd Party, the PII is encrypted using the Mosip key manager to safeguard the data.&#x20;

Information collected:&#x20;

Demographic data- Name, Gender, Age, Address, Contact Number, E-Mail ID and other household information regarding family structure.



3. Sharing and Disclosure&#x20;

OpenG2P does not disclose or share any data stored on our platforms with any third party or private entity. OpenG2P uses an inbuilt consent sharing mechanism. OpenG2P may share the information with government bodies or law enforcement agencies pursuant to a legal obligation. Data from the registry is sharable, and the department has to take consent to share.



4. Security Practices

We follow industry-standard best practices with respect to encryption and storage of users’ information. The security measures are as follows:&#x20;

## User authentication and access Control

* **Multi-factor Authentication (MFA)**: Building on Odoo's MFA capabilities, OpenG2P allows users to strengthen their authentication process by requiring multiple factors such as passwords, one-time codes, and biometric verification. This includes built-in support for Two-Factor Authentication (2FA), where users must enter both a password and a time-based code from an authenticator app—greatly enhancing account security and giving users greater confidence in protecting their data.
* **Role-Based Access Control (RBAC)**: Administrators define roles and permissions within OpenG2P, ensuring authorised personnel have access to specific functionalities and beneficiary data while preventing unauthorised access.
* **User Groups and Access Rules**: OpenG2P builds upon Odoo's user groups and access rules to provide granular control over beneficiary data access, ensuring data confidentiality is maintained.
* **OAuth and OpenID Connect**: Additionally, OpenG2P's implementation of OAuth and OpenID Connect offers the option to seamlessly connect with Identity platforms such as MOSIP (Modular Open Source Identity Platform). This integration empowers OpenG2P to leverage established identity systems, enabling beneficiaries and users to authenticate securely using their MOSIP credentials. By bridging the gap between OpenG2P and MOSIP, this feature enhances security, reduces authentication friction, and fosters a unified and trusted user experience. This also extends the usage of bio-metric and VC (Verifiable Credentials) based authentications.

## Encryption and data protection

* **Data Encryption**: OpenG2P utilizes Odoo's data encryption protocols to secure data transmission between users' browsers and the server, safeguarding beneficiary data during communication.
* **Database Encryption**: Sensitive beneficiary data stored in the database is encrypted using established encryption algorithms, providing an additional layer of protection.
* **Attachment Security**: Files and attachments uploaded to OpenG2P are securely stored in an S3 bucket and accessed only by authorised users, with unauthorised data exposure.
* **PII Encryption:** OpenG2P has a [privacy module](https://github.com/OpenG2P/openg2p-security) for the registry which encrypts all the PII information stored in the database.

Encryption of data is achieved with production-grade Key Manager module. Learn more >>

## Secure input handling

Input security is handled in the following ways:

* Input validation
* Memory safe programming language (Python)
* Type safe programming using Python Pydantic
* ORM capabilities to avoid SQL Injection threats

## Document Encryption

The Document Encryption module in OpenG2P safeguards all documents uploaded to the registry through secure encryption. This functionality protects sensitive data using advanced encryption techniques, reliable key management, and stringent access controls. Key features include:

* **Complete** **End-to-End Encryption:**
  * Documents are automatically encrypted before being stored, whether in the database or an S3 bucket.
  * Encryption is conditional based on registry settings, ensuring flexibility and compliance with system configurations.
* **Key Management:**
  * OpenG2P utilizes a secure and reliable Key Manager module to manage encryption keys efficiently.
  * The Key Manager ensures keys are safely stored, periodically rotated, and accessed securely.
* **Secure** **Decryption**:
  * Only authorized users with valid permissions can access and see decrypted documents.

## Secure deployment

OpenG2P offers support for Kubernetes-based production grade deployment with security features like [Wireguard](https://www.wireguard.com/), [Istio](https://istio.io/), access control, traffic control etc. [Learn more >>](/broken/pages/tDNeRfLR3IBWdGnZI5X1)



5. Rights of the Users (consent taken, withdraw consent, update information) :&#x20;

User login is provided to update information. OpenG2P uses OpenID connect (OIDC) interface an authentication protocol that verifies user identities, only the user is giving consent and also can update data on the social registry. Withdrawal of consent is planned for future implementation.&#x20;

\
6\. Data Retention&#x20;

The OpenG2P platform allows data retention for as long as the scheme requires and is goal oriented. Upon request, the administrator can remove data, we do not have a policy as such to remove data, but can be customised as per the policy of the country or department.



7. Grievance Redressal&#x20;

Our Legal Counsel is our designated grievance officer, and may be contacted through the following means:

Email: conduct@openg2p.org\
Address: 26/C, Electronics City,\
Hosur Road, Bangalore - 560100\
Phone: +91 80 4140 7777/ 2852 7627

## FAQ

<details>

<summary>OpenG2P is an open-source software. How secure is it?</summary>

In general, for any product, security is handled at multiple levels.

* Product security features

We have privacy and security features embedded in our product and we are constantly striving to add more such features. Please refer to the above note.

OpenG2P is built over Oodo ERP which was elected as the best secure open-source ERP by OWASP in 2021. This is because of the extensive work by the community on the underlying platform. OWASP is the largest security reporting system in the world.

OpenG2P has adopted all the best practices of Oodo. OpenG2P has also adopted the GitHub security validation and has been regularly scanned by GitHub for dependency security.

* Deployment of secure infrastructure

While deployment infrastructure is a choice of the implementer/system integrator we offer secure [production-grade deployment reference architecture](../deployment/) for implementors. This secure infra comprising of Kubernetes, Wireguard, Istio etc offers a high level of data and access security.

* Security policies and processes

OpenG2P team can help review security policies defined by the government/system Integrator.<br>

</details>
