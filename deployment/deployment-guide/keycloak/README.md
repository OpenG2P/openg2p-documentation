# Keycloak

These guides cover **Keycloak as the OpenG2P applications' identity provider** — the per-environment Keycloak installed by the environment stage (part of commons). It issues OIDC clients, realms, and user accounts for the OpenG2P modules (Registry, PBMS, SPAR, eSignet, the Staff Portal, etc.).

{% hint style="info" %}
**This is the apps' IdP, not Rancher's login.** Rancher (the cluster-management UI) uses **local authentication** — its admin users are created directly in Rancher, with no SSO. There is one Keycloak **per environment**, reached at `keycloak.<environment-domain>`.
{% endhint %}
