# Use Case Implementation

This page is the operating contract for the OpenG2P Advisor when it walks an implementer through deploying OpenG2P Registry. It is structured for machine consumption: every Discovery item, Activity, Gap-analysis check, and Output element has a deterministic shape, and the advisor relies on that shape. Human readers will find the format unusually rigid; that is intentional.

A typical implementation proceeds through five phases: **Requirements**, **Build**, **Sandbox**, **Pilot**, and **Full Rollout**. Each phase has the same internal structure:

1. **Purpose** — what the phase achieves and why it exists as a distinct phase.
2. **Enter / Exit** — preconditions for entry and the durable test for completion.
3. **Discovery items** — facts the advisor must establish, each with a fixed schema.
4. **Activities** — named steps the advisor performs, each with a paragraph body.
5. **References** — pointers to product entities, concepts, and worked examples relevant to this phase.
6. **Gap analysis** — verifiable checks the advisor runs before the phase ends.
7. **Output** — the report produced when the phase ends.
8. **Common pitfalls** — issues observed in past implementations, populated as evidence accumulates.

## Discovery item schema

Every Discovery item has the following fields. Items are identified by their heading, which is the fact key the advisor uses internally.

* **Ask** — the canonical form of the question. The advisor may rephrase for tone but must elicit the same information.
* **Why** — what downstream decision, activity, or phase consumes this answer.
* **Required** — `yes`, `no`, or `conditional: <expression>`.
* **Type** — `text`, `number`, `boolean`, `enum [...]`, `list`, `prose`, `file`, or `classification` (a typed answer that may include free text).
* **Impact** — one of: `code`, `configuration`, `informational`, `deployment`, `migration`. Captures the kind of downstream effect the answer has: `code` items feed Phase 2 generation; `configuration` items become seed SQL or env vars; `informational` items appear only in the Requirements Analysis Report; `deployment` items feed Phase 3+; `migration` items gate the brownfield sub-track. Distinct from `Affects`, which names specific phases.
* **Affects** _(optional)_ — specific downstream phases or activities that consume this answer.
* **Follow-ups** _(optional)_ — conditional sub-items, each itself a Discovery item, conditioned on the parent answer.
* **Validation** _(optional)_ — explicit constraints beyond the Type.
* **Examples** _(optional)_ — sample answers.

## Phase Transition Protocol

The same protocol applies after every phase report is produced.

1. Inform the implementer that the phase report is ready, and ask them to review it.
2. If they request changes, capture them, update the underlying facts, and regenerate the report.
3. Obtain explicit approval that the report is accurate and complete.
4. Briefly describe the next phase — what it involves and what information will be needed.
5. Ask whether the implementer is ready to proceed.
6. Advance only after explicit confirmation.

***

## Phase 1: Requirements Analysis

### Purpose

Capture the implementer's social-protection objectives, registry structure, integration constraints, infrastructure preferences, and operational characteristics. Map the captured requirements against OpenG2P Registry's feature surface, identify gaps, and produce a Requirements Analysis Report that anchors every later phase.

### Enter / Exit

* **Enter when:** the implementer has decided to use OpenG2P Registry as part of their G2P stack.
* **Exit when:** a Requirements Analysis Report has been produced and explicitly approved by the implementer.

### Discovery items

The Discovery items below are grouped into thematic blocks for readability. The advisor walks them in order; the bold block headings are organisational only and have no contract significance.

---

**Project context**

#### country

* **Ask:** In which country will the registry operate?
* **Why:** Establishes regulatory context, language defaults, and data-residency constraints that affect later-phase deployment region and the support model.
* **Required:** yes
* **Type:** text
* **Impact:** code

#### implementing_organisation

* **Ask:** Which department, agency, or organisation will host this Registry?
* **Why:** Identifies the operational owner and the stakeholder model; informs operational handover and access policies.
* **Required:** yes
* **Type:** text
* **Impact:** informational

#### registry_name

* **Ask:** What is the full name of the Registry?
* **Why:** Used in user-facing labels and report headers.
* **Required:** yes
* **Type:** text
* **Impact:** configuration

#### supported_languages

* **Ask:** In which languages will users access the platform?
* **Why:** Drives Keycloak theme and frontend i18n configuration, and number/date format selection.
* **Required:** yes
* **Type:** list
* **Impact:** configuration

#### use_case_detail

* **Ask:** Describe the end-to-end use case in prose. How will registry data be consumed and by whom? Will data be shared with other departments, systems, agencies, or applications?
* **Why:** Drives integration scope and informs the gap analysis on data sharing and interoperability. Catches narrative context that the structured items below cannot.
* **Required:** yes
* **Type:** prose
* **Impact:** informational
* **Affects:** Phase 1 gap analysis on interoperability; integration design in later phases.

---

**Registry typology**

#### registry_typology

* **Ask:** Is this Registry serving a specific benefit-delivery programme, or is it a general-purpose registry?
* **Why:** Determines registry typology and the feature set the advisor surfaces during Product Feature Discovery.
* **Required:** yes
* **Type:** enum \[`specific-programme`, `general-purpose`]
* **Impact:** code
* **Follow-ups:**
  * **program_name** _(when registry_typology = specific-programme)_ — what is the name of the programme?
  * **registry_type** _(when registry_typology = general-purpose)_ — which type of registry: national social registry, farmer registry, family registry, health workers registry, disability registry, students registry, crop registry, land registry, vehicle registry, or other?

---

**Registers and structure**

#### registers

* **Ask:** What entities does this Registry manage? Will there be one main entity or more than one? If multiple, indicate the hierarchical relationship between them.
* **Why:** Each Register becomes a distinct table and entity in the generated code. Hierarchy determines parent/child relationships in schema and UI.
* **Required:** yes
* **Type:** list
* **Impact:** code
* **Examples:** A Social Registry typically has two Registers — a Households Register and an Individuals Register, where an Individual reports into a Household.

#### registers_physical_object

* **Ask:** For each Register, what is the physical object it identifies?
* **Why:** Anchors the domain model. Affects ID generation rules and UI defaults.
* **Required:** yes
* **Type:** classification — a map of register name to physical object kind.
* **Impact:** code
* **Examples:** PERSON, HOUSE, VEHICLE, SCHOOL, FARM, LAND PARCEL.

#### supporting_tables

* **Ask:** What supporting tables (child entities) are required to complement the main Registers? For each, indicate which Register it relates to.
* **Why:** Supporting tables capture multi-valued attributes (e.g., a person's land holdings, a household's assets). They become tables linked to the main Registers via foreign keys.
* **Required:** yes
* **Type:** list
* **Impact:** code
* **Examples:** A Land table for an Individual where each individual may own multiple land parcels.

#### main_register_attributes

* **Ask:** List all attributes for the Main Registers.
* **Why:** Forms the schema for the Register tables. Each attribute becomes a column with a chosen type.
* **Required:** yes
* **Type:** classification — a map of register name to list of attribute names with types.
* **Impact:** code

#### supporting_table_attributes

* **Ask:** List all attributes for the Supporting Tables.
* **Why:** Forms the schema for the supporting tables.
* **Required:** yes
* **Type:** classification — a map of supporting table name to list of attribute names with types.
* **Impact:** code

---

**Foundational ID**

#### has_foundational_id

* **Ask:** If a main Register identifies a person, does the country have a nationwide Foundational Identity?
* **Why:** Determines whether identity verification can rely on the national identity provider or requires an alternative mechanism.
* **Required:** conditional: any Register has registers_physical_object = PERSON
* **Type:** boolean
* **Impact:** code
* **Follow-ups (when yes):** all subsequent Foundational ID items below.

#### foundational_id_name

* **Ask:** What is the name of this Foundational Identity?
* **Why:** Used in generated UI labels and configuration references.
* **Required:** conditional: has_foundational_id = yes
* **Type:** text
* **Impact:** informational
* **Examples:** PHILSYS National ID (Philippines), AADHAAR (India), Fayda National ID (Ethiopia).

#### foundational_id_responsible_department

* **Ask:** Which department is responsible for allocation of this Foundational Identity?
* **Why:** Identifies the integration counterpart and the governance owner of the ID.
* **Required:** conditional: has_foundational_id = yes
* **Type:** text
* **Impact:** informational

#### foundational_id_verification_mechanism

* **Ask:** How will your department verify the Foundational ID?
* **Why:** Affects integration design between the registry and the national identity provider.
* **Required:** conditional: has_foundational_id = yes
* **Type:** prose
* **Impact:** code

#### foundational_id_biometrics

* **Ask:** Are biometrics involved in the verification?
* **Why:** Drives device requirements for field agents and additional integration considerations.
* **Required:** conditional: has_foundational_id = yes
* **Type:** boolean
* **Impact:** code

#### foundational_id_integration_mechanism

* **Ask:** What integration mechanism exists for verification of the Foundational ID? Does it follow any standard, e.g., OIDC?
* **Why:** Determines the eSignet / OAuth-OIDC configuration approach.
* **Required:** conditional: has_foundational_id = yes
* **Type:** prose
* **Impact:** code

#### foundational_id_kyc_periodicity

* **Ask:** How frequently do individuals have to verify themselves with the Foundational ID — i.e., the KYC periodicity?
* **Why:** Drives scheduled re-verification jobs and consent renewal flows.
* **Required:** conditional: has_foundational_id = yes
* **Type:** text
* **Impact:** code

#### foundational_id_length

* **Ask:** How long is the Foundational ID — number of characters?
* **Why:** Required for input validation and storage column sizing.
* **Required:** conditional: has_foundational_id = yes
* **Type:** number
* **Impact:** configuration

#### foundational_id_format

* **Ask:** Is the Foundational ID alphanumeric or pure numeric?
* **Why:** Drives input validation regex and storage type.
* **Required:** conditional: has_foundational_id = yes
* **Type:** enum \[`alphanumeric`, `numeric`]
* **Impact:** code

#### foundational_id_prefix_suffix_encoding

* **Ask:** Does the Foundational ID have any prefix or suffix encoding tied to geographic or other demographic profile?
* **Why:** Affects ID parsing logic and any region-derived attributes.
* **Required:** conditional: has_foundational_id = yes
* **Type:** prose
* **Impact:** informational

#### foundational_id_attributes_stored

* **Ask:** What attributes does the Foundational ID system store? (Name, date of birth, address, etc.)
* **Why:** Determines which attributes the registry can fetch via verification vs. must collect itself.
* **Required:** conditional: has_foundational_id = yes
* **Type:** list
* **Impact:** code

---

**Functional ID**

#### has_functional_id

* **Ask:** Apart from the Foundational ID, does your department issue any other ID to the Register records?
* **Why:** Triggers the functional ID generation and tracking subsystem.
* **Required:** yes
* **Type:** boolean
* **Impact:** code

#### functional_id_examples

* **Ask:** Give examples of these functional IDs.
* **Why:** Helps clarify intent and naming conventions.
* **Required:** conditional: has_functional_id = yes
* **Type:** prose
* **Impact:** informational
* **Examples:** Voter ID (electoral register), Household ID (social register), Pension ID (pension register).

#### functional_id_length

* **Ask:** How long is the Functional ID — number of characters?
* **Why:** Used during code generation in the build phase.
* **Required:** conditional: has_functional_id = yes
* **Type:** number
* **Impact:** code
* **Validation:** typically nine to twelve; confirm with implementer if outside this range.

#### functional_id_format

* **Ask:** Is the Functional ID alphanumeric or pure numeric?
* **Why:** Drives ID generation logic.
* **Required:** conditional: has_functional_id = yes
* **Type:** enum \[`alphanumeric`, `numeric`]
* **Impact:** code

#### functional_id_prefix_suffix_encoding

* **Ask:** Does the Functional ID have any prefix or suffix encoding tied to geographic or other demographic profile?
* **Why:** Affects ID generation algorithm.
* **Required:** conditional: has_functional_id = yes
* **Type:** prose
* **Impact:** code

#### functional_id_generation_timing

* **Ask:** When is the Functional ID generated — when the entity is registered, or when an application is received?
* **Why:** Determines whether ID generation is part of the registration workflow or a separate event.
* **Required:** conditional: has_functional_id = yes
* **Type:** enum \[`at-registration`, `at-application`, `other`]
* **Impact:** code

#### functional_id_owning_department

* **Ask:** Is your department responsible for generating this Functional ID, or is there another department that allocates it?
* **Why:** Determines whether the registry generates IDs locally or integrates with an external service.
* **Required:** conditional: has_functional_id = yes
* **Type:** enum \[`own-department`, `external-department`]
* **Impact:** code

#### functional_id_integration_mechanism

* **Ask:** If another department is responsible for allocation, what interface mechanism exists to facilitate this integration?
* **Why:** Drives external integration design.
* **Required:** conditional: functional_id_owning_department = external-department
* **Type:** prose
* **Impact:** code

---

**Scores**

#### has_scores

* **Ask:** Do any of the identified Registers need scores computed for each record?
* **Why:** Drives the scoring subsystem in the registry. Scores affect indexing, search, eligibility, and reporting.
* **Required:** yes
* **Type:** boolean
* **Impact:** code

#### scores_examples

* **Ask:** What scores are required and what do they represent?
* **Why:** Anchors the scoring logic to a real-world definition.
* **Required:** conditional: has_scores = yes
* **Type:** prose
* **Impact:** code
* **Examples:** Poverty score (Social Registry), Disability score (Disability Registry), Food Security score.

#### scores_per_register

* **Ask:** How many scores are required for each Register, and what are they?
* **Why:** Each score becomes a configured score type with its own computation pipeline.
* **Required:** conditional: has_scores = yes
* **Type:** classification — a map of register name to list of score types.
* **Impact:** code

#### scores_external_dependencies

* **Ask:** Do the parameters that contribute to each score depend only on attributes of the Register, or are there external dependencies (e.g., geographical region attributes)?
* **Why:** Affects whether the score computation is local or requires external lookups.
* **Required:** conditional: has_scores = yes
* **Type:** prose
* **Impact:** code

#### scores_periodicity

* **Ask:** How frequently are these scores computed? Is there a specified periodicity (annual, monthly, etc.)?
* **Why:** Drives scheduled jobs in the celery worker.
* **Required:** conditional: has_scores = yes
* **Type:** text
* **Impact:** code

#### scores_compute_on_change

* **Ask:** Are scores recomputed whenever there is any change in Register attributes?
* **Why:** Drives event-driven score recomputation logic.
* **Required:** conditional: has_scores = yes
* **Type:** boolean
* **Impact:** configuration

#### scores_notify_registrant

* **Ask:** Does the registrant need to be notified about their score?
* **Why:** Drives notification triggers.
* **Required:** conditional: has_scores = yes
* **Type:** boolean
* **Impact:** code

#### scores_notify_other_departments

* **Ask:** Do scores need to be published to any other department?
* **Why:** Drives outgoing integration / event-publishing design.
* **Required:** conditional: has_scores = yes
* **Type:** boolean
* **Impact:** code

---

**Registration channel and enumeration**

#### registration_channel

* **Ask:** Will registration happen online via a portal, offline via field agents, or both?
* **Why:** Affects UI scope, sync behaviour, and offline tooling decisions.
* **Required:** yes
* **Type:** enum \[`online`, `offline`, `both`]
* **Impact:** code

#### enumeration_field_agents

* **Ask:** Do you have field agents who visit the homes of people to enumerate them into the Registry?
* **Why:** Drives mobile-app and offline-first feature requirements.
* **Required:** yes
* **Type:** boolean
* **Impact:** informational

#### enumeration_offices_in_villages

* **Ask:** Do you have department offices in villages and towns to assist with the enumeration?
* **Why:** Affects deployment topology and access models for distributed offices.
* **Required:** yes
* **Type:** boolean
* **Impact:** informational

#### internet_connectivity_in_remote_regions

* **Ask:** What is the internet connectivity in the remote regions where enumeration takes place?
* **Why:** Drives offline-mode requirements and sync strategy.
* **Required:** yes
* **Type:** prose
* **Impact:** code

#### enumeration_devices

* **Ask:** If field agents are involved, what devices do they carry — tablets, laptops, biometric devices?
* **Why:** Affects mobile-app target platforms and device-integration scope.
* **Required:** conditional: enumeration_field_agents = yes
* **Type:** list
* **Impact:** code

#### uses_odk

* **Ask:** Do field agents use any other open-source framework like ODK to support their enumeration effort?
* **Why:** Drives ODK integration / form-import scope.
* **Required:** conditional: enumeration_field_agents = yes
* **Type:** boolean
* **Impact:** code

#### enumeration_periodicity

* **Ask:** Are enumerations conducted periodically? If yes, how frequently?
* **Why:** Drives scheduled enumeration cycles and re-survey workflows.
* **Required:** yes
* **Type:** prose
* **Impact:** informational

---

**Required documents at registration**

#### required_documents

* **Ask:** What documents must registrants provide at registration time?
* **Why:** Drives upload, verification, and storage design — including blob storage configuration and document-verification workflow.
* **Required:** yes
* **Type:** list
* **Impact:** configuration

---

**Workflow (record acceptance)**

#### approval_workflow_levels

* **Ask:** What is the workflow process involved in accepting a record into a Register? How many levels of approval are required before a record becomes valid?
* **Why:** Drives the approval-level configuration on each Register and the change-request workflow.
* **Required:** yes
* **Type:** number
* **Impact:** code
* **Examples:** 0 (auto-approve), 1, 2, 3 levels of approval.

#### approval_workflow_approvers_login

* **Ask:** Are approvers expected to log into the Registry system to provide their approvals?
* **Why:** Drives access management and notification design for approvers.
* **Required:** yes
* **Type:** boolean
* **Impact:** informational

#### approval_workflow_approvers_location

* **Ask:** Are the approvers within the department office or remotely located?
* **Why:** Affects authentication strategy and offline considerations for approvers.
* **Required:** yes
* **Type:** enum \[`in-office`, `remote`, `both`]
* **Impact:** informational

#### approval_workflow_approvers_devices

* **Ask:** Do these approvers need device support for their activities?
* **Why:** Drives mobile-friendly approval UI scope.
* **Required:** yes
* **Type:** prose
* **Impact:** informational

---

**Changes / Edits to Registers**

#### edit_mechanism

* **Ask:** What is the mechanism for introducing edits to records in the Registers?
* **Why:** Drives the change-request flow and the user-facing edit UI.
* **Required:** yes
* **Type:** prose
* **Impact:** configuration

#### edit_submission_channel

* **Ask:** How do registrants submit change requests — by visiting a department office, through a field agent, or online?
* **Why:** Drives UI scope and channel-specific workflows.
* **Required:** yes
* **Type:** enum \[`office`, `field-agent`, `online`, `multiple`]
* **Impact:** configuration

#### edit_approval_workflow

* **Ask:** What is the workflow process to approve such edit requests?
* **Why:** Drives the change-request approval configuration, possibly distinct from new-record approval.
* **Required:** yes
* **Type:** prose
* **Impact:** code

---

**Agent support**

#### agent_devices

* **Ask:** What kind of device support do agents require — laptops, tablets, both?
* **Why:** Affects target platforms for agent applications.
* **Required:** yes
* **Type:** list
* **Impact:** code

#### agent_named_login

* **Ask:** Are agents named users with individual login profiles?
* **Why:** Drives identity provisioning for agents.
* **Required:** yes
* **Type:** boolean
* **Impact:** configuration

#### agent_profile_management

* **Ask:** How are agent login profiles managed? Will the department administer them, or is another system involved?
* **Why:** Drives Keycloak realm configuration and admin workflow.
* **Required:** yes
* **Type:** prose
* **Impact:** configuration

#### agent_authentication_with_foundational_id

* **Ask:** Will the Foundational ID be involved in any way to authenticate field agents?
* **Why:** Drives agent-app authentication design.
* **Required:** yes
* **Type:** boolean
* **Impact:** code

---

**Beneficiary portal**

#### has_beneficiary_portal

* **Ask:** Does your department plan or already have a self-service portal for the registrants (beneficiaries)?
* **Why:** Determines whether the beneficiary portal API and frontend are in scope.
* **Required:** yes
* **Type:** boolean
* **Impact:** configuration

#### beneficiary_portal_capabilities

* **Ask:** What can a registrant do on the portal that impacts or affects the Registry?
* **Why:** Defines the beneficiary portal's feature surface — view records, request edits, claim/attest, etc.
* **Required:** conditional: has_beneficiary_portal = yes
* **Type:** prose
* **Impact:** code

#### beneficiary_portal_access_management

* **Ask:** How is access to the Beneficiary Portal managed? Is the national ID department involved in administering access?
* **Why:** Drives authentication integration for beneficiaries.
* **Required:** conditional: has_beneficiary_portal = yes
* **Type:** prose
* **Impact:** code
* **Examples:** Aadhaar Login (India), PHILSYS authentication (Philippines).

---

**Integrations with other departments**

#### api_integrations

* **Ask:** What kind of API integrations will the Registry require?
* **Why:** Forms the baseline for the integration design.
* **Required:** yes
* **Type:** list
* **Impact:** code

#### kyc_based_edits

* **Ask:** Will edits be triggered into a Register based on KYC updates from the Foundational ID department?
* **Why:** Drives event-subscription / sync design with the foundational ID provider.
* **Required:** yes
* **Type:** boolean
* **Impact:** code

#### outgoing_notifications_on_edits

* **Ask:** Will you notify any other department when there are edits to a Register record? If yes, list those departments and the payload that is published, plus the trigger event.
* **Why:** Drives outgoing event-publishing and webhook configuration.
* **Required:** yes
* **Type:** prose
* **Impact:** code

#### outgoing_periodic_publishes

* **Ask:** Are other departments notified periodically without any triggering event? E.g., a semi-annual feed published to another department of all the records.
* **Why:** Drives scheduled bulk-export jobs.
* **Required:** yes
* **Type:** prose
* **Impact:** code

#### incoming_feeds

* **Ask:** Similar to outgoing publishes, do you receive any such publish from another department?
* **Why:** Drives ingestion-pipeline design.
* **Required:** yes
* **Type:** prose
* **Impact:** code

#### incoming_feeds_approval_workflow

* **Ask:** If incoming feeds lead to edits in a Register, what is the approval workflow process to approve such edits?
* **Why:** Determines whether incoming-feed-driven changes are auto-applied or require approval.
* **Required:** conditional: incoming_feeds is non-empty
* **Type:** prose
* **Impact:** code

#### vc_ingestion

* **Ask:** Does the Registry support ingestion using Verifiable Credentials? List the details of such use cases.
* **Why:** Drives VC-verification subsystem inclusion.
* **Required:** yes
* **Type:** prose
* **Impact:** code

---

**Benefit programs**

#### registry_used_for_benefit_programs

* **Ask:** Will this Registry be used by your department (or any other department) for effecting any Benefit Programs?
* **Why:** Determines whether the Programme Register feature is in scope.
* **Required:** yes
* **Type:** boolean
* **Impact:** code

#### benefit_programs_list

* **Ask:** List all such Programs and the departments that run them.
* **Why:** Drives the programme catalogue configuration.
* **Required:** conditional: registry_used_for_benefit_programs = yes
* **Type:** list
* **Impact:** code

#### track_benefit_program_memberships

* **Ask:** Will this Registry be required to maintain a record of all the benefit programs that a registrant is part of?
* **Why:** Drives Programme Register + membership-tracking design.
* **Required:** conditional: registry_used_for_benefit_programs = yes
* **Type:** boolean
* **Impact:** code

#### benefit_programs_scope

* **Ask:** If the Registry is aware of benefit-programme memberships, is it only the programmes administered by your department, or does it also cover programmes from other departments?
* **Why:** Determines cross-department integration scope for programme data.
* **Required:** conditional: track_benefit_program_memberships = yes
* **Type:** enum \[`own-department-only`, `cross-department`]
* **Impact:** code

#### benefit_coverage_change_workflow

* **Ask:** How do changes in Benefit Program coverage (inclusions and exclusions) get effected in the Registry?
* **Why:** Drives the membership-update workflow.
* **Required:** conditional: track_benefit_program_memberships = yes
* **Type:** prose
* **Impact:** code

---

**Verifiable Credentials**

#### issues_verifiable_credentials

* **Ask:** Does your department issue Verifiable Credentials (or plan to issue them) to the registrants?
* **Why:** Drives VC issuance subsystem inclusion.
* **Required:** yes
* **Type:** boolean
* **Impact:** code

#### vc_platform

* **Ask:** If yes, has the VC platform been identified? Provide details.
* **Why:** Determines integration target for VC issuance.
* **Required:** conditional: issues_verifiable_credentials = yes
* **Type:** prose
* **Impact:** code

---

**Cards and printouts**

#### registry_provides_cards

* **Ask:** Does your department provide cards or printouts to all the registrants?
* **Why:** Drives card-generation and printing subsystem design.
* **Required:** yes
* **Type:** boolean
* **Impact:** code

#### card_contents

* **Ask:** What does the card or printout carry?
* **Why:** Defines the card layout template and the data fields included.
* **Required:** conditional: registry_provides_cards = yes
* **Type:** list
* **Impact:** code

#### card_qr_code

* **Ask:** Does the card carry a QR code that needs to be authenticated from external systems?
* **Why:** Drives QR generation and verification-API design.
* **Required:** conditional: registry_provides_cards = yes
* **Type:** boolean
* **Impact:** code

---

**Notifications (SMS / Email)**

#### has_notification_requirements

* **Ask:** Do you have notification requirements? Notifications to registrants? To agents? To staff users?
* **Why:** Determines whether the notification subsystem is in scope.
* **Required:** yes
* **Type:** prose
* **Impact:** code

#### notification_triggering_events

* **Ask:** What are the triggering events that issue such notifications?
* **Why:** Drives the notification-trigger configuration.
* **Required:** conditional: has_notification_requirements is non-empty
* **Type:** list
* **Impact:** code

---

**Greenfield vs brownfield decision**

#### existing_data

* **Ask:** Is this a greenfield implementation (fresh data collection) or brownfield (existing data to import)?
* **Why:** Brownfield implies a data-migration sub-track in later phases; greenfield does not.
* **Required:** yes
* **Type:** enum \[`greenfield`, `brownfield`]
* **Impact:** migration

#### existing_data_form

* **Ask:** In what form does the existing data exist — Excel, database, APIs of another system, or other?
* **Why:** Drives the ingestion connector design for migration.
* **Required:** conditional: existing_data = brownfield
* **Type:** classification
* **Impact:** migration

#### existing_registry_platform

* **Ask:** Does your department already have an existing Registry platform that you use today?
* **Why:** Identifies the source system for data migration.
* **Required:** conditional: existing_data = brownfield
* **Type:** prose
* **Impact:** migration

#### existing_registry_technology

* **Ask:** What technology platform is the current registry built on?
* **Why:** Drives migration-tooling selection (export formats, connector libraries).
* **Required:** conditional: existing_data = brownfield
* **Type:** prose
* **Impact:** migration

#### existing_registry_rdbms

* **Ask:** Provide RDBMS details of the current registry — vendor, version, schema specifics.
* **Why:** Determines the migration ETL approach.
* **Required:** conditional: existing_data = brownfield
* **Type:** prose
* **Impact:** migration

---

**Open-ended functional requirements**

#### functional_requirements

* **Ask:** What specific functionalities must OpenG2P Registry support for this use case? List every requirement, including any that may not be standard registry features and aren't covered by the questions above.
* **Why:** Catch-all for domain-specific needs not covered by the structured items. Forms the requirements baseline against which the gap analysis runs.
* **Required:** yes
* **Type:** list
* **Impact:** code

---

**Infrastructure**

#### sandbox_hosting_strategy

* **Ask:** Explain your Sandbox Hosting Strategy — within country, public cloud hosting, within office premises, private data centre, or captive data centre. Multiple may apply; prose answer.
* **Why:** Drives sandbox-phase deployment topology choices and the support model.
* **Required:** yes
* **Type:** prose
* **Impact:** deployment

#### sandbox_outside_office_ok

* **Ask:** Can the sandbox be hosted outside your office premises?
* **Why:** Boundary constraint on where the sandbox can physically/logically run.
* **Required:** yes
* **Type:** boolean
* **Impact:** deployment

#### sandbox_outside_country_ok

* **Ask:** Can the sandbox be hosted outside your country?
* **Why:** Affects data-residency and compliance for development/test environments.
* **Required:** yes
* **Type:** boolean
* **Impact:** deployment

#### sandbox_on_cloud

* **Ask:** Is a sandbox on a public cloud acceptable for development?
* **Why:** Affects sandbox-phase deployment topology, separately from the production deployment.
* **Required:** yes
* **Type:** boolean
* **Impact:** deployment

#### production_hosting_strategy

* **Ask:** Explain your Production Hosting Strategy — within country, public cloud hosting, within office premises, private data centre, or captive data centre. Multiple may apply; prose answer.
* **Why:** Drives production-phase deployment topology and the support model. Complements the high-level `production_infrastructure` enum below with the specific hosting category.
* **Required:** yes
* **Type:** prose
* **Impact:** deployment

#### production_infrastructure

* **Ask:** Will the pilot and production systems run on on-premises hardware, on cloud, or in a hybrid configuration?
* **Why:** Affects later-phase deployment design and the support model.
* **Required:** yes
* **Type:** enum \[`on-prem`, `cloud`, `hybrid`]
* **Impact:** deployment

#### existing_cloud_service_provider

* **Ask:** Do you already have a Cloud Service Provider empanelled within your department?
* **Why:** Determines whether the production deployment can use an existing CSP arrangement.
* **Required:** conditional: production_infrastructure in [`cloud`, `hybrid`]
* **Type:** prose
* **Impact:** informational

---

**Technology operations**

#### it_personnel_model

* **Ask:** Do you have skilled IT personnel to manage the Technology Operations for the Registry, do you plan to use a Software Service Provider, or a hybrid approach?
* **Why:** Determines support model and handover scope.
* **Required:** yes
* **Type:** enum \[`in-house`, `service-provider`, `hybrid`]
* **Impact:** informational

#### software_policies

* **Ask:** Does your department have established formal processes and policies with respect to software usage — open-source, proprietary software, etc.? Provide details.
* **Why:** Drives compliance considerations for the deployment.
* **Required:** yes
* **Type:** prose
* **Impact:** informational

#### network_for_distributed_offices

* **Ask:** If the Registry is to be used in distributed office environments (department offices, field agents), provide network details and bandwidth.
* **Why:** Drives sync strategy and offline-mode scope.
* **Required:** conditional: enumeration_offices_in_villages = yes OR enumeration_field_agents = yes
* **Type:** prose
* **Impact:** informational

#### needs_offline_features

* **Ask:** Do we need offline features? If yes, where — agent application, office terminals, both?
* **Why:** Drives offline-first and sync design.
* **Required:** yes
* **Type:** prose
* **Impact:** code

---

**Volumetric**

#### record_scale_current

* **Ask:** What is the current volume of records (if there is an existing registry)?
* **Why:** Drives migration sizing and initial deployment topology.
* **Required:** yes
* **Type:** number
* **Impact:** deployment

#### record_scale_5_year_estimate

* **Ask:** What is the estimated record volume over the next five years?
* **Why:** Drives capacity planning and topology decisions for production.
* **Required:** yes
* **Type:** number
* **Impact:** deployment

---

**Usage stats**

#### staff_user_count

* **Ask:** Provide the expected number of Staff Users.
* **Why:** Drives capacity planning for the staff portal API and Keycloak realm.
* **Required:** yes
* **Type:** number
* **Impact:** deployment

#### agent_user_count

* **Ask:** Provide the expected number of Agent Users.
* **Why:** Drives capacity planning for agent-application and partner-API loads.
* **Required:** yes
* **Type:** number
* **Impact:** deployment

#### beneficiary_portal_user_volume

* **Ask:** If the Beneficiary Portal is involved, provide an estimate of beneficiary user volume.
* **Why:** Drives capacity planning for the beneficiary portal API.
* **Required:** conditional: has_beneficiary_portal = yes
* **Type:** number
* **Impact:** deployment

#### integration_traffic_volumetrics

* **Ask:** If integration with other departments is involved, provide traffic volumetrics for these use cases.
* **Why:** Drives capacity planning for the integration tier.
* **Required:** conditional: api_integrations is non-empty
* **Type:** prose
* **Impact:** deployment

---

**Interoperability**

#### interoperability_requirements

* **Ask:** Are there specific interoperability requirements — integration with other systems, APIs, or standards (for example G2P Connect or MOSIP)?
* **Why:** Drives external-interface scope and standards conformance.
* **Required:** no
* **Type:** prose
* **Impact:** code

### Activities

#### walk_discovery

Walk the implementer through each Discovery item in order. Defer decisions that belong to later phases. For each item, record the answer against the item's fact key. For items with conditional follow-ups, evaluate the condition against the recorded answer and run the follow-up if it applies.

#### product_feature_discovery

After every Discovery item is recorded, review every feature documented for OpenG2P Registry. For each feature not yet raised by the implementer through their stated functional requirements, ask the implementer whether it is needed. Group related features into a single conversational turn — identity and deduplication features together, reporting features together, integration features together. For each feature surfaced, record one of: `required`, `not_required`, or `gap` (required-but-not-supported). This activity is mandatory; the phase cannot end until every documented feature has been classified.

#### gap_classification

For every entry in `functional_requirements`, every feature surfaced via `product_feature_discovery`, and every Discovery item answered, look for explicit support in the OpenG2P knowledge base. Mark as `Supported` (native or via configuration) when explicit evidence exists. Mark as `Gap` otherwise — including obvious or seemingly basic items, since the gap analysis depends on explicit evidence rather than assumption. For each gap, classify as one of: `configurable-at-deploy`, `requires-customisation` (defer to Phase 2), or `requires-upstream-change` (raise as an issue).

### References

* OpenG2P Registry feature surface, deployment patterns, and capacity profiles.
* Concepts: eligibility modelling, identifier resolution, data sharing, brownfield import, scoring.
* Worked examples: Farmer Registry, National Social Registry.
* MOSIP integration touchpoints; eSignet OAuth/OIDC integration.

### Gap analysis

Before producing the Phase 1 report, the advisor verifies:

* Every Discovery item is recorded — answered, deferred with explicit acknowledgement, or marked unknown.
* Every entry in `functional_requirements` is assessed against the product knowledge base and recorded as `Supported` or `Gap`.
* Product Feature Discovery is complete: every feature documented for OpenG2P Registry is classified as `required`, `not_required`, or `gap`.
* Infrastructure preferences for sandbox, pilot, and production are recorded.
* Volumetric and usage-stats expectations are recorded.
* No feature documented in the knowledge base remains undiscussed.

### Output

**Requirements Analysis Report**, with these sections:

1. **Project context** — country, implementing organisation, registry name, supported languages, end-to-end use case (two to three sentences).
2. **Discovered facts** — the complete list of fact keys and their recorded values from Discovery, grouped by the thematic blocks above.
3. **Requirements vs OpenG2P mapping** — for each entry in `functional_requirements` and each feature surfaced via Product Feature Discovery: the requirement as worded; the OpenG2P feature or module that addresses it; support level (`native`, `configuration`, `partial`, `gap`); a one-sentence description of how it is addressed (sourced from the knowledge base) or, for gaps, a description of what is missing.
4. **Gaps summary** — all `Gap` and `Partial` items, with the missing capability and the custom work it implies.
5. **Resource requirements** — recommended deployment architecture (`single-node`, `three-node`, or `high-availability`) and compute specifications for development sandbox, pilot, and production environments. Sourced from the knowledge base only.

### Common pitfalls

(none recorded yet)

***

## Phase 2: Build

### Purpose

Take the approved Phase 1 specification and produce a running, customised registry: two GitLab repositories under the implementer's subgroup (`<mnemonic>-extension` and `<mnemonic>-deployment`), Docker images published to GitLab Container Registry, a generated Python test suite, and a verified local sandbox running the customised stack. The implementer-facing output of this phase is a green smoke-test run plus the published GitLab artefacts, ready for Phase 3 (Sandbox).

### Enter / Exit

* **Enter when:** the Requirements Analysis Report is approved AND every Phase 2 Discovery item below has been recorded (the build runs as a single linear job; missing inputs cannot be filled in mid-flight).
* **Exit when:** all generated code is pushed to GitLab, GitLab CI has built and published every Docker image to GitLab Container Registry under the `:develop` tag, the local sandbox is up, and the generated smoke-test suite passes.

### Execution model

Phase 2 runs as **one linear, abort-on-error, build-locally-first** job per project. Two policies frame everything:

* **Build-locally-first.** Code does not reach GitLab until every local check is green. Generation, compilation, Docker image build, sandbox bring-up, and smoke tests all happen on the advisor host *before* any `git push` or `docker push` to GitLab. A failed local check leaves zero side effects on GitLab — the implementer iterates locally without polluting the GitLab repo with broken commits or the Container Registry with unusable images.
* **Abort-on-error.** Activities run in strict order. If Activity *N* fails, Activity *N+1* never starts. The advisor reports the failure with the failing step + captured logs, the implementer fixes the underlying cause (usually a Discovery answer or a model output), and re-runs the entire phase from scratch. There is no resume mid-flight.

Inputs are collected upfront. The advisor refuses to start the build if any required Discovery item is missing.

The job produces side effects in three places: the project workspace on the advisor host (filesystem), a local docker-compose stack on the advisor host (sandbox), and — only after every local check succeeds — the implementer's GitLab subgroup (two repositories + their Container Registry images).

The job is idempotent at the granularity of the whole run: re-running rewrites the workspace, replaces the local sandbox stack, force-pushes to the same GitLab repositories, and overwrites the same image tags in the Container Registry. Re-runs leverage Docker layer caching and git's incremental push, so unchanged work is cheap.

**Update / change loop.** When the implementer changes any Phase 2 Discovery answer after a successful build, re-running the build re-executes every Activity. Activities 1–10 regenerate the workspace + images; 11–12 redeploy + retest the sandbox; 13–16 republish to GitLab and refresh the Build Report. Same abort-on-error semantics; same build-locally-first ordering.

### Discovery items

**Build identity**

#### organisation_mnemonic

* **Ask:** What is a short identifier for the implementing organisation? Pick a 2–15-character lowercase code that reads as the org's "stamp" on the generated artefacts (e.g. `doh` for Department of Health, `moh` for Ministry of Health, `tnsr` for Tanzania National Social Registry).
* **Why:** Becomes the leading segment of every generated Docker image name (`<org>-<registry_mnemonic>-<service>:develop`) and the Helm wrapper-chart name (`<org>-<registry_mnemonic>-registry`). Without this, image names default to `openg2p-...` and read as generic OpenG2P artefacts rather than this implementer's customised stack.
* **Required:** yes
* **Type:** text
* **Impact:** configuration
* **Validation:** lowercase letters, digits, and hyphens only; 2–15 characters; cannot start or end with a hyphen.
* **Examples:** `doh` ✓, `tnsr` ✓, `dept-of-health` ✓, `Department of Health` ✗ (use the org's name elsewhere; this is just a short identifier).

#### registry_mnemonic

* **Ask:** What is the registry mnemonic — a short identifier code used in filenames, image names, service names, GitLab repository names, and URLs?
* **Why:** Drives every generated artefact: Python package names, table prefixes, image names, GitLab project slugs.
* **Required:** yes
* **Type:** text
* **Impact:** configuration
* **Validation:** lowercase letters and hyphens only; no whitespace; must not include the word `registry`; 3–30 characters.
* **Examples:** `health-worker` ✓, `HealthWorkerRegistry` ✗, `health worker registry` ✗

#### registry_logo_small

* **Ask:** Provide a small-sized logo image for the Registry or the implementing department (used in the staff portal header and beneficiary portal small-format placements).
* **Why:** Compiled into the customised UI images. Sized for header use.
* **Required:** yes
* **Type:** file (image)
* **Impact:** configuration

#### registry_logo_medium

* **Ask:** Provide a medium-sized logo image for the Registry or the implementing department (used in landing pages, generated reports, and printed cards).
* **Why:** Compiled into the customised UI images. Sized for full-width and print use.
* **Required:** yes
* **Type:** file (image)
* **Impact:** configuration

#### ui_theme

* **Ask:** Does the department have a UI theme — fonts, colours, accents — that the registry should adopt? Describe it (or attach a brand kit).
* **Why:** Drives staff-portal-ui theme overrides and beneficiary portal styling.
* **Required:** no
* **Type:** prose
* **Impact:** configuration

#### register_mnemonics

* **Ask:** Provide a mnemonic for every Register and supporting Table identified in Phase 1 — short identifier codes used in code generation, table names, model class names, and service paths.
* **Why:** Each Register/Table mnemonic becomes a Python module name, an ORM class suffix, a database table name (`g2p_register_<mnemonic>s`), and a service path component. Distinct from `registry_mnemonic` (which identifies the overall registry).
* **Required:** yes
* **Type:** classification — a map of register/table name to mnemonic.
* **Impact:** code
* **Validation:** lowercase letters and hyphens only; no whitespace; unique within the project.
* **Examples:** `{ "Households Register": "household", "Individuals Register": "individual", "Land Holdings": "land" }`

**Schema and constraints**

#### register_columns

* **Ask:** For each Register and supporting Table, list the exact names and data types of the database columns.
* **Why:** Names and types are used directly during code generation; exactness matters for ORM models, migrations, schemas, and UI generation.
* **Required:** yes
* **Type:** classification — a map of register/table name to an ordered list of `{column_name, type}` entries.
* **Impact:** code

#### attribute_constraints

* **Ask:** For each column, which are NOT NULL, which have a default value, and what are those defaults?
* **Why:** NOT NULL and DEFAULT clauses are emitted into ORM model definitions and migration SQL. Without this the build cannot decide nullability and would have to guess — kept separate from `database_constraints` (which covers cross-column / cross-table rules) to make the per-column shape explicit upfront.
* **Required:** yes
* **Type:** classification — a map of `register/table name → column_name → {nullable: bool, default: <value | null>}`.
* **Impact:** code
* **Examples:** `{ "Households Register": { "head_of_household_id": { "nullable": false, "default": null }, "registered_at": { "nullable": false, "default": "now()" } } }`

#### database_constraints

* **Ask:** What database constraints apply between tables and columns — foreign keys, unique constraints, check constraints?
* **Why:** Reflected in generated migrations and validation logic. Determines referential integrity.
* **Required:** yes
* **Type:** list of `{kind: foreign_key | unique | check, ...}` records.
* **Impact:** code

#### functional_id_encoding_pattern

* **Ask:** What is the exact pattern for the Functional ID — fixed prefix, fixed suffix, separator, body composition (sequential, random, year-prefixed, etc.)?
* **Why:** The Functional ID generator class in the extension package needs a deterministic pattern. Phase 1 captured length and high-level format; this captures the exact composition the generator emits, including any literal prefix/suffix per Register. Without it the build would have to invent the encoding.
* **Required:** yes
* **Type:** classification — a map of register name to `{prefix, suffix, separator, body_kind: sequential | random | year_seq, body_length}`.
* **Impact:** code
* **Examples:** `{ "Households Register": { "prefix": "HH-", "suffix": "", "separator": "", "body_kind": "sequential", "body_length": 8 } }`

**Notification payloads**

#### notification_payloads

* **Ask:** For each triggering event captured in `notification_triggering_events` during Phase 1, provide the payload (subject, body template, variables) for SMS and Email notifications.
* **Why:** Drives generation of notification templates seeded into the registry's outbound-message tables.
* **Required:** conditional: `notification_triggering_events` is non-empty
* **Type:** classification — a map of event name to `{sms, email}` payload templates.
* **Impact:** code

**Deployment shape**

#### production_domain_name

* **Ask:** What will be the domain name(s) the Registry uses in production? List all that apply (e.g., one for the staff portal, one for the beneficiary portal, one for partner APIs).
* **Why:** Drives Helm/ingress values, certificate generation, and external URL patterns baked into the deployment chart.
* **Required:** yes
* **Type:** list
* **Impact:** deployment
* **Examples:** `staff.registry.gov.cs`, `portal.registry.gov.cs`, `api.registry.gov.cs`

#### sandbox_base_domain

* **Ask:** What base domain should the sandbox use? Internal-only, not exposed to the public.
* **Why:** Configures sandbox ingress routing for the docker-compose stack on the advisor host. Default is `*.<registry_mnemonic>.internal` if unanswered.
* **Required:** no
* **Type:** text
* **Impact:** deployment
* **Examples:** `*.health-worker.internal`, `*.farmer-registry.dev`

#### helm_resource_profile

* **Ask:** What replica count and per-pod CPU/memory request should each component (staff-portal-api, partner-api, celery, staff-portal-ui, db) be sized at for production? A simple T-shirt size is acceptable (`small | medium | large`); custom per-component overrides are also accepted.
* **Why:** Drives `replicas:` and `resources.requests` blocks in the generated Helm wrapper chart's `values.yaml`. Sandbox always uses `small` regardless of this answer.
* **Required:** yes
* **Type:** classification — either a single t-shirt size or a map of component → `{replicas, cpu, memory}`.
* **Impact:** deployment
* **Examples:** `"medium"` or `{ "staff-portal-api": { "replicas": 3, "cpu": "500m", "memory": "1Gi" } }`

**Brownfield migration (informational)**

#### migration_plan_summary

* **Ask:** If this registry will replace or absorb data from an existing system, summarise the cutover plan in one paragraph: source system(s), record volume, planned migration approach (bulk import / incremental sync / parallel run), and target cutover date if known.
* **Why:** Recorded in the Build Report for traceability. Does not affect generated code in v2.0; future versions may use this to schedule the migration sub-track.
* **Required:** conditional: `existing_system_to_replace` (Phase 1) is non-empty
* **Type:** prose
* **Impact:** migration

**GitLab workspace**

#### gitlab_user_handle

* **Ask:** What is your GitLab username on `gitlab.com`? The advisor will create a private subgroup `OpenG2P/g2p-advisor/<your-username>/` and place the generated repositories under it.
* **Why:** Determines the per-implementer subgroup path. GitLab usernames are globally unique, so the path is collision-free without an extra suffix.
* **Required:** yes
* **Type:** text
* **Impact:** deployment
* **Validation:** must match GitLab's username rules (lowercase, alphanumerics, dashes/underscores; 2–255 chars).

#### gitlab_user_email

* **Ask:** What email address should be added as a `Developer` member on the two generated GitLab projects? Use the email tied to your GitLab account so you receive CI notifications and can clone via SSH.
* **Why:** The advisor's GitLab service token creates the projects, but the implementer is the human owner. Adding them as Developer grants pull/push and pipeline-trigger access without giving them group-admin rights they shouldn't need.
* **Required:** yes
* **Type:** text
* **Impact:** deployment
* **Validation:** valid email; should match the GitLab account associated with `gitlab_user_handle`.

### Activities

The advisor's build executor runs these Activities sequentially as one linear, **abort-on-error, build-locally-first** job. Every Activity either succeeds or aborts the phase; there is no pause / resume.

The order below is the contract — the orchestrator implementation MUST execute Activities in this exact sequence. Activities 1–12 happen entirely on the advisor host (no GitLab side effects). Activities 13–16 publish to GitLab only AFTER 1–12 have all succeeded. A failed local Activity leaves zero remote artefacts.

Each Activity body declares: **Inputs** consumed (Discovery items / prior outputs), **Side effects** (workspace, sandbox, GitLab, registry), and **On failure** semantics.

#### 1. collect_build_inputs

* **Inputs:** every required Phase 2 Discovery item.
* **Side effects:** none. Just validates working_case.
* **On failure:** abort with a "missing inputs" list. The implementer fills the gaps via Phase 2 chat and re-runs.

Confirm every required Phase 2 Discovery item is present in working_case. If any required item is missing or invalid, abort before opening a build job. Otherwise present a one-line input summary in the activity log and proceed.

#### 2. prepare_gitlab_workspace

* **Inputs:** `gitlab_user_handle`, `gitlab_user_email`, `registry_mnemonic`, `organisation_mnemonic`.
* **Side effects:** GitLab — creates subgroup + two project shells (extension + deployment), invites Developer, allowlists CI_JOB_TOKEN, unprotects `develop`. Idempotent.
* **On failure:** abort. Permission errors (token scope, project-deletion-grace-period, etc.) surface here.

Reserve the GitLab namespace early so we know the image-registry path before the local build (the docker images are tagged with this path even though they're not pushed until Activity 15). Subgroup at `OpenG2P/g2p-advisor/<gitlab_user_handle>`. Two private projects under it: `<registry_mnemonic>-extension` and `<registry_mnemonic>-deployment`, default branch `develop`. The deployment project's CI_JOB_TOKEN is allowlisted to read the extension project. The implementer is added as Developer on both. **Refuse to use a project that is in GitLab's deletion grace period** (path suffix `-deletion_scheduled-<id>`); surface a clear error so the implementer either waits or chooses a different mnemonic.

#### 3. clone_reference_registry

* **Inputs:** none.
* **Side effects:** workspace — fresh clone of Farmer Registry into `<workspace>/reference/`.
* **On failure:** abort. Network / git-clone errors.

Clone Farmer Registry (`https://github.com/OpenG2P/farmer-registry`) at the configured branch into the project workspace. The clone is the substitution surface; the advisor never edits Farmer Registry itself.

#### 4. generate_extension_files

* **Inputs:** `register_mnemonics`, `register_columns`, `attribute_constraints`, `database_constraints`, `functional_id_encoding_pattern`, `notification_payloads` (optional), `organisation_mnemonic`, `registry_mnemonic`.
* **Side effects:** workspace — writes the customised extension repo to `<workspace>/extension/`. **No GitLab push.**
* **On failure:** abort. LLM errors, codegen schema violations, file-write errors.

Adapt the cloned reference's `farmer-extension/` into the customised extension. Specifically: rename the Python package, generate per-Register model + schema + service + factory files (LLM-driven), regenerate `app.py` migrations registration, regenerate the ID generator from `functional_id_encoding_pattern`, regenerate the seed SQL trees (register-metadata, sample-data, lookup-data), apply attribute and database constraints. The result is committable code in `<workspace>/extension/`.

#### 5. review_extension_code

* **Inputs:** generated per-Register files at `<workspace>/extension/src/<package>/register_domain/`, the Discovery items the codegen consumed (`register_columns`, `attribute_constraints`, `functional_id_encoding_pattern`, `register_mnemonics`).
* **Side effects:** none. Read-only LLM-driven review.
* **On failure:** abort with the structured list of findings. Each finding identifies the file + the specific contract violation. Common cause: LLM omitted a column from the model, picked the wrong base class, or hardcoded a value that should come from inputs.

Run a build-mode LLM pass over every generated per-Register Python file (`models/<mnemonic>.py`, `schemas/<mnemonic>.py`, `services/<mnemonic>.py`). The review compares each file against the Discovery items as ground truth and produces a structured findings list via a `submit_findings` tool call. Findings have a severity:

* **critical** — aborts the phase. Examples: a column from `register_columns` is missing as a `Mapped[…]` field; `__tablename__` doesn't match `g2p_register_<plural>`; class name doesn't follow the `G2PRegister<Pascal>` contract; an import references an undeclared symbol; the ID generator hardcodes a prefix that should come from `functional_id_encoding_pattern`.
* **warning** — surfaced in the activity log; build proceeds. Examples: nullable / default drift between SQLAlchemy column and Pydantic schema; identifying-column choice in `construct_search_text` looks weak.

This is the LLM's structured second-pass review; `compile_extension` (next) catches Python syntax errors that this review can't reasonably check. Together they cover most of the codegen failure surface before any Docker build runs.

#### 6. compile_extension

* **Inputs:** generated extension at `<workspace>/extension/`.
* **Side effects:** none. Read-only validation.
* **On failure:** abort. Surface the compile error tail to the chat for diagnosis. Common cause: codegen produced syntactically invalid Python.

Run `python -m py_compile` over every `.py` file in the extension package. Catches syntax errors in seconds, before any container build.

#### 7. generate_deployment_files

* **Inputs:** `helm_resource_profile`, `production_domain_name`, `sandbox_base_domain`, `organisation_mnemonic`, `registry_mnemonic`, image base path computed from Activity 2.
* **Side effects:** workspace — writes Dockerfiles, Helm wrapper chart, sandbox compose file, README, disabled `.gitlab-ci.yml` to `<workspace>/deployment/`.
* **On failure:** abort.

Adapt the reference's `docker/` and `helm/` into the customised deployment repo. Substitute farmer→`<org>-<mnemonic>` per the substitution map. Generate the Helm `Chart.yaml` + `values.yaml` from inputs. Generate the `docker-compose.sandbox.yaml`. Generate a stub `.gitlab-ci.yml` with `workflow.rules: when: never` (CI is disabled in v0.x because builds happen locally; the file is preserved as a hook for future toggling).

#### 8. compile_deployment

* **Inputs:** generated deployment at `<workspace>/deployment/`.
* **Side effects:** none. Read-only validation.
* **On failure:** abort. Surface the offending file + parser error.

Run `helm lint` on the wrapper chart and parse every YAML file with a strict YAML parser. Catches malformed templates and bad indentation before the docker build.

#### 9. build_images_locally

* **Inputs:** `<workspace>/deployment/` + staged copy of `<workspace>/extension/`.
* **Side effects:** advisor host docker daemon — produces locally-tagged images. **No `docker push`.**
* **On failure:** abort. Surface the docker-build log tail.

Build all five service images with `docker build`, tagging each with the GitLab Container Registry path. Backend services (staff-portal-api, partner-api, celery, staff-portal-ui) use `docker/scripts/build.sh` from the reference; db-seed uses a direct `docker build` with `--build-arg EXTENSION_DIR`. Layer caching keeps re-runs fast when only minor changes were made.

#### 10. generate_test_suite

* **Inputs:** `register_mnemonics`, `register_columns`, `functional_id_encoding_pattern`, `notification_payloads` (optional), generated deployment workspace.
* **Side effects:** workspace — writes `tests/` under `<workspace>/deployment/`.
* **On failure:** abort.

Generate a Python pytest suite tailored to this build:

* `tests/api/` (`pytest` + `httpx`) — one module per Register with create / read / update / list, plus Functional ID format check, plus a smoke check on every notification template if `notification_payloads` is non-empty.
* `tests/ui/` (`pytest-playwright`, headless Chromium) — staff-portal flows: login, navigate to each Register's list view, create a record, see it in the list.
* `tests/conftest.py` — fixtures pointing at the running sandbox (set by Activity 11).

The Farmer Registry reference carries no tests. This suite is generated from scratch by the advisor and committed in Activity 13. Tests are reusable beyond the build phase: the implementer takes them with the deployment repo and re-runs them in pilot / production.

#### 11. deploy_local_sandbox

* **Inputs:** `<workspace>/deployment/` (containing the generated compose file), local docker images from Activity 9.
* **Side effects:** advisor host — brings up a per-project docker-compose stack.
* **On failure:** abort. Surface the failing service's logs.

Bring up the customised stack via `docker compose -f docker-compose.sandbox.yaml up -d`. Detect the available compose CLI (`docker compose` v2 plugin or `docker-compose` v1 binary; honour `DOCKER_COMPOSE_CMD`). Wait for every service's healthcheck. Tear down any prior sandbox for this project first.

#### 12. run_smoke_tests

* **Inputs:** generated test suite at `<workspace>/deployment/tests/`, running sandbox from Activity 11.
* **Side effects:** none beyond test artefacts (logs, JUnit XML).
* **On failure:** abort. **No GitLab push happens.** Surface failing test names + assertions to the chat.

Execute `pytest tests/api tests/ui` against the running sandbox. The phase advances to publishing only if both layers pass.

#### 13. push_extension_repo

* **Inputs:** `<workspace>/extension/`, GitLab project from Activity 2.
* **Side effects:** GitLab — git push to `<mnemonic>-extension` `develop`. **First publishing Activity.**
* **On failure:** abort.

Init git in the extension workspace, commit, and force-push to GitLab. By the time this runs, the code has been compiled, the docker image built using it, the sandbox brought up using that image, and smoke tests passed against the sandbox. Pushing here means everything is genuinely green.

#### 14. push_deployment_repo

* **Inputs:** `<workspace>/deployment/`, GitLab project from Activity 2, generated test suite.
* **Side effects:** GitLab — git push to `<mnemonic>-deployment` `develop`.
* **On failure:** abort.

Same shape as Activity 12 but for the deployment repo. The push includes the generated `tests/` directory so the implementer can re-run the suite in their own environment later.

#### 15. push_images_to_registry

* **Inputs:** locally-tagged images from Activity 9, GitLab project's Container Registry.
* **Side effects:** GitLab Container Registry — `docker push` for each image.
* **On failure:** abort.

`docker login` to the GitLab Container Registry, then `docker push` for each image. Tag is `:develop`.

#### 16. produce_build_report

* **Inputs:** every captured artefact reference (workspace, GitLab URLs, image refs, test results).
* **Side effects:** `phase_reports/` on disk (a new versioned report file).
* **On failure:** the build is functionally done; report failures should not block the implementer. Surface the error but mark the build as succeeded.

Generate the Build Report (see [Output](#output)) and present it to the implementer for approval per the Phase Transition Protocol. On approval, save via the `save_phase_report` tool and call `phase_complete` to advance to Phase 3.

### Testing contract

Phase 2 generates and runs a real test suite — it's not a smoke check that's thrown away.

**Test layers:**

| Layer | Tool | Catches | When it runs |
|---|---|---|---|
| LLM-driven code review | build-mode LLM with `submit_findings` tool | Generated code drift from Discovery items: missing columns, wrong base classes, hardcoded values | Activity 5 |
| Compile / lint | `python -m py_compile`, `helm lint`, YAML parser | Syntax errors, malformed templates, bad indentation | Activities 6 + 8 |
| Local Docker build | `docker build` | Dockerfile path issues, dep install failures, base-image mismatches, missing system packages | Activity 9 |
| Local sandbox bring-up | `docker compose up -d` + healthchecks | Service-level wiring: containers actually start, healthchecks pass, DB seeds run, Keycloak realm imports | Activity 11 |
| Generated smoke tests (API) | `pytest` + `httpx` | API correctness per Register: create / read / list, Functional ID encoding, notification template generation | Activity 12 |
| Generated smoke tests (UI) | `pytest-playwright` (headless Chromium) | UI correctness: login, navigate to each Register list view, create-and-see-in-list flow | Activity 12 |
| Live regression suite (the same generated tests, re-runnable later) | `pytest` from the cloned deployment repo | Same coverage; manual / scheduled runs against pilot / prod environments | Manual, post-handover |

**Test generation parameters.** Tests are parameterised — they are not a fixed scaffold. Inputs that drive what gets generated:

* `register_mnemonics` → one test module per Register
* `register_columns` + `attribute_constraints` → field-level assertions in create / read tests
* `functional_id_encoding_pattern` → Functional ID format check per Register
* `notification_payloads` → notification template smoke checks (skipped if empty)
* `production_domain_name` → expected `Host` headers in API tests (sandbox uses internal hostnames)

**Failure semantics.** A failure at any test layer aborts the phase before any GitLab push happens. The advisor surfaces the failure in the Build Activity Panel + Phase 2 chat for diagnosis. The implementer iterates locally (typically by changing a Discovery answer and re-running) until tests pass; only then does code reach GitLab.

**Tests as artefacts.** The generated test suite is committed to the deployment repo (Activity 13). The implementer takes ownership of it at handover. They can re-run `pytest` against pilot / production environments to validate later changes.

### References

* Farmer Registry reference repository: `https://github.com/OpenG2P/farmer-registry` — the structural baseline this phase substitutes against.
* Registry extensions package conventions and the extension build contract (multiple-inheritance pattern: `G2PRegister<Entity>(G2PRegister, G2PPerson, G2PGeo, G2P<Entity>)`).
* Registry deployment repository conventions: per-service `Dockerfile` + `develop.txt`, wrapper Helm chart over `openg2p-registry` base chart, sample-data SQL seeds keyed per Register/Table.
* `g2p_register_definitions` schema and master-register hierarchy.
* GitLab Container Registry conventions: image path `registry.gitlab.com/<group>/<project>/<service>:<tag>`.
* OpenG2P Registry feature and configuration surface.

### Gap analysis

Before producing the Build Report, the advisor verifies:

* Every required Phase 2 Discovery item is recorded.
* Activity 5 (review_extension_code) raised no critical findings.
* Activities 6 (compile_extension) and 8 (compile_deployment) exited clean.
* Activity 9 (build_images_locally) produced every expected image tag in the local docker daemon.
* Activity 11 (deploy_local_sandbox) brought up every service with healthchecks passing.
* Activity 12 (run_smoke_tests) exited 0 — both `tests/api/` and `tests/ui/` passed against the running sandbox.
* Activities 13 + 14 pushed the extension and deployment repos to GitLab; both contain the latest generated code on `develop`.
* `gitlab_user_email` is a Developer on both GitLab projects.
* Activity 15 published every expected image to the deployment project's Container Registry under `:develop`.

### Output

**Build Report**, with these sections:

1. **Build identity** — `registry_mnemonic`, `register_mnemonics`, `ui_theme` summary, logos referenced.
2. **Schema summary** — Registers, supporting Tables, columns, attribute constraints, cross-table constraints, Functional ID encoding patterns applied.
3. **GitLab artefacts** — links to the two created projects (`<mnemonic>-extension`, `<mnemonic>-deployment`), the final commit SHAs on `develop`, the CI pipeline URLs, and the published image references in Container Registry.
4. **Helm + deployment summary** — chart name, applied `helm_resource_profile`, `production_domain_name` ingress entries, sandbox base domain.
5. **Test suite summary** — generated test counts (API + UI), pass/fail per layer, link to the captured smoke-test log.
6. **Sandbox deployment** — docker-compose CLI used, sandbox URL on the advisor host, port range allocated.
7. **Brownfield migration plan** — verbatim from `migration_plan_summary` (informational only).

### Common pitfalls

(none recorded yet)

***

## Phase 3: Sandbox

### Purpose

Deploy the built Docker images to a sandbox (development) environment and verify the registry works end-to-end. This is the first live deployment of the customised registry.

### Enter / Exit

* **Enter when:** the Build Report is approved and Docker images are available.
* **Exit when:** _(to be defined when phase details are added)_.

### Discovery items

The Phase 3 Discovery items below capture infrastructure and access information needed for the **production** rollout. They are gathered during the sandbox phase because the answers (especially SSL/DNS lead times) determine the Phase 5 rollout schedule. The sandbox itself does NOT require these — sandbox uses the internal base domain captured in Phase 2 and doesn't issue real SSL certificates.

**Production domains, certificates, and DNS**

#### ssl_cert_acquisition

* **Ask:** How easily and quickly can you acquire SSL certificates for the production domains listed in `production_domain_name`? Describe the process, the certificate authority, and the typical lead time.
* **Why:** SSL acquisition lead time is the long pole in many deployments. Captured in Phase 3 so Phase 5 (Full Rollout) scheduling is realistic. Sandbox doesn't need this.
* **Required:** yes
* **Type:** prose
* **Impact:** deployment
* **Examples:** "Let's Encrypt automated, ~5 minutes"; "Internal CA, 2-week request process"; "Commercial cert via department procurement, 4-6 weeks".

#### wildcard_ssl_supported

* **Ask:** Can you obtain a wildcard SSL certificate (e.g., `*.registry.gov.cs`) so that subdomains can be assigned without per-subdomain certificates?
* **Why:** Wildcards dramatically simplify multi-service deployments (staff portal + beneficiary portal + partner API + sandbox subdomains all on one cert). Drives ingress and subdomain-allocation strategy.
* **Required:** yes
* **Type:** boolean
* **Impact:** deployment

#### dns_access_lead_time

* **Ask:** Do you (or your teams) have access to a DNS server that can point to the production system? How long will DNS configuration take?
* **Why:** DNS access and lead time are go-live gates. Drives Phase 5 (Full Rollout) sequencing and identifies whether DNS work needs to start in parallel with build/sandbox or can be deferred to rollout.
* **Required:** yes
* **Type:** prose
* **Impact:** deployment
* **Examples:** "Direct access via Route53, immediate"; "Submit ticket to central IT, 2-day SLA"; "Department doesn't control DNS, requires inter-ministry coordination, 2-4 weeks".

### Activities

_(to be added)_

### References

_(to be added)_

### Gap analysis

_(to be added)_

### Output

_(to be added)_

### Common pitfalls

(none recorded yet)

***

## Phase 4: Pilot

### Purpose

Deploy to a limited production-like environment with real users and real data at reduced scale. Validate the registry against actual operational requirements before full rollout.

### Enter / Exit

* **Enter when:** Sandbox deployment is verified.
* **Exit when:** _(to be defined when phase details are added)_.

### Discovery items

_(to be added)_

### Activities

_(to be added)_

### References

_(to be added)_

### Gap analysis

_(to be added)_

### Output

_(to be added)_

### Common pitfalls

(none recorded yet)

***

## Phase 5: Full Rollout

### Purpose

Deploy to the full production environment at planned scale. Includes data migration (for brownfield implementations), staff training, and operational handover.

### Enter / Exit

* **Enter when:** Pilot is approved.
* **Exit when:** _(to be defined when phase details are added)_.

### Discovery items

_(to be added)_

### Activities

_(to be added)_

### References

_(to be added)_

### Gap analysis

_(to be added)_

### Output

_(to be added)_

### Common pitfalls

(none recorded yet)
