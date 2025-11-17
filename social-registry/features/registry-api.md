# Registry API

The Registry API serves as the central gateway for all external and internal interactions with the OpenG2P Registry. It enables seamless data exchange between the Registry and connected systems - such as digital data collection tools, program management systems, and beneficiary portals. Through standardized and secure endpoints, the API ensures consistent handling of registrations, program enrollments, and change requests, maintaining data integrity across the entire beneficiary lifecycle.



### Registry interaction modes

In the OpenG2P Registry, external systems can interact through APIs in three primary ways — Registration, Program Enrollment, and Change Requests. These represent the different entry points for data coming into the Registry from various external sources or systems.

Regardless of the interaction type, all submissions follow the same approval workflow — ensuring that data undergoes validation, review, and approval before becoming part of the authoritative Registry.

#### **1. Registration**&#x20;

Registration is the process of submitting a new record to be added to the Registry. This typically represents a complete set of information about an individual or household, often collected through digital data collection tools or other national systems.

**Purpose**:

To onboard a new individual or household into the Registry with all relevant demographic, socioeconomic, and supporting document information.

**Key Characteristics:**

* Involves a full data submission, not a partial update.
* May include multiple sections such as identification details, household members, socioeconomic indicators, and contact information.
* Often accompanied by supporting documents such as ID cards, proof of residence, or income certificates.

Upon successful validation, the Registry assigns a unique Social ID (for individuals) or Household ID (for households).

#### **2. Program Enrollment**

Program Enrollment refers to the process of submitting beneficiary applications that are specifically intended for enrollment into a program or scheme configured within the Program Benefit Management System (PBMS).

These enrollments are typically captured through surveys, assisted form submissions, or direct beneficiary applications, depending on the operational setup of the program. Although these forms correspond to a program defined within PBMS, the actual beneficiary applications are first received and stored within the Registry — often referred to as the Application Registry.

**Purpose**:

To capture and manage applications for specific programs or schemes, ensuring that all beneficiary-related submissions are centralized within the Registry before PBMS processing begins.

**Key Characteristics:**

* Each enrollment submission is linked to a particular program or scheme defined in PBMS.
* The submitted application data (and supporting documents) is stored in the Registry to serve as the source of truth.
* Once an application enters the Registry, PBMS interacts with it to:
* Check eligibility based on program criteria.
* Prepare entitlements for approved beneficiaries.
* Execute benefit disbursement through the payment system.
* Throughout this lifecycle, PBMS continuously updates the Registry with the current status of the application and stages of the benefit transfer (e.g., verified, approved, paid, etc.).
* This two-way interaction ensures data consistency between the Registry and PBMS while maintaining a full audit trail of beneficiary enrollment and payment activity.\


#### 3. Change requests&#x20;

Change Requests represent the way in which a beneficiary — either directly or through an authorized agent or staff member — can request an update to an existing record in the Registry.

These requests ensure that beneficiary information remains current and accurate as circumstances change over time. Examples include updating demographic, socioeconomic, or supporting document information.

**Purpose :**

To allow beneficiaries to submit updates or corrections to their existing records in a controlled and auditable manner.

**Key Characteristics:**

* Initiated by the beneficiary or by a designated field staff, or service agent acting on their behalf.
* Used for updates such as:
* Updating income details when the economic status changes.
* Changing address after relocation.
* Adding or replacing documents, such as new ID proofs or utility bills.
* Each request is reviewed through the standard approval workflow before being applied to the main Registry record.
* Maintains full traceability, with every change logged and versioned for audit purposes.
* Ensures data integrity and governance across the lifecycle of a beneficiary’s record.



### User categories

The OpenG2P Registry supports interaction from different types of users, each playing a specific role in the management, verification, and maintenance of registry data. These users can be broadly categorized into Staff, Partners, Agents, and Beneficiaries.

Each category has distinct responsibilities, levels of access, and modes of interaction — ranging from data entry and validation to self-service updates and program enrollment.

#### **1. Staff**

Staff refers to government or institutional personnel who are directly responsible for managing registry operations.

They usually have administrative or supervisory privileges and operate from within the official systems or portals.

**Typical Roles:**

* Data verification and approval
* Oversight of registration, enrollment, and change request workflows
* Managing user roles and permissions
* Reviewing and resolving exceptions or data quality issues

**Mode of Interaction:**

* Through web-based administrative dashboards or back-office systems.
* Typically authenticated via secure identity providers (e.g., Keycloak or Single Sign-On).\


#### 2. Partners

Partners include organizations or systems that integrate with the Registry through APIs to share or consume data.

They are typically external stakeholders such as National ID authorities, payment service providers, or program management systems (PBMS).

**Typical Roles:**

* Submitting or synchronizing data (e.g., registration, enrollment, or updates).
* Consuming validated data for downstream processes like payments or eligibility checks.
* Posting back status updates and transaction outcomes to maintain data consistency.

**Mode of Interaction:**

* Through API-based system integrations with proper authentication and authorization.

#### 3. Agents

Agents act as intermediaries who assist beneficiaries in interacting with the Registry.

They often represent field-level staff, enumerators, or service center operators working on behalf of a government department or partner organization.

**Typical Roles:**

* Supporting beneficiaries in registration, program enrollment, or change requests.
* Collecting data through assisted digital forms or mobile applications.
* Verifying beneficiary identity and attaching supporting documents.

**Mode of Interaction:**

* Through mobile data collection tools, assisted service portals, or agent dashboards.
* Operate under authentication and role-based access control managed by the system administrator.\


#### 4. Beneficiaries

Beneficiaries are the primary subjects of the Registry — individuals or households whose information is maintained within it.

They may also interact directly with the system, especially in environments that support self-service portals or mobile applications.

Typical Roles:

* Submitting personal or household information during registration.
* Applying for program enrollment or benefits.
* Requesting changes to their existing records (e.g., address updates, document replacements).

Mode of Interaction:

* Directly through mobile apps, web portals, or assisted service channels.
* Often require identity verification (e.g., OTP, National ID, or biometric).



#### Registry add and update interfaces - Table

| Typical Users       | Interface Type     | Add (New Record through CR) | Update (Change Request) | Connectivity     |
| ------------------- | ------------------ | --------------------------- | ----------------------- | ---------------- |
| Partner systems     | API Interface      | True                        | True                    | Online           |
| Staff, Admins       | Web Portal         | True                        | True                    | Online           |
| Agents, Enumerators | Agent Portal       | True                        | True                    | Offline / Online |
| Beneficiaries       | Beneficiary Portal | True (limited)              | True                    | Online           |



### Layers of Registry API

All user types and interface channels — whether through staff portals, partner integrations, agent tools, or beneficiary applications — ultimately interact with the Registry through well-defined APIs.

The OpenG2P Registry architecture separates these APIs into different logical components to ensure clear boundaries, role-based access, and security isolation between different kinds of interactions.

Each API component serves a specific user or system category while maintaining consistent interaction with the core registry data model and approval workflows.



| API Component                                            | Primary Users / Systems                                       | Purpose                                                          | Typical Use                                                                                      |
| -------------------------------------------------------- | ------------------------------------------------------------- | ---------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| <mark style="color:orange;">openg2p-registry-core</mark> | <mark style="color:orange;">Internal registry services</mark> | <mark style="color:orange;">Core registry data management</mark> | <p><mark style="color:orange;">Foundational service used by other components.</mark><br><br></p> |
| openg2p-registry-partner-api                             | External partner systems (PBMS, NID, PSP)                     | System-to-system data exchange                                   | Submit/fetch registrations, enrollments, and updates                                             |
| openg2p-registry-bene-portal-api                         | Beneficiaries                                                 | Direct citizen interaction                                       | Self-registration and change requests                                                            |
| openg2p-registry-agency-portal-api                       | Agents and agencies                                           | Assisted beneficiary services                                    | Agent-led registration and program enrollment                                                    |
| openg2p-registry-staff-portal-api                        | Registry staff and administrators                             | Operational management                                           | Review, verification, and approval workflows                                                     |



### Form.io

Form.io is used within the OpenG2P Registry to design, manage, and render dynamic data collection forms. It provides a flexible, form-based interface that powers various types of submissions — including Registry forms, Program Enrollment forms, and Change Request forms.

By using Form.io, OpenG2P ensures a configurable and extensible form management layer, allowing administrators to modify or create forms without altering the underlying application code. This enables rapid adaptation to changing program requirements and data models.



#### Data flow for registry update - Registration

{% embed url="https://miro.com/app/board/uXjVJsjtI5o=/?share_link_id=971612514795" %}

Registration forms are hosted within the Registry as core data collection forms used to onboard new individuals or households. Unlike program applications, these forms are not associated with any specific program in PBMS. They are designed to capture and maintain the foundational demographic and socioeconomic information within the Registry.

Each registration form is created and managed in the Registry backend using Form.io, allowing administrators to define or modify the structure of the form — including fields, validation rules, and document requirements — without changing the underlying application code.

Upon submission, the completed form is recorded in the Registry as a Change Request (CR). This CR then goes through the validation and approval workflow configured in the system to ensure completeness and correctness of the submitted data.

Once validated and approved, the Registry assigns a Unique ID (for example, a Unique Social ID or Household ID), establishing the record as part of the centralized beneficiary dataset. This serves as the authoritative source of demographic and socioeconomic information that other systems — including PBMS — rely on for program enrollment and benefit delivery.



#### Data flow for registry update - Program Enrollment

{% embed url="https://miro.com/app/board/uXjVJtL8784=/?share_link_id=816159461605" %}

Forms for various programs will be hosted within the Registry as a separate application module called “Program Applications.”

By design, the PBMS does not manage or store any beneficiary demographic information. All beneficiary data will therefore be maintained centrally within the Registry. The PBMS will interact with the Registry to update application statuses and disbursement states, ensuring a unified and centralized view of beneficiary information.

Program-specific forms are created in the Registry backend using Form.io, and each form is linked to the corresponding program in PBMS through its unique program mnemonic.

When rendering program forms, the Beneficiary Portal or any other assisted mode applications will retrieve the relevant form from the Registry based on the associated program.

Upon submission, the completed form is recorded in the Registry as a Change Request (CR). This CR then proceeds through the defined approval workflow within the Registry, ensuring that all submissions are validated and approved before becoming part of the central beneficiary data.



#### Data flow for registry update - Change Request

{% embed url="https://miro.com/app/board/uXjVJtdSE08=/?share_link_id=377290230238" %}

Change Requests (CRs) represent the mechanism through which a beneficiary — either directly or through an authorized agent or staff member — can request an update to an existing record in the Registry.

These requests ensure that beneficiary information remains current, accurate, and reflective of real-world conditions as circumstances evolve over time. A Change Request may involve updates to demographic details, socioeconomic status, address, land ownership information, education level, income data, or supporting documents.

Each change request is configured and managed in the Registry backend using Form.io, which enables administrators to define forms and workflows for different update scenarios without modifying application code.

Upon submission, the request is recorded in the Registry as a CR entry and proceeds through the approval workflow configured for the respective registry module.&#x20;

Once approved, the updates are merged into the existing beneficiary record, ensuring that the Registry remains the single, authoritative source of truth for all beneficiary information across integrated systems such as PBMS and other national registries.
