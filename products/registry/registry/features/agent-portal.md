---
description: >-
  A separate portal for field agents, authenticated against its own Keycloak
  'agent' realm. Its first capability is Verifiable Credential issuance; it is
  built to carry further agent tasks.
layout:
  width: default
  title:
    visible: true
  description:
    visible: true
  tableOfContents:
    visible: true
  outline:
    visible: true
  pagination:
    visible: true
  metadata:
    visible: true
  tags:
    visible: true
---

# Agent Portal

The **Agent Portal** is a second staffed surface on the Registry Platform,
alongside the Staff Portal. It exists for a different audience doing a different
job: a **field agent** standing at a counter with a citizen in front of them,
rather than a back-office user working through a queue.

It ships with the platform, so every registry manifestation (Farmer Registry,
National Social Registry, …) inherits it. It is **off by default** —
`agentPortalApi.enabled` and `agentPortalUi.enabled` — because a deployment
that has no agents should expose no agent surface.

## A generic portal, not a credential tool

Today the portal carries exactly one capability: **issuing a Verifiable
Credential** to an authenticated beneficiary. That is the first task, not the
definition of the product.

The landing page is therefore a **list of tasks**, one card per capability,
rather than the issuance form itself. Adding a capability means adding a card;
it does not mean restructuring the application. A task the signed-in agent is
not permitted to perform is shown **disabled with the reason**, rather than
hidden — an agent who was told they can do something needs to see why they
cannot.

## Why a separate `agent` realm

Agents authenticate against a Keycloak realm of their own — `agent` — not the
`staff` realm.

They are a genuinely different population: typically far more numerous, often
contracted rather than employed, and entitled to a much narrower set of
actions. Keeping them in their own realm means a staff account grants nothing
in the agent portal and an agent account grants nothing in the staff portal,
without either side having to be careful about role naming.

| | Staff | Agent |
|---|---|---|
| Keycloak realm | `staff` | `agent` |
| Confidential client | `staff-portal` | `agent-portal` |
| Login theme | `staff-portal` | `agent-portal` |
| Permission | the full registry catalogue | `register:issue_credential` |

The realm, its confidential client and the client's Secret are created by
**commons-services**' `keycloak-init`, exactly as the `staff` realm is. The
registry chart adds only the demo `agent` user. This split matters: the client
is confidential and `iam-agent-portal-api` is its only consumer, so the client
and its Secret have to come from the release that configures that API.

{% hint style="info" %}
`keycloak-init` never resets an **existing** user's password, and the realm
lives in the Keycloak database, which outlives a registry reinstall. Changing
`global.agentUserPassword` therefore only takes effect on a realm that does not
yet have that user.
{% endhint %}

## How authentication works

The Agent Portal uses the **same model as the Staff Portal** — deliberately, so
there is one authentication design in the platform rather than two.

The UI is a **Next.js application whose `/api/*` routes are a Backend-For-Frontend
(BFF)**. The browser never holds a token:

```
Browser ──► /api/login ──► iam-agent-portal-api
                              /auth/start_authentication_transaction
                           ──► Keycloak (agent realm, PKCE)
Keycloak ──► iam-agent-portal-api /auth/callback
                           ──► exchanges the code, sets httpOnly cookies
Browser ──► /api/agent/* ──► BFF reads the cookies server-side,
                             adds Authorization/Cookie/CSRF headers
                           ──► Agent Portal API
```

**IAM is the OIDC confidential client.** It holds the client secret, performs
the code exchange, owns the session, and refreshes tokens silently. The browser
sees only httpOnly cookies it cannot read.

### Cookie names are prefixed

The agent and staff portals share a parent cookie domain (`.<namespace>.<domain>`),
and browsers match cookies by **domain, not origin** — so each portal receives
the other's cookies. With identical names the second login silently overwrites
the first, and each portal's API is then handed the other realm's tokens, which
it cannot verify.

The agent portal's cookies are therefore prefixed (`agent-X-Access-Token`,
`agent-X-ID-Token`, `agent-X-Session-Id`, `agent-X-CSRF-Token`) via
`IAM_AGENT_AUTH_COOKIE_PREFIX`. Staff keeps the unprefixed names. Both the IAM
service that **sets** the cookies and the Agent Portal API that **reads** them
must be configured with the same prefix.

### Signing out

Sign-out is RP-initiated OIDC logout: the portal calls `/api/logout`, IAM clears
the session cookies and redirects to Keycloak's `end_session_endpoint`, and
Keycloak returns the browser to `post_logout_redirect_uri` — which IAM takes from
the login provider's `default_redirect_uri`.

{% hint style="warning" %}
**`global.agentPortalHostname` must name the registry's REAL agent UI host on the
commons-services install.** It defaults to `agent-portal.<baseDomain>`, but the
portal is served by the registry chart at its own host (e.g.
`fr-agent.<baseDomain>`). If the two disagree, **login still works and only
sign-out breaks** — login redirects via the IAM callback, which is registered
correctly, while logout sends the browser to a host that serves nothing.

That one value drives three things, which are wrong together:

* `login_providers.default_redirect_uri` — where logout returns to
* the Keycloak client's `redirectUris` / `post.logout.redirect.uris`
* `IAM_AGENT_CORS_ALLOW_ORIGINS`

```
--set global.agentPortalHostname=fr-agent.<baseDomain>
```

Easy to miss, because commons-services has to be told a hostname that only the
registry chart really knows.
{% endhint %}

### Permissions

Roles live on the `agent-portal` Keycloak client and are resolved into
permissions by the **staff** IAM API — `/user-access/*` exists only there. This
requires two things to line up, and returns an empty list (with HTTP 200) if
either is missing:

1. the agent's roles under `resource_access['agent-portal']` in the token, and
2. an IAM **application** registered with mnemonic `agent-portal`.

The registry's `iam-register` Job registers that application, declaring the
`register:issue_credential` and `register:verify_credential` permissions and the
roles that grant them. The two are **separate on purpose**: checking a card
someone presents and creating a new one are different acts with different risk,
and a deployment may well want staff who can do the first and not the second.

{% hint style="warning" %}
`keycloak-init` creates a realm and its client only when **absent** — it does not
reconcile roles onto an existing client, and the Keycloak database outlives a
registry reinstall. On an environment created before a role existed, that role is
silently skipped even though the chart requests it, and the corresponding card
does not appear in the portal. Adding a role to an existing deployment means
adding it to the Keycloak client directly.
{% endhint %}

## Current functionality: Verifiable Credential issuance

The agent's job is to establish that the person in front of them is who they
claim to be, and then hand them a credential. That is three steps, and the
portal presents them on one screen because the citizen is waiting and the
authentication expires in minutes.

```
1. Verify the ID     agent enters/scans the beneficiary's national ID
   (look-up)         → the portal confirms a record exists, is ACTIVE,
                       and is eligible for a credential

2. Authenticate      the beneficiary authenticates themselves at eSignet
   (the beneficiary)  (OTP, or biometric at the counter)
                     → the portal polls until the authentication lands
                     → the authenticated subject is checked AGAINST the
                       record's foundational_id — it is not enough that
                       someone authenticated, it must be this person

3. Issue             claims are read from the registry and pushed to
                     Inji Certify, which builds and signs the credential
                     → the portal renders a printable PDF with a signed QR
                       and streams it to the agent's browser
```

Step 2 is the point of the whole flow. The **agent** is authenticated by their
own token on every call; the **beneficiary** is authenticated by eSignet, and
that authentication is re-checked at the moment of issue rather than trusted
from an earlier screen — the window may well have elapsed while the agent was
reading.

## Current functionality: Verifiable Credential verification

A second card, **Verify VC**, gated by `register:verify_credential`.

The agent uploads the printed credential (PDF) or a photo of it, and gets a
verdict plus the credential's contents.

```
1. Read the QR       in the BROWSER — pdf.js rasterises a PDF page, a JS QR
   (client-side)     reader handles images, PixelPass unwraps Base45 → zlib
                     → hex CWT
                     → the image itself is NEVER uploaded

2. Check it          the hex payload goes to the Agent Portal API, which calls
   (server-side)     verify-service in-cluster; verify-service resolves the
                     issuer's ES256 key from Certify's published JWKS and
                     checks the COSE signature

3. Show it           the verdict, and beneath it the signed contents —
                     issuer, validity, Full Name, Date of Birth, Gender,
                     Farmer ID
```

**The image never leaves the agent's device.** A photo of a credential is a
photo of someone's identity document; uploading it would put that image in
request logs, proxies and every intermediary in between. Only the signed payload
the QR already encodes is transmitted.

**Showing the contents is the point, not decoration.** "Valid" alone says the
card is genuine without saying whose it is, so it cannot catch a real credential
presented by the wrong person. The fields shown are decoded from the signed
payload — exactly what was signed — and only after a `SUCCESS`.

Every verification is audited with its **verdict**, so the trail distinguishes a
genuine card from a forged one. See
[Verification](../../../../platform/platform-services/vc-issuance/verification.md).

For the full design — what each step guarantees, what the QR contains, which
signature a verifier checks, and how a registry supplies its claims — see
[Verifiable Credential Issuance](../../../../platform/platform-services/vc-issuance/README.md)
and in particular [Phase 1 — Paper Credential](../../../../platform/platform-services/vc-issuance/phase-1-paper-credential.md).

## Components

| Component | Repo | Role |
|---|---|---|
| `agent-portal-ui` | Registry Platform | Next.js app; its `/api/*` routes are the BFF |
| `agent-portal-api` | Registry Platform | Resolves the record, drives the beneficiary's authentication, pushes claims to Certify, renders the PDF, logs the issuance |
| `iam-agent-portal-api` | IAM | OIDC confidential client for the `agent` realm |

A variant registry rebuilds `agent-portal-api` from the platform image with its
own extension installed, exactly as it does for `staff-api` — the service maps
the registry's own register-domain model, and running the platform's default
model against a variant's database is a schema mismatch.

## Extending the portal

A new agent capability needs:

1. a **permission** on the `agent-portal` client, declared in the registry's
   `iam-register` payload;
2. **routes** on the Agent Portal API, guarded by that permission;
3. **BFF routes** in the UI that proxy them, so the browser still holds no token;
4. a **card** on the landing page, enabled by that permission.

Nothing about the authentication model changes.
