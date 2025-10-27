# Why Odoo?

Often the following question is asked:  _why did OpenG2P choose Odoo framework as base technology for implemening modules_.  The explanation provided below addresses this question.

OpenG2P was inherited from UNDP’s original version which had implemented the program management capabilities using Odoo.  At several junctures in the project we have  evaluated the cost/benefit of moving out of Odoo,  but the general consensus has been to continue with Odoo for Registry and PBMS given the flexibility and rapid deployment of features.  Also, since we are still in a phase where we encounter new requirements and business processes followed in countries, adaptability and ability to update the core platform rapidly is important. Moreover, we realise that UI is a must for all applications, rather than just having an API based system, and this where Odoo scores above the others.

Odoo gives tremendous capabilities to rapidly build MIS type applications with user interface. Odoo offers great **RAD** capabilities where we need to only define the persistent model and Odoo with its framework, provides a UI with CRUD functionality without much coding. We can choose from pre-built custom UI widgets to present the model. Plus, there is a **large active community** - from where we can get additional widgets wherever required. Having said that, for PBMS (Beneficiary management system), we use Odoo only for Program Configuration and Disbursement Cycle Configuration and Approvals. During the disbursement cycle, the actual beneficiary list creation, eligibility evaluation, entitlement computations - processes which are candidates for high volumes, we have delegated these processes into a decoupled microservice (a fastapi based microservice with asynchronous processing using the celery framework). This microservice can be scaled out to handle beneficiary volumes. Since the Odoo part of the application is not challenged with volumes, we can continue to leverage the strengths of Odoo.

**Extensibility**: Odoo never forces you to modify any code to change the behaviour or build a new use case. It can be completely extensible.. The extensibility is available in every area like Data model, business logic, UI, forms and integrations. This means that the implementation team is never modifying any OpenG2P code, rather they are keeping it intact and extending through their own code.

**High configurability** - Using Odoo’s built-in configuration tools—such as custom fields, dynamic forms, configurable workflows, and granular role-based access—administrators can quickly adapt household registration, case management, eligibility reviews, and payment approvals without needing software development effort.

**Localization capabilities**- Odoo natively handles multiple languages, regional formats, and country-specific business rules, allowing systems to align seamlessly with local administrative practices. Localization packs provide ready configurations for address formats, currency conventions, calendars, and compliance features. User interfaces and data entry forms can be translated dynamically, enabling frontline workers to operate in their preferred language while administrators maintain centralized control.

**Security**: Odoo is widely used and has a proven track record on **security** of software.  With the assurance of secure undelying software, OpenG2P has added several security layers to and achieved an [A+ security rating](../privacy-and-security/security-audits/security-audit-2025-march.md) awarded by an independent assessment agency.

Two important modules related to cash transfer - [G2P Bridge](../g2p-bridge/) and [SPAR](../spar/) **do not use Odoo**. They have been developed using fastAPI. &#x20;

**Licensing**: Odoo is available under the LGPL license which is more permissive than say, AGPL, or GPL. We have ensured that all dependent libraries that we use are strictly LGPL only. All the dependencies that had restrictive licenses like AGPL, GPL have been removed. The licensing of Odoo (under LGPL) and other components of OpenG2P (under MPL) have been carefully examined in consultation with our IP lawyers. The clarification on the usage of these licenses for System Integrators in the context of OpenG2P has been published [here](https://docs.openg2p.org/license)





