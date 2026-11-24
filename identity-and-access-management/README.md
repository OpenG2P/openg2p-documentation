---
description: >-
  Identity and Access Management (IAM) for OpenG2P: who can sign in, how they
  are authenticated, which data they may see, and how the product APIs trust
  the result.
---

# Identity & Access Management

IAM answers four questions for every OpenG2P product: **who is calling, how did they sign in, what may they do, and which records may they see.** One IAM service answers them for four groups of callers, and every product API relies on the same answers.

## The four groups of callers

| Group | Signs in through | Identity provider | Portal or client |
|---|---|---|---|
| Staff users | `iam-staff-api` | Keycloak, realm `staff` (or another configured OIDC provider) | Staff Portal |
| Agency users (agency administrators and agents) | `iam-agent-api` | Keycloak, realm `agent` | Agent Portal; Agent App on an Android tablet |
| Beneficiaries | `iam-bene-api` | eSignet, backed by an ID provider (Farmer Registry, Disability Registry, Foundational ID Registry) | Bene Portal |
| Partner systems | No sign-in | None: each request is signed | `iam-partner-api` and the Product Partner APIs |

The names are fixed throughout: **`iam-staff-api`, `iam-agent-api`, `iam-bene-api`, `iam-partner-api`** for the APIs, and **Staff Portal, Agent Portal, Bene Portal, Partner Systems and Agent App** for the clients.

## Architecture in brief

* **Three audiences, four APIs, one database.** Staff, agency and beneficiary users are the three audiences. The partner API is an integration surface, not an audience: there is no partner realm and no partner user type.
* **`iam-core`** is a shared library used by all four APIs: OIDC adapters (Keycloak and eSignet), token validation, CSRF protection, the data-policy engine, the Keycloak admin client and the ORM models.
* **One PostgreSQL database** sits behind a connection pooler. Each API writes only its own tables and has read access to the others, and Postgres grants enforce the split.
* **Migrations belong to `iam-staff-api` only.** It runs every schema change and the seeding of configuration data such as the login providers. The other APIs get no CREATE, ALTER or DROP rights, and start only after the staff API has migrated.
* **Keycloak** has two realms, `staff` and `agent`. The staff, agent and partner APIs administer it through service accounts. eSignet issues and manages beneficiary tokens, so beneficiaries are not users in IAM: the bene API keeps only a pairwise subject and a login/logout log.

### Who writes what

| Data | Written by |
|---|---|
| Applications, roles, permissions | `iam-staff-api` |
| Login providers | Seeding script only; staff can browse it, and the login code of each API reads it |
| `AGC_` policy definitions (agency policies) | `iam-staff-api` |
| `AGT_` policy definitions (agent policies) | `iam-agent-api` |
| Agencies and their `AGC_` assignments | `iam-staff-api` and `iam-partner-api` |
| Agents and their `AGT_` assignments | `iam-agent-api` and `iam-partner-api` |
| Beneficiary login/logout log | `iam-bene-api` |

## Authentication flow

Staff, agency and beneficiary users follow the same eleven-step authorisation-code flow. Only the identity provider and the API differ.

1. The portal calls `/auth/start-authentication-transaction` on its IAM API.
2. The API creates an auth-transaction object, keeps it in memory keyed by `STATE`, and returns it to the portal.
3. The portal redirects the browser to the identity provider's authorisation endpoint.
4. The browser navigates to the identity provider.
5. The user authenticates (password, OTP and so on).
6. The identity provider redirects the browser to the `redirect_uri` with an authorisation code.
7. The browser calls the IAM API at the `redirect_uri` with the code.
8. The API exchanges the code for tokens.
9. The identity provider returns the tokens.
10. The API validates the ID token and creates the auth context (for beneficiaries it logs the login event instead).
11. The API returns a success response to the browser.

The Agent App on the tablet is the exception: it signs in with OIDC (PKCE) directly against Keycloak and sends the bearer token to the product agent APIs. Partner systems do not sign in at all.

## Data policies

A **data policy** limits which records a role may see. Policies reach the token as Keycloak roles with a prefix.

| Prefix | Who it is for | Created by | Granted to |
|---|---|---|---|
| `DP_` | Staff | Staff users, in the Staff Portal | Staff users, as client roles under the application's client in realm `staff` |
| `AGC_` | Agencies (mandatory, the outer boundary) | Staff users | The agency's Keycloak group in realm `agent` |
| `AGT_{AGENCY_MNEMONIC}_` | Agents (optional, can only narrow) | Agency administrators, for their own agency | The agent's Keycloak user |

* **Staff enforcement.** The data-policy middleware in `iam-core` runs on endpoints that carry the data-policy decorator. It collects the `DP_` roles from all of the user's clients, asks the IAM API to evaluate them, and puts the resulting filter on the request. `ALLOW` policies are combined with OR, and `DISALLOW` policies are negated and combined with AND. With no `DP_` role there is no restriction.
* **Agent enforcement.** Keycloak returns the union of group and user roles, so it cannot intersect them. The agency middleware in `iam-core` resolves the `AGC_` roles to one filter and the `AGT_` roles to another and applies **`AGC_` AND `AGT_`**. With no `AGC_` role the agent sees nothing (deny by default); with no `AGT_` role the agency policy applies as it is; an `AGT_` role can never widen access.
* **Who may do what.** Staff manage only the policies they create (`AGC_` and `DP_`) and cannot edit `AGT_` policies. Partners read policy definitions and can attach `AGC_` policies to the agencies and `AGT_` policies to the agents they created, but cannot create or change definitions.
* **Narrowing an agency policy** does not delete agent policies. The intersection is computed on every read, and the Agent Portal shows which assignments are no longer effective.

## Agencies in IAM

Each agency is a Keycloak group in realm `agent`, named by its `agency_id`, and every agent or agency administrator belongs to exactly one agency group. The access token carries an `agency` claim, and services read that claim and never accept an agency from the request. Only staff (through `iam-staff-api`) and partner systems (through `iam-partner-api`) can create agencies. Agency administrators create agents through `iam-agent-api`.

Partner systems are onboarded in Partner-Management. The partner API checks that the partner exists and is active, fetches its public key and verifies the request signature. A partner can manage only the agencies and agents it created.

## Product APIs

Every product has an API for each caller group, built in the same layers.

1. **Clients.** The portals, the Agent App or the partner systems.
2. **Login layer.** The IAM API for that group, together with its identity provider, issues the token.
3. **Enforcement.** For staff and agent APIs, a small middleware injected from IAM into every product API checks the role and applies the data policy. Bene and partner APIs differ, as below.
4. **Product API layer.** For example `farmer-registry-staff-api`, `disability-registry-agent-api`, `pbms-bene-api` and `bridge-partner-api`, and the IAM business services.

| Product API | Token | Enforcement |
|---|---|---|
| Product Staff APIs | Staff token from Keycloak, realm `staff` | Role-based access and `DP_` data policies |
| Product Agent APIs | Agent token from Keycloak, realm `agent` | Roles, `AGC_` AND `AGT_` data policy, agency status. The Agent Portal calls only `iam-agent-api`; the Agent App calls every product agent API |
| Product Bene APIs | Bene token from `iam-bene-api` and eSignet | No role or data-policy middleware. The context is always the beneficiary ID in the token, and the APIs return data only for it |
| Product Partner APIs | No token: signed request, partner mnemonic in the payload header | Signature check against the partner's public key, from `partner-management-partner-api` (partner validation and public key) |

## In this section

* [Architecture](architecture.md)
* [Authentication Flow](authentication-flow/README.md): [Staff Portal Users](authentication-flow/staff-portal-users.md), [Agent Portal Users](authentication-flow/agent-portal-users.md), [Bene Portal Users](authentication-flow/bene-portal-users.md)
* [Data Policies](data-policies/README.md): [Staff Portal Users](data-policies/staff-portal-users.md), [Agent Portal Users](data-policies/agent-portal-users.md)
* [Product APIs](product-apis/README.md): [Staff](product-apis/apis-serving-staff-portal-users.md), [Agent and Agent App](product-apis/apis-serving-agent-users-and-agent-apps.md), [Bene](product-apis/apis-serving-bene-portal-users.md), [Partner Systems](product-apis/apis-serving-partner-systems.md)
