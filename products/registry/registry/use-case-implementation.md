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

- **Ask** — the canonical form of the question. The advisor may rephrase for tone but must elicit the same information.
- **Why** — what downstream decision, activity, or phase consumes this answer.
- **Required** — `yes`, `no`, or `conditional: <expression>`.
- **Type** — `text`, `number`, `boolean`, `enum [...]`, `list`, `prose`, or `classification` (a typed answer that may include free text).
- **Affects** *(optional)* — specific downstream phases or activities that consume this answer.
- **Follow-ups** *(optional)* — conditional sub-items, each itself a Discovery item, conditioned on the parent answer.
- **Validation** *(optional)* — explicit constraints beyond the Type.
- **Examples** *(optional)* — sample answers.

## Phase Transition Protocol

The same protocol applies after every phase report is produced.

1. Inform the implementer that the phase report is ready, and ask them to review it.
2. If they request changes, capture them, update the underlying facts, and regenerate the report.
3. Obtain explicit approval that the report is accurate and complete.
4. Briefly describe the next phase — what it involves and what information will be needed.
5. Ask whether the implementer is ready to proceed.
6. Advance only after explicit confirmation.

---

## Phase 1: Requirements Analysis

### Purpose

Understand the use case in detail, map it to OpenG2P Registry capabilities, identify gaps, and capture deployment plans (pilot vs. full rollout, scale, infrastructure preferences).

### Enter / Exit

- **Enter when:** the implementer has decided to use OpenG2P Registry as part of their G2P stack.
- **Exit when:** a Requirements Analysis Report has been produced and explicitly approved by the implementer.

### Discovery items

#### country
- **Ask:** In which country will the registry operate?
- **Why:** Establishes regulatory and language context; surfaces data-residency constraints that affect later-phase deployment region.
- **Required:** yes
- **Type:** text

#### implementing_organisation
- **Ask:** Which department, agency, or organisation owns the implementation?
- **Why:** Identifies the operational owner; informs stakeholder model and operational handover.
- **Required:** yes
- **Type:** text

#### registry_purpose
- **Ask:** Is this registry serving a specific benefit-delivery programme, or is it a general-purpose registry?
- **Why:** Determines registry typology and the feature set the advisor surfaces during Product Feature Discovery.
- **Required:** yes
- **Type:** enum [`specific-programme`, `general-purpose`]
- **Follow-ups:**
  - **program_name** *(when registry_purpose = specific-programme)* — what is the name of the programme?
  - **registry_type** *(when registry_purpose = general-purpose)* — which type of registry: national social registry, farmer registry, family registry, health workers registry, disability registry, students registry, crop registry, land registry, vehicle registry, or other?

#### use_case_detail
- **Ask:** Describe the end-to-end use case. How will data be consumed, and who consumes it? Will data be shared with other departments, systems, agencies, or applications?
- **Why:** Drives integration scope; informs gap analysis on data sharing and interoperability.
- **Required:** yes
- **Type:** prose
- **Affects:** Phase 1 gap analysis on interoperability; integration design in later phases.

#### registration_channel
- **Ask:** Will registration happen online via a portal, offline via field agents, or both?
- **Why:** Affects UI scope, sync behaviour, and offline tooling decisions.
- **Required:** yes
- **Type:** enum [`online`, `offline`, `both`]

#### required_documents
- **Ask:** What documents are required for registration?
- **Why:** Drives upload, verification, and storage design.
- **Required:** yes
- **Type:** list

#### existing_data
- **Ask:** Is this a greenfield implementation (fresh data collection) or brownfield (existing data to import)?
- **Why:** Brownfield implies a data-migration sub-track in later phases; greenfield does not.
- **Required:** yes
- **Type:** enum [`greenfield`, `brownfield`]
- **Follow-ups:**
  - **existing_data_form** *(when existing_data = brownfield)* — in what form does the existing data take: Excel, database, APIs of another system, or other?

#### functional_requirements
- **Ask:** What specific functionalities must OpenG2P Registry support for this use case? List every requirement, including any that may not be standard registry features.
- **Why:** Forms the requirements baseline against which gap analysis runs.
- **Required:** yes
- **Type:** list

#### sandbox_on_cloud
- **Ask:** Is a sandbox on a public cloud acceptable for development?
- **Why:** Affects sandbox-phase deployment topology.
- **Required:** yes
- **Type:** boolean

#### production_infrastructure
- **Ask:** Will the pilot and production systems run on on-premises hardware, on cloud, or in a hybrid configuration?
- **Why:** Affects later-phase deployment design and the support model.
- **Required:** yes
- **Type:** enum [`on-prem`, `cloud`, `hybrid`]

#### record_scale
- **Ask:** How many primary records are expected in the registry (farmers, citizens, vehicles, families, etc.)?
- **Why:** Determines deployment topology and capacity profile.
- **Required:** yes
- **Type:** number
- **Validation:** order of magnitude is acceptable when the implementer is uncertain.

#### identifier_types
- **Ask:** Which identifier scheme(s) will be used for records — national ID, MOSIP ID, or custom functional ID?
- **Why:** Determines integration with the chosen identity provider.
- **Required:** yes
- **Type:** list

#### interoperability_requirements
- **Ask:** Are there specific interoperability requirements — integration with other systems, APIs, or standards (for example G2P Connect or MOSIP)?
- **Why:** Drives external-interface scope.
- **Required:** no
- **Type:** prose

### Activities

#### walk_discovery
Walk the implementer through each Discovery item in order. Defer decisions that belong to later phases. For each item, record the answer against the item's fact key. For items with conditional follow-ups, evaluate the condition against the recorded answer and run the follow-up if it applies.

#### product_feature_discovery
After every Discovery item is recorded, review every feature documented for OpenG2P Registry. For each feature not yet raised by the implementer through their stated functional requirements, ask the implementer whether it is needed. Group related features into a single conversational turn — identity and deduplication features together, reporting features together, integration features together. For each feature surfaced, record one of: `required`, `not_required`, or `gap` (required-but-not-supported). This activity is mandatory; the phase cannot end until every documented feature has been classified.

#### gap_classification
For every entry in `functional_requirements` and every feature surfaced via `product_feature_discovery`, look for explicit support in the OpenG2P knowledge base. Mark as `Supported` (native or via configuration) when explicit evidence exists. Mark as `Gap` otherwise — including obvious or seemingly basic items, since the gap analysis depends on explicit evidence rather than assumption. For each gap, classify as one of: `configurable-at-deploy`, `requires-customisation` (defer to Phase 2), or `requires-upstream-change` (raise as an issue).

### References

- OpenG2P Registry feature surface, deployment patterns, and capacity profiles.
- Concepts: eligibility modelling, identifier resolution, data sharing, brownfield import.
- Worked examples: Farmer Registry, National Social Registry.
- MOSIP integration touchpoints.

### Gap analysis

Before producing the Phase 1 report, the advisor verifies:

- Every Discovery item is recorded — answered, deferred with explicit acknowledgement, or marked unknown.
- Every entry in `functional_requirements` is assessed against the product knowledge base and recorded as `Supported` or `Gap`.
- Product Feature Discovery is complete: every feature documented for OpenG2P Registry is classified as `required`, `not_required`, or `gap`.
- Infrastructure preferences for sandbox, pilot, and production are recorded.
- No feature documented in the knowledge base remains undiscussed.

### Output

**Requirements Analysis Report**, with these sections:

1. **Project context** — programme or registry name, country, implementing organisation, scale, and purpose (two to three sentences).
2. **Discovered facts** — the complete list of fact keys and their recorded values from Discovery.
3. **Requirements vs OpenG2P mapping** — for each entry in `functional_requirements` and each feature surfaced via Product Feature Discovery: the requirement as worded; the OpenG2P feature or module that addresses it; support level (`native`, `configuration`, `partial`, `gap`); a one-sentence description of how it is addressed (sourced from the knowledge base) or, for gaps, a description of what is missing.
4. **Gaps summary** — all `Gap` and `Partial` items, with the missing capability and the custom work it implies.
5. **Resource requirements** — recommended deployment architecture (`single-node`, `three-node`, or `full-scale`) and compute specifications for development sandbox, pilot, and production environments. Sourced from the knowledge base only.

### Common pitfalls

(none recorded yet)

---

## Phase 2: Build

### Purpose

Capture the fine-grained technical details of the registry, perform the necessary code changes and configurations, and produce deployment artefacts (Docker images, Helm charts).

### Enter / Exit

- **Enter when:** the Requirements Analysis Report is approved.
- **Exit when:** a Build Report is produced, all required Docker images are available, and code changes are committed to the implementer's repository.

### Discovery items

#### registry_name
- **Ask:** What is the full name of the registry? Keep it short — it appears on UI labels.
- **Why:** Used in user-facing labels across the registry's interface.
- **Required:** yes
- **Type:** text
- **Examples:** `Health Workers Registry`, `Farmer Registry`

#### registry_mnemonic
- **Ask:** What is the registry mnemonic — a short identifier code used in filenames, image names, service names, and URLs?
- **Why:** Used directly during code generation, in file paths, and in image tags. Constraints follow because downstream tooling depends on the form.
- **Required:** yes
- **Type:** text
- **Validation:** lowercase letters and hyphens only; no whitespace; must not include the word `registry`.
- **Examples:** `health-worker` ✓, `HealthWorkerRegistry` ✗, `health worker registry` ✗

#### registers
- **Ask:** How many registers does this registry contain, and what is the name of each?
- **Why:** Each register becomes a distinct table and entity in the generated code.
- **Required:** yes
- **Type:** list

#### register_columns
- **Ask:** For each register, what are the exact names of the database columns?
- **Why:** Names are used directly during code generation; exactness matters.
- **Required:** yes
- **Type:** classification — a map of register name to list of column names.

#### database_constraints
- **Ask:** What database constraints apply between tables — foreign keys, unique constraints, check constraints?
- **Why:** Constraints are reflected in schema generation and validation logic.
- **Required:** yes
- **Type:** list

#### functional_id_length
- **Ask:** How many digits are required for the functional ID?
- **Why:** Determines the format of generated identifiers.
- **Required:** yes
- **Type:** number
- **Validation:** typically between nine and twelve; confirm with the implementer if outside this range.

### Activities

These activities are performed automatically by the advisor's build executor after the implementer has confirmed the Build phase summary. The list captures the canonical build flow; the precise mechanics — exact source paths, target paths, and replacement patterns — are documented on the registry build-contract page and may evolve as the build automation matures.

#### repository_setup
Clone the registry extensions repository on its development branch. Clone the registry docker repository on its development branch.

#### extension_customisation
In the registry extensions repository, copy the reference farmer-extension folder into a new folder named after `registry_mnemonic`. The reference folder location and target naming convention are documented on the registry build-contract page.

#### docker_descriptor_customisation
For each of the three service folders (`staff-portal-api`, `partner-api`, `celery`) in the registry docker repository, perform the following steps in order:

1. Copy the reference build descriptor into a new descriptor file named after `registry_mnemonic`.
2. In the new descriptor, replace the dependency line that points at the upstream farmer extension with a path that points at the local extension folder created in `extension_customisation`. The exact source pattern and replacement form are documented on the registry build-contract page.
3. In the same descriptor, replace the Docker image name in the leading comment line — substituting the reference name with `registry_mnemonic`.

The dependency line replacement (step 2) must run before the image name replacement (step 3) on the same descriptor. All file copies must complete before any in-file replacements; all in-file replacements must complete before any image-build runs.

#### image_build
From the root of the registry docker repository, run the build script for each of the three descriptors (`staff-portal-api`, `partner-api`, `celery`).

#### code_commit
Commit the modified extensions and docker repositories to the implementer's repository. Capture the final commit hash for inclusion in the Build Report.

### References

- The registry extensions repository — extension folder structure, reference folder, naming conventions.
- The registry docker repository — service folders, build descriptors, build scripts.
- The registry build-contract page — formal contract for build-time customisation: source paths, target paths, replacement rules, validation rules.
- The OpenG2P Registry feature and configuration surface.

### Gap analysis

Before producing the Phase 2 report, the advisor verifies:

- Every Discovery item is recorded.
- The Build phase summary has been confirmed by the implementer.
- All three Docker images have been built successfully (`staff-portal-api`, `partner-api`, `celery`).
- Code changes have been committed to the implementer's repository.

### Output

**Build Report**, with these sections:

1. **Registry configuration summary** — `registry_name`, `registry_mnemonic`, `registers`, `register_columns`, `database_constraints`, `functional_id_length`.
2. **Modifications made** — high-level list of files copied, renamed, and modified, with the owning repository for each.
3. **Docker images built** — names and tags of all images produced.
4. **Git commit ID** — the final commit hash after code is checked in.

### Common pitfalls

(none recorded yet)

---

## Phase 3: Sandbox

### Purpose

Deploy the built Docker images to a sandbox (development) environment and verify the registry works end-to-end. This is the first live deployment of the customised registry.

### Enter / Exit

- **Enter when:** the Build Report is approved and Docker images are available.
- **Exit when:** _(to be defined when phase details are added)_.

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

---

## Phase 4: Pilot

### Purpose

Deploy to a limited production-like environment with real users and real data at reduced scale. Validate the registry against actual operational requirements before full rollout.

### Enter / Exit

- **Enter when:** Sandbox deployment is verified.
- **Exit when:** _(to be defined when phase details are added)_.

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

---

## Phase 5: Full Rollout

### Purpose

Deploy to the full production environment at planned scale. Includes data migration (for brownfield implementations), staff training, and operational handover.

### Enter / Exit

- **Enter when:** Pilot is approved.
- **Exit when:** _(to be defined when phase details are added)_.

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
