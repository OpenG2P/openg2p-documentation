---
description: g2p_register_sections
---

# G2PRegisterSection

The [`g2p_register_sections`](https://github.com/OpenG2P/registry-platform/blob/develop/core/openg2p-registry-core/src/openg2p_registry_core/models/g2p_register_sections.py) table defines **sections within a tab of a register**. Each tab can contain one or more sections, where each section represents a **logical grouping of related attributes**.

Examples of sections include:

* Personal Profile
* Educational Qualifications
* Employment Details
* Income Details

Sections are the **primary unit of modification** within a register. During edit operations, **only one section can be modified at a time**.

Any modification to a section creates a **Change Request (CR)**. The change request must undergo **verification and approval** before the changes are written to the corresponding **REGISTER** or **PROGRAM\_REGISTER** dataset.

***

## Attributes

| Attribute                 | Description                                                                       |
| ------------------------- | --------------------------------------------------------------------------------- |
| **section\_id**           | Primary key of the table. Uniquely identifies a section across the platform.      |
| **register\_id**          | Identifier of the register to which this section belongs (for display in the UI). |
| **tab\_id**               | Identifier of the tab under which this section appears.                           |
| **section\_register\_id** | Specifies the underlying dataset that the section operates on.                    |

***

## Section Data Source

The **`section_register_id`** determines the dataset that provides the data for the section.

Example scenario:

* A **Household Register** contains a tab showing **Individuals belonging to the household**.
* Within that tab, there may be a **section displaying the list of individuals**.

In this case:

* `register_id` → Household Register (used for display context)
* `section_register_id` → Individual Register (actual data source)

If the data shown in the section belongs to the same register in which the section appears, then:

```
section_register_id = register_id
```

#### Cross-Register Editing Rules

If `section_register_id` refers to another **REGISTER** (not a TABLE), the section becomes **display-only**.

The platform **does not allow cross-register modifications**.

For example:

* A Household Register may display Individuals belonging to the household.
* However, edits to Individual records must be performed within the **Individuals Register** itself.

The platform **does allow modifications to TABLE datasets** from within the parent register.

***

## Section Lifecycle Attributes

| Attribute                | Description                                                                                                                                                          |
| ------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **is\_primary\_section** | Indicates that the section is the **primary and mandatory section** required for creating a record in the register. A record cannot be created without this section. |
| **section\_order**       | Defines the order in which sections appear within a tab.                                                                                                             |
| **section\_mnemonic**    | Unique name used to identify the section within the platform.                                                                                                        |
| **section\_description** | Describes the purpose and contents of the section.                                                                                                                   |

***

## Intake Form Behavior

When an **intake form** contains multiple sections:

1. Submitting the intake form creates **Change Requests for each section**.
2. The **primary section** is processed first.
3. Once the intake submission is approved, the associated **change requests are automatically approved**.

This process ensures that the record is created only after the mandatory section has been validated.

***

## Document Requirement Configuration

| Attribute               | Description                                                                                                                    |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **documents\_required** | Boolean flag indicating whether **documentary evidence** must be submitted when creating or modifying records in this section. |

When this flag is enabled, the UI allows users to upload **supporting documents** as proof for the claims made in the section.

***

## Verification Configuration

| Attribute                           | Description                                                                                                          |
| ----------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| **no\_of\_verifications\_required** | Specifies the number of independent verifications required before a change request for this section can be approved. |

This allows the platform to support **multi-level verification workflows** for sensitive information.

***

## UI Configuration

| Attribute    | Description                                                                                |
| ------------ | ------------------------------------------------------------------------------------------ |
| **is\_list** | Indicates whether the section represents **multiple records** for a given register record. |

Example:

An Individual may have multiple **Public Utility Subscriptions**.\
In such cases, the section listing the subscriptions would have:

```
is_list = TRUE
```

***

#### `section_ui_schema`

This attribute contains a **JSON schema that defines how the UI should render the section**.

The schema describes how the section should behave in:

* **View mode**
* **Edit mode**

The Registry UI dynamically renders the section interface using **React components** based on this JSON schema.

This metadata-driven approach allows UI changes without modifying frontend code.

***

## Change Request Auto-Approval Configuration

The following attributes control whether **change requests generated from different operational channels** are automatically approved.

| Attribute                                 | Description                                                                        |
| ----------------------------------------- | ---------------------------------------------------------------------------------- |
| **cr\_auto\_approve\_for\_bene\_portal**  | Auto-approve change requests originating from the **Beneficiary Portal**.          |
| **cr\_auto\_approve\_for\_agent\_portal** | Auto-approve change requests originating from the **Agent Portal**.                |
| **cr\_auto\_approve\_for\_staff\_portal** | Auto-approve change requests originating from the **Staff Portal**.                |
| **cr\_auto\_approve\_for\_partner**       | Auto-approve change requests originating from **Partner systems or integrations**. |

If the value is **FALSE**, the generated change request must be **manually verified and approved** before the changes are applied to the register.

## Reference Implementation

Database scripts for g2p\_register\_sections for a Reference Farmer Registry are available [here](https://github.com/OpenG2P/farmer-registry/blob/develop/farmer-extension/src/openg2p_registry_farmer_extension/db_scripts/register-metadata/g2p_register_sections.sql).
