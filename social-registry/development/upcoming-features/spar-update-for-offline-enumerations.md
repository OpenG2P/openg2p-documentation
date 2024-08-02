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

# SPAR Update for offline enumerations

## Context

* SPAR would be included in every OpenG2P deployment case where payment is required.
* The financial address of individual beneficiaries need to be updated to SPAR for any transfer to happen.
* The possibility of beneficiaries using any means of Self Service for updating the financial service is meagre.
* SPAR is yet to have a admin UI to perform any directly update by the back-end users.
* Beneficiary data is enumerated using ODK form through ODK Collect app and then imported to social registry.
* Mobile money payments contribute the the lion share of DBT in Africa. &#x20;

## Functional Requirements

* Add financial addresses to SPAR for the data collected from the beneficiaries. This is applicable for both online and offline registration means.&#x20;
* &#x20;Admin/Backend users should be able to update (maintain) the financial addresses in SPAR based on beneficiary requests for amendment. There should be a UI to facilitate this requirement.
* Mobile Number that is used to disburse funds - may be a different number than that is used for communication. The payment mobile number should be separately collected during registration
* Payment related Financial Address (can be mobile number, email address or account number) - should be segregated from communication address information

## Initial Design Thoughts

**Ingest into SR**

1\. ODK Central - Poll and pull into SR - Offline Field Agents

2\. Admin UI based on Odoo - Department Users (online)

3\. Registration Portal based on Odoo - Field Agents / Enumerators (when online)

4\. Social Registry -- Self Service Portal - Non Odoo - based on FastAPI framework

**Possible Approach**

1. Data may come into SR - through any of the aforesaid 4 means
2. There will be a job in SR - that will update SPAR  - This job has to be a recovery proof job - means that if there is a failure in updation of SPAR, the job has to manage retries
3. The information in SR - will not be treated as TRUTH - but only a channel input - This means all subsequent referrals - whether the referral is from g2p-bridge or showing in the UI - this data will be fetched using SPAR lookup APIs
4. &#x20;SR will be registered as a partner for SPAR and the partner verification mechanism of JWT will hold good
5. The user privileges in SR - in terms of who can update Financial Information - is not relevant for SPAR. As far as SPAR is concerned, once the information comes into SR, SR  as an authorized partner system can invoke SPAR APIs
6. SR should manage the user roles and privileges for Financial Information - like it does for other attributes
7. Whether we use the Odoo queue or Kafka -- between SR and SPAR - is to explored during the design. FIFO - order of update to SPAR has to be ensured

&#x20;&#x20;
