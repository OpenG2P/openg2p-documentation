---
description: Technical design
---

# Record level permissions

### Strategic Implementation - Full Solution

A comprehensive solution leveraging both IAM and Registry platforms to implement record-level permissions. The solution integrates data policy management, user-policy assignments, and runtime filtering across multiple systems.

#### Architecture Overview

The strategic implementation involves three key layers:

1. **Data Policy Definition Layer** (Registry)
2. **User-Policy Assignment Layer** (IAM)
3. **Data Access Control Layer** (Registry)

***

#### Registry Platform

**Data Policy Model**

**Table: g2p\_registry\_data\_policies**

| Field                      | Type   | Description                       |
| -------------------------- | ------ | --------------------------------- |
| policy\_id                 | UUID   | Primary key                       |
| policy\_mnemonic           | String | Policy identifier/name            |
| policy\_description        | String | Description of the policy         |
| register\_id               | UUID   | Associated register               |
| policy\_type               | ENUM   | ALLOW or DISALLOW                 |
| policy\_filter\_expression | JSON   | Filter expression for data access |

**Policy Filter Expression Schema**

The `policy_filter_expression` is a JSON structure supporting complex, nested filtering logic:

```json
{
  "type": "GROUP",
  "operator": "AND|OR|NOT",
  "children": [
    {
      "type": "CONDITION",
      "field_id": "field_name",
      "operator": "EQ|IN|GT|LT|GTE|LTE|BETWEEN",
      "value": "value",
      "values": ["value1", "value2"]
    }
  ]
}
```

**Registry APIs**

| API            | Purpose                              |
| -------------- | ------------------------------------ |
| get\_policies  | Retrieve data policies from Registry |
| add\_policy    | Create a new data policy in Registry |
| remove\_policy | Delete a data policy from Registry   |

**Data-Policy Middleware**

A new Data-Policy middleware layer is introduced in the Registry Platform to handle record-level access control:

* **Policy Parsing:** Parses data policies from user access tokens and retrieves corresponding filter expressions from the g2p\_registry\_data\_policies table
* **REGISTER-Specific Filtering:** Applies REGISTER-specific filters defined in the data policies to all SEARCH API operations
* **Overarching Filters:** These filters are overarching controls that apply uniformly to all users with the assigned data policies
* **User Control Restriction:** Users have no control over these filters - they are enforced at the middleware level and cannot be bypassed or modified by user-level operations
* **Filter Evaluation:** Evaluates complex filter expressions against registry records to determine which records a user can access based on their assigned data policies
* **Seamless Integration:** Operates transparently within the SEARCH API call chain without requiring changes to application code

***

#### IAM Platform

**IAM-Staff-Portal-UI Application**

A comprehensive UI application called **IAM-Staff-Portal-UI** bound to **IAM-Staff-Portal-API** for API support. This application serves as the central management portal for roles, permissions, data policies, and user assignments.

**Menu 1: Applications**

* **Browse Applications:** Display a list of applications (Farmer-Registry, National-Social-Registry, PBMS, G2P-Bridge, etc.)
* **Application Detail View:** Click on each application to access a detailed view with the following tabs:
  * **Tab 1 - Roles:** View and add new roles for the application
  * **Tab 2 - Permissions:** View permissions for the application (no add capability)
  * **Tab 3 - Role-Permission Mapping:** Search and filter roles to view all permissions linked to a specific role. Add new mappings between existing roles and existing permissions
  * **Tab 4 - Data Policies:** List all data policies published by the application. Click on each policy to view the complete policy definition. Applications provide standard APIs to publish a list of policies

**Menu 2: Users**

* **Realm Selection:** Browse realms from IAM - Staff, Beneficiaries, Agents (displayed as filter on top)
* **User List:** Display all users for the selected realm
* **User Detail View:** Click on a user to view detailed user information fetched from ID-Provider
* **Data Policy Assignment:** Add one or multiple data policies as user attributes to a single user
* **Multiple Policy Support:** Users can have multiple data policies assigned across different applications

**KeyCloak User Data Policies**

* **Storage Location:** User-Data-Policies are persisted only in KeyCloak, not in Registry or IAM-Staff-Portal database
* **Retrieval Mechanism:** IAM-Staff-Portal-UI fetches user-data-policies from KeyCloak to display current assignments
* **Persistence Mechanism:** IAM-Staff-Portal-UI stores user-data-policy assignments back to KeyCloak user attributes

**User Data Policies JSON Structure (Stored in KeyCloak)**

```json
[
  {
    "farmer-registry": [
      "policy-1",
      "policy-2",
      "policy-3"
    ]
  },
  {
    "social-registry": [
      "policy-11",
      "policy-12",
      "policy-13"
    ]
  }
]
```

Structure: A list of applications, where each application contains a list of associated data policies assigned to the user.

**End-to-End Flow**

1. **Policy Management:** Data policies are defined in Registry. When assigning users to data policies in IAM-Staff-Portal-UI, the UI invokes Registry APIs to retrieve available data policies for each application. IAM-Staff-Portal-UI facilitates user-to-data-policy mappings across all applications but does not store the data policies themselves.
2. **User-Policy Mapping Publication:** User-to-data-policy mappings are published to KeyCloak as custom user attributes in JSON format, mapping application names to their respective assigned policies.
3. **Token Generation:** KeyCloak protocol mappers include these custom user attributes in the access token based on the configured protocol mapper definitions.
4. **Registry Consumption:** Registry receives the access token with user-assigned data policies and applies corresponding filters on SEARCH API operations based on the policy filter expressions.

***

### Tactical Implementation - Current Release (1.2.0)

The tactical implementation provides an immediate, pragmatic approach to implementing record-level permissions by leveraging existing KeyCloak infrastructure and introducing minimal new components.

#### Registry Platform

Data Policy Definition and Model are as described in the Strategic Implementation section. The Registry platform defines and manages data-policies using the g2p\_registry\_data\_policies table with the policy filter expression schema.

**Publishing Data Policies to KeyCloak**

* **Publication Mechanism:** Data policies are published from Registry to KeyCloak as "ROLES" with a "DP\_" prefix
* **Prefix Convention:** "DP\_" prefix is used to distinguish data policy roles from functional roles (e.g., DP\_policy-1, DP\_policy-2)
* **Purpose:** This allows data policy roles to coexist with functional roles in the same role-based system

**Role Integration with Access Token**

* **Token Inclusion:** Data policy roles (DP\_ prefixed) travel with the access token as already in place for functional roles
* **Standard Flow:** Users assigned to data policies in KeyCloak receive these roles in their access tokens upon login

**Privilege Middle Layer Separation**

* **Current Behavior:** The existing privilege middle layer in Registry only processes roles that do NOT have the "DP\_" prefix
* **Scope:** Only functional roles are evaluated by the current privilege middleware
* **Unaffected:** This ensures backward compatibility with existing permission checks

**New Data Policy Middle Layer**

* **Purpose:** A new dedicated middle layer processes "DP\_" prefixed roles from the access token
* **Filter Application:** This layer identifies which data policies are assigned to the user
* **Search API Integration:** Applies the filter expressions defined in the corresponding data policies to the SEARCH API

**Search API Filtering**

* **Filter Lookup:** Retrieves the policy definition from g2p\_registry\_data\_policies based on policy roles in the token
* **Filter Expression Evaluation:** Evaluates the policy\_filter\_expression against the REGISTER associated with the policy
* **Record-Level Access:** Only returns records that match the filter conditions to the user
* **Multiple Policies:** If a user has multiple policies, applies all applicable filters (union/intersection based on policy configuration)

**Registry APIs**

| API            | Purpose                              |
| -------------- | ------------------------------------ |
| get\_policies  | Retrieve data policies from Registry |
| add\_policy    | Create a new data policy in Registry |
| remove\_policy | Delete a data policy from Registry   |

***

#### IAM Platform

**KeyCloak Role Management**

* **Data Policy Role Creation:** Data policy roles are created in KeyCloak by Registry with the "DP\_" prefix
* **User Role Assignment:** IAM administrators can assign "DP\_" prefixed roles directly to users in KeyCloak
* **Realm Support:** Three realms are supported - Staff, Beneficiaries, Agents

**Data Policy Storage in KeyCloak**

* **User Attributes:** User-data-policy assignments are stored as user attributes in KeyCloak (not in IAM or Registry databases)
* **JSON Structure:** Multiple policies per user are stored in JSON format as user attributes
* **Token Claims:** Assigned data policies appear as role claims in the access token
