---
description: Administering Agri Stack after install.
---

# Administration

The install sets up everything Agri Stack needs to run ([what the install sets up](../deployment/README.md#what-the-install-sets-up)). What remains are decisions people make, in the portals of their own install. Each page below is one task, step by step. The [test script](../deployment/testing.md) does none of them for real partners.

| Guide | What it does | Who |
| --- | --- | --- |
| [Managing Partners](managing-partners.md) | Onboard a partner, assign and remove its use cases, disable it | The Exchange's partner manager |
| [Partner Portal Users](partner-portal-users.md) | Create and disable partner portal accounts for a partner's staff | The Exchange's Keycloak administrator |
| [Collecting a Consent](collecting-a-consent.md) | Record a farmer's consent in the partner portal and approve it | Partner staff; the Exchange's CM staff |
| [Releasing Data to the Composite](releasing-data-to-the-composite.md) | Set what a registry releases to the Composite; widen or narrow it as use cases change | Each department's partner manager |
| [Onboarding the Composite](onboarding-the-composite.md) | Onboard the Composite in a department by hand, where the install did not | Each department's partner manager |
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
