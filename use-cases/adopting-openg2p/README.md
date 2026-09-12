# Adopting OpenG2P — A Guide for Evaluators

This guide is for a **government department or programme lead deciding to adopt OpenG2P**. It is deliberately non-technical: no deployment, no code. If you are implementing or operating OpenG2P, see the Deployment and product guides instead.

> **How this guide is maintained.** Every section below lists the questions it must answer. Those questions come from real evaluation conversations, captured in the OpenG2P knowledge-gap pipeline. A section is "done" when a reader can answer its questions without asking anyone. Please keep the question lists when editing — they are the acceptance criteria.
>
> Blocks marked **TODO (needs input)** could not be written from existing documentation. They require facts only the OpenG2P team holds. Please do not fill them with assumptions — an unsupported claim here is worse than a gap.

---

## 1. What OpenG2P is

OpenG2P is **open-source software that your government installs, owns, and runs** — not a hosted service and not a product licensed from a vendor. The source is public (GitHub) under open-source licences, so there is no per-seat cost and no vendor who can withdraw it.

It is **modular**. The main building blocks are:

| Module | What it does |
|---|---|
| Registry | Holds beneficiary/household records (social registry, farmer registry, etc.) |
| PBMS | Defines programmes, eligibility rules, enrolment and disbursement cycles |
| SPAR | Maps a beneficiary ID to their financial address (bank account / wallet) |
| G2P Bridge | Sends approved payments to banks and payment providers |

> **TODO (needs input):** Confirm which modules can genuinely be adopted independently vs which have hard dependencies, and state the supported combinations. Evaluators specifically ask "can we pick what we need?" — answer it explicitly.

All the above modules can be adopted independently based on your need. OpenG2P understands that governments will have existing systems running. Replacing entire benefit delivery chain in just one phase may not be feasible. 

The modules listed above are production ready.

---

## 2. What OpenG2P does *not* do

OpenG2P is not an foundational ID issuance system like MOSIP. While functional IDs like social benefit ID, farmer ID, worker ID etc. may be issued, these are not suitable for uniquely identifying an individual.

On digital cash transfer OpenG2P provides the "bridge" infrastructure to connect the upstream program management systems to the payment rails of your country. However, systems like payment switch, payment gateways, banking software etc are not in the scope of OpenG2P.  See G2P Bridge documentation.

---

## 3. Is OpenG2P right for our programme?

OpenG2P fits well wherever you have  bulk cash or in-kind transfer from government to person - where a registry maintains the potential beneficiaries that needs to be filtered based on certain criteria and then the transfer carried out as cycles/batches. So pension schemes, emergency payments to registered families as a rapid disaster reponse also can benefit from such a infrastructure in addition to ongoing regular programs. 

OpenG2P is scalable platform - applicable for just a few thousand beneficiaries to millions. For small scale you may install the platform on minimal hardware and then expand as the need increases.

---

## 4. Moving from what we have today

Almost no government is starting from nothing, so "how do we get there from here" is usually the deciding question. As mentioned above, OpenG2P is modular and hence you can decide to upgrade parts of your system while keeping the rest of the system and maybe consider it upgrading later. OpenG2P uses Postgersql database with published schemas structure. Migration from legacy systems should not be a difficult exercise. However, cleaning of data is the responsibility of the departments implementing as it is very specific to the domain, department and context. After loading of data in registry deduplication may be done using tools provided by OpenG2P. 

We support governments and partners with guidance on architecture, design and migration process. However, OpenG2P does not have capacity to implement or conduct the migration process itself.

---

## 5. Standards, compliance and open-government requirements

OpenG2P is positioned as Digital Public Infrastructure and interoperates through open standards — notably **G2P Connect / DCI** for ID-to-account mapping and payment interoperability, and integration with **MOSIP** where a national ID exists. Is is part of the Digital Public Goods Alliance registry as a DPG. OpenG2P endevaours to use published open standards as well the emerging once.  

---

## 6. Maturity — who is already using it

OpenG2P is already in production in several countries for use cases like farmer registry, end2end cash for work program, pension program, national social registry, cash transfer system for welfare department etc. We conduct annual conference for countries and partners to come together and their exchange their successes, learnings, and challenges.

OpenG2P has a basic Grievance Redresssal Mechanish (GRM) module, however, generally, most implementations would like to use their GRM frontends as they are tightly coupled with their citizen facing portals. To facilitate this we provide API access to access data for GRM.

---

## 7. Who is behind OpenG2P, and will it still be here in ten years?

**Stewardship.** OpenG2P is housed at the **International Institute of Information Technology, Bangalore (IIITB)**, a non-profit research university. It is not a commercial product of a single company.

**Origins.** OpenG2P originated in 2018 as a response to Ebola Crisis in Sierra Leone. UNDP in partnershop with Seirra Leone government quickly put together a software system using open source components to deliver cash to the needy. Later, on 2022 this project was handed over to IIITB to take it forward, enhance it and offer it to countries.   

**Licensing and your right to modify.** The code is open source: **MPL-2.0** for OpenG2P-originated components, and **LGPLv3** for Odoo-derived components such as PBMS. In practice your IT team may modify the software for local rules and processes; obligations differ between the two licences.

**Continuity.** Because the software is open source and self-hosted, a government that has deployed OpenG2P retains the code and the running system regardless of what happens to any organisation. OpenG2P is funded by well established international philanthropic funds like Gates Foundation, CoDevelop and NORAD. IIITB being a reputed educational institution will continue to support countries. Inherent in OpenG2P engagement is the capacity building which is key for countries to continue with their infrastructure without having to be depedent on any external agencies. 

OpenG2P has a governing body. Refer to [openg2p.org](https://openg2p.org)

---

## 8. What adoption takes — effort, team and support

**This section must answer:**
- Roughly how long does it take to go from a decision to adopt OpenG2P to actually paying out benefits to real beneficiaries?
- If something goes wrong in a live payment run — say disbursements fail — is there an official helpdesk or support team we can call, or are we entirely responsible for fixing it ourselves?

The timelines for adoption depends on several factors like the nature of the engagement, prepardness of countries, availablity of developers and DevOps engineers, availability of hardware, champion on the government side to drive the initiative etc.  As such, an OpenG2P sandbox can be brought up in just a few hours and a setup for pilot can be created in a few days.  

OpenG2P provides advisory, design and archirtecture guidance, and L3 support to the governments during all phases of the project. Beyond the engagement, OpenG2P maintains the code base and provides bug fixes, enhancements and upgrades for the core platform.

---

## Related

* [Use Cases](../README.md)
* [Deployment](../../deployment/README.md)
* [License](../../license.md)
