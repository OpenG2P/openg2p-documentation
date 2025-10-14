---
layout:
  width: default
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
  metadata:
    visible: true
---

# Roles & privileges

Roles and Privileges in PBMS have been organized into two tiers

1. High Level Groups &
2. &#x20;Low Level Groups

High Level Groups - are groups created based on business functions. From an end-user perspective, department users (staff members) should be associated to the High Level Groups.

Internally, these high level groups are associated to one ore more low level groups. These low level groups in turn define RUCD (Read, Update, Create & Delete) access to the various Odoo Models.

The High Level Groups that are available for User Mappings are as follows

<table><thead><tr><th width="254.8662109375">High Level Group</th><th width="545.702392578125">Description</th></tr></thead><tbody><tr><td>Program Administration</td><td>Edit programs, add benefit codes, view service providers and geography, create enrolment and disbursement cycles and view lists inside them</td></tr><tr><td>Enrolment Operation</td><td>View &#x26; Create Enrolment Cycles<br>Create Beneficiary lists (enrolment lists) inside Enrolment Cycles</td></tr><tr><td>Enrolment Verification</td><td>Verify Enrolment lists and add observations (upload documents to support their observations)</td></tr><tr><td>Enrolment Approval</td><td>Approve a beneficiary list (enrolment list) as final list under an enrolment cycle</td></tr><tr><td>Disbursement Operation</td><td>View &#x26; Create Disbursement Cycles<br>Create Beneficiary lists (disbursement lists) inside Disbursement Cycles</td></tr><tr><td>Disbursement Verification</td><td>Verify Disbursement lists and add observations (upload documents to support their observations)</td></tr><tr><td>Disbursement Approval</td><td>Approve a beneficiary list (disbursement list) as final list under an enrolment cycle</td></tr><tr><td>Service Provider Operation</td><td>View and Create Agencies and Warehouses<br>Associate Benefit codes to Agencies and Warehouses<br>Associate Geographies to Agencies and Warehouses</td></tr><tr><td>Geography Operation</td><td>View and Create Administrative Areas (Large &#x26; Small)</td></tr><tr><td>Audit Operation</td><td>View Access to the entire PBMS application</td></tr><tr><td>Program Super Administration</td><td>Edit programs, add benefit codes, view service providers and geography, create enrolment and disbursement cycles and view lists inside them — BUT NOT RESTRICTED by PROGRAM ACCESS. This role has access to all the programs defined in PBMS.</td></tr></tbody></table>



