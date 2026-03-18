# Use Case Implementation

OpenG2P Registry provides a base platform to create a Registry, but it needs to be configured and customised for your specific use case. A typical implementation follows five phases: Requirements, Build, Sandbox, Pilot, and Full Rollout.

Each phase follows a consistent structure: **Purpose → Information to Collect → Actions → Completion Criteria → Output**.

---

## Phase 1: Requirements Analysis

### Purpose

Understand the use case and requirements in detail, map them to what OpenG2P Registry offers, and clearly identify any gaps. Also understand the deployment plan — pilot vs. full rollout, scale, timelines, and infrastructure preferences.

### Information to Collect

The following facts must be collected. Each fact has a key (shown in quotes) that is used to record it in the advisory system.

| # | Question | Fact Key | Type | Mandatory |
|---|----------|----------|------|-----------|
| 1 | What country is this implementation for? | `country` | text | Yes |
| 2 | Which department or organisation is implementing this? | `department` | text | Yes |
| 3 | What is the end-to-end use case? Is this for a specific benefit delivery programme (give the programme name), or a general-purpose registry (e.g. National Social Registry, Farmer Registry, Family Registry, Health Workers Registry, Disability Registry, Students Registry, Crop Registry, Land Registry, Vehicle Registry)? | `program` / `registry_type` | text | Yes |
| 4 | Describe the use case in detail. How will data be consumed — who are the consumers? Will data be shared with other departments, systems, agencies, or applications? | `use_case_info` | text | Yes |
| 5 | How will registration happen — online via a portal, or offline via agents collecting data in the field? | `offline_registrations` | true/false | Yes |
| 6 | What documents are required for registration? | `documents` | list | Yes |
| 7 | Is this a greenfield implementation (fresh data collection) or brownfield (existing data to import)? If brownfield, what form is the existing data in — Excel, database, APIs of another system? | `existing_data_import` | true/false + details | Yes |
| 8 | What specific functionalities are required that must be supported by OpenG2P Registry? List all requirements explicitly, including any that may not be standard registry features. | `requirements` | list | Yes |
| 9 | Is a development sandbox on a public cloud acceptable? | `sandbox_on_cloud` | true/false | Yes |
| 10 | Will the pilot and production systems run on on-premises hardware or on cloud? | `production_on_cloud` | true/false | Yes |
| 11 | How many primary records are expected in the registry (e.g. number of farmers, citizens, vehicles, families)? | `n_records` | number | Yes |
| 12 | Which ID type(s) will be used for records (e.g. national ID, MOSIP ID, custom functional ID)? | `id_types` | list | Yes |
| 13 | Are there any specific interoperability requirements — integration with other systems, APIs, or standards (e.g. G2P Connect, MOSIP)? | `interoperability` | text | No |

### Gap Analysis Rules

For each requirement stated by the user:

1. Search the OpenG2P product knowledge base for explicit evidence of support.
2. If the knowledge base confirms support — mark as **Supported** (Native or Configuration).
3. If the knowledge base does not clearly confirm support — mark as **GAP**, regardless of how obvious or basic the requirement sounds.
4. Record every requirement and its gap status as a fact. Requirements not recorded will not appear in the report.
5. Use fact key `gap_<topic>` for gap items (e.g. `gap_loan_management`, `gap_weather_reports`).

### Completion Criteria

All of the following must be satisfied before generating the Phase 1 report:

- [ ] All mandatory facts in the table above are recorded (confirmed or explicitly deferred as unknown)
- [ ] Every stated requirement has been assessed against the product KB and recorded as Supported or GAP
- [ ] All OpenG2P Registry features have been reviewed with the user — each marked as Required, Not Required, or GAP
- [ ] Infrastructure preferences (sandbox, pilot, production) are recorded

### Output

**Requirements Analysis Report** containing:

1. **Project Context** — Programme/registry name, country, department, scale, purpose (2–3 sentences)
2. **Discovered Facts** — Complete list of all recorded facts with values
3. **Requirements vs OpenG2P Mapping** — For each stated requirement:
   - Exact wording as stated by the user
   - OpenG2P feature or module that addresses it
   - Support level: Native / Configuration / Partial / Gap
   - How it is addressed (one sentence from KB), or gap description
4. **Gaps Summary** — All Gap and Partial items clearly listed with what is missing and what custom work is needed
5. **Resource Requirements** — Recommended deployment architecture (single-node / three-node / full-scale) and compute specs for development sandbox, pilot, and production environments — sourced from KB only

### Phase Transition Protocol

After the report is generated, follow this sequence strictly before moving to Phase 2:

1. Inform the user the Requirements Analysis Report has been generated and ask them to review it.
2. If the user requests changes — capture them, update the facts, and regenerate the report.
3. Get explicit approval from the user that the report is accurate and complete.
4. Briefly describe Phase 2 (Build) — what it involves and what information will be needed.
5. Ask: "Are you ready to proceed to the Build phase?"
6. Only advance to Phase 2 after the user explicitly confirms.

---

## Phase 2: Build

### Purpose

Collect the fine-grained technical details of the registry, make the necessary code changes and configurations, and build the deployment artefacts (Docker images, Helm charts).

### Information to Collect

All of the following facts are **mandatory**. Do not proceed to Actions until all are recorded (confirmed or explicitly deferred as unknown by the user).

| # | Question | Fact Key | Type | Mandatory |
|---|----------|----------|------|-----------|
| 1 | What is the full name of your registry? Keep it as short as possible — it will appear on all UI labels. Example: `Health Workers Registry` | `registry_name` | text | Yes |
| 2 | What is the registry mnemonic? This is a very short code used in filenames, Docker image names, service names, and URLs. Use lowercase letters and hyphens only. Do NOT include the word "registry". Example: `health-worker` | `registry_mnemonic` | text (lowercase, hyphens only) | Yes |
| 3 | How many registers does this registry contain? What is the name of each register? | `registers` | list of names | Yes |
| 4 | For each register, what are the exact names of the database columns (fields)? | `register_columns` | map: register name → list of column names | Yes |
| 5 | What are the database constraints between tables (foreign keys, unique constraints, check constraints)? | `database_constraints` | list | Yes |
| 6 | How many digits are required for the functional ID? | `id_length` | number | Yes |

**Validation rules:**

- `registry_mnemonic` must be lowercase, hyphen-separated, no spaces, no "registry" prefix/suffix. Example: `health-worker` ✓, `HealthWorkerRegistry` ✗
- Column names must be exact — they will be used directly in code generation
- `id_length` is typically 9–12 digits; confirm with the user if unsure

### Actions

The following steps are executed automatically by the system after the user confirms the Build phase summary. All paths are relative to the build working directory.

**Repository setup:**

| Step | Type | Details |
|------|------|---------|
| Clone extensions repo | `clone` | Repo: `https://github.com/OpenG2P/openg2p-registry-gen2-extensions` Branch: `develop` |
| Clone docker repo | `clone` | Repo: `https://github.com/OpenG2P/openg2p-registry-gen2-docker` Branch: `develop` |

**Code customisation (Repo 1 — extensions):**

| Step | Type | Details |
|------|------|---------|
| Copy farmer extension folder | `copy_dir` | src: `openg2p-registry-gen2-extensions/openg2p-registry-farmer-extension` → dest: `openg2p-registry-gen2-extensions/openg2p-registry-<registry_mnemonic>-extension` |

**Code customisation (Repo 2 — docker, repeat for each of: `staff-portal-api`, `partner-api`, `celery`):**

| Step | Type | Details |
|------|------|---------|
| Copy develop.txt | `copy_file` | src: `openg2p-registry-gen2-docker/<folder>/farmer-develop.txt` → dest: `openg2p-registry-gen2-docker/<folder>/<registry_mnemonic>-develop.txt` |
| Replace pip dependency line | `replace_in_file` | file: `openg2p-registry-gen2-docker/<folder>/<registry_mnemonic>-develop.txt` find: `git://develop//https://github.com/openg2p/openg2p-registry-gen2-extensions#subdirectory=openg2p-registry-farmer-extension` replaceWith: `{{workDir}}/openg2p-registry-gen2-extensions/openg2p-registry-<registry_mnemonic>-extension` Note: no `#subdirectory=` in the replacement path |
| Replace Docker image name | `replace_in_file` | file: `openg2p-registry-gen2-docker/<folder>/<registry_mnemonic>-develop.txt` find: first line of the file — the `#` comment line containing the Docker image name, which includes the word `farmer` replaceWith: same line with `farmer` replaced by `<registry_mnemonic>` Note: this step must run AFTER the pip dependency replacement above |

**Build Docker images (run from root of Repo 2):**

| Step | Type | Details |
|------|------|---------|
| Build staff-portal-api | `run` | cmd: `bash` args: `["scripts/build.sh", "staff-portal-api/<registry_mnemonic>-develop.txt"]` cwd: `openg2p-registry-gen2-docker` |
| Build partner-api | `run` | cmd: `bash` args: `["scripts/build.sh", "partner-api/<registry_mnemonic>-develop.txt"]` cwd: `openg2p-registry-gen2-docker` |
| Build celery | `run` | cmd: `bash` args: `["scripts/build.sh", "celery/<registry_mnemonic>-develop.txt"]` cwd: `openg2p-registry-gen2-docker` |

**Important ordering rules:**
- The `replace_in_file` step for the pip dependency line must run BEFORE the Docker image name replacement on the same file
- All `copy_file` steps must complete before any `replace_in_file` steps on those files
- All `replace_in_file` steps must complete before any `run` (build) steps

### Completion Criteria

- [ ] All mandatory facts in the Information to Collect table above are recorded
- [ ] User has confirmed the Build phase summary
- [ ] All three Docker images built successfully: `staff-portal-api`, `partner-api`, `celery`
- [ ] Code checked in to git repository (TBD)

### Output

**Build Report** containing:

1. **Registry Configuration Summary** — registry name, mnemonic, registers, columns, constraints, ID length
2. **Modifications Made** — high-level list of files copied, renamed, and modified, with repository names
3. **Docker Images Built** — names and tags of all Docker images created
4. **Git Commit ID** — final commit hash after code check-in

### Phase Transition Protocol

After the Build Report is generated:

1. Inform the user the Build Report is available and ask them to review it.
2. Confirm all Docker images are available and accessible.
3. Get explicit user approval on the Build Report.
4. Briefly describe Phase 3 (Sandbox) — deploying the built images to a sandbox environment for testing.
5. Ask: "Are you ready to proceed to the Sandbox phase?"

---

## Phase 3: Sandbox

### Purpose

Deploy the built Docker images to a sandbox (development) environment and verify the registry is working correctly end-to-end. This is the first live deployment of the customised registry.

_Details to be added._

---

## Phase 4: Pilot

### Purpose

Deploy to a limited production-like environment with real users and real data at reduced scale. Validate the registry against actual operational requirements before full rollout.

_Details to be added._

---

## Phase 5: Full Rollout

### Purpose

Deploy to the full production environment at the planned scale. Includes data migration (for brownfield implementations), staff training, and operational handover.

_Details to be added._
