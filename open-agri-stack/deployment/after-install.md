---
description: >-
  The one step after installing Agri Stack: each department releases its
  registry's data to the Exchange. Everything else is set up by the install.
---

# After Install

Step 3 of the [install steps](README.md#install-steps). The install has set up the keys, the Composite's entries in every Partner Management and the trust between the Consent Managers ([what the install sets up](README.md#what-the-install-sets-up)). One decision is left, in each department.

## Each department releases its registry's data

In each department's Partner Management, add the Composite's scope policy for its registry: what the registry releases to the Exchange. Until then every query through the Exchange is denied by that registry. Steps: [Releasing Data to the Exchange](../administration/releasing-data-to-the-exchange.md).

For a test install, the [test script](testing.md) adds these policies itself, covering the use case it tests.

## Check

In each department (here `trial`), Partner Management serves the Composite's key and its policy:

```bash
curl -s https://partner-management-partner-api.trial.openg2p.org/keys/PARTNER_AGRI_COMPOSITE
curl -s https://partner-management-partner-api.trial.openg2p.org/policies/PARTNER_AGRI_COMPOSITE
```

| Result | Cause | Fix |
| --- | --- | --- |
| `/keys/…` answers 404 | The department's Commons Services has no **Exchange Role**, or its Partner Management cannot reach the Composite's JWKS URL | Set **Exchange Role** `department` (and **Exchange Domain** or **Composite JWKS URL** if the Exchange is elsewhere); check the PM staff API log for "Bootstrap" |
| `/policies/…` answers 404 | No scope policy yet | [Add it](../administration/releasing-data-to-the-exchange.md#add-the-policy) |

Then: [Testing](testing.md). Partners are onboarded by the Exchange's administrators: [Administration](../administration/README.md).
