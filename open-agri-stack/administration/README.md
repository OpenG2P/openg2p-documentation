---
description: >-
  What the administrators of Agri Stack do by hand once it is installed: at
  the Exchange, partners and their staff accounts; in each department, what it
  releases to the Exchange; everywhere, keys.
---

# Administration

The install sets up everything Agri Stack needs to run ([what the install sets up](../architecture/exchange.md#what-the-install-sets-up)). What remains are decisions people make, in the portals of their own install. These pages give the steps; the test script does some of them for a test partner only ([Testing](../deployment/testing.md)).

| Who | Task | Page |
| --- | --- | --- |
| The Exchange's partner manager | Onboard a partner, assign and remove its use cases, disable it | [Managing Partners](managing-partners.md) |
| The Exchange's Keycloak administrator | Partner portal accounts for a partner's staff | [Partner Portal Users](partner-portal-users.md) |
| Each department's partner manager | Decide what its registry releases to the Exchange, and widen or narrow it as use cases change | [Releasing Data to the Exchange](releasing-data-to-the-exchange.md) |
| Each install's operator | Replace or rotate the signing keys; respond to a compromised key | [Keys](keys.md) |

Where each one works:

| Install | Portal |
| --- | --- |
| The Exchange | Partner Management `https://partner-management.<Exchange domain>`; Keycloak `https://keycloak.<Exchange domain>` (realm `partner`) |
| A department | Its own Partner Management `https://partner-management.<department domain>` |

## Approvals

* **Separate the roles.** Every Partner Management change is a request that is raised and then approved, and Partner Management lets the person who raised it approve it. In production, have one person raise and another approve every onboarding, key and policy request, at the Exchange and in each department.
* **One exception: the Composite's onboarding.** The install raises and approves it itself (actor `bootstrap` in the Partner Management audit), with no policy: it grants nothing until a department adds the Composite's scope policy.
* **Departments own their scope policies for the Composite.** The Exchange's operator should not hold Partner Management admin rights in a department. Review widenings before approving them.
