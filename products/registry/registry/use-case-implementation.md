# Use Case Implementation

OpenG2P Registry provides a base platform for creating a Registry, but it must be configured and customised to a specific use case. A typical implementation proceeds through five phases: **Requirements**, **Build**, **Sandbox**, **Pilot**, and **Full Rollout**.

Each phase is documented in a consistent structure so that any guide — a human consultant or an automated advisor — can walk an implementer through it. The structure is:

1. **Purpose** — what the phase achieves and why it exists as a distinct phase.
2. **Enter / Exit** — the preconditions for entering this phase and the durable test that determines when it is complete.
3. **Discovery** — what the guide must learn from the implementer, and why each item matters.
4. **Activities** — the work performed during the phase, in approximate order.
5. **References** — pointers to product features, related concepts, and worked examples relevant to this phase.
6. **Gap analysis** — verifiable checks the guide runs before the phase ends.
7. **Output** — the artefact produced when the phase ends.
8. **Common pitfalls** — issues observed in past implementations, populated as evidence accumulates.

## Phase Transition Protocol

After each phase report is produced, the same protocol applies:

1. Inform the implementer that the phase report is ready, and ask them to review it.
2. If they request changes, capture them, update the underlying facts, and regenerate the report.
3. Obtain explicit approval that the report is accurate and complete.
4. Briefly describe the next phase — what it involves, what information will be needed.
5. Ask whether the implementer is ready to proceed.
6. Advance only after explicit confirmation.

---

## Phase 1: Requirements Analysis

### Purpose

Understand the implementer's use case in detail, map it to the capabilities of OpenG2P Registry, identify gaps clearly, and capture deployment plans — pilot versus full rollout, scale, and infrastructure preferences.

### Enter / Exit

- **Enter** — the implementer has decided to use OpenG2P Registry as part of their G2P stack.
- **Exit** — a Requirements Analysis Report has been produced and explicitly approved by the implementer.

### Discovery

The guide establishes each of the following before this phase ends. Each item carries a "(why)" pointing to where the answer feeds downstream decisions.

- **Country and implementing organisation** — the country and the department or agency owning the implementation. (Establishes regulatory and language context; surfaces any data-residency constraints.)
- **End-to-end use case** — whether this registry serves a specific benefit-delivery programme, or is a general-purpose registry such as a national social registry, farmer registry, family registry, health workers registry, disability registry, students registry, crop registry, land registry, or vehicle registry. (Determines registry typology and which feature set to highlight.)
- **Use case detail and consumers** — how data will be consumed, and which downstream departments, systems, agencies, or applications use it. (Drives integration scope.)
- **Registration channel** — whether registration happens online via a portal, offline via field agents, or both. (Affects UI scope, sync behaviour, and offline tooling.)
- **Documents required for registration** — what documentation accompanies a record. (Drives upload, verification, and storage design.)
- **Greenfield or brownfield** — whether the implementation begins with fresh data collection or imports existing data. For brownfield, the form of existing data — Excel, database, APIs of another system, or other. (Determines whether a data-migration sub-track is needed.)
- **Specific functionalities required** — every capability the implementer expects, including any that may not be standard registry features. (Forms the requirements baseline against which gap analysis runs.)
- **Sandbox infrastructure preference** — whether a sandbox on a public cloud is acceptable. (Affects sandbox-phase deployment topology.)
- **Pilot and production infrastructure** — on-premises or cloud. (Affects later-phase deployment design and the support model.)
- **Scale** — the order of magnitude of expected primary records (farmers, citizens, vehicles, families, etc.). (Determines deployment topology and capacity profile.)
- **Identifier types** — which identifier schemes apply to records (national ID, MOSIP ID, custom functional ID). (Determines integration with the chosen identity provider.)
- **Interoperability requirements** *(optional)* — integrations with other systems, APIs, or standards (for example G2P Connect or MOSIP). (Drives external-interface scope.)

### Activities

- Walk the implementer through each Discovery item, deferring decisions that belong to later phases.
- After the implementer's stated requirements have been captured, perform **Product Feature Discovery**: review every feature documented for OpenG2P Registry and raise with the implementer any feature not yet discussed. Group related features into a single conversational turn — identity and deduplication features together, reporting features together, integration features together. For each feature surfaced, record one of: required, not required, or required-but-not-supported (gap).
- For every stated requirement and every feature surfaced via Product Feature Discovery, look for explicit support in the OpenG2P knowledge base. Mark as **Supported** (native or via configuration) when explicit evidence exists. Mark as **Gap** otherwise — including obvious or seemingly basic items, since the gap analysis depends on explicit evidence rather than assumption.
- For each gap, classify it as: (a) configurable at deploy time, (b) requires customisation (will be addressed in Phase 2), or (c) requires upstream change (raise as an issue).

### References

- The OpenG2P Registry feature surface, deployment patterns, and capacity profiles.
- Conceptual material on eligibility modelling, identifier resolution, data sharing, and brownfield data import.
- MOSIP integration touchpoints.
- The Farmer Registry as a worked example of an agriculture-domain implementation.
- The National Social Registry as a worked example of a national-scale implementation.

### Gap analysis

The guide verifies before producing the Phase 1 report:

- [ ] Every Discovery item has been answered, deferred with explicit acknowledgement, or marked unknown.
- [ ] Every requirement stated by the implementer has been assessed against the product knowledge base and recorded as Supported or Gap.
- [ ] Product Feature Discovery is complete: every feature documented for OpenG2P Registry has been raised with the implementer and classified as Required, Not Required, or Gap.
- [ ] Infrastructure preferences for sandbox, pilot, and production are recorded.
- [ ] No feature documented in the knowledge base remains undiscussed.

### Output

**Requirements Analysis Report**, containing:

1. **Project context** — programme or registry name, country, department, scale, and purpose (two to three sentences).
2. **Discovered facts** — the complete list of facts collected during Discovery.
3. **Requirements vs OpenG2P mapping** — for each stated requirement: the requirement as worded by the implementer; the OpenG2P feature or module that addresses it; the support level (native, configuration, partial, or gap); a one-sentence description of how it is addressed (sourced from the knowledge base) or, for gaps, a description of what is missing.
4. **Gaps summary** — all Gap and Partial items, with the missing capability and the custom work it implies.
5. **Resource requirements** — recommended deployment architecture (single-node, three-node, or full-scale) and compute specifications for development sandbox, pilot, and production environments. Sourced from the knowledge base only.

### Common pitfalls

(none recorded yet)

---

## Phase 2: Build

### Purpose

Capture the fine-grained technical details of the registry, perform the necessary code changes and configurations, and produce deployment artefacts (Docker images, Helm charts).

### Enter / Exit

- **Enter** — the Requirements Analysis Report is approved.
- **Exit** — a Build Report is produced, all required Docker images are available, and code changes are committed to the implementer's repository.

### Discovery

- **Registry name** — the full, public-facing name of the registry. Kept short, since it appears on user-interface labels.
- **Registry mnemonic** — a short identifier code used in filenames, image names, service names, and URLs. Lowercase, hyphens only, no whitespace, and excluding the word "registry".
- **Registers** — how many distinct registers this registry contains, and the name of each.
- **Register columns** — for each register, the exact names of the database fields. Names are used directly during code generation, so exactness matters.
- **Database constraints** — foreign keys, unique constraints, check constraints, and any other inter-table relationships.
- **Functional ID length** — number of digits required for the functional identifier, typically nine to twelve.

The formal validation rules for these inputs (character classes, allowed forms, length bounds) are documented on the registry build-contract page and surfaced by the guide when collecting answers.

### Activities

These activities are performed automatically by the advisor's build executor after the implementer has confirmed the Build phase summary. The list captures the canonical build flow; the precise mechanics — exact source paths, target paths, and replacement patterns — are documented on the registry build-contract page and may evolve as the build automation matures.

**Repository setup**

- Clone the registry extensions repository on its development branch.
- Clone the registry docker repository on its development branch.

**Code customisation — extensions repository**

- Copy the reference farmer-extension folder into a new folder named after the registry mnemonic. The reference folder location and target naming convention are documented on the registry build-contract page.

**Code customisation — docker repository**

For each of the three service folders (`staff-portal-api`, `partner-api`, `celery`):

- Copy the reference build descriptor into a new descriptor file named after the registry mnemonic.
- Replace the dependency line that points at the upstream farmer extension with a path that points at the new local extension folder created in the previous step. The exact source pattern and replacement form are documented on the registry build-contract page.
- Replace the Docker image name in the descriptor's leading comment line — substituting the reference name with the registry mnemonic. This step must run after the dependency line replacement above.

**Build Docker images**

From the root of the docker repository, run the build script for each of the three descriptors (`staff-portal-api`, `partner-api`, `celery`).

**Ordering rules**

- The dependency line replacement must run before the Docker image name replacement on the same descriptor.
- All file copies must complete before any in-file replacements on those files.
- All in-file replacements must complete before any image-build runs.

### References

- The registry extensions repository — extension folder structure, reference folder, naming conventions.
- The registry docker repository — service folders, build descriptors, build scripts.
- The registry build-contract page — formal contract for build-time customisation: source paths, target paths, replacement rules, validation rules.
- The OpenG2P Registry feature and configuration surface.

### Gap analysis

- [ ] Every Discovery item is recorded.
- [ ] The Build phase summary has been confirmed by the implementer.
- [ ] All three Docker images have been built successfully (`staff-portal-api`, `partner-api`, `celery`).
- [ ] Code changes have been committed to the implementer's repository.

### Output

**Build Report**, containing:

1. **Registry configuration summary** — registry name, mnemonic, registers, columns, constraints, ID length.
2. **Modifications made** — high-level list of files copied, renamed, and modified, with the owning repository for each.
3. **Docker images built** — names and tags of all images produced.
4. **Git commit ID** — the final commit hash after code is checked in.

### Common pitfalls

(none recorded yet)

---

## Phase 3: Sandbox

### Purpose

Deploy the built Docker images to a sandbox (development) environment and verify the registry works end-to-end. This is the first live deployment of the customised registry.

_Details to be added._

---

## Phase 4: Pilot

### Purpose

Deploy to a limited production-like environment with real users and real data at reduced scale. Validate the registry against actual operational requirements before full rollout.

_Details to be added._

---

## Phase 5: Full Rollout

### Purpose

Deploy to the full production environment at planned scale. Includes data migration (for brownfield implementations), staff training, and operational handover.

_Details to be added._
