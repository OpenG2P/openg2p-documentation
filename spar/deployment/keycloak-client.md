---
description: Legacy — Keycloak client for the Keymanager crypto backend (1.0.0)
---

# Keycloak Client (legacy — Keymanager backend)

{% hint style="warning" %}
**Legacy page — not used by the current SPAR.** With the default
`global.sparCryptoBackend=local`, the Mapper API verifies partner signatures
**in-process** (against the `partner_keys` DB table) and needs **no Keymanager and
no OIDC client**. `keycloak-init.enabled` is therefore **`false`** by default. This
page applies only if you deliberately switch to the legacy `keymanager` backend
(SPAR 1.0.0's mechanism). For the current setup see
[Privacy & Security](../features/privacy-and-security.md).
{% endhint %}

The SPAR chart can provision a Keycloak OIDC client through the `keycloak-init`
subchart. This page explains **when** that client is needed and how it is created.

## Why a Keycloak client is needed (keymanager backend)

The SPAR Mapper Partner API can protect its endpoints with **partner signature
validation** performed by MOSIP **Keymanager**. To obtain tokens and call
Keymanager, the Mapper API authenticates as a confidential OIDC client using the
**client-credentials** grant. The credentials come from the `openg2p-spar`
Keycloak client.

1. **Authenticating to Keymanager.** The Mapper API exchanges its client id +
   secret for a token at the realm's token endpoint
   (`global.keycloakIssuerUrl` → `…/protocol/openid-connect/token`) and uses it to
   reach Keymanager's `jwtVerify` endpoint.
2. **A single, named service identity.** Giving SPAR its own client
   (`openg2p-spar`) provides a dedicated machine identity in the `staff` realm, so
   its access can be granted, audited and revoked independently of human users and
   of other components.
3. **Consistency with the OpenG2P platform.** Other OpenG2P products (NSR, G2P
   Bridge, PBMS) provision their service clients the same way via `keycloak-init`,
   so a single Keycloak realm secures the whole platform.

{% hint style="info" %}
The client is a **confidential, service-account** client (it authenticates
machine-to-machine, not on behalf of a logged-in user). `keycloak-init` marks the
client non-public and provisions no browser redirect URIs / web origins.
{% endhint %}

## How the client is created

When `keycloak-init.enabled` is `true` (the default), an install job:

1. Creates the OIDC client `global.authClientId` (default `openg2p-spar`) in realm
   `global.keycloakRealm` (default `staff`) at the Keycloak installed in the
   namespace (reached internally at `http://commons-keycloak:80`).
2. Generates the client secret and stores it in a Kubernetes **Secret named after
   the client id** (`openg2p-spar`), under the key `client_secret`.
3. The Mapper API reads that secret (`global.authClientSecret` /
   `global.authClientSecretKey`) to obtain tokens.

## Key values

| Value | Default | Description |
| --- | --- | --- |
| `keycloak-init.enabled` | `true` | Create the client + secret. |
| `global.keycloakBaseUrl` | `https://keycloak.<namespace>.openg2p.org` | Keycloak base URL (used by apps for the OIDC issuer/token URL). |
| `global.keycloakRealm` | `staff` | Realm in which the client lives / is created. |
| `global.authClientId` | `openg2p-spar` | OIDC client id (and the name of the K8s secret holding its password). |
| `global.authClientSecret` | `openg2p-spar` | Name of the K8s secret holding the client password (defaults to the client id). |
| `global.authClientSecretKey` | `client_secret` | Key inside that secret. |

{% hint style="info" %}
The Keycloak realm/client lives in Keycloak, not in the release namespace, so it
**survives** `helm uninstall` and the [uninstall script](teardown.md).
`keycloak-init` is idempotent — reinstalling reuses the existing client, and the
uninstall script keeps the client secret by default.
{% endhint %}
