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

<table><thead><tr><th width="144.77761840820312">High Level Group</th><th width="545.702392578125">Description</th></tr></thead><tbody><tr><td>Program Administration</td><td>Edit programs, add benefit codes, view service providers and geography, create enrolment and disbursement cycles and view lists inside them</td></tr><tr><td>Enrolment Operation</td><td>View &#x26; Create Enrolment Cycles<br>Create Beneficiary lists (enrolment lists) inside Enrolment Cycles</td></tr><tr><td>Enrolment Verification</td><td>Verify Enrolment lists and add observations (upload documents to support their observations)</td></tr><tr><td>Enrolment Approval</td><td>Approve a beneficiary list (enrolment list) as final list under an enrolment cycle</td></tr><tr><td>Disbursement Operation</td><td>View &#x26; Create Disbursement Cycles<br>Create Beneficiary lists (disbursement lists) inside Disbursement Cycles</td></tr><tr><td>Disbursement Verification</td><td>Verify Disbursement lists and add observations (upload documents to support their observations)</td></tr><tr><td>Disbursement Approval</td><td>Approve a beneficiary list (disbursement list) as final list under an enrolment cycle</td></tr><tr><td>Service Provider Operation</td><td>View and Create Agencies and Warehouses<br>Associate Benefit codes to Agencies and Warehouses<br>Associate Geographies to Agencies and Warehouses</td></tr><tr><td>Geography Operation</td><td>View and Create Administrative Areas (Large &#x26; Small)</td></tr><tr><td>Audit Operation</td><td>View Access to the entire PBMS application</td></tr><tr><td>Program Super Administration</td><td>Edit programs, add benefit codes, view service providers and geography, create enrolment and disbursement cycles and view lists inside them — BUT NOT RESTRICTED by PROGRAM ACCESS. This role has access to all the programs defined in PBMS.</td></tr></tbody></table>

<mark style="color:blue;">**PBMS uses Keycloak for user identity management, authentication, and authorization. In Keycloak, the high-level groups described above must be defined as roles.**</mark>

### High Level Groups to Low Level Groups - Mapping

<table><thead><tr><th width="167.15216064453125">High Level Group</th><th width="545.702392578125">Low Level Groups</th></tr></thead><tbody><tr><td>Program Administration</td><td>group_abstract_model_viewer<br>group_agency_viewer<br>group_warehouse_viewer<br>group_geography_viewer<br>group_beneficiary_list_viewer<br>group_benefit_codes_editor<br>group_program_editor<br>group_program_viewer<br>group_enrolment_editor<br>group_disbursement_editor<br>group_priority_rules_viewer</td></tr><tr><td>Enrolment Operation</td><td><p>group_beneficiary_list_editor</p><p>group_beneficiary_list_viewer</p><p>group_enrolment_editor</p><p>group_program_viewer</p><p>group_benefit_codes_viewer</p><p>group_disbursement_viewer</p></td></tr><tr><td>Enrolment Verification</td><td><p>group_beneficiary_list_verifier</p><p>group_beneficiary_list_viewer</p><p>group_enrolment_viewer</p><p>group_program_viewer</p><p>group_benefit_codes_viewer</p><p>group_disbursement_viewer</p></td></tr><tr><td>Enrolment Approval</td><td><p>group_enrolment_approver</p><p>group_beneficiary_list_viewer</p><p>group_enrolment_viewer</p><p>group_program_viewer</p><p>group_benefit_codes_viewer</p><p>group_disbursement_viewer</p></td></tr><tr><td>Disbursement Operation</td><td><p>group_beneficiary_list_editor</p><p>group_beneficiary_list_viewer</p><p>group_disbursement_editor</p><p>group_priority_rules_editor</p><p>group_program_viewer</p><p>group_benefit_codes_viewer</p><p>group_enrolment_viewer</p></td></tr><tr><td>Disbursement Verification</td><td><p>group_disbursement_viewer</p><p>group_beneficiary_list_verifier</p><p>group_beneficiary_list_viewer</p><p>group_priority_rules_viewer</p><p>group_program_viewer</p><p>group_benefit_codes_viewer</p><p>group_enrolment_viewer</p></td></tr><tr><td>Disbursement Approval</td><td><p>group_disbursement_viewer</p><p>group_disbursement_approver</p><p>group_beneficiary_list_viewer</p><p>group_priority_rules_viewer</p><p>group_program_viewer</p><p>group_benefit_codes_viewer</p><p>group_enrolment_viewer</p></td></tr><tr><td>Service Provider Operation</td><td><p>group_agency_editor</p><p>group_agency_viewer</p><p>group_warehouse_editor</p><p>group_warehouse_viewer</p><p>group_program_viewer</p><p>group_benefit_codes_viewer</p></td></tr><tr><td>Geography Operation</td><td><p>group_geography_editor</p><p>group_geography_viewer</p></td></tr><tr><td>Audit Operation</td><td><p>group_abstract_model_viewer</p><p>group_benefit_codes_viewer</p><p>group_agency_viewer</p><p>group_beneficiary_list_viewer</p><p>group_disbursement_viewer</p><p>group_enrolment_viewer</p><p>group_geography_viewer</p><p>group_priority_rules_viewer</p><p>group_program_viewer</p><p>group_warehouse_viewer</p></td></tr><tr><td>Program Super Administration</td><td><p>group_agency_viewer</p><p>group_benefit_code_editor</p><p>group_program_editor</p><p>group_warehouse_viewer</p><p>group_geography_viewer</p><p>group_beneficiary_list_editor</p><p>group_beneficiary_list_verifier</p><p>group_enrolment_editor</p><p>group_enrolment_approver</p><p>group_disbursement_editor</p><p>group_disbursement_approver</p><p>group_priority_rules_editor</p></td></tr></tbody></table>

### Low Level Groups to Odoo Models - Mapping

#### **Models with 1,1,1,1 (R,W,C,D) - access rights**

<table><thead><tr><th width="370.47698974609375">model name</th><th>1,1,1,1 - R,W,C,D - access rights</th></tr></thead><tbody><tr><td>g2p_agency</td><td>group_agency_editor</td></tr><tr><td>g2p_warehouse</td><td>group_warehouse_editor</td></tr><tr><td>g2p_benefit_codes</td><td>group_benefit_codes_editor</td></tr><tr><td>g2p_agency_program_benefit_codes</td><td>group_benefit_codes_editor</td></tr><tr><td>g2p_warehouse_program_benefit_codes</td><td>group_warehouse_editor</td></tr><tr><td>g2p_administrative_area_small</td><td>group_geography_editor</td></tr><tr><td>g2p_administrative_area_large</td><td>group_geography_editor</td></tr><tr><td>g2p_program_definition</td><td>group_program_editor</td></tr><tr><td>g2p_program_benefit_codes</td><td>group_benefit_codes_editor</td></tr><tr><td>g2p_eligibility_rule_definition</td><td>group_program_editor</td></tr><tr><td>g2p_beneficiary_list</td><td>group_beneficiary_list_editor</td></tr><tr><td>g2p_enrollment_cycle</td><td>group_enrolment_editor</td></tr><tr><td>g2p_bgtask_summary_wizard</td><td>group_enrolment_editor</td></tr><tr><td>g2p_api_summary_line</td><td>group_program_editor</td></tr><tr><td>g2p_api_disbursement_envelope_line</td><td>group_program_editor</td></tr><tr><td>g2p_api_disbursement_batch_line</td><td>group_program_editor</td></tr><tr><td>g2p_entitlement_rule_definition</td><td>group_program_editor</td></tr><tr><td>g2p_disbursement_cycle</td><td>group_disbursement_editor</td></tr><tr><td>g2p_priority_rule_definition</td><td>group_priority_rules_editor</td></tr><tr><td>g2p_disbursement_envelope_summary_wizard</td><td>group_disbursement_editor</td></tr><tr><td>g2p_disbursement_envelope_summary_geo</td><td>group_disbursement_editor</td></tr><tr><td>g2p_disbursement_batch_summary_wizard</td><td>group_disbursement_editor</td></tr><tr><td>g2p_disbursement_batch_summary_geo</td><td>group_disbursement_editor</td></tr></tbody></table>

#### Models with 1,0,0,0 (R,W,C,D) - access rights

<table><thead><tr><th width="385.9864501953125">model name</th><th>1,0,0,0 - R,W,C,D - access rights</th></tr></thead><tbody><tr><td>g2p_agency</td><td>group_agency_viewer</td></tr><tr><td>g2p_warehouse</td><td>group_warehouse_viewer</td></tr><tr><td>g2p_benefit_codes</td><td>group_benefit_codes_viewer</td></tr><tr><td>g2p_agency_program_benefit_codes</td><td>group_benefit_codes_viewer</td></tr><tr><td>g2p_warehouse_program_benefit_codes</td><td>group_warehouse_viewer</td></tr><tr><td>g2p_administrative_area_small</td><td>group_geography_viewer</td></tr><tr><td>g2p_administrative_area_large</td><td>group_geography_viewer</td></tr><tr><td>g2p_program_definition</td><td>group_program_viewer</td></tr><tr><td>g2p_program_benefit_codes</td><td>group_benefit_codes_viewer</td></tr><tr><td>g2p_eligibility_rule_definition</td><td>group_program_viewer</td></tr><tr><td>g2p_beneficiary_list</td><td>group_beneficiary_list_viewer</td></tr><tr><td>g2p_enrollment_cycle</td><td>group_enrolment_viewer</td></tr><tr><td>g2p_bgtask_summary_wizard</td><td></td></tr><tr><td>g2p_api_summary_line</td><td>group_program_viewer</td></tr><tr><td>g2p_api_disbursement_envelope_line</td><td>group_program_viewer</td></tr><tr><td>g2p_api_disbursement_batch_line</td><td>group_program_viewer</td></tr><tr><td>g2p_entitlement_rule_definition</td><td>group_program_viewer</td></tr><tr><td>g2p_disbursement_cycle</td><td>group_disbursement_viewer</td></tr><tr><td>g2p_priority_rule_definition</td><td>group_priority_rules_viewer</td></tr><tr><td>g2p_disbursement_envelope_summary_wizard</td><td></td></tr><tr><td>g2p_disbursement_envelope_summary_geo</td><td>group_disbursement_viewer</td></tr><tr><td>g2p_disbursement_batch_summary_wizard</td><td></td></tr><tr><td>g2p_disbursement_batch_summary_geo</td><td>group_disbursement_viewer</td></tr></tbody></table>

#### Models with 1,1,1,0 (R,W,C,D) - access rights

<table><thead><tr><th width="388.54522705078125">model name</th><th>1,1,1,0 - R,W,C,D - access rights</th></tr></thead><tbody><tr><td>g2p_bgtask_summary_wizard</td><td>group_enrolment_viewer</td></tr><tr><td>g2p_disbursement_envelope_summary_wizard</td><td>group_disbursement_viewer</td></tr><tr><td>g2p_disbursement_batch_summary_wizard</td><td>group_disbursement_viewer</td></tr></tbody></table>

#### Buttons with access rights

<table><thead><tr><th width="260.27020263671875">action buttons</th><th>low level group having access</th></tr></thead><tbody><tr><td>Verification Button</td><td>group_beneficiary_list_verifier</td></tr><tr><td>Approve Enrolment Button</td><td>group_enrolment_approver</td></tr><tr><td>Approve Disbursement Button</td><td>group_disbursement_approver</td></tr><tr><td>Create Benefit Code</td><td>group_benefit_code_editor</td></tr><tr><td>Create L/S Area</td><td>group_geography_editor</td></tr><tr><td>Create Service Providers</td><td>group_warehouse_editor,<br>group_agency_editor</td></tr><tr><td>Create Program</td><td>group_program_super_administration</td></tr></tbody></table>
