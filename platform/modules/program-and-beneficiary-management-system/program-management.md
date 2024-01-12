# Program Management

## Introduction

OpenG2P platform's program management enables program managers to define and manage multiple programs. The program managers can

* Define and manage multiple programs
* Manage program lifecycle&#x20;
* Target both individual and groups&#x20;
* Define program disbursement cycles

## Program lifecycle

\<diagram>

## Program configurations

A program is composed of various managers, each of which configures the parameters for a specific program management process such as eligibility determination, deduplication, and entitlement. The diagram below shows the relationships of these managers with the program.

\<image to be incorporated>

## Multiple programs

* Define and configure multiple programs
* Data source for these programs
* Control of each of the programs -- role base access control

## Program disbursement cycles

### Eligibility criteria

Program administrators configure eligibility criteria to enroll the eligible registrants in the program. OpenG2P Eligibility Managers provide these functions:

<table><thead><tr><th width="194">Function</th><th>Description</th></tr></thead><tbody><tr><td>Domain filters</td><td>OpenG2P supports a variety of domain filters to set criteria for age, gender, household size, composition, and location. Program administrators can use these filters to define eligibility criteria.</td></tr><tr><td>Proxy Means Test</td><td>The Proxy Means Test (PMT) is considered the most effective approach to reduce the error of exclusion. PMT is available as a separate plug-in in the OpenG2P platform. Using this plug-in, Program administrators can configure the regression analysis formula.</td></tr><tr><td>Computed fields</td><td>Computed fields are a powerful tool for abstracting information from a set of fields. Program administrators can use these fields in PMT and domain filters to configure complex eligibility criteria.</td></tr></tbody></table>

### Deduplication criteria

The OpenG2P registry allows multiple entries for the same registrant. Hence once the registrants are enrolled in the program as beneficiaries, they should be deduplicated. OpenG2P Deduplication Managers can deduplicate the beneficiaries based on foundational/functional IDs, and phone numbers.

### Program cycles

Social benefit delivery programs for unemployment benefits, pensions, and scholarships are cyclic in nature and disburse payments in multiple cycles. Using OpenG2P Program Manager and Cycle Manager, the program administrators can create multiple cycles and disburse benefits.

### Entitlements

Program administrators can use OpenG2P Entitlement Manager to configure all the aspects related to beneficiary entitlement. OpenG2P Entitlement Manager provides these configurations:

<table><thead><tr><th width="230">Configuration</th><th>Description</th></tr></thead><tbody><tr><td>Entitlement amount</td><td>Program administrators can configure entitlement amount, currency, and transfer fee. Further, the entitlement amount for each individual in a group and the maximum number of individuals in the group can be configured.</td></tr><tr><td>Entitlement vouchers</td><td>An entitlement voucher authorizes the intended beneficiary to claim the benefits at the service provider facility. The voucher has customized QR codes embedded. The QR code provides a digital signature that makes the voucher tamper-proof and establishes the authenticity of the voucher.</td></tr><tr><td>Multi-stage approvals</td><td>Program administrators can configure multiple stages and assign a role for each stage to avoid concentration of power and errors in deciding the entitlement amount</td></tr></tbody></table>

### Notifications

The beneficiaries can be notified (not shown in the diagram above) when they are entitled to benefits. OpenG2P platform provides Notification Managers that can be configured to send SMS, email, and Fast2SMS notifications to the beneficiaries. These notifications can be customized using templates. To learn more, click [here](notifications.md).
