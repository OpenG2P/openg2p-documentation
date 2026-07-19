---
description: Historical — the Keycloak/Keymanager crypto backend removed after 1.0.0
---

# Keycloak Client (historical — removed)

{% hint style="warning" %}
**Historical page.** Version 1.0.0 shipped an optional **Keymanager** crypto
backend: when enabled, the Bridge authenticated to MOSIP Keymanager as a
confidential `g2p-bridge` OIDC client — provisioned by the `keycloak-init`
subchart — to validate partner signatures. That backend, the `keycloak-init`
dependency, and their `global.g2pBridge*` / `keycloak-init.*` values have been
**removed** in later versions and no longer exist in the chart.

The current Bridge verifies partner signatures **in-process** against public keys
served by the **Partner Manager (PM)** service (`GET /keys`, unauthenticated) — no
Keycloak or key service at runtime. For the current model see
[Onboarding Partners](onboarding-partners.md) and
[Partner Signing Key](partner-signing-key.md).
{% endhint %}

{% hint style="info" %}
The trial's partner-onboarding Job (`pm-register` / `pm-seed`) still uses a Keycloak
client with the `partner_manager` role to *onboard* partners into PM — but that is
Partner Manager's `commons-services-staff-portal` client, unrelated to the removed
`g2p-bridge` client described above.
{% endhint %}
