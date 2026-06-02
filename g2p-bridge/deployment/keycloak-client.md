---
description: Why the G2P Bridge needs a Keycloak (OIDC) client
---

# Keycloak Client

The G2P Bridge chart provisions a Keycloak OIDC client through the
`keycloak-init` subchart. This page explains **why** that client is required and
how it is created.

## Why a Keycloak client is required

The G2P Bridge does not talk to sponsor banks (or, in in-kind mode, to PBMS and
the Registry) with anonymous calls. Several of its outbound and inbound
interactions are secured, and the security model is **OAuth2 / OIDC backed by
Keycloak**:

1. **Authenticating to MOSIP Keymanager.** Partner API requests are protected by
   partner **signature validation**, which uses MOSIP Keymanager. To call
   Keymanager, the Bridge authenticates as a confidential OIDC client using the
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

## Enabling for production

On `develop`/demo, `global.g2pBridgeKeymanagerAuthEnabled` is `false` — the
client is still created (so it is ready), but the Bridge does not yet enforce
Keymanager authentication. **In production**, set
`global.g2pBridgeKeymanagerAuthEnabled: true` (with `keycloak-init.enabled: true`)
so Partner API signature validation against Keymanager is active.

{% hint style="info" %}
The Keycloak realm/client lives in Keycloak, not in the release namespace, so it
**survives** `helm uninstall` and the [uninstall script](teardown.md).
`keycloak-init` is idempotent — reinstalling reuses the existing client.
{% endhint %}
