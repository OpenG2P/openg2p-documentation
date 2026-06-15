---
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
description: >-
  How applications (e.g. registries) self-register their Staff Portal tile,
  roles and permissions into the IAM Staff service at install time.
---

# Staff Portal Application Registration

## **1. Overview**

The IAM Staff service drives the **Staff Portal** home screen: the set of application tiles a staff user sees (Registry, MinIO, Superset, Keycloak …), and the roles/permissions that gate access to each.

Historically this catalog was **seeded into IAM ahead of time**, which had two problems:

* IAM is installed **before** the applications it points to, so an application URL (e.g. a registry's) had to be hardcoded into IAM before that application even existed.
* An environment may run **multiple instances of the same product** (e.g. two registries), which a single hardcoded entry cannot represent.

To solve both, an application now **registers itself into IAM at install time** via a dedicated API. The application pushes its own tile (URL, icon, ordering) together with its roles and permissions. The call is idempotent and keyed by a mnemonic, so re-installs/upgrades simply refresh the entry, and multiple instances coexist by each using a distinct mnemonic.

***

### **1.1 Key Rule — mnemonic == Keycloak client\_id**

The `application_mnemonic` an application registers with **must equal its Keycloak `client_id`**. Staff Portal tiles and permissions are gated by the `resource_access` client-roles in the user's token, so this equality is what lets IAM resolve which tiles a user can open and which permissions a role grants.

For multiple instances of the same product, each instance has its **own Keycloak client** (e.g. `nsr-staff-portal`, `fr-staff-portal`) and registers its catalog under that mnemonic.

***

## **2. API Reference**

### **2.1 Register / update a Staff Portal application**

Upserts an application and its access catalog. Creates the application on first call, updates it on subsequent calls (matched by `application_mnemonic`).

```
POST /user-access/staff_portal_applications
Authorization: Bearer <access-token>
Content-Type: application/json
```

#### **Authentication**

The endpoint requires a valid bearer token issued by a login provider IAM trusts (the staff realm). It is guarded by the `auth_api_register_staff_portal_application` setting; operators can restrict it to a specific role by configuring a required claim (`claim_name` / `claim_values`) via `IAM_STAFF_AUTH_API_REGISTER_STAFF_PORTAL_APPLICATION__*`.

#### **Request body**

<table data-full-width="true"><thead><tr><th width="230">Field</th><th width="140">Type</th><th>Description</th></tr></thead><tbody><tr><td><code>application_mnemonic</code></td><td>string (required)</td><td>Unique identifier; <strong>must equal the application's Keycloak <code>client_id</code></strong>.</td></tr><tr><td><code>application_url</code></td><td>string (required)</td><td>URL the tile opens (the application's Staff Portal UI).</td></tr><tr><td><code>application_description</code></td><td>string</td><td>Display name / description.</td></tr><tr><td><code>icon_base64</code></td><td>string</td><td>Base64-encoded tile icon (SVG/PNG).</td></tr><tr><td><code>width</code></td><td>integer</td><td>Tile width hint.</td></tr><tr><td><code>order</code></td><td>integer</td><td>Tile ordering on the home screen.</td></tr><tr><td><code>active</code></td><td>boolean (default true)</td><td>Whether the tile is active/visible.</td></tr><tr><td><code>permissions</code></td><td>array</td><td>The application's permission catalog (see below).</td></tr><tr><td><code>roles</code></td><td>array</td><td>The application's roles, each granting a set of permissions (see below).</td></tr></tbody></table>

**`permissions[]` item**

<table data-full-width="true"><thead><tr><th width="230">Field</th><th width="140">Type</th><th>Description</th></tr></thead><tbody><tr><td><code>permission_mnemonic</code></td><td>string (required)</td><td>Unique permission key within the application.</td></tr><tr><td><code>permission_description</code></td><td>string</td><td>Human-readable description.</td></tr><tr><td><code>active</code></td><td>boolean (default true)</td><td>Whether the permission is active.</td></tr></tbody></table>

**`roles[]` item**

<table data-full-width="true"><thead><tr><th width="230">Field</th><th width="140">Type</th><th>Description</th></tr></thead><tbody><tr><td><code>role_mnemonic</code></td><td>string (required)</td><td>Role name; must match the Keycloak client role name.</td></tr><tr><td><code>role_description</code></td><td>string</td><td>Human-readable description.</td></tr><tr><td><code>active</code></td><td>boolean (default true)</td><td>Whether the role is active.</td></tr><tr><td><code>permissions</code></td><td>array of string</td><td>Permission mnemonics granted to this role. Each must appear in the request's <code>permissions</code> array.</td></tr></tbody></table>

#### **Behaviour**

* **Upsert by `application_mnemonic`** — first call inserts, later calls update in place. The row is flagged as self-registered so the IAM seed loader never overwrites it.
* **Permissions and roles** are upserted **scoped to this application's id**.
* **Role → permission mappings are rebuilt** to exactly match the payload (mappings dropped from the payload are removed).
* A role referencing a permission that is **not** in the request's `permissions` list is rejected with **`400 Bad Request`**.

#### **Response**

```json
{
  "id": 5,
  "application_mnemonic": "nsr-staff-portal",
  "created": true,
  "permissions_count": 72,
  "roles_count": 11
}
```

<table data-full-width="true"><thead><tr><th width="230">Field</th><th width="140">Type</th><th>Description</th></tr></thead><tbody><tr><td><code>id</code></td><td>integer</td><td>The application's id in IAM.</td></tr><tr><td><code>application_mnemonic</code></td><td>string</td><td>Echo of the registered mnemonic.</td></tr><tr><td><code>created</code></td><td>boolean</td><td><code>true</code> if newly created, <code>false</code> if an existing row was updated.</td></tr><tr><td><code>permissions_count</code></td><td>integer</td><td>Permissions in the payload.</td></tr><tr><td><code>roles_count</code></td><td>integer</td><td>Roles in the payload.</td></tr></tbody></table>

#### **Example request**

```json
{
  "application_mnemonic": "nsr-staff-portal",
  "application_url": "https://nsr.trial.openg2p.org",
  "application_description": "National Social Registry",
  "icon_base64": "PHN2ZyB3aWR0aD0i...",
  "width": 80,
  "order": 1,
  "active": true,
  "permissions": [
    { "permission_mnemonic": "intakeSubmission:edit", "permission_description": "Edit intake submissions" },
    { "permission_mnemonic": "intakeSubmission:view", "permission_description": "View intake submissions" }
  ],
  "roles": [
    {
      "role_mnemonic": "Intake Officer",
      "role_description": "Handles initial data entry",
      "permissions": ["intakeSubmission:edit", "intakeSubmission:view"]
    }
  ]
}
```

***

## **3. How an application registers (install-time)**

Registration is driven by the application's own deployment so the correct URL is known at the application's install time. For OpenG2P registries this is a **post-install / post-upgrade Helm hook Job** in the registry chart that:

1. Waits for the IAM Staff API to be reachable.
2. Obtains an access token (client-credentials using the application's own per-release Keycloak client + secret).
3. Builds the payload — its own `application_mnemonic` (= `<release>-staff-portal`) and `application_url` (its Staff Portal UI host) merged with its packaged roles/permissions catalog.
4. POSTs to `/user-access/staff_portal_applications`, retrying while the Keycloak client / IAM finish coming up.

Because the call is an idempotent upsert, the hook runs safely on **every** install and upgrade.

***

## **4. CORS — manual step**

If the application's web UI makes cross-origin browser calls into the IAM Staff API, the browser will block them unless the application's **origin** is in IAM's CORS allow-list.

That list (`IAM_STAFF_CORS_ALLOW_ORIGINS`) is read **once at IAM startup**, so an application installed later is not covered automatically. When installing such an application:

1. Add its **origin** (scheme + host only, e.g. `https://nsr.trial.openg2p.org`) to `IAM_STAFF_CORS_ALLOW_ORIGINS` on the IAM chart.
2. `helm upgrade` IAM and roll the `iam-staff-portal-api` pods.

> Notes
>
> * `*` cannot be used — IAM uses auth cookies (credentialed requests), and browsers forbid `Access-Control-Allow-Origin: *` with credentials. List origins explicitly.
> * If the application does **not** make browser calls into the IAM Staff API (only links out, or talks to IAM server-to-server), no CORS change is needed.

***

## **5. Uninstall / cleanup**

`helm uninstall` of an application does **not** touch IAM, so its registered rows (tile + roles + permissions) remain. A stale tile is inert for users who no longer hold its client roles (it renders disabled), but the rows persist.

Clean teardown is handled by the application's uninstall tooling, which removes that application's rows from the IAM database — keyed strictly by its `application_mnemonic`, so other applications and the built-in singletons (Keycloak / MinIO / Superset) are untouched. (For OpenG2P registries, this is built into the registry `uninstall-registry.sh` script.)

***

## **6. Multiple instances of the same product**

Two registries of the same product in one environment register independently:

<table data-full-width="true"><thead><tr><th width="240">Instance</th><th width="240">application_mnemonic</th><th>application_url</th></tr></thead><tbody><tr><td>National Social Registry</td><td><code>nsr-staff-portal</code></td><td><code>https://nsr.&#x3C;ns>.openg2p.org</code></td></tr><tr><td>Farmer Registry</td><td><code>fr-staff-portal</code></td><td><code>https://fr.&#x3C;ns>.openg2p.org</code></td></tr></tbody></table>

Each pushes its own (identical) roles/permissions catalog under its own mnemonic, so they appear as separate tiles with independently resolved access.

***
