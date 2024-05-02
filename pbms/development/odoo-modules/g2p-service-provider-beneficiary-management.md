---
description: WORK IN PROGRESS
---

# G2P Service Provider Beneficiary Management



{% embed url="https://www.figma.com/proto/35RyDtSlVe2kJFwPcxzCgo/SPP?node-id=363-937&starting-point-node-id=363:935" %}

{% @jira/embed url="https://openg2p.atlassian.net/browse/G2P-2182" %}

#### Module: g2p\_service\_provider\_beneficiary\_management

**Purpose:**

The "g2p\_service\_provider\_beneficiary\_management" module is designed to manage beneficiaries within a specific region, facilitating user interactions for both individuals and groups.

**Features:**

**Beneficiary Creation and Update:**

* Users can create new beneficiary profiles for groups within their assigned region.
* Update existing beneficiary information such as contact details, household data, demographics, and eligibility criteria.

**Group Management:**

* Allow users to maintain lists of beneficiary groups within a region.
* Add new groups and update group information, including members, contact information, and group demographics.
* Household Data (demographic data) should be static form in the portal and inside the group view, there should one more button for adding individual(as members).

**EDRMC Integration:**

Once the EDRMC package is installed, all household data specific to EDRMC form will be accessible. The beneficiary management system will inherit the base of the service provider portal.

**Details covered in the EDRMC form:**

1. **Household Head Details**
2. **Location Details**
3. **Household Data Questions**

Additionally, there will be a separate form for family members.



