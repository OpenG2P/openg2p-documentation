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

### High Level Groups&#x20;

These are groups created based on business functions. From an end-user perspective, department users (staff members) should be associated to the High Level Groups.

Internally, these high level groups are associated to one ore more low level groups. These low level groups in turn define RUCD (Read, Update, Create & Delete) access to the various Odoo Models.

The High Level Groups that are available for User Mappings are as follows

<table><thead><tr><th width="249.63140869140625">High Level Group</th><th width="545.702392578125">Description</th></tr></thead><tbody><tr><td>Program Administration</td><td>Edit programs, add benefit codes, view service providers and geography, create enrolment and disbursement cycles and view lists inside them</td></tr><tr><td>Enrolment Operation</td><td>View &#x26; Create Enrolment Cycles<br>Create Beneficiary lists (enrolment lists) inside Enrolment Cycles</td></tr><tr><td>Enrolment Verification</td><td>Verify Enrolment lists and add observations (upload documents to support their observations)</td></tr><tr><td>Enrolment Approval</td><td>Approve a beneficiary list (enrolment list) as final list under an enrolment cycle</td></tr><tr><td>Disbursement Operation</td><td>View &#x26; Create Disbursement Cycles<br>Create Beneficiary lists (disbursement lists) inside Disbursement Cycles</td></tr><tr><td>Disbursement Verification</td><td>Verify Disbursement lists and add observations (upload documents to support their observations)</td></tr><tr><td>Disbursement Approval</td><td>Approve a beneficiary list (disbursement list) as final list under an enrolment cycle</td></tr><tr><td>Service Provider Operation</td><td>View and Create Agencies and Warehouses<br>Associate Benefit codes to Agencies and Warehouses<br>Associate Geographies to Agencies and Warehouses</td></tr><tr><td>Geography Operation</td><td>View and Create Administrative Areas (Large &#x26; Small)</td></tr><tr><td>Audit Operation</td><td>View Access to the entire PBMS application</td></tr><tr><td>Program Super Administration</td><td>Edit programs, add benefit codes, view service providers and geography, create enrolment and disbursement cycles and view lists inside them — BUT NOT RESTRICTED by PROGRAM ACCESS. This role has access to all the programs defined in PBMS.</td></tr></tbody></table>

<mark style="color:blue;">**PBMS uses Keycloak for user identity management, authentication, and authorization. In Keycloak, the high-level groups described above must be defined as roles.**</mark>

### High Level Groups to Low Level Groups - Mapping

<table><thead><tr><th width="249.63140869140625">High Level Group</th><th width="545.702392578125">Low Level Groups</th></tr></thead><tbody><tr><td>Program Administration</td><td>group_abstract_model_viewer<br>group_agency_viewer<br>group_warehouse_viewer<br>group_geography_viewer<br>group_beneficiary_list_viewer<br>group_benefit_codes_editor<br>group_program_editor<br>group_program_viewer<br>group_enrolment_editor<br>group_disbursement_editor<br>group_priority_rules_viewer</td></tr><tr><td>Enrolment Operation</td><td><p>group_beneficiary_list_editor</p><p>group_beneficiary_list_viewer</p><p>group_enrolment_editor</p><p>group_program_viewer</p><p>group_benefit_codes_viewer</p><p>group_disbursement_viewer</p></td></tr><tr><td>Enrolment Verification</td><td><p>group_beneficiary_list_verifier</p><p>group_beneficiary_list_viewer</p><p>group_enrolment_viewer</p><p>group_program_viewer</p><p>group_benefit_codes_viewer</p><p>group_disbursement_viewer</p></td></tr><tr><td>Enrolment Approval</td><td><p>group_enrolment_approver</p><p>group_beneficiary_list_viewer</p><p>group_enrolment_viewer</p><p>group_program_viewer</p><p>group_benefit_codes_viewer</p><p>group_disbursement_viewer</p></td></tr><tr><td>Disbursement Operation</td><td></td></tr><tr><td>Disbursement Verification</td><td></td></tr><tr><td>Disbursement Approval</td><td></td></tr><tr><td>Service Provider Operation</td><td><p>group_agency_editor</p><p>group_agency_viewer</p><p>group_warehouse_editor</p><p>group_warehouse_viewer</p><p>group_program_viewer</p><p>group_benefit_codes_viewer</p></td></tr><tr><td>Geography Operation</td><td></td></tr><tr><td>Audit Operation</td><td></td></tr><tr><td>Program Super Administration</td><td></td></tr></tbody></table>
