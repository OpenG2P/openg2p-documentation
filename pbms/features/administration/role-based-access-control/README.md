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

# RBAC

## Introduction

OpenG2P platform defines role-based access control (RBAC) to authorize its users. The user can access the views and menus of the OpenG2P platform based on their roles. RBAC also prevents unauthorized access to the OpenG2P system and safeguards beneficiary data from malicious actors.

### User types

OpenG2P platform has three types of users:

1. **Internal:** These users access the OpenG2P backend application.
2. **Portal:** These users access the portals created using the OpenG2P backend application, i.e. Self-Service Portal and Service-Provider Portal users. Access to these portals is governed by the administrative policies of the program.
3. **Public:** These users do not have any access to the OpenG2P backend application or portals.

### Pre-defined groups

In the OpenG2P platform, a role is implemented by defining a group, and the users playing the role are added to the group. Each user can be added to multiple groups. OpenG2P provides a large variety of pre-defined groups (roles). The users can be directly added to these groups (roles).&#x20;

{% hint style="info" %}
OpenG2P pre-defined group name start with the prefix OpenG2P. All the other groups are provided by underlying Odoo platform.
{% endhint %}

The commonly used roles pre-defined via groups in OpenG2P are:

* **Administrator:** The users in this group are system administrators and superusers who assign user access to other users in the OpenG2P platform. These users must install the Odoo platform on their machines, which will be used to provide access.
* **Registrar:** Every user who needs access to the registry views and menus should be assigned to this group.
* **Program Validator:** The users in this group validate the soundness of the program and duplicate registrants. Therefore, these users can access Programs->Programs and Programs->Duplicates view and menus.
* **Program Cycle Approver:** These users in this group approve the program cycles and have access rights to Program -> Cycles views and actions.
* **Program Manager:** The users in this group have access to all the menus, views, and actions related to program management, payments, account journals, and funds.
* **Finance Validator:** These users in this group have access to all the menus, views, and actions related to entitlement/fund/batch finance, program funds, and account journals.
* **Document Write, Document Read, Document Admin:** Registrants' documents, payment files, entitlement vouchers, etc. are stored in the storage configured by the administrators. To preserve privacy and enforce authorized viewing, these documents can only be accessed by authorized users who are part of these groups.
* **Rest API POST, Rest API GET:** The OpenG2P platform provides access to REST APIs for various functionalities. However, access to these APIs is restricted to only authorized users who are part of these groups.

The excel below describes all the OpenG2P pre-configured groups and their access permissions.

{% embed url="https://docs.google.com/spreadsheets/d/1uzIlr9XDG1qmKb2kRIIzLaWZLqC7Jf6_R4LnYMICzwM/edit?usp=sharing" %}

### Configuring custom groups

The administrators can also create custom groups from scratch or inherit from pre-defined groups. Inheriting from an existing group is the most effective way to create new groups as menus, views and access rights from the existing groups need not be redefined. After inheriting from existing groups, system administrators can add custom menus, views and access rights.

\<image to be incorporated>

The figure below shows the access rights for a group (role) that requires access to payment accounts.

\<image to be incorporated>

## Related links

[Create User and Assign Role](user-guides/assign-roles-to-users.md)
