---
description: Administering Agri Stack after install.
---

# Administration

The install sets up everything Agri Stack needs to run ([what the install sets up](../deployment/README.md#what-the-install-sets-up)). What remains are decisions people make, in the portals of their own install. Each page below is one task, step by step. The [test script](../deployment/testing.md) does none of them for real partners.

| Guide | What it does | Who |
| --- | --- | --- |
| [Managing Partners](managing-partners.md) | Onboard a partner, give its staff partner portal accounts, assign and remove its use cases, disable it | The Exchange's partner manager; portal accounts, its Keycloak administrator |
| [Collecting a Consent](collecting-a-consent.md) | Record a farmer's consent in the partner portal and approve it | Partner staff; a Consent Approver at the Exchange |
| [Releasing Data to the Composite](releasing-data-to-the-composite.md) | Check the Composite is onboarded in the department (or onboard it); set what a registry releases to it; widen or narrow it as use cases change | Each department's partner manager |
| [Keys](keys.md) | Replace or rotate a signing key; respond to a compromised key | Each install's operator |

Where each one works:

| Install | Portal |
| --- | --- |
| The Exchange | Partner Management `https://partner-management.<Exchange domain>`; Keycloak `https://keycloak.<Exchange domain>` (realm `partner`) |
| A department | Its own Partner Management `https://partner-management.<department domain>` |

## Approvals

* **Separate the roles.** Every Partner Management change is a request that is raised and then approved, and Partner Management lets the person who raised it approve it. In production, have one person raise and another approve every onboarding, key and policy request, at the Exchange and in each department.
* **One exception: the Composite's onboarding.** The install raises and approves it itself (actor `bootstrap` in the Partner Management audit), with no policy: it grants nothing until a department adds the Composite's scope policy.
* **Departments own their scope policies for the Composite.** The Exchange's operator should not hold Partner Management admin rights in a department. Review widenings before approving them.
