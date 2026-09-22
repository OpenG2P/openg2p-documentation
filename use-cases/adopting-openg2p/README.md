# Adopting OpenG2P — A Guide for Evaluators

This guide is for a **government department or programme lead deciding whether to adopt OpenG2P**. It is deliberately non-technical: no deployment, no code. If you are implementing or operating OpenG2P, see the Deployment and product guides instead.

---

## 1. What OpenG2P is

OpenG2P is **open-source software that your government installs, owns, and runs** — not a hosted service, and not a product licensed from a vendor. The source is public under open-source licences, so there is no per-seat cost and no vendor who can withdraw it.

It is **modular**. The main building blocks are:

| Module | What it does |
|---|---|
| Registry | Holds beneficiary and household records (social registry, farmer registry, and similar) |
| PBMS | Defines programmes, eligibility rules, enrolment and disbursement cycles |
| SPAR | Maps a beneficiary ID to their financial address (bank account or wallet) |
| G2P Bridge | Sends approved payments to banks and payment providers |

**You can adopt these modules independently**, according to what you need. We recognise that governments already have systems running, and that replacing an entire benefit-delivery chain in a single phase is rarely feasible.

All the modules listed above are production-ready.

---

## 2. What OpenG2P does *not* do

**OpenG2P is not a foundational ID system** such as MOSIP. It can issue functional IDs — a social benefit ID, farmer ID, or worker ID, for example — but these are not intended to uniquely identify an individual across government.

**OpenG2P is not a payment system.** For digital cash transfer it provides the *bridge* that connects upstream programme-management systems to your country's payment rails. Payment switches, payment gateways, and core banking software remain outside its scope. See the [G2P Bridge documentation](../../g2p-bridge/README.md).

---

## 3. Is OpenG2P right for our programme?

OpenG2P fits wherever government makes **bulk cash or in-kind transfers to people**: a registry holds the potential beneficiaries, a set of criteria filters them, and the transfer is carried out in cycles or batches.

That pattern covers more than regular ongoing programmes. Pension schemes and emergency payments to registered families — such as a rapid disaster response — benefit from the same infrastructure.

OpenG2P is **scalable**, from a few thousand beneficiaries to many millions. At small scale you can install the platform on minimal hardware and expand it as demand grows.

---

## 4. Moving from what we have today

Almost no government starts from nothing, so "how do we get there from here" is usually the deciding question.

Because OpenG2P is modular, you can replace parts of your system while leaving the rest in place and upgrading it later. OpenG2P uses a **PostgreSQL** database with published schemas, so migration from a legacy system is not normally a difficult exercise.

Two things are worth planning for:

- **Data cleaning is yours.** It depends heavily on your domain, department, and context, so the implementing department must own it.
- **Deduplication comes after loading.** Once records are in the registry, you can deduplicate using the tools OpenG2P provides.

We support governments and partners with guidance on architecture, design, and the migration process. We do not, however, have the capacity to carry out the migration ourselves.

---

## 5. Standards, compliance and open-government requirements

OpenG2P is positioned as **Digital Public Infrastructure** and interoperates through open standards — notably **G2P Connect / DCI** for ID-to-account mapping and payment interoperability, and integration with **MOSIP** where a national ID exists.

OpenG2P is listed in the **Digital Public Goods Alliance registry as a DPG**. We aim to use published open standards, and emerging ones as they mature.

---

## 6. Maturity — who is already using it

OpenG2P is **already in production in several countries**, across use cases including farmer registries, an end-to-end cash-for-work programme, a pension programme, a national social registry, and a cash transfer system for a welfare department.

We hold an **annual conference** where countries and partners exchange their successes, learnings, and challenges.

OpenG2P includes a basic **Grievance Redress Mechanism (GRM)** module. In practice most implementations prefer to use their own GRM front end, because it is tightly coupled to their citizen-facing portal. We provide API access to GRM data to support this.

---

## 7. Who is behind OpenG2P, and will it still be here in ten years?

**Stewardship.** OpenG2P is housed at the **International Institute of Information Technology, Bangalore (IIITB)**, a non-profit research university. It is not the commercial product of a single company.

**Origins.** OpenG2P began in 2018 as a response to the Ebola crisis in Sierra Leone, when UNDP — in partnership with the Government of Sierra Leone — assembled a system from open-source components to deliver cash to people in need. In 2022 the project was handed over to IIITB to take forward, enhance, and offer to other countries.

**Licensing and your right to modify.** The code is open source: **MPL-2.0** for OpenG2P-originated components, and **LGPLv3** for Odoo-derived components such as PBMS. In practice your IT team may modify the software to fit local rules and processes; the obligations differ between the two licences.

**Continuity.** Because the software is open source and self-hosted, a government that has deployed OpenG2P keeps the code and the running system regardless of what happens to any organisation. OpenG2P is funded by well-established international philanthropic funders including the Gates Foundation, Co-Develop, and NORAD, and IIITB — a reputable educational institution — will continue to support countries. Capacity building is built into every OpenG2P engagement, precisely so that countries can run their own infrastructure without depending on an external agency.

**Governance.** OpenG2P has a governing body. See [openg2p.org](https://openg2p.org).

---

## 8. What adoption takes — effort, team and support

Timelines depend on several factors: the nature of the engagement, how prepared the country is, the availability of developers and DevOps engineers, access to hardware, and whether there is a champion on the government side to drive the initiative.

As a practical reference point, an OpenG2P **sandbox can be running in a few hours**, and a **pilot setup in a few days**.

We provide advisory, design and architecture guidance, and **L3 support** to governments through all phases of a project. Beyond the engagement, we maintain the code base and provide bug fixes, enhancements, and upgrades to the core platform.

---

## Related

* [Use Cases](../README.md)
* [Deployment](../../deployment/README.md)
* [License](../../license.md)
