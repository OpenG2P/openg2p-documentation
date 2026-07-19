---
description: Historical — the Keycloak/Keymanager crypto backend removed after 1.0.0
---

# Keycloak Client (historical — removed)

{% hint style="warning" %}
**Historical page.** SPAR 1.0.0 shipped an optional **Keymanager** crypto backend:
when enabled, the Mapper Partner API authenticated to MOSIP Keymanager as a
confidential `openg2p-spar` OIDC client — provisioned by the `keycloak-init`
subchart — to verify partner signatures. That backend, the `keycloak-init`
dependency, and their `global.authClient*` / `keycloak-init.*` / `KEYMANAGER_*`
values have been **removed** in later versions and no longer exist in the chart.

The current SPAR verifies partner signatures **in-process** against public keys
served by the **Partner Manager (PM)** service (`GET /keys`, unauthenticated) — no
Keycloak or key service at runtime. For the current model see
[Privacy & Security](../features/privacy-and-security.md).
{% endhint %}
