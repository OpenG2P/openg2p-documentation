# Why Odoo?

A frequent question in the OpenG2P community is _why the project has chosen the Odoo framework as its underlying technology_ for building some of the core modules. This blog post clarifies the rationale behind that decision.

The story goes back to OpenG2P’s roots: the platform was originally developed as an extension of UNDP’s system, which made extensive use of Odoo for program management functions. During the course of OpenG2P's evolution, multiple project milestones involved thoughtful evaluations about potentially moving away from Odoo. Each time, the conclusion remained consistent—Odoo continues to deliver critical flexibility and rapid feature deployment, especially for core OpenG2P modules like [Registry](../products/registry/registry/social-registry/) and [PBMS](../pbms/).

**Adaptability and speed** remain vital for OpenG2P, as new country requirements and business processes frequently emerge. The ability to update the core platform rapidly is a significant advantage and Odoo’s integrated user interface makes a big difference—even when compared to purely API-driven systems.

Odoo’s platform enables rapid development of MIS-style applications with full UI support. Its robust rapid application development (**RAD**) tools allow teams to define data models and immediately gain fully functional CRUD interfaces with minimal code. A rich ecosystem of pre-built widgets and **vibrant community** support provide even more options for customization and enhancement.

When it comes to the [PBMS](../pbms/) (Beneficiary Management System) module, Odoo excels in configuring programs, managing disbursement cycles, and handling approval workflows. However, OpenG2P leverages a separate FastAPI-based microservice (using asynchronous Celery processing) for high-volume operations like beneficiary list creation, eligibility checks, and entitlement computation. This decoupling ensures that while Odoo drives configuration and approvals, heavy data tasks scale efficiently outside the core system.

Odoo’s **extensibility** stands out: implementation teams never have to modify OpenG2P’s base code. Instead, every aspect—data model, business logic, UI, forms, and integrations—can be extended independently, promoting maintainability and flexibility.

**Configuration** is equally powerful. Odoo’s built-in tools mean administrators can adapt workflows, registration forms, eligibility criteria, and payment approval processes through configuration rather than custom development. Dynamic fields, customizable forms, and granular access controls let organizations evolve quickly.

**Localization** is another strength. Odoo supports multi-language interfaces, various regional formats, and country-specific rules, ensuring a smooth fit for local administrative practices. Address formats, currencies, calendars, compliance settings, and translation packs are all managed natively, giving both frontline workers and administrators the tools to operate in their preferred languages.

**Security** is central to the platform. Odoo’s widespread usage and solid security reputation provide a strong foundation for OpenG2P’s own standards. Through additional protective layers, OpenG2P has achieved an [A+ security score](../privacy-and-security/security-audits/security-audit-2025-march.md) from independent evaluators.

It’s important to note that key cash transfer functions—such as [G2P Bridge](../g2p-bridge/) and [SPAR](../spar/)—are architected with **fastAPI** rather than Odoo. This choice reflects OpenG2P’s focus on performance and scalability for specialized modules.

[**Licensing**](../products/registry/registry/social-registry/features/online-assisted-registration/) considerations also shaped our technology choices. Odoo is offered under the permissive LGPL license, and care has been taken to remove any AGPL or GPL dependencies. OpenG2P Odoo libraries rely strictly on LGPL components. Legal reviews have confirmed these choices to support straightforward adoption and compliance for system integrators.

In summary, OpenG2P continues to rely on Odoo for its flexibility, extensibility, configuration ease, robust localization, and proven security—while innovating with complementary technologies where needed. This strategic choice helps OpenG2P deliver adaptable, secure, and scalable solutions for social protection programs across the world.
