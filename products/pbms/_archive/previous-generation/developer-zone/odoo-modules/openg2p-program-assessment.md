# OpenG2P Program: Assessment

### Module name

g2p\_program\_assessment

### Module title

OpenG2P Program: assessment

### Technology base

Odoo

### Functionality

* The OpenG2P Program: Assessment module extends the functionality of the OpenG2P platform by introducing features related to program assessments and entitlements. This module enhances the management of program memberships and assessments, allowing for a more comprehensive evaluation of participants within G2P programs.

#### Key Features

#### Program Memberships

1. **Membership Assessment Wizard**: The module introduces a wizard for assessing program memberships. This wizard facilitates the evaluation of participants' progress and status within the program.
2. **Enhanced Views**: Views for program memberships are extended to accommodate additional assessment-related information, providing a holistic view of participants' engagement and progress.

#### Entitlement Management

1. **Entitlement Creation Wizard**: A wizard is available for creating entitlements, streamlining the process of defining the benefits and privileges associated with program participation.
2. **Entitlement Amount Validation**: The module includes JavaScript and back-end validation mechanisms to ensure accurate and valid amounts for entitlements, preventing discrepancies in benefit calculations.
3. **Entitlement Assessment Templates**: Assessment templates are provided to structure and document the evaluation criteria used for determining entitlement amounts.

#### Program Assessments

1. **Assessment Logging**: The module logs assessments associated with program memberships and entitlements. Assessments capture key information, including assessment date, author, and remarks.
2. **Assessment Copying**: The ability to copy assessments from previous entitlements, streamlining the assessment process and maintaining historical records.
3. **Assessment Templates**: Assessment templates are utilised to standardise the assessment process and ensure consistency across program participants.

#### Notifications and Logging

1. **Notification System**: The module includes a notification system to inform users about assessment results, membership status changes, and other relevant updates.
2. **Logging Mechanisms**: Extensive logging ensures that any changes, rejections, or failures in the assessment and entitlement processes are recorded for auditing and debugging purposes.

### Design notes

### Relationships with other entities

None

### Dependencies

Module Dependencies

* g2p\_program
* mail

### User interface

### Configuration

### Source code

[https://github.com/OpenG2P/openg2p-program/tree/15.0-develop/g2p\_program\_assessment](https://github.com/OpenG2P/openg2p-program/tree/15.0-develop/g2p\_program\_assessment)

### Installation

* Ensure that the required dependencies (`g2p_programs` and `mail`) are installed and configured.
* Install the "OpenG2P Program: Assessment" module using the Odoo Apps interface.
* Once installed, configure the module settings and access the new features via the Odoo interface.
