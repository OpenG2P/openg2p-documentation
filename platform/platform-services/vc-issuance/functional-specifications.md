---
description: >-
  The citizen's journey: phone-OTP login, the "My Wallet" tab (branded Inji
  Web), generating a Registry credential into the hosted wallet, and
  downloading it as a PDF.
---

# Functional Specifications

## Actors

| Actor | Role |
|-------|------|
| **Citizen (beneficiary)** | Logs into the department/Beneficiary Portal on a desktop, generates a credential into their hosted wallet, downloads a PDF. |
| **Department / Beneficiary Portal** | The citizen-facing portal. Hosts a **"My Wallet"** tab that is a **branded Inji Web** (same parent domain). |
| **Logto** | Citizen IdP — **phone-number + OTP** login; the OIDC authorization server for the whole flow. |
| **Inji Web** | Hosted-wallet frontend (branded, embedded as the "My Wallet" tab). |
| **Mimoto** | Hosted-wallet backend — performs the OpenID4VCI download, **stores** the VC, renders the **PDF**. |
| **Inji Certify** | The issuer — signs the VC, pulling claims from the Registry. |
| **OpenG2P Registry** | Source of the citizen's data; in Phase 1 surfaced to Certify as a phone-keyed, active-only **DB view**. |

## 1. Login — phone number + OTP

The citizen logs into the portal with their **phone number + OTP**, authenticated by **Logto**.
This single login establishes a **Logto SSO session** reused for everything that follows
(including the wallet deposit) — the citizen does **not** log in again.

* The portal identifies the citizen by **phone number** (and/or a Logto user id). That phone
  number is what links to the Registry record.
* No eSignet is involved in Phase 1. (If a deployment has eSignet, see
  [Identity & IdP → eSignet](identity-and-idp.md#optional-esignet).)

## 2. "My Wallet" — a branded Inji Web tab

The portal has a **"My Wallet"** tab which is a **branded Inji Web** instance hosted on the same
parent domain (see [Department Integration](department-integration.md)). It is initially empty.
Because Inji Web uses the **same Logto**, opening it does not prompt another login (SSO).

The citizen can generate a credential in two equivalent ways:
* from **"My Wallet"**, a **"Generate credential"** action lists the credentials they're eligible
  for; or
* from a specific **Registry/Register** page, a **"Download credential"** action for that type.

## 3. Generate the credential into the hosted wallet

```
Citizen        Branded Inji Web        Logto (OIDC AS)        Mimoto            Certify         Registry API
   │ pick credential │                      │                   │                 │                 │
   │ ───────────────►│ 1. authz_code+PKCE   │                   │                 │                 │
   │                 │ ───────────────────► │ (silent via SSO)  │                 │                 │
   │                 │ ◄──── auth code ──────│                   │                 │                 │
   │                 │ 2. POST /wallets/{id}/credentials                           │                 │
   │                 │    {issuer, code, grantType=authorization_code, codeVerifier}│                │
   │                 │ ──────────────────────────────────────► │                 │                 │
   │                 │                       3. token exchange  │ ──► Logto        │                 │
   │                 │                       4. GET credential (Bearer) ─────────► │                 │
   │                 │                                          │  5. resolve phone → record → claims│
   │                 │                                          │     ───────────────────────────►   │
   │                 │                                          │  6. render + sign VC (.p12)         │
   │                 │ ◄───────────── signed VC ─────────────── │ ◄────────────── │                 │
   │                 │                       7. Mimoto STORES the VC                                 │
   │ ◄─ shows VC ────│                                                                               │
```

* The branded Inji Web obtains an **`authorization_code` + PKCE** from Logto (silent, thanks to
  the existing session) and hands the code to **Mimoto**.
* **Mimoto** exchanges the code for a token, calls **Certify**, receives the **signed VC**, and
  **stores** it in the citizen's hosted wallet.
* **Certify** builds the VC by **pulling** the citizen's claims — Phase 1 via the stock Postgres
  plugin querying a **phone-keyed, active-only view** over the Registry data (`:id` = token
  `sub` = phone). See [Registry Data Connector](registry-data-connector.md).
* The citizen sees the new credential listed in **My Wallet**.

## 4. Download the PDF

From "My Wallet", the citizen clicks **Download**. Inji Web requests the credential from Mimoto
as a **PDF** (`GET /wallets/{id}/credentials/{credId}`, `Accept: application/pdf`); Mimoto renders
and returns it. The PDF can carry an embedded QR for offline verification.

> Phase 1 "download" = **PDF**. Online sharing to third parties (OpenID4VP) and the device-wallet
> (QR-to-phone) path are **later scenarios** — see [Technical Architecture](technical-architecture.md).

## Assisted (agent) variant

In a desk/kiosk setting an agent can drive the same journey on the citizen's behalf (agent
authenticated separately); the backend flow is identical. The citizen still owns the hosted
wallet (keyed to their identity).

## Assumptions for Phase 1

* Desktop portal; **phone + OTP** login via **Logto**; **no eSignet**.
* The Registry holds the citizen's record and can be **looked up by phone number** (one-to-one),
  surfaced to Certify as a phone-keyed, active-only DB view (Phase 1 DB-direct).
* Source = **Registry** only (PBMS/SPAR are later, same pattern).
* Delivery = **Mimoto-based hosted wallet + PDF** (no device wallet in Phase 1).
