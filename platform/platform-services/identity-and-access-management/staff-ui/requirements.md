---
description: Design & Requirements
---

# Requirements

## Identity & Access Management — iam-staff-ui UI Requirements

**iam-staff-ui** is the internal admin console operations staff use to manage every application registered in the IAM platform, and the login providers that authenticate their users. It consumes REST APIs exposed by **iam-staff-portal-api**; there is no direct database access from the UI.

### 1. Global Shell

* Application title bar always displays: **"Identity & Access Management"**.
* Left-hand navigation menu has exactly two items, always visible, indicating the active section:
  * Applications
  * Login Providers

### 2. Applications — List View

* Reachable from the "Applications" left-nav item.
* Backed by model: `StaffPortalApplication`.
* Displays a paginated table of applications. Pagination controls are anchored to the bottom of the page.
* Top-right of the list has an **"Add new Application"** button.
  * Clicking it opens a popup to create a new application.
  * On **Save**, the popup closes, the user is returned to the Applications list, and the newly created application appears at the top of the list.
* Clicking a row opens the **Application Detail View** for that application.

#### Add New Application — popup fields (`StaffPortalApplication`)

| Field                     | Notes                                                                                                |
| ------------------------- | ---------------------------------------------------------------------------------------------------- |
| `application_mnemonic`    | String, unique, required — stable key identifying the application                                    |
| `application_description` | Free-text description                                                                                |
| `application_url`         | Base URL the staff portal links to / launches                                                        |
| `icon_base64`             | Base64-encoded icon                                                                                  |
| `order`                   | Optional integer, display order in lists                                                             |
| `width`                   | Optional integer, layout hint                                                                        |
| `is_self_registered`      | Boolean, system-managed — **not editable** from this form; set by the API when an app self-registers |

### 3. Application Detail View

Opened by clicking a row in the Applications list. Contains 5 tabs:

1. Application
2. Roles
3. Permissions
4. Roles to Permissions
5. Data Policies

#### 3.1 Tab — Application

Shows all attributes of the selected application (model: `StaffPortalApplication`). Same field set as listed above in section 2, rendered as a read/edit attribute view (no popup).

#### 3.2 Tab — Roles

* List view of all roles defined for this application. Backed by model: `StaffRole` (`role_mnemonic`, `role_description`, `application_id` — implicit, scoped to the current application).
* Supports pagination.
* **Add** button opens a popup to create a new role scoped to this application.
* Each row has a **Delete** action to remove that role.

#### 3.3 Tab — Permissions

* List view of all permissions defined for this application. Backed by model: `StaffApplicationPermission` (`permission_mnemonic`, `permission_description`, `application_id` — implicit, scoped to the current application).
* Supports pagination.
* **Add** button opens a popup to create a new permission scoped to this application.
* Each row has a **Delete** action to remove that permission.

#### 3.4 Tab — Roles to Permissions

* List view of all role↔permission mappings for this application. Backed by model: `StaffRolePermission` (`role_id`, `permission_id` — join table between `StaffRole` and `StaffApplicationPermission`).
* Supports **filtering by Role and by Permission**, so a user can find:
  * what permissions a given role has, and
  * what roles grant a given permission.
* Supports pagination.
* User can **add** a new mapping (Role → Permission) and **remove** an existing mapping.

#### 3.5 Tab — Data Policies

* List view of all data policies for this application.
* Supports pagination.
* **Add** button opens a popup to create a new data policy for the application.
* User can **remove** an existing data policy.

> **Implementation note:** Data policies are not a separate table today. They are `StaffRole` rows whose `role_mnemonic` is prefixed `"DP_"` (see `DataPolicyMiddleware` / `DP_ROLE_PREFIX` in `iam-core`). The UI should present these as a distinct tab, stripping the `DP_` prefix for display and re-applying it on create. If a dedicated data-policy model is introduced later, this tab's data source should be swappable without changing its UX.

### 4. Login Providers

* Reachable from the "Login Providers" left-nav item.
* Backed by model: `LoginProvider` (one row per OIDC/OAuth identity provider staff can authenticate against).
* Displays a paginated list of login providers.
* **Add** button opens a popup to create a new login provider.
* Clicking a row opens the provider for view/edit, using the same field set as the create popup.

#### Add New Login Provider — popup field groups (`LoginProvider`)

**Identity**

* `provider_name`
* `description`
* `icon_base64`

**OAuth Client**

* `client_id`
* `client_secret` _(sensitive — mask/never redisplay after save)_
* `client_private_key` _(sensitive — mask/never redisplay after save)_
* `token_endpoint_auth_method`

**OIDC Endpoints**

* `issuer`
* `authorization_endpoint`
* `token_endpoint`
* `userinfo_endpoint`
* `server_metadata_url`
* `jwks_uri`

**Behavior & Routing**

* `adapter_name`
* `scope`
* `enable_pkce`
* `extra_authorize_params`
* `jwt_assertion_aud`
* `audiences`
* `oauth_callback_url`
* `default_redirect_uri`

**System-managed (read-only in UI)**

* `keymanager_app_id`
* `keymanager_ref_id`

### 5. Screen → Backend Model Reference

| Screen                              | Backend model                                  | Source                                 |
| ----------------------------------- | ---------------------------------------------- | -------------------------------------- |
| Applications list & Application tab | `StaffPortalApplication`                       | `iam_staff_portal_api/models`          |
| Roles tab                           | `StaffRole`                                    | `iam_staff_portal_api/models`          |
| Permissions tab                     | `StaffApplicationPermission`                   | `iam_staff_portal_api/models`          |
| Roles ↔ Permissions tab             | `StaffRolePermission`                          | `iam_staff_portal_api/models`          |
| Data Policies tab                   | `StaffRole` (`role_mnemonic` prefixed `"DP_"`) | `iam_core` / `data_policy_role_helper` |
| Login Providers list & popup        | `LoginProvider`                                | `iam_core/models`                      |

All models extend `BaseORMModelWithTimes`, so every record also carries platform-standard system fields (e.g. `id`, created/updated timestamps). These are not shown as editable UI fields except where noted.

### 6. Assumptions

* New Application is inserted at the top of the list — assumes the API returns/allows client-side sort by most-recently-created, or the UI re-fetches sorted by `created_at desc`.
* Delete/remove actions on Roles, Permissions, mappings, and Data Policies are irreversible from the UI and should carry a confirmation step.
* Data Policies are modeled as `DP_`-prefixed `StaffRole` rows today; if a dedicated model is introduced later, this tab's data source should be swapped without changing its UX.

### 7. Open Questions

* `iam-staff-portal-api` currently exposes auth-only endpoints (auth, identity provider, OAuth callback, user access). CRUD endpoints for Applications, Roles, Permissions, and mappings will need to be added to support this UI.
* `client_secret` and `client_private_key` on Login Providers are sensitive — confirm the UI should mask/never redisplay secrets after save.
* Pagination page size and default sort order to be confirmed with the backend team, per list.

{% file src="../../../../.gitbook/assets/iam-staff-ui-requirements.pdf" %}
