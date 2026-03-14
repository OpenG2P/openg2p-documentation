---
description: Base registry models available in the platform
---

# Registry vs Register

#### Registry and Register Terminology

Within the OpenG2P platform, a deployed registry instance is referred to as a **Registry**, while the individual data stores (tables or models) that hold records are referred to as **Registers**.

The platform classifies registers into three categories, defined as enumerations in the [`g2p_register_metadata.py`](https://github.com/OpenG2P/openg2p-registry-gen2-core/blob/develop/openg2p-registry-core/src/openg2p_registry_core/models/g2p_register_metadata.py) file within the [`openg2p-registry-core`](https://github.com/OpenG2P/openg2p-registry-gen2-core) module:

* **REGISTER**
* **TABLE**
* **PROGRAM\_REGISTER**

***

#### REGISTER

A **Register** represents a formally managed record set within a registry and typically defines the core purpose of that registry. In essence, the primary function of a registry is to maintain and govern one or more registers.

Each register usually assigns a **functional identifier** to every record it contains. Examples include:

* **Farmer ID** in a Farmer Register
* **Household ID** in a Household Register
* **Vehicle ID** in a Vehicle Register

A single registry instance may contain multiple registers. For example, a **Household Registry** might include:

* A **Household Register** to manage households
* An **Individual Register** to manage the members belonging to those households

Registers are governed through **formal approval workflows**. Any modification to a record is treated as a **claim**, which must be supported by appropriate documentation. These claims are then subject to verification and approval by authorized registry personnel according to the registry’s governance processes.

#### TABLE

A **Table** is a supporting data structure used to store additional attributes related to records in a **Register**. Tables are typically used when a single record in a register needs to be associated with **multiple related records**.

For example, an **Individual Register** within a Household Registry may require a table to record the **public utility services** that an individual has subscribed to, such as:

* Electricity connections
* Water connections
* Internet subscriptions
* Library memberships

In such cases, multiple records in the table may be linked to a single record in the register.

Unlike registers, **tables do not assign functional identifiers to their records**. They exist solely to provide structured, supporting information for records stored in a register.

***

#### PROGRAM\_REGISTER

A **Program Register** is used to collect and manage **applications from individuals or households for a specific benefit program**.

Government or implementing agencies typically announce application windows for such programs, inviting eligible members of the population to apply within a defined **date range**. Applicants submit the required information along with supporting documentation to be considered as potential beneficiaries.

Similar to registers, records in a program register typically undergo **verification and approval workflows**, where submitted claims and documents are reviewed by authorized personnel.

Within OpenG2P, a **Program Register** commonly serves as the **base register for benefit programs managed by the Program and Benefit Management System (PBMS)**. Eligibility rules defined as part of the program configuration are evaluated against the records stored in the program register to determine which applicants qualify for benefits.

The following table provides a quick summary of these 3 categories.

<table><thead><tr><th width="130.671142578125">Aspect</th><th>REGISTER</th><th>TABLE</th><th>PROGRAM_REGISTER</th></tr></thead><tbody><tr><td><strong>Purpose</strong></td><td>Represents a formally managed register that defines the core purpose of a registry instance.</td><td>Stores supporting or repeating attributes related to records in a register.</td><td>Collects and manages applications from individuals or households for a specific benefit program.</td></tr><tr><td><strong>Typical Usage</strong></td><td>Core datasets such as Farmers, Households, Individuals, Vehicles, etc.</td><td>Supporting datasets linked to a register, often representing one-to-many relationships.</td><td>Application datasets used to capture requests to participate in a benefit program.</td></tr><tr><td><strong>Functional ID</strong></td><td>Each record is assigned a <strong>functional identifier</strong> (e.g., Farmer ID, Household ID).</td><td>No functional identifier is assigned to table records.</td><td>Will typically assign an <strong>Application ID</strong> or similar identifier to each submitted application.</td></tr><tr><td><strong>Relationship to Registry</strong></td><td>One or more registers typically define the primary scope of a registry instance.</td><td>Always linked to a parent register and cannot exist independently.</td><td>Typically associated with a specific program and may serve as the base dataset for program processing.</td></tr><tr><td><strong>Data Structure Pattern</strong></td><td>Usually represents <strong>primary entities</strong> managed by the registry.</td><td>Represents <strong>supporting or repeating attributes</strong> of a register record.</td><td>Represents <strong>applications or requests</strong> submitted by the population for a benefit program.</td></tr><tr><td><strong>Approval Workflow</strong></td><td>Changes to records are treated as <strong>claims</strong> and go through verification and approval workflows.</td><td>Typically does not have independent approval workflows; follows the parent register’s processes.</td><td>Applications undergo <strong>verification and approval workflows</strong> before eligibility determination.</td></tr><tr><td><strong>Example</strong></td><td>Household Register, Individual Register, Farmer Register.</td><td>Utility Connections Table, Education History Table, Contact Numbers Table.</td><td>Farmer Subsidy Application Register, Scholarship Application Register.</td></tr><tr><td><strong>Use in PBMS</strong></td><td>May provide the base population for programs.</td><td>Not directly used by programs.</td><td>Often used as the <strong>base register for Program and Benefit Management System (PBMS)</strong> eligibility evaluation.</td></tr></tbody></table>



