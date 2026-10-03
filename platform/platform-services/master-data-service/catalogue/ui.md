---
description: >-
  The Master Data admin UI for MDS as Catalogue: Reference Data lists and their
  versions, drafts, approvals and diffs; Geo Locations with change events,
  boundaries and the crosswalk; Releases; and Recent Changes
---

# Admin UI

The catalogue is managed from the existing **Master Data admin UI**
(`master-data-ui`). It is extended, not replaced. The side menu has four pages:

| Page | What it is for |
|---|---|
| **Geo Locations** | The geography: its versions, hierarchy, units, change events, boundaries and crosswalk |
| **Reference Data** | The code lists, and for each list its versions, values, attribute schema and history |
| **Releases** | Catalogue releases: named sets of pinned list and geography versions |
| **Recent Changes** | The catalogue change feed across lists, geography and releases |

Wherever the UI shows who did something (created, submitted, decided, published,
recorded), it shows the person's **display name**, and falls back to the user id
when no name is recorded (system actors such as the country-pack loader, or rows
older than the names). See
[Change control and approvals](change-control.md#permission-maker-checker-within-mds).

## Reference Data

### The list of lists

The Reference Data page lists every code list, with a search box and, for users
with `referenceData:create`, a button to add a list. Each row shows:

| Column | Shows |
|---|---|
| Code | The list's label (in the user's language when there is one) and its code |
| Owner | The owner department (`owner_org`) |
| Published version | The **published version in effect** (for example `v3`), or *Not published* |
| Draft / pending | A **Draft** or **Submitted** badge with the open draft's number, and **Changes pending** when a published version has a **future effective date** (it is published but not yet in effect) |
| Hierarchical | Whether values may have parents |
| Actions | **Edit** (list details); **Delete** only for a list that was **never published** |

A new list is created with its first draft (version 1) and opens on that draft:
add values, then submit it for approval. A published list cannot be deleted; its
values are retired in a new version instead.

### A list's page

Clicking a list opens its page. The header shows the code, owner, hierarchy flag,
description and labels per language, and an **Edit list details** button (code,
label, labels per language, description, owner, hierarchy flag). Description and
owner apply at once; the other details are saved into the list's draft.

Below the header is the **version bar**:

* a **version selector**: *Latest* (the version in effect), the open draft, and
  every other version, each with its status; a published version that is not yet in
  effect shows its date;
* a **badge** for the version on screen (**Draft**, **Submitted**, **Published**,
  **Rejected**, **Discarded**), an **In effect** badge for the version in effect,
  its effective date, and who created, submitted, published or rejected it and
  when, with the change note and decision note;
* the **lifecycle buttons** the user may use (see
  [Drafts and approval](#drafts-and-approval)).

The page has five tabs:

| Tab | Shows |
|---|---|
| **Values** | The values of the selected version, with a search box and an *Include retired* switch (on by default when viewing the draft). Hierarchical lists are browsed level by level. Retired values are shown struck through |
| **Attribute schema** | The list's attribute schema as JSON, with a summary of its fields (name, type, required, list reference) |
| **Version history** | Every version with its status, effective date, who made it (created, submitted) and who decided it, and the notes; *View* opens a version |
| **Compare versions** | The diff between two versions (by default a version against its base): changes to the list itself (code, labels, schema) and values **added**, **changed** (before and after), **retired** and **reactivated** |
| **Activity** | The change feed for this list |

### Editing the draft

Editing is possible **only on the open draft, while its status is `DRAFT`**, and
only for a user with `referenceData:edit`. Any other version is read-only, with a
hint to switch to the draft (or to open one). On the draft:

* **Add** and **Edit** open the value form: code, label, labels per language,
  parent (for hierarchical lists), sort order and attributes. Changing a value's
  code keeps the same value (a recode).
* Attributes are shown as fields generated from the list's attribute schema: a
  property with `x-list-ref` is a dropdown of the referenced list's values in its
  **published version in effect** (a referenced list's draft is never offered,
  because the API accepts only published values); enums are selects, numbers,
  booleans and text are inputs. A list without a schema takes attributes as free
  JSON.
* Values are never deleted: **Retire** retires a value in the draft (a value added
  in the same draft is removed instead), optionally with its child values;
  **Reactivate** brings a retired value back.
* The **Attribute schema** tab becomes editable: a JSON editor that checks the
  schema as you type (valid JSON, an object schema, known property types, required
  names, and that every `x-list-ref` names an existing list), with *Insert
  example*, *Reset* and *Remove schema*. *Save schema to draft* saves it into the
  draft.

### Drafts and approval

The version bar offers, depending on the state and the user's permissions:

| Button | When |
|---|---|
| **Open draft** | No open draft, and the user has the edit permission. Asks for a change note and an optional effective date |
| **Rework as new draft** | A rejected version is on screen and there is no open draft: opens a draft that copies its content |
| **View draft** | There is an open draft and another version is on screen |
| **Draft details**, **Submit for approval** | The draft is `DRAFT` and the user has the edit permission. Submit asks for the change note and an optional effective date |
| **Approve and publish**, **Reject** | `permission` mode only, the draft is `SUBMITTED`, and the user has the publish permission and **did not create, last edit or submit** it. Approval can override the effective date; rejection needs a note |
| **Discard draft** | The user has the edit permission and the draft is `DRAFT`, or `SUBMITTED` in `permission` mode. The draft is kept as **Discarded** and its number is not reused |

When a draft is submitted, the version bar says what happens next:

* in **`permission` mode**, that it is waiting for a user with the publish
  permission, or, to its maker, that another person must approve or reject it;
* in **`awe` mode**, that approval runs in the Approval Workflow Engine, with the
  **AWE request reference** (`approval_ref`). There are no approve or reject
  buttons; the page shows the result once AWE has decided.

There is no separate approvals queue: a user with the publish permission finds
submitted drafts by their **Submitted** badge on the Reference Data page (and the
geography's on Geo Locations), or in Recent Changes.

## Geo Locations

The geography is one dataset with one version bar, the same as a list's: version
selector, badge, the country, owner and unit count of the version on screen, and
the same lifecycle buttons (with `geo:edit` and `geo:publish`). Editing is
possible only on the open draft while it is `DRAFT`. The page has these tabs:

| Tab | Shows |
|---|---|
| **Hierarchy** | The tree of units level by level, with an *Include retired* switch. On the draft: **Manage levels** (add, edit, remove levels), add, edit and retire units; otherwise **View levels** |
| **Units** | A flat, searchable table of units: filter by level and parent P-code, search by code or name, include retired. Shows each unit's level, parent, status and validity dates. On the draft: edit, **Retire** and **Reactivate** |
| **Change events** | The change events of the version on screen, or of all versions, filterable by P-code, with type, from and to units, effective date, note, who recorded it and when, and an **Auto** badge for events MDS generated. On the draft: a form to **record a change event** (type, from units, to units, effective date, note, with the rule for each type) and to remove a recorded event |
| **Boundaries** | Shown only when the boundary store is configured (`boundary_store_enabled`). For each level, the boundary object key of the version on screen (marked when it is shared, unchanged, from an earlier version) and a **Download** link. On the draft: **Upload GeoJSON** per level |
| **Crosswalk** | A lookup: a unit code, a published from-version and a to-version (latest, the draft, or a published version); shows the successor (or predecessor) units, units without one, and the change events followed |
| **Version history** | Every geography version, as for a list, with its unit count |
| **Activity** | The change feed for the geography |

Unit changes left without a recorded event are not blocked: the Change events tab
says that MDS adds automatic events for them on submit, and once submitted they
appear with the **Auto** badge. The UI does not preview them before submit.

A boundary upload must be a GeoJSON `FeatureCollection`; the UI checks that the file
is JSON and a FeatureCollection, and the API matches features to units (by
`properties.pcode`). The UI does not preview the shapes. A boundary of a published
version cannot be replaced.

## Releases

The Releases page lists catalogue releases (code, title, status, number of lists,
geography version, and when and by whom it was published). A user with
`referenceData:edit` can **create a release** (code, title, note) and **set its
members**: a published version of each chosen list (with *Pin all versions in
effect* as a shortcut) and optionally a published geography version.

**Publish** is shown to a user with `referenceData:publish` who is **neither the
release's creator nor whoever last set its members**; to such a maker the page
says that another person must publish it. A draft release can be deleted (with
`referenceData:delete`); a published release shows its members and cannot be
changed.

## Recent Changes

The Recent Changes page shows the catalogue change feed, newest first: when, the
event, the subject (list, geography or release, and which), the version, who did it
and the details. It can be filtered by subject type and by text (event, subject or
user name or id), and is paged. Each list's and the geography's **Activity** tab
shows the same feed for that subject.

## Permissions in the UI

Buttons appear only for users who hold the matching permission
(`referenceData:*`, `geo:*`); see
[Change control and approvals](change-control.md#permissions). The API enforces the
same rules, including maker ≠ checker, so a hidden button is a convenience, not the
control.
