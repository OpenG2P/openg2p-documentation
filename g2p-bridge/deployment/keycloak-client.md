---
description: Legacy — Keycloak client for the Keymanager crypto backend (1.0.0)
---

# Keycloak Client (legacy — Keymanager backend)

{% hint style="warning" %}
**Legacy page — not the current model.** The current Bridge verifies partner
signatures against the **Partner Manager (PM)** service (`GET /keys`, unauthenticated)
and needs **no Keycloak or Keymanager at runtime**; `keycloak-init.enabled` is
therefore **`false`** by default. This page's `g2p-bridge` OIDC client applies only to
the legacy `keymanager` backend (1.0.0's mechanism). For the current setup see
[Onboarding Partners](onboarding-partners.md) and [Partner Signing Key](partner-signing-key.md).

Note: the trial's **`pm-seed` Job** does need a Keycloak client with the
`partner_manager` role to *onboard* partners into PM — but that is the
`commons-services-staff-portal` client owned by Partner Manager (its
`<release>-staff-portal` client), **not** the `g2p-bridge` client described here.
{% endhint %}

The G2P Bridge chart can provision a Keycloak OIDC client through the
`keycloak-init` subchart. This page explains **when** that client is needed and
how it is created.

## Why a Keycloak client is needed (keymanager backend)

When `global.g2pBridgeCryptoBackend: keymanager`, the security model is **OAuth2 /
OIDC backed by Keycloak**:

1. **Authenticating to MOSIP Keymanager.** With the keymanager backend, partner
   **signature validation** is delegated to MOSIP Keymanager. To call Keymanager,
   the Bridge authenticates as a confidential OIDC client using the
   **client-credentials** grant. The credentials come from the `g2p-bridge`
   Keycloak client. This is controlled by `global.g2pBridgeKeymanagerAuthEnabled`.
2. **A single, named service identity.** Giving the Bridge its own client
   (`g2p-bridge`) provides a dedicated machine identity in the `staff` realm,
   so its access can be granted, audited and revoked independently of human
   users and of other components.
3. **Consistency with the OpenG2P platform.** Other OpenG2P products (NSR, SPAR,
   PBMS) provision their service clients the same way via `keycloak-init`. The
   Bridge follows the same convention so a single Keycloak realm secures the
   whole platform.

{% hint style="info" %}
The client is a **confidential, service-account** client (it authenticates
machine-to-machine, not on behalf of a logged-in user). `keycloak-init` enables
service accounts and marks the client non-public automatically.
{% endhint %}

## How the client is created

When `keycloak-init.enabled` is `true` (the default), a post-install job:

1. Creates the OIDC client `global.g2pBridgeAuthClientId` (default `g2p-bridge`)
   in realm `global.keycloakRealm` (default `staff`) at `global.keycloakBaseUrl`.
2. Generates the client secret and stores it in a Kubernetes **Secret named after
   the client id** (`g2p-bridge`), under the key `client_secret`.
3. The Bridge workloads read that secret (`global.g2pBridgeAuthClientSecret` /
   `…SecretKey`) to obtain tokens.

{% hint style="warning" %}
**Secret-name collision.** Because `keycloak-init` names the client secret after
the client id (`g2p-bridge`), the Bridge **database** secret is deliberately
named `<release>-db` (not the bare release name) to avoid clashing with it. This
is the one place the Bridge differs from NSR's naming.
{% endhint %}

## Key values

| Value | Default | Description |
| --- | --- | --- |
| `keycloak-init.enabled` | `true` | Create the client + secret. |
| `global.keycloakBaseUrl` | `https://keycloak.<namespace>.openg2p.org` | Keycloak base URL. |
| `global.keycloakRealm` | `staff` | Realm in which the client lives / is created. |
| `global.g2pBridgeAuthClientId` | `g2p-bridge` | OIDC client id (and the name of the K8s secret holding its password). |
| `global.g2pBridgeAuthClientSecretKey` | `client_secret` | Key inside that secret. |
| `global.g2pBridgeKeymanagerAuthEnabled` | `false` | When `true`, the Bridge authenticates to Keymanager using this client. |

## Enabling the Keymanager backend

Partner signature validation is **on by default** using the local backend, which
needs no Keymanager — this is the recommended setup for production too. Switch to
Keymanager only if your environment mandates it: set
`global.g2pBridgeCryptoBackend: keymanager` and
`global.g2pBridgeKeymanagerAuthEnabled: true` (with `keycloak-init.enabled: true`)
so the Bridge authenticates to Keymanager via this client.

{% hint style="info" %}
The Keycloak realm/client lives in Keycloak, not in the release namespace, so it
**survives** `helm uninstall` and the [uninstall script](teardown.md).
`keycloak-init` is idempotent — reinstalling reuses the existing client.
{% endhint %}
