---
description: >-
  How a government department integrates VC issuance into its own portal — the
  embedding options (A–D, we use C), branding a hosted Inji Web, shared-Logto
  SSO, and the Registry data connection (Phase 1: DB-direct).
---

# Department Integration

A government department already has its own citizen portal. VC issuance is delivered by
embedding a **branded Inji Web** (hosted wallet) into that portal as a **"My Wallet"** tab, with
**shared login** via Logto, and the **Registry data** supplied to Certify (Phase 1: DB-direct via
the stock Postgres plugin).

## Embedding options

There are four ways to put the wallet UI inside a department portal:

| Option | How it works | Seamlessness | Effort | Notes |
|---|---|---|---|---|
| **A. Iframe** | Branded Inji Web embedded in an `<iframe>` on a portal page | Medium | Low | Inji Web doesn't block framing by default; avoid iframe *silent* session checks (3rd-party cookies) — log in via redirect/popup |
| **B. Micro-frontend** | Mount Inji Web as a module/route (both are React; module federation) | High | High | Pixel-perfect, but tight build/version coupling |
| **C. Branded sub-site, linked as a tab** ✅ | Inji Web hosted at e.g. `wallet.dept.gov`, themed to match; portal links to it as a tab | Medium-High | Low–Med | **Chosen.** Cleanest technically; shared-Logto SSO makes it feel native |
| **D. Build your own UI on Mimoto APIs** | Portal calls Mimoto directly; no Inji Web | Highest | Highest | You reimplement list/PDF/sharing UI |

### We use Option C

A **branded Inji Web**, hosted under the **same parent domain** as the portal (e.g.
`wallet.dept.gov` alongside `portal.dept.gov`), surfaced as a **"My Wallet" tab**. This reuses
MOSIP's wallet UI (list, **PDF**, and later sharing) instead of rebuilding it, while looking and
feeling like part of the department portal.

## Branding Inji Web

Branding is **config-driven** (no rebuild for the basics):

* Runtime config (`env.config.js` → `window._env_`, applied by `theme.config.js`): **title,
  favicon, font, theme class, default language**.
* **Languages** via `locales/*.json`.
* Deeper visual match (colors, layout) via **Tailwind/CSS** — a light theme fork.

Prefer config-level branding to keep upgrades to new Inji Web versions painless; reserve forks
for deeper visual changes.

## Shared login (no second login)

Because the **portal and the branded Inji Web use the same Logto**, the citizen logs in **once**:

* The citizen logs into the portal (**phone + OTP** at Logto) → a Logto session exists.
* Opening "My Wallet" (Inji Web) triggers an OIDC login that **redirects to Logto**; Logto sees
  the existing session and returns silently — **no re-entry of OTP**.

Two rules keep this smooth:

1. **Host everything under one parent domain** (`portal.dept.gov`, `wallet.dept.gov`,
   `id.dept.gov`) so the Logto session cookie is first-party during the redirect.
2. **Do the Inji Web login via full redirect or popup**, not a hidden iframe (a silent
   in-iframe session check relies on third-party cookies, which modern browsers block).

## The Registry data connection (the department's data integration)

Certify needs the citizen's data to build the VC. **Phase 1 is DB-direct**: Certify uses the
stock **Postgres DataProvider plugin** to read a **phone-keyed, active-only view** that surfaces
the Registry data inside Certify's database. This needs **no Certify code** — only SQL/config —
but it requires:

* the token **`sub` = phone number** (Logto config), since the plugin keys `:id` on `sub`; and
* the Registry data **reachable inside Certify's DB** (via FDW / a synced table / a same-database
  view), exposed as a read-only view.

The cleaner **Phase-2 alternative** is a **custom REST connector** (a `DataProviderPlugin` JAR
that calls the Registry REST API, reads the `phone_number` claim, and avoids DB coupling) — at
the cost of custom Java.

Full design, SQL, and behaviours: **[Registry Data Connector](registry-data-connector.md)**.

## What a department actually does (checklist)

1. **Deploy** the shared stack: Inji Certify, Mimoto, branded Inji Web, Logto, reusing the
   cluster PostgreSQL (see [Deployment](deployment.md)).
2. **Configure Logto** for phone+OTP and register the OIDC clients (portal + Inji Web/Mimoto).
3. **Brand Inji Web** (config) and host it under the portal's parent domain; add the **My Wallet
   tab** (Option C).
4. **Register Certify as an issuer in Mimoto** (`mimoto-issuers-config.json`, auth server = Logto).
5. **Define the credential type(s)** in Certify (`credential_config`: template, issuer DID, key).
6. **Wire the Registry data** (Phase 1): expose a phone-keyed, active-only **view** inside
   Certify's DB (FDW/synced/cross-schema) and set the Postgres plugin's `scope-query-mapping`.

Each department is effectively a **tenant**: its own branded Inji Web, its own Logto clients,
its own Certify `credential_config`(s) and Registry connector.
