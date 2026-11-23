---
description: >-
  The Agents Registry: a generic reference registry of the agents who serve
  farmers (extension agents, development agents, animal health workers) and
  their trainings, customised for each country
---

# Agents Registry

{% hint style="info" %}
**Built, not yet deployed.** Source: [github.com/OpenG2P/agents-registry](https://github.com/OpenG2P/agents-registry), on registry platform `0.0.0-develop.843`. Its lists and Ethiopia's sample agents are in [openg2p-data](https://github.com/OpenG2P/openg2p-data) (ETH pack).
{% endhint %}

The Agents Registry holds the **agents** who serve farmers (extension agents, development agents, animal health workers and the like) and what is known about them: who they are, their employment, where they are assigned, their specializations and qualifications, and the trainings they have completed. It is a **reference registry**: generic fields and lists that a system integrator customises for a country. Ethiopia's Development Agents are the first case it is designed against.

It is built on the [registry platform](../../products/registry/registry/README.md) in the same way as the [Farmer Registry](../../products/registry/farmer-registry/README.md) and the [Crop Sown Registry](../../products/registry/crop-sown-registry/README.md): an **entity register** for the agents and an **[activity register](../../products/registry/registry/features/activity-register.md)** for their trainings, in one registry.

## How it differs from the other registries

* **Not shared with partners.** No bank, insurer or OAN service reads agents through the Exchange. The registry has no Partner API search output and no data scopes, and consent enforcement is off. Its users are the staff who manage agents.
* **Generic, not country-specific.** The fields assume no country. Positions, specializations, statuses and the like are Master Data lists; the assigned area is a geography unit at whatever level the country's geography has. A country changes the lists and the forms, not the code.
* **Its own ID.** Each agent gets an **Agent ID** from the ID generator. The national ID is one of the fields, not the key.

## Scope

The registry is the record of the agents and their information. What agents **do** for farmers is out of scope: those are separate services that read the registry when they need to.

| In the registry | Out of the registry |
| --- | --- |
| Agent ID, person, contact, national ID | Task planning, field visits and activity reporting |
| Employment: position, employer, employment type, date of hire | Advisory, packages of practice, weather and GIS services |
| Current assignment: area, service point, since when | Broadcasts, alerts and notifications to farmers |
| Service status: active, on leave, suspended, retired, separated | Grievance handling, feedback, satisfaction surveys |
| Specializations and qualifications | KPI calculation, performance management, incentives |
| Lifecycle changes, approved, with full history | The agents' mobile app and offline field data |
| Trainings completed and certifications awarded | Registering farmers and linking them to agents |

Linking agents to farmers is **not stored**. An agent's assigned area and a farmer's location in the Farmer Registry give the link when a service needs it, so the registries stay independent and no list of farmers per agent goes out of date.

## Agent (entity register)

One register, **Agent**, with the Agent ID as its record ID. It inherits the platform's person fields (`G2PPerson`) and location fields (`G2PGeo`); the location is the agent's **assigned area**, not their home.

| Group | Fields |
| --- | --- |
| **Identity** | Agent ID (generated, read-only), national ID (`foundational_id`), employee number (the employer's HR or payroll number) |
| **Person** | First, middle and last name, gender (`GENDER`), date of birth, languages spoken |
| **Contact** | Mobile number, alternate phone, email |
| **Employment** | Position (`AGENT_POSITION`), employer type (`AGENT_EMPLOYER_TYPE`), employer name, employment type (`AGENT_EMPLOYMENT_TYPE`), date of hire |
| **Current assignment** | Assigned area (a geography unit, any level), service point name, service point type (`AGENT_SERVICE_POINT_TYPE`), assigned since, assignment reason (`AGENT_ASSIGNMENT_REASON`) |
| **Service status** | Status (`AGENT_SERVICE_STATUS`), status date, status reason |
| **Documents** | Appointment letter, national ID document |

Two list sections, each a table of rows under the agent:

| Section | Fields per row |
| --- | --- |
| **Specializations** | Specialization (`AGENT_SPECIALIZATION`), primary (yes/no), since |
| **Qualifications** | Level (`AGENT_QUALIFICATION_LEVEL`), field of study (`AGENT_FIELD_OF_STUDY`), institution, year completed |

The current assignment is held on the agent record, not as a list of postings: the geography widget works on the record, and the record's [version history](../../products/registry/registry/features/version-history.md) keeps every earlier assignment with its dates.

### Agent ID

* Generated by the ID generator when the registration is approved, from the pool `agent`: **8 digits, no prefix**.
* Shown read-only; staff never type it.
* A country can change the length or add a prefix in the chart's ID generator settings.

### National ID and duplicates

* The national ID is a plain field. It is **not verified** against a national ID system by default.
* Duplicates are flagged by the platform's [deduplication](../../products/registry/registry/features/deduplication.md) on the national ID, name and date of birth.
* A country with an online ID service can switch on the platform's registrant authentication (for example through eSignet) for this register.

### Lifecycle and approvals

Every change to an agent is a **change request**, approved in [AWE](../../products/registry/registry/features/change-management-and-approval-workflow.md). New agents are registered through an intake form, approved the same way. Approval stages and approvers are set per country, for example the district officer, then the regional officer.

| Lifecycle event | What the change request changes |
| --- | --- |
| Onboarding | A new agent record (intake form); the Agent ID is generated on approval |
| Transfer or reassignment | Assigned area, service point, assigned since, reason "transfer" |
| Promotion or role change | Position; reason "promotion" when the assignment changes too |
| Specialization update | Rows of the Specializations section |
| Leave, suspension | Status, status date and reason |
| Reactivation | Status back to active |
| Retirement, separation, death | Status, status date and reason |

The history is the audit trail: each approved change is a version, with who asked, who approved and when. Lifecycle events are **not** recorded a second time as activities.

## Trainings (activity register)

An activity register, **AgentTraining**. Each training an agent completes, and each certification awarded, is an append-only activity against the agent. The agent is the activity's **subject**: a reference to an Agent record in this registry (`LOCAL_RECORD`, by Agent ID, strict), so the trainings show on the agent's profile.

| Activity type | Fields |
| --- | --- |
| **Training completed** | Topic (`AGENT_TRAINING_TOPIC`), course title, course code, provider, start and end date, course days (derived), hours, delivery mode (`AGENT_TRAINING_DELIVERY_MODE`), result (`AGENT_TRAINING_RESULT`), score, location (optional) |
| **Certification awarded** | Certification, issuing body, certificate number, issued on, valid until, topic (`AGENT_TRAINING_TOPIC`) |

* **One context per agent.** Its current state summarises the agent's trainings: number of trainings, hours, last training, latest certification and its validity.
* **Sources.**
  * Staff record trainings in the staff portal, one at a time or in a batch for a whole course.
  * A learning management system sends them through the signed Partner API, each message idempotent.
* **Corrections** are supersede or void with a reason, as in every activity register. Verification is off by default; a country can require a supervisor's verification per activity type.
* A topic code an external system sends that is not in the topic list is accepted with a warning, not rejected. An unknown agent, delivery mode or result is rejected.
* **Checks:** a course that ends before it starts is rejected; more than 12 hours a day, or a failed course with no score, is a warning.

## Master Data lists

New lists in the agriculture domain of the country packs ([openg2p-data](https://github.com/OpenG2P/openg2p-data)), with codes prefixed by the list, as the other agriculture lists are. Each country edits them.

| List | Example values |
| --- | --- |
| `AGENT_POSITION` | Field agent, senior field agent, supervisor, subject-matter specialist, coordinator |
| `AGENT_SPECIALIZATION` | Crop production, livestock, animal health, natural resources, irrigation, horticulture, cooperatives, agribusiness, nutrition, general |
| `AGENT_SERVICE_STATUS` | Active, on leave, suspended, retired, separated, deceased |
| `AGENT_EMPLOYMENT_TYPE` | Permanent, contract, temporary, volunteer |
| `AGENT_EMPLOYER_TYPE` | Government, NGO, private company, cooperative, community |
| `AGENT_SERVICE_POINT_TYPE` | Extension office, farmer training centre, animal health post, demonstration site, other |
| `AGENT_ASSIGNMENT_REASON` | First posting, transfer, reassignment, promotion, temporary cover |
| `AGENT_QUALIFICATION_LEVEL` | Certificate, diploma, bachelor's, master's, doctorate, other |
| `AGENT_FIELD_OF_STUDY` | Plant science, animal science, animal health, natural resources, agricultural economics, agricultural extension, irrigation, horticulture, other |
| `AGENT_TRAINING_TOPIC` | Crop production, livestock, animal health, natural resources, climate-smart agriculture, post-harvest, extension methods, digital tools, nutrition, other |
| `AGENT_TRAINING_DELIVERY_MODE` | In person, online, blended |
| `AGENT_TRAINING_RESULT` | Completed, passed, failed, attended only |

Gender uses the existing `GENDER` list.

## Reports

Reporting views for Superset or Insights. Geography levels are read by position in the area's hierarchy, so they work for any country:
* `agents_rpt_agent`: one row per agent, with each level of the assigned area, primary specialization, qualifications, trainings, hours and the latest certification;
* `agents_rpt_agents_by_area`: agents per area, position and status (women, trained, certified);
* `agents_rpt_training`: one row per current training or certification, with the agent's area.

Not built yet: areas with no active agent (the registry holds no list of areas; Master Data does), and dashboards.

## Packaging

As for the other registries ([Packaging](../../products/registry/registry/deployment-and-extension/packaging-and-reference-registry.md)):
* the `agents-extension` package: models, domain services, seed metadata, the training register's configuration;
* `scripts/agents_definitions.py`: the registers, sections, tabs, intake form, search, duplicate check, approval bindings, activity types and indicators in one file, from which `scripts/build_seed_sql.py` generates the seed SQL;
* thin images over the platform's (`staff-api`, `partner-api`, `celery`, `db-seed`);
* the `openg2p-agents-registry` chart over `openg2p-registry`, pinned to a platform version.

The Partner API is deployed only to take data in: the training feed and an existing agent system's data through `ingest_data`. Consent enforcement is off; partner signatures are still checked.

**Sample data**, both switches off by default:
* **Load Sample Data:** db-seed loads the country pack's `samples/agents.json` from openg2p-data as approved Agent records, with their specializations and qualifications. It picks the pack whose areas Master Data knows. The ETH pack has 24 Development Agents in eleven woredas of eight regions, including the Tigray woredas of the pack's sample farmers.
* **Load sample trainings:** the platform's sample task records trainings and certifications for them through the activity APIs, one of them corrected.

## Customising for a country

What a system integrator changes for a rollout, with Ethiopia's Development Agents as the example:

| Item | Generic | Ethiopia (in the ETH pack) |
| --- | --- | --- |
| Assigned area | Any geography unit | The woreda today; the kebele once the pack has a kebele level (it stops at woreda) |
| Positions | `AGENT_POSITION` | Development Agent (DA), Senior DA, DA supervisor, woreda subject-matter specialist, woreda extension coordinator, community animal health worker |
| Service point | `AGENT_SERVICE_POINT_TYPE` | Farmer Training Centre (FTC), Pastoral Training Centre, woreda agriculture office, animal health post |
| Specializations | `AGENT_SPECIALIZATION` | Crop, livestock, natural resource management, home economics, small-scale irrigation, … |
| Qualifications | `AGENT_QUALIFICATION_LEVEL` | TVET Level III and IV, diploma, degrees |
| Existing system | `ingest_data` mapping | The Ministry of Agriculture's DA Registry: map its fields once its schema is known |
| National ID | Plain field | Fayda; optionally verified through registrant authentication |
| Training feed | Partner API | ATI's learning platform |
| Approvers | Two demo stages | Woreda office, then regional office |
| Dates | Gregorian | Ethiopian-calendar entry, as the Crop Sown Registry does |

## Open questions

* The fields of the Ministry's existing DA Registry, to confirm the generic fields cover them and to write the ingestion mapping.
* Whether agents may hold more than one assignment at a time. The design holds one current assignment; extra areas would be a list section.
* Whether sync back to an existing agent system is needed, which would need the registry's outgestion configured.
