---
description: >-
  Step by step, for a department's partner manager: onboard the Composite in
  the department's Partner Management by hand, where the install did not.
---

# Onboarding the Composite

Onboards the Composite (`PARTNER_AGRI_COMPOSITE`) in a Partner Management, with its keys read from the Composite's JWKS URL. **Usually not needed:** Commons Services does it at install when **Exchange Role** is set ([what the install sets up](../deployment/README.md#what-the-install-sets-up)). Do it by hand only where that was off, or the entry was removed.

## Steps

In the department's Partner Management (`https://partner-management.<department domain>`):

1. **Requests → + Onboard partner**:

   | Field | Value |
   | --- | --- |
   | Partner ID | `PARTNER_AGRI_COMPOSITE` |
   | Name | e.g. `Agri Stack Composite` |
   | Public keys | None |
   | JWKS URL | `https://agri-composite.<Exchange domain>/.well-known/jwks.json` |
   | Read keys from this JWKS URL whenever they are needed | **On** |
   | Policies | None |

2. **Submit request**, then approve the request (another person, in production).

The Composite then has no policy, so the registry still releases nothing to it: next, [Releasing Data to the Composite](releasing-data-to-the-composite.md).

## Check

```bash
curl -s https://partner-management-partner-api.<department domain>/keys/PARTNER_AGRI_COMPOSITE
```

It serves the same `kid` as `https://agri-composite.<Exchange domain>/.well-known/jwks.json`. If not: Partner Management cannot reach that URL.
