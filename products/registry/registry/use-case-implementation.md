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

#### implementing_organisation

* **Ask:** Which department, agency, or organisation will host this Registry?
* **Why:** Identifies the operational owner and the stakeholder model; informs operational handover and access policies.
* **Required:** yes
* **Type:** text

#### registry_name

* **Ask:** What is the full name of the Registry?
* **Why:** Used in user-facing labels and report headers.
* **Required:** yes
* **Type:** text

#### registry_logo_small

* **Ask:** Provide a small-sized logo image for the Registry or the implementing department.
* **Why:** Used in the staff portal header and beneficiary portal small-format placements.
* **Required:** yes
* **Type:** file (image)

#### registry_logo_medium

* **Ask:** Provide a medium-sized logo image for the Registry or the implementing department.
* **Why:** Used in landing pages, generated reports, and printed cards.
* **Required:** yes
* **Type:** file (image)

#### supported_languages

* **Ask:** In which languages will users access the platform?
* **Why:** Drives Keycloak theme and frontend i18n configuration, and number/date format selection.
* **Required:** yes
* **Type:** list

#### use_case_detail

* **Ask:** Describe the end-to-end use case in prose. How will registry data be consumed and by whom? Will data be shared with other departments, systems, agencies, or applications?
* **Why:** Drives integration scope and informs the gap analysis on data sharing and interoperability. Catches narrative context that the structured items below cannot.
* **Required:** yes
* **Type:** prose
* **Affects:** Phase 1 gap analysis on interoperability; integration design in later phases.

---

**Registry typology**

#### registry_typology

* **Ask:** Is this Registry serving a specific benefit-delivery programme, or is it a general-purpose registry?
* **Why:** Determines registry typology and the feature set the advisor surfaces during Product Feature Discovery.
* **Required:** yes
* **Type:** enum \[`specific-programme`, `general-purpose`]
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
* **Examples:** A Social Registry typically has two Registers — a Households Register and an Individuals Register, where an Individual reports into a Household.

#### registers_physical_object

* **Ask:** For each Register, what is the physical object it identifies?
* **Why:** Anchors the domain model. Affects ID generation rules and UI defaults.
* **Required:** yes
* **Type:** classification — a map of register name to physical object kind.
* **Examples:** PERSON, HOUSE, VEHICLE, SCHOOL, FARM, LAND PARCEL.

#### supporting_tables

* **Ask:** What supporting tables (child entities) are required to complement the main Registers? For each, indicate which Register it relates to.
* **Why:** Supporting tables capture multi-valued attributes (e.g., a person's land holdings, a household's assets). They become tables linked to the main Registers via foreign keys.
* **Required:** yes
* **Type:** list
* **Examples:** A Land table for an Individual where each individual may own multiple land parcels.

#### main_register_attributes

* **Ask:** List all attributes for the Main Registers.
* **Why:** Forms the schema for the Register tables. Each attribute becomes a column with a chosen type.
* **Required:** yes
* **Type:** classification — a map of register name to list of attribute names with types.

#### supporting_table_attributes

* **Ask:** List all attributes for the Supporting Tables.
* **Why:** Forms the schema for the supporting tables.
* **Required:** yes
* **Type:** classification — a map of supporting table name to list of attribute names with types.

---

**Foundational ID**

#### has_foundational_id

* **Ask:** If a main Register identifies a person, does the country have a nationwide Foundational Identity?
* **Why:** Determines whether identity verification can rely on the national identity provider or requires an alternative mechanism.
* **Required:** conditional: any Register has registers_physical_object = PERSON
* **Type:** boolean
* **Follow-ups (when yes):** all subsequent Foundational ID items below.

#### foundational_id_name

* **Ask:** What is the name of this Foundational Identity?
* **Why:** Used in generated UI labels and configuration references.
* **Required:** conditional: has_foundational_id = yes
* **Type:** text
* **Examples:** PHILSYS National ID (Philippines), AADHAAR (India), Fayda National ID (Ethiopia).

#### foundational_id_responsible_department

* **Ask:** Which department is responsible for allocation of this Foundational Identity?
* **Why:** Identifies the integration counterpart and the governance owner of the ID.
* **Required:** conditional: has_foundational_id = yes
* **Type:** text

#### foundational_id_verification_mechanism

* **Ask:** How will your department verify the Foundational ID?
* **Why:** Affects integration design between the registry and the national identity provider.
* **Required:** conditional: has_foundational_id = yes
* **Type:** prose

#### foundational_id_biometrics

* **Ask:** Are biometrics involved in the verification?
* **Why:** Drives device requirements for field agents and additional integration considerations.
* **Required:** conditional: has_foundational_id = yes
* **Type:** boolean

#### foundational_id_integration_mechanism

* **Ask:** What integration mechanism exists for verification of the Foundational ID? Does it follow any standard, e.g., OIDC?
* **Why:** Determines the eSignet / OAuth-OIDC configuration approach.
* **Required:** conditional: has_foundational_id = yes
* **Type:** prose

#### foundational_id_kyc_periodicity

* **Ask:** How frequently do individuals have to verify themselves with the Foundational ID — i.e., the KYC periodicity?
* **Why:** Drives scheduled re-verification jobs and consent renewal flows.
* **Required:** conditional: has_foundational_id = yes
* **Type:** text

#### foundational_id_length

* **Ask:** How long is the Foundational ID — number of characters?
* **Why:** Required for input validation and storage column sizing.
* **Required:** conditional: has_foundational_id = yes
* **Type:** number

#### foundational_id_format

* **Ask:** Is the Foundational ID alphanumeric or pure numeric?
* **Why:** Drives input validation regex and storage type.
* **Required:** conditional: has_foundational_id = yes
* **Type:** enum \[`alphanumeric`, `numeric`]

#### foundational_id_prefix_suffix_encoding

* **Ask:** Does the Foundational ID have any prefix or suffix encoding tied to geographic or other demographic profile?
* **Why:** Affects ID parsing logic and any region-derived attributes.
* **Required:** conditional: has_foundational_id = yes
* **Type:** prose

#### foundational_id_attributes_stored

* **Ask:** What attributes does the Foundational ID system store? (Name, date of birth, address, etc.)
* **Why:** Determines which attributes the registry can fetch via verification vs. must collect itself.
* **Required:** conditional: has_foundational_id = yes
* **Type:** list

---

**Functional ID**

#### has_functional_id

* **Ask:** Apart from the Foundational ID, does your department issue any other ID to the Register records?
* **Why:** Triggers the functional ID generation and tracking subsystem.
* **Required:** yes
* **Type:** boolean

#### functional_id_examples

* **Ask:** Give examples of these functional IDs.
* **Why:** Helps clarify intent and naming conventions.
* **Required:** conditional: has_functional_id = yes
* **Type:** prose
* **Examples:** Voter ID (electoral register), Household ID (social register), Pension ID (pension register).

#### functional_id_length

* **Ask:** How long is the Functional ID — number of characters?
* **Why:** Used during code generation in the build phase.
* **Required:** conditional: has_functional_id = yes
* **Type:** number
* **Validation:** typically nine to twelve; confirm with implementer if outside this range.

#### functional_id_format

* **Ask:** Is the Functional ID alphanumeric or pure numeric?
* **Why:** Drives ID generation logic.
* **Required:** conditional: has_functional_id = yes
* **Type:** enum \[`alphanumeric`, `numeric`]

#### functional_id_prefix_suffix_encoding

* **Ask:** Does the Functional ID have any prefix or suffix encoding tied to geographic or other demographic profile?
* **Why:** Affects ID generation algorithm.
* **Required:** conditional: has_functional_id = yes
* **Type:** prose

#### functional_id_generation_timing

* **Ask:** When is the Functional ID generated — when the entity is registered, or when an application is received?
* **Why:** Determines whether ID generation is part of the registration workflow or a separate event.
* **Required:** conditional: has_functional_id = yes
* **Type:** enum \[`at-registration`, `at-application`, `other`]

#### functional_id_owning_department

* **Ask:** Is your department responsible for generating this Functional ID, or is there another department that allocates it?
* **Why:** Determines whether the registry generates IDs locally or integrates with an external service.
* **Required:** conditional: has_functional_id = yes
* **Type:** enum \[`own-department`, `external-department`]

#### functional_id_integration_mechanism

* **Ask:** If another department is responsible for allocation, what interface mechanism exists to facilitate this integration?
* **Why:** Drives external integration design.
* **Required:** conditional: functional_id_owning_department = external-department
* **Type:** prose

---

**Scores**

#### has_scores

* **Ask:** Do any of the identified Registers need scores computed for each record?
* **Why:** Drives the scoring subsystem in the registry. Scores affect indexing, search, eligibility, and reporting.
* **Required:** yes
* **Type:** boolean

#### scores_examples

* **Ask:** What scores are required and what do they represent?
* **Why:** Anchors the scoring logic to a real-world definition.
* **Required:** conditional: has_scores = yes
* **Type:** prose
* **Examples:** Poverty score (Social Registry), Disability score (Disability Registry), Food Security score.

#### scores_per_register

* **Ask:** How many scores are required for each Register, and what are they?
* **Why:** Each score becomes a configured score type with its own computation pipeline.
* **Required:** conditional: has_scores = yes
* **Type:** classification — a map of register name to list of score types.

#### scores_external_dependencies

* **Ask:** Do the parameters that contribute to each score depend only on attributes of the Register, or are there external dependencies (e.g., geographical region attributes)?
* **Why:** Affects whether the score computation is local or requires external lookups.
* **Required:** conditional: has_scores = yes
* **Type:** prose

#### scores_periodicity

* **Ask:** How frequently are these scores computed? Is there a specified periodicity (annual, monthly, etc.)?
* **Why:** Drives scheduled jobs in the celery worker.
* **Required:** conditional: has_scores = yes
* **Type:** text

#### scores_compute_on_change

* **Ask:** Are scores recomputed whenever there is any change in Register attributes?
* **Why:** Drives event-driven score recomputation logic.
* **Required:** conditional: has_scores = yes
* **Type:** boolean

#### scores_notify_registrant

* **Ask:** Does the registrant need to be notified about their score?
* **Why:** Drives notification triggers.
* **Required:** conditional: has_scores = yes
* **Type:** boolean

#### scores_notify_other_departments

* **Ask:** Do scores need to be published to any other department?
* **Why:** Drives outgoing integration / event-publishing design.
* **Required:** conditional: has_scores = yes
* **Type:** boolean

---

**Registration channel and enumeration**

#### registration_channel

* **Ask:** Will registration happen online via a portal, offline via field agents, or both?
* **Why:** Affects UI scope, sync behaviour, and offline tooling decisions.
* **Required:** yes
* **Type:** enum \[`online`, `offline`, `both`]

#### enumeration_field_agents

* **Ask:** Do you have field agents who visit the homes of people to enumerate them into the Registry?
* **Why:** Drives mobile-app and offline-first feature requirements.
* **Required:** yes
* **Type:** boolean

#### enumeration_offices_in_villages

* **Ask:** Do you have department offices in villages and towns to assist with the enumeration?
* **Why:** Affects deployment topology and access models for distributed offices.
* **Required:** yes
* **Type:** boolean

#### internet_connectivity_in_remote_regions

* **Ask:** What is the internet connectivity in the remote regions where enumeration takes place?
* **Why:** Drives offline-mode requirements and sync strategy.
* **Required:** yes
* **Type:** prose

#### enumeration_devices

* **Ask:** If field agents are involved, what devices do they carry — tablets, laptops, biometric devices?
* **Why:** Affects mobile-app target platforms and device-integration scope.
* **Required:** conditional: enumeration_field_agents = yes
* **Type:** list

#### uses_odk

* **Ask:** Do field agents use any other open-source framework like ODK to support their enumeration effort?
* **Why:** Drives ODK integration / form-import scope.
* **Required:** conditional: enumeration_field_agents = yes
* **Type:** boolean

#### enumeration_periodicity

* **Ask:** Are enumerations conducted periodically? If yes, how frequently?
* **Why:** Drives scheduled enumeration cycles and re-survey workflows.
* **Required:** yes
* **Type:** prose

---

**Required documents at registration**

#### required_documents

* **Ask:** What documents must registrants provide at registration time?
* **Why:** Drives upload, verification, and storage design — including blob storage configuration and document-verification workflow.
* **Required:** yes
* **Type:** list

---

**Workflow (record acceptance)**

#### approval_workflow_levels

* **Ask:** What is the workflow process involved in accepting a record into a Register? How many levels of approval are required before a record becomes valid?
* **Why:** Drives the approval-level configuration on each Register and the change-request workflow.
* **Required:** yes
* **Type:** number
* **Examples:** 0 (auto-approve), 1, 2, 3 levels of approval.

#### approval_workflow_approvers_login

* **Ask:** Are approvers expected to log into the Registry system to provide their approvals?
* **Why:** Drives access management and notification design for approvers.
* **Required:** yes
* **Type:** boolean

#### approval_workflow_approvers_location

* **Ask:** Are the approvers within the department office or remotely located?
* **Why:** Affects authentication strategy and offline considerations for approvers.
* **Required:** yes
* **Type:** enum \[`in-office`, `remote`, `both`]

#### approval_workflow_approvers_devices

* **Ask:** Do these approvers need device support for their activities?
* **Why:** Drives mobile-friendly approval UI scope.
* **Required:** yes
* **Type:** prose

---

**Changes / Edits to Registers**

#### edit_mechanism

* **Ask:** What is the mechanism for introducing edits to records in the Registers?
* **Why:** Drives the change-request flow and the user-facing edit UI.
* **Required:** yes
* **Type:** prose

#### edit_submission_channel

* **Ask:** How do registrants submit change requests — by visiting a department office, through a field agent, or online?
* **Why:** Drives UI scope and channel-specific workflows.
* **Required:** yes
* **Type:** enum \[`office`, `field-agent`, `online`, `multiple`]

#### edit_approval_workflow

* **Ask:** What is the workflow process to approve such edit requests?
* **Why:** Drives the change-request approval configuration, possibly distinct from new-record approval.
* **Required:** yes
* **Type:** prose

---

**Agent support**

#### agent_devices

* **Ask:** What kind of device support do agents require — laptops, tablets, both?
* **Why:** Affects target platforms for agent applications.
* **Required:** yes
* **Type:** list

#### agent_named_login

* **Ask:** Are agents named users with individual login profiles?
* **Why:** Drives identity provisioning for agents.
* **Required:** yes
* **Type:** boolean

#### agent_profile_management

* **Ask:** How are agent login profiles managed? Will the department administer them, or is another system involved?
* **Why:** Drives Keycloak realm configuration and admin workflow.
* **Required:** yes
* **Type:** prose

#### agent_authentication_with_foundational_id

* **Ask:** Will the Foundational ID be involved in any way to authenticate field agents?
* **Why:** Drives agent-app authentication design.
* **Required:** yes
* **Type:** boolean

---

**Beneficiary portal**

#### has_beneficiary_portal

* **Ask:** Does your department plan or already have a self-service portal for the registrants (beneficiaries)?
* **Why:** Determines whether the beneficiary portal API and frontend are in scope.
* **Required:** yes
* **Type:** boolean

#### beneficiary_portal_capabilities

* **Ask:** What can a registrant do on the portal that impacts or affects the Registry?
* **Why:** Defines the beneficiary portal's feature surface — view records, request edits, claim/attest, etc.
* **Required:** conditional: has_beneficiary_portal = yes
* **Type:** prose

#### beneficiary_portal_access_management

* **Ask:** How is access to the Beneficiary Portal managed? Is the national ID department involved in administering access?
* **Why:** Drives authentication integration for beneficiaries.
* **Required:** conditional: has_beneficiary_portal = yes
* **Type:** prose
* **Examples:** Aadhaar Login (India), PHILSYS authentication (Philippines).

---

**Integrations with other departments**

#### api_integrations

* **Ask:** What kind of API integrations will the Registry require?
* **Why:** Forms the baseline for the integration design.
* **Required:** yes
* **Type:** list

#### kyc_based_edits

* **Ask:** Will edits be triggered into a Register based on KYC updates from the Foundational ID department?
* **Why:** Drives event-subscription / sync design with the foundational ID provider.
* **Required:** yes
* **Type:** boolean

#### outgoing_notifications_on_edits

* **Ask:** Will you notify any other department when there are edits to a Register record? If yes, list those departments and the payload that is published, plus the trigger event.
* **Why:** Drives outgoing event-publishing and webhook configuration.
* **Required:** yes
* **Type:** prose

#### outgoing_periodic_publishes

* **Ask:** Are other departments notified periodically without any triggering event? E.g., a semi-annual feed published to another department of all the records.
* **Why:** Drives scheduled bulk-export jobs.
* **Required:** yes
* **Type:** prose

#### incoming_feeds

* **Ask:** Similar to outgoing publishes, do you receive any such publish from another department?
* **Why:** Drives ingestion-pipeline design.
* **Required:** yes
* **Type:** prose

#### incoming_feeds_approval_workflow

* **Ask:** If incoming feeds lead to edits in a Register, what is the approval workflow process to approve such edits?
* **Why:** Determines whether incoming-feed-driven changes are auto-applied or require approval.
* **Required:** conditional: incoming_feeds is non-empty
* **Type:** prose

#### vc_ingestion

* **Ask:** Does the Registry support ingestion using Verifiable Credentials? List the details of such use cases.
* **Why:** Drives VC-verification subsystem inclusion.
* **Required:** yes
* **Type:** prose

---

**Benefit programs**

#### registry_used_for_benefit_programs

* **Ask:** Will this Registry be used by your department (or any other department) for effecting any Benefit Programs?
* **Why:** Determines whether the Programme Register feature is in scope.
* **Required:** yes
* **Type:** boolean

#### benefit_programs_list

* **Ask:** List all such Programs and the departments that run them.
* **Why:** Drives the programme catalogue configuration.
* **Required:** conditional: registry_used_for_benefit_programs = yes
* **Type:** list

#### track_benefit_program_memberships

* **Ask:** Will this Registry be required to maintain a record of all the benefit programs that a registrant is part of?
* **Why:** Drives Programme Register + membership-tracking design.
* **Required:** conditional: registry_used_for_benefit_programs = yes
* **Type:** boolean

#### benefit_programs_scope

* **Ask:** If the Registry is aware of benefit-programme memberships, is it only the programmes administered by your department, or does it also cover programmes from other departments?
* **Why:** Determines cross-department integration scope for programme data.
* **Required:** conditional: track_benefit_program_memberships = yes
* **Type:** enum \[`own-department-only`, `cross-department`]

#### benefit_coverage_change_workflow

* **Ask:** How do changes in Benefit Program coverage (inclusions and exclusions) get effected in the Registry?
* **Why:** Drives the membership-update workflow.
* **Required:** conditional: track_benefit_program_memberships = yes
* **Type:** prose

---

**Verifiable Credentials**

#### issues_verifiable_credentials

* **Ask:** Does your department issue Verifiable Credentials (or plan to issue them) to the registrants?
* **Why:** Drives VC issuance subsystem inclusion.
* **Required:** yes
* **Type:** boolean

#### vc_platform

* **Ask:** If yes, has the VC platform been identified? Provide details.
* **Why:** Determines integration target for VC issuance.
* **Required:** conditional: issues_verifiable_credentials = yes
* **Type:** prose

---

**Cards and printouts**

#### registry_provides_cards

* **Ask:** Does your department provide cards or printouts to all the registrants?
* **Why:** Drives card-generation and printing subsystem design.
* **Required:** yes
* **Type:** boolean

#### card_contents

* **Ask:** What does the card or printout carry?
* **Why:** Defines the card layout template and the data fields included.
* **Required:** conditional: registry_provides_cards = yes
* **Type:** list

#### card_qr_code

* **Ask:** Does the card carry a QR code that needs to be authenticated from external systems?
* **Why:** Drives QR generation and verification-API design.
* **Required:** conditional: registry_provides_cards = yes
* **Type:** boolean

---

**Notifications (SMS / Email)**

#### has_notification_requirements

* **Ask:** Do you have notification requirements? Notifications to registrants? To agents? To staff users?
* **Why:** Determines whether the notification subsystem is in scope.
* **Required:** yes
* **Type:** prose

#### notification_triggering_events

* **Ask:** What are the triggering events that issue such notifications?
* **Why:** Drives the notification-trigger configuration.
* **Required:** conditional: has_notification_requirements is non-empty
* **Type:** list

---

**Greenfield vs brownfield decision**

#### existing_data

* **Ask:** Is this a greenfield implementation (fresh data collection) or brownfield (existing data to import)?
* **Why:** Brownfield implies a data-migration sub-track in later phases; greenfield does not.
* **Required:** yes
* **Type:** enum \[`greenfield`, `brownfield`]

#### existing_data_form

* **Ask:** In what form does the existing data exist — Excel, database, APIs of another system, or other?
* **Why:** Drives the ingestion connector design for migration.
* **Required:** conditional: existing_data = brownfield
* **Type:** classification

#### existing_registry_platform

* **Ask:** Does your department already have an existing Registry platform that you use today?
* **Why:** Identifies the source system for data migration.
* **Required:** conditional: existing_data = brownfield
* **Type:** prose

#### existing_registry_technology

* **Ask:** What technology platform is the current registry built on?
* **Why:** Drives migration-tooling selection (export formats, connector libraries).
* **Required:** conditional: existing_data = brownfield
* **Type:** prose

#### existing_registry_rdbms

* **Ask:** Provide RDBMS details of the current registry — vendor, version, schema specifics.
* **Why:** Determines the migration ETL approach.
* **Required:** conditional: existing_data = brownfield
* **Type:** prose

---

**Open-ended functional requirements**

#### functional_requirements

* **Ask:** What specific functionalities must OpenG2P Registry support for this use case? List every requirement, including any that may not be standard registry features and aren't covered by the questions above.
* **Why:** Catch-all for domain-specific needs not covered by the structured items. Forms the requirements baseline against which the gap analysis runs.
* **Required:** yes
* **Type:** list

---

**Infrastructure**

#### sandbox_on_cloud

* **Ask:** Is a sandbox on a public cloud acceptable for development?
* **Why:** Affects sandbox-phase deployment topology, separately from the production deployment.
* **Required:** yes
* **Type:** boolean

#### production_infrastructure

* **Ask:** Will the pilot and production systems run on on-premises hardware, on cloud, or in a hybrid configuration?
* **Why:** Affects later-phase deployment design and the support model.
* **Required:** yes
* **Type:** enum \[`on-prem`, `cloud`, `hybrid`]

#### existing_cloud_service_provider

* **Ask:** Do you already have a Cloud Service Provider empanelled within your department?
* **Why:** Determines whether the production deployment can use an existing CSP arrangement.
* **Required:** conditional: production_infrastructure in [`cloud`, `hybrid`]
* **Type:** prose

---

**Technology operations**

#### it_personnel_model

* **Ask:** Do you have skilled IT personnel to manage the Technology Operations for the Registry, do you plan to use a Software Service Provider, or a hybrid approach?
* **Why:** Determines support model and handover scope.
* **Required:** yes
* **Type:** enum \[`in-house`, `service-provider`, `hybrid`]

#### software_policies

* **Ask:** Does your department have established formal processes and policies with respect to software usage — open-source, proprietary software, etc.? Provide details.
* **Why:** Drives compliance considerations for the deployment.
* **Required:** yes
* **Type:** prose

#### network_for_distributed_offices

* **Ask:** If the Registry is to be used in distributed office environments (department offices, field agents), provide network details and bandwidth.
* **Why:** Drives sync strategy and offline-mode scope.
* **Required:** conditional: enumeration_offices_in_villages = yes OR enumeration_field_agents = yes
* **Type:** prose

#### needs_offline_features

* **Ask:** Do we need offline features? If yes, where — agent application, office terminals, both?
* **Why:** Drives offline-first and sync design.
* **Required:** yes
* **Type:** prose

---

**Volumetric**

#### record_scale_current

* **Ask:** What is the current volume of records (if there is an existing registry)?
* **Why:** Drives migration sizing and initial deployment topology.
* **Required:** yes
* **Type:** number

#### record_scale_5_year_estimate

* **Ask:** What is the estimated record volume over the next five years?
* **Why:** Drives capacity planning and topology decisions for production.
* **Required:** yes
* **Type:** number

---

**Usage stats**

#### staff_user_count

* **Ask:** Provide the expected number of Staff Users.
* **Why:** Drives capacity planning for the staff portal API and Keycloak realm.
* **Required:** yes
* **Type:** number

#### agent_user_count

* **Ask:** Provide the expected number of Agent Users.
* **Why:** Drives capacity planning for agent-application and partner-API loads.
* **Required:** yes
* **Type:** number

#### beneficiary_portal_user_volume

* **Ask:** If the Beneficiary Portal is involved, provide an estimate of beneficiary user volume.
* **Why:** Drives capacity planning for the beneficiary portal API.
* **Required:** conditional: has_beneficiary_portal = yes
* **Type:** number

#### integration_traffic_volumetrics

* **Ask:** If integration with other departments is involved, provide traffic volumetrics for these use cases.
* **Why:** Drives capacity planning for the integration tier.
* **Required:** conditional: api_integrations is non-empty
* **Type:** prose

---

**Interoperability**

#### interoperability_requirements

* **Ask:** Are there specific interoperability requirements — integration with other systems, APIs, or standards (for example G2P Connect or MOSIP)?
* **Why:** Drives external-interface scope and standards conformance.
* **Required:** no
* **Type:** prose

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
5. **Resource requirements** — recommended deployment architecture (`single-node`, `three-node`, or `full-scale`) and compute specifications for development sandbox, pilot, and production environments. Sourced from the knowledge base only.

### Common pitfalls

(none recorded yet)

***

## Phase 2: Build

### Purpose

Capture the fine-grained technical inputs required to generate the customised registry, generate the code by adapting the Farmer Registry reference, compile until clean, review against the Phase 1 specification, and produce Docker images published to a private Docker Hub repository. The implementer-facing output of this phase is a working set of build artefacts and source code, ready to be exercised in the local sandbox in Phase 3.

### Enter / Exit

* **Enter when:** the Requirements Analysis Report is approved.
* **Exit when:** every component of the customised registry compiles cleanly, every code-level review check passes against the Phase 1 specification, and all Docker images have been built and pushed to the configured private Docker Hub repository.

### Discovery items

**Build identity**

#### registry_mnemonic

* **Ask:** What is the registry mnemonic — a short identifier code used in filenames, image names, service names, and URLs?
* **Why:** Used directly during code generation, in file paths, and in image tags. Constraints follow because downstream tooling depends on the form.
* **Required:** yes
* **Type:** text
* **Validation:** lowercase letters and hyphens only; no whitespace; must not include the word `registry`.
* **Examples:** `health-worker` ✓, `HealthWorkerRegistry` ✗, `health worker registry` ✗

#### ui_theme

* **Ask:** Does the department have a UI Theme — fonts, colours, accents — that the registry should adopt? Provide details.
* **Why:** Drives the staff-portal-ui theme generation and the beneficiary portal styling.
* **Required:** no
* **Type:** prose

**Schema and constraints**

#### register_columns

* **Ask:** For each Register and supporting table, what are the exact names and data types of the database columns?
* **Why:** Names and types are used directly during code generation; exactness matters for downstream queries, migrations, and UI generation.
* **Required:** yes
* **Type:** classification — a map of register/table name to ordered list of `{column_name, type, nullable, default}` entries.

#### database_constraints

* **Ask:** What database constraints apply between tables — foreign keys, unique constraints, check constraints?
* **Why:** Constraints are reflected in schema generation and validation logic. Determines referential integrity in the generated migrations.
* **Required:** yes
* **Type:** list

**Notification payloads**

#### notification_payloads

* **Ask:** For each triggering event captured in `notification_triggering_events` during Phase 1, provide the payload (subject, body template, variables) for SMS and Email notifications.
* **Why:** Drives the generation of notification templates in the registry.
* **Required:** conditional: notification_triggering_events is non-empty
* **Type:** classification — a map of event name to `{sms, email}` payload templates.

### Activities

These activities are performed automatically by the advisor's build executor after the implementer has confirmed the Phase 2 input summary. Each activity acts on the Phase 1 + Phase 2 working_case and produces artefacts in the project's workspace.

#### collect_build_inputs

Walk the implementer through every Phase 2 Discovery item and record the answers in working_case. Confirm the captured inputs as a Phase 2 input summary before proceeding.

#### clone_reference_registry

Use Farmer Registry — `https://github.com/OpenG2P/farmer-registry` — as the reference template. Clone the repository into the project workspace as the structural baseline for the customised registry.

#### generate_extensions_and_dockers

Adapt the cloned reference into the customised registry by applying the Phase 1 + Phase 2 specification:

* Rename the extension package from `farmer-extension` to `<registry_mnemonic>-extension`.
* Replace the reference Registers with the implementer's Registers and supporting tables, generating the corresponding ORM models, Pydantic schemas, UI configurations, and seed SQL.
* Apply the implementer's database constraints (foreign keys, unique, check) to the generated migrations.
* Adapt the Functional ID generation logic to honour `functional_id_length`, `functional_id_format`, and any prefix/suffix encoding.
* Update Docker descriptors (staff-portal-api, partner-api, celery) with the new image names and dependency paths pointing at the renamed extension package.
* Generate the Helm chart with the implementer's chart name, image references, replica counts derived from `record_scale_5_year_estimate` and `staff_user_count` / `agent_user_count`, and ID type configuration matching the implementer's identifier choices.
* Generate notification templates from `notification_payloads` if applicable.

#### compile_until_success

Run build commands sequentially across the customised packages and Docker images. When a compilation error arises, analyse the failure, apply the targeted fix to the generated code, and continue. Iterate until every component compiles cleanly.

#### review_against_specifications

Carefully review the generated code against the Phase 1 + Phase 2 working_case before finalising the build:

* Every Register defined matches the implementer's structure and naming.
* Every supporting table is present with the correct columns and data types.
* Database constraints (foreign keys, unique, check) are reflected in the generated migrations.
* Functional ID generation logic matches `functional_id_length`, `functional_id_format`, and any prefix/suffix encoding.
* UI labels, themes, and locale files match `ui_theme` and `supported_languages`.
* Approval workflow levels match `approval_workflow_levels`.
* Notification templates are present for every event in `notification_triggering_events`.

Record any specification mismatches as findings. Mismatches block phase exit until resolved.

#### build_and_push_dockers

Build all Docker images for the customised registry — staff-portal-api, partner-api, celery, and any auxiliary images. Tag images with `<registry_mnemonic>-<service>:<version>`. Push every image to the configured **private Docker Hub** repository.

### References

* Farmer Registry reference repository: `https://github.com/OpenG2P/farmer-registry`.
* Registry extensions package conventions and the extension build contract.
* Registry docker repository structure and per-service descriptors (staff-portal-api, partner-api, celery).
* Helm chart generation and ID type configuration.
* OpenG2P Registry feature and configuration surface.

### Gap analysis

Before producing the Phase 2 report, the advisor verifies:

* Every Phase 2 Discovery item is recorded.
* The Phase 2 input summary has been confirmed by the implementer.
* `compile_until_success` has terminated with every component compiling cleanly.
* `review_against_specifications` has run with no unresolved findings.
* Every Docker image required for the customised registry has been built and pushed to the private Docker Hub repository.

### Output

**Build Report**, with these sections:

1. **Build identity** — `registry_mnemonic`, `registry_name`, `ui_theme` summary.
2. **Schema summary** — Registers, supporting tables, columns, and database constraints applied.
3. **Modifications made** — high-level list of files generated, renamed, and modified, grouped by repository (extensions, docker scripts, helm chart, notification templates).
4. **Compilation log summary** — terminal compile-success status per component, plus any compile fixes applied automatically.
5. **Review findings** — outcome of `review_against_specifications`. Any mismatches blocked the phase; the section confirms zero open findings at exit.
6. **Docker images published** — names, tags, sizes, and the destination Docker Hub repository for every image produced.
7. **Git commit identifiers** — final commit hashes for the customised extension and docker repositories in the project workspace.

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
