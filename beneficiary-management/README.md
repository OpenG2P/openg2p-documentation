# 🅿 Program Management

## Introduction <a href="#introduction" id="introduction"></a>

OpenG2P platform's program management is a sequence of processes encompassing program creation to deciding entitlement for the beneficiaries. Digitalization of these processes offers multiple benefits such as ease of administration, agility of operations, and data empowerment to name a few.

{% hint style="warning" %}
## Program management challenges <a href="#program-management-challenges" id="program-management-challenges"></a>

OpenG2P platform's program management module is built to solve the challenges faced by program administrators in their day-to-day operations. Some of the common challenges are:

**Error of exclusion**

The error of exclusion usually happens during registrants' enrollment. For example, a first come first serve approach is easy to monitor and audit, but it may favour registrants with better awareness, approach, and access. Furthermore, beneficiaries' income, household size and composition, address, etc. can change over time, but they may not be deemed eligible due to the lack of regular updates.

**Implementing a progressive approach**

A progressive approach works towards the betterment of beneficiaries in the long term. One example is an unemployment assistance program encompassing training, skill development, and job assistance instead of handing out cash benefits to unemployed registrants. This approach is challenging to implement as multiple programs should be monitored in parallel.

#### Categorical targeting

Often, program administrators need to target populations from a specific geographic location, people with debilitating disabilities, or people above/below a certain age. Administrators need filtering criteria to glean this information from existing registry records instead of conducting another costly and time-consuming registration drive.

**Deciding the entitlement amount**

Depending upon the beneficiaries' profile, the benefit amount may vary. Determining eligibility and entitlement often requires different information. For example, a program for child nutrition may enrol two families based on total income but may allot entitlement benefits based on the number of children.

**Monopoly in enrolment and entitlement**

Program enrolment and entitlement decisions can be monopolized by a single entity, and hence it is a good practice to digitize and distribute these decisions in a program.

#### Timely notifications

Not notifying beneficiaries about their enrolment and entitlement can leave them confused, and undermines credibility and transparency. This step is often neglected in administrative-driven systems.
{% endhint %}

## OpenG2P program management interface

OpenG2P platform has a backend office application for program administrators. The platform allows multiple programs to run in parallel. These programs enrol the registrants from the same registry database. Its program management module offers a rich set of functions for enrolment, eligibility criteria, program cycles, entitlement, and notifications.

## OpenG2P program management process

The figure below shows a high-level representation of the enrollment management process.

<figure><img src="https://github.com/smita-g2p/openg2p-documentation/raw/c68b3e6da99fe077e2cbe5d5fc166b3e3487fbce/.gitbook/assets/program-management-process.png" alt=""><figcaption></figcaption></figure>

### Eligibility criteria

Program administrators configure eligibility criteria to enrol the eligible registrants in the program. OpenG2P Eligibility Managers provide these functions:

#### Domain filters

OpenG2P supports a variety of domain filters to set criteria for age, gender, household size, composition, and location. Program administrators can use these filters to define eligibility criteria.

#### Proxy Means Test

The Proxy Means Test (PMT) is considered the most effective approach to reduce the error of exclusion. PMT is available as a separate plug-in in the OpenG2P platform. Using this plug-in, Program administrators can configure the regression analysis formula.

#### Computed fields

Computed fields are a powerful tool for abstracting information from a set of fields. Program administrators can use these fields in PMT and domain filters to configure complex eligibility criteria.

### Deduplication criteria

The OpenG2P registry allows [multiple entries](../secure-registry/registry.md#multiple-entries) for the same registrant. Hence once the registrants are enrolled in the program as beneficiaries, they should be deduplicated. OpenG2P Deduplication Managers can deduplicate the beneficiaries based on foundational/functional IDs, and phone numbers.

### Program cycles

Social benefit delivery programs for unemployment benefits, pensions, and scholarships are cyclic in nature and disburse payments in multiple cycles. Using OpenG2P Program Manager and Cycle Manager, the program administrators can create multiple cycles and disburse benefits.

### Entitlements

Program administrators can use OpenG2P Entitlement Manager to configure all the aspects related to beneficiary entitlement. OpenG2P Entitlement Manager provides these configurations:

#### Entitlement amount

Program administrators can configure entitlement amount, currency, and transfer fee. Further, the entitlement amount for each individual in a group and the maximum number of individuals in the group can be configured.&#x20;

#### Entitlement vouchers

An entitlement voucher authorises the intended beneficiary to claim the benefits at the service provider facility. The voucher has customized QR codes embedded. The QR code provides a digital signature that makes the voucher tamper-proof and establishes the authenticity of the voucher.

#### Multi-stage approvals

To avoid concentration of power and errors in deciding the entitlement amount, Program administrators can configure multiple stages and assign a role for each stage.

### Notifications

The beneficiaries can be notified (not shown in the diagram above) when they are entitled to benefits. OpenG2P platform provides Notification Managers that can be configured to send SMS, email, and Fast2SMS notifications to the beneficiaries. These notifications can be customized using templates. To learn more, click [here](notifications.md).

### Entity relationships in a program

A program is composed of various managers, each of which configures the parameters for a specific program management process such as eligibility determination, deduplication, and entitlement. The diagram below shows the relationships of these managers with the program.

&#x20;

<figure><img src="https://raw.githubusercontent.com/smita-g2p/openg2p-documentation/1.1/.gitbook/assets/program-management-entity-relationships.png" alt=""><figcaption></figcaption></figure>

Payment Manager is described in the [next section](../eligibility-and-enrolment/).
