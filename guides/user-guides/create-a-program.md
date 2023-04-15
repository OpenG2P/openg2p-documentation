# Create Program

## Description&#x20;

The guide here provides steps to create a new program. A program is typically created by a Program Manager who can create and administer programs.

## Pre-requisites

The user must have a Program Manager role. See [Create User and Assign Role](assign-roles-to-users.md) guide.

## Steps

1. Navigate to _Programs_ using the menu bar.

<figure><img src="../../.gitbook/assets/programs.png" alt=""><figcaption><p>Create a new program</p></figcaption></figure>

2. Click on the _Create Program_ to reach the Program creation page.  Provide Program name, target type and currency. There are tabs for the configuration of various managers.
3.  **Eligibility criteria:**

    <figure><img src="../../.gitbook/assets/program-creation-page.png" alt=""><figcaption><p>Configure eligibility criteria</p></figcaption></figure>
4. Use_+Add filter_ to set eligibility criteria using [Domain Filters](../../modules/program-management/eligibility.md#domain-filters). You may set multiple eligibility criteria.&#x20;
5.  **Cycle Manager:**  Set parameters of [disbursement cycles](../../modules/beneficiary-management/disbursement-cycles.md).

    <figure><img src="../../.gitbook/assets/cycle-manager.png" alt=""><figcaption></figcaption></figure>

    * _Auto-approve Entitlements:_ To set entitlements via rules, without any manual approvals.
    * _Approver Group:_ The group name of the user who has permission to approve cycles. See [Create User and Assign Role](assign-roles-to-users.md).
    * _Recurrence:_ The time period for the repetition of a cycle.
6.  **Entitlement Manager:**  Set parameters for [entitlements](../../modules/program-management/entitlement.md).



    <figure><img src="../../.gitbook/assets/entitlement-manager.png" alt=""><figcaption></figcaption></figure>

    * _Amount Per Cycle:_ The amount disbursement of a group or individual per cycle.
    * _Amount Per Individual In Group:_ Amount of disbursement per individual in a group when the program [target type](../../modules/beneficiary-management.md#target-types) is "group".
    * _Maximum number of individuals in a group:_  Maximum number of individuals who get disbursements per group (optional).
    * _Transfer Fee(%):_ Fee incurred for disbursement as a percentage of disbursement (optional).
    * _Transfer Fee Amount:_ Fee incurred for disbursement as an absolute amount (optional).
    * _Entitlement Validation Group:_ The group name of the user who has permission to approve entitlements. See [Create User and Assign Role](assign-roles-to-users.md).&#x20;
7. **Map Portal form:** Map a portal form to this program. [Create a portal form](https://app.gitbook.com/o/bnTr6Kp4z4CXR4QVIPSa/s/xkdlCOLME2p03rS8nG8u/\~/changes/168/guides/user-guides/create-portal-form) before this mapping. &#x20;
8. Click the _Next_ button to import the matching registrants to the creating program. In the pop-up window select _Yes_.

<figure><img src="../../.gitbook/assets/maching-registrants.png" alt=""><figcaption></figcaption></figure>

9. Once the program is created it will be listed under the program list view page.

