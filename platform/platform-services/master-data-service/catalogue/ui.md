---
description: >-
  The Master Data admin UI for MDS as Catalogue: a catalogue overview home page;
  Datasets with their versions, entries, schema, drafts, approvals, diffs and
  history; Geography with data, lineage (change events and crosswalk) and
  history; Releases; and Activity
---

# Admin UI

The catalogue is managed from the existing **Master Data admin UI**
(`master-data-ui`). It is extended, not replaced. The UI uses common
data-catalogue terms (W3C DCAT, SKOS): the whole service is the **Catalogue**,
each code list is a **dataset**, a dataset's values are its **entries**, and a
dataset's domain is its **theme**. The API keeps its own names (`get_lists`,
`list_code`, `owner_org`, `domain`, ...); the table below maps them.

| In the UI | In the API |
|---|---|
| Catalogue | MDS as Catalogue (`/catalogue/*`) |
| Dataset | A list (code list): `list_id`, `list_code` |
| Entry, with its **Code** and **Label** | A list value: `value_code`, `display` |
| Labels by language | `display_i18n` |
| Parent entry | `parent_code` |
| Schema, and an entry's **Fields** | `attribute_schema`, a value's `attributes` |
| Dataset reference | `x-list-ref` |
| Publisher | `owner_org` |
| Theme (Core, Agriculture, ..., Other) | `domain` (`core`, `agriculture`, ..., `null`) |
| Visibility: Public / Private | `visibility` (`public`, `private`) |
| Licence, Licence URL | `licence_label`, `licence_uri` |
| Version, Effective from | `version_no`, `effective_from` |
| Release | A catalogue release |
| Geography: Levels, Administrative units, Boundaries, Change events, Crosswalk | Geography versions, levels, units, boundaries, change events, crosswalk |
| Activity | The change feed (`get_changes`) |

The side menu has five pages, shown to every signed-in user (every read in the
catalogue API needs only a signed-in user; buttons that change something need a
permission, see [Permissions in the UI](#permissions-in-the-ui)). The logo and
product name at the top of the menu also lead to the home page.

| Page | What it is for |
|---|---|
| **Home** | The catalogue overview: datasets by theme, the geography in effect, pending work and recent activity |
| **Datasets** | Every dataset, and for each dataset its versions, entries, schema and history |
| **Geography** | The geography: its versions, hierarchy, administrative units, change events, boundaries and crosswalk |
| **Releases** | Catalogue releases: named sets of pinned dataset and geography versions |
| **Activity** | The catalogue change feed across datasets, geography and releases |

The Datasets page was at `/reference-data`; that address now redirects to
`/datasets` (and `/reference-data/<id>` to `/datasets/<id>`).

Wherever the UI shows who did something (created, submitted, decided, published,
recorded), it shows the person's **display name**, and falls back to the user id
when no name is recorded (system actors such as the country-pack loader, or rows
older than the names). See
[Change control and approvals](change-control.md#permission-maker-checker-within-mds).

## Home

The home page, **Catalogue overview**, has:

* a **search box**: searching opens the Datasets page filtered by that text;
* four tiles: **Datasets** (how many, in how many themes), **Geography** (the
  version in effect and its number of administrative units), **Pending work**
  (how many versions await approval and how many drafts are open) and
  **Releases** (how many, and the latest published one). Each tile opens its page;
* **Datasets by theme**: one group per theme (*Core* first, *Other* last for
  datasets without a theme), with the number of datasets and every dataset's
  label as a link to its page; a dot marks a dataset with an open draft. A theme's
  name opens the Datasets page filtered by that theme;
* **Geography**: the country, the version in effect, its effective date, and each
  level with its number of active administrative units;
* **Pending work**: **Awaiting approval** lists every submitted version (datasets
  and the geography), and **Drafts in progress** every open draft and draft
  release, each with its status and a link. For a user who may act on an item
  (the publish permission for a submitted version, the edit permission for a
  draft) it says *Review* or *Continue*; other users see the same list for
  information;
* **Recent activity**: the ten newest events of the change feed, as readable
  summaries, each subject linking to its page, and a link to the Activity page.

The page loads with a few requests in parallel (the datasets, geography
versions, releases, the newest activity, and one unit count per geography level),
not one request per dataset.

## Datasets

### The list of datasets

The Datasets page lists every dataset, with:

* a **Theme** filter: *All themes*, or one of the themes the datasets have
  (*Core*, *Agriculture*, ..., and *Other* for datasets without a theme);
* a search box (label, code, publisher, theme or id);
* **Rows per page**: 10, 25 (default), 50 or 100;
* for users with `referenceData:create`, a **New dataset** button.

The page also takes `?q=<text>` and `?theme=<theme>` (`theme=other` for datasets
without a theme), which is how the home page links to it. Each row shows:

| Column | Shows |
|---|---|
| Dataset | The dataset's label (in the user's language when there is one) and its code |
| Theme | Core, Agriculture, ... or Other |
| Publisher | The publishing department (`owner_org`) |
| Published version | The **published version in effect** (for example `v3`), or *Not published* |
| Draft / pending | A **Draft** or **Submitted** badge with the open draft's number, **Changes pending** when a published version has a **future effective date** (it is published but not yet in effect), and a **Public** badge for a dataset in the public catalogue |
| Hierarchical | Whether entries may have parent entries |
| Actions | **Edit** (dataset details); **Delete** only for a dataset that was **never published** |

A new dataset is created with its first draft (version 1) and opens on that
draft: add entries, then submit it for approval. A published dataset cannot be
deleted; its entries are retired in a new version instead.

A dataset's theme comes from the country pack (`core` for the pack's core lists,
the domain name such as `agriculture` for a domain's lists; see
[Country packs](country-packs-and-migration.md)). A maker can set or change it in
the dataset's details; it applies at once and is not versioned.

### A dataset's page

Clicking a dataset opens its page. The header shows the code, publisher, theme,
hierarchy flag, description and labels by language, a **Public** or **Private**
badge with the licence, and an **Edit dataset details** button (code, label,
labels by language, description, publisher, theme, visibility, licence, hierarchy
flag). Description, publisher, theme, visibility and licence apply at once; the
other details are saved into the dataset's draft.

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

The page has four tabs:

| Tab | Shows |
|---|---|
| **Entries** | The entries of the selected version, with a search box and an *Include retired* switch (on by default when viewing the draft). Hierarchical datasets are browsed level by level. Retired entries are shown struck through |
| **Schema** | The dataset's schema as JSON, with a summary of its fields (name, type, required, dataset reference) |
| **History** | Version history and activity together, as two sub-tabs. **Versions**: every version with its status, effective date, who made it (created, submitted) and who decided it, and the notes; *View* opens a version, and each row **expands** to that version's activity timeline. **All activity**: the full change feed for this dataset |
| **Compare versions** | The diff between two versions (by default a version against its base): changes to the dataset itself (code, labels, schema) and entries **added**, **changed** (before and after), **retired** and **reactivated** |

### Editing the draft

Editing is possible **only on the open draft, while its status is `DRAFT`**, and
only for a user with `referenceData:edit`. Any other version is read-only, with a
hint to switch to the draft (or to open one). On the draft:

* **Add entry** and **Edit** open the entry form: code, label, labels by
  language, parent entry (for hierarchical datasets), sort order and fields.
  Changing an entry's code keeps the same entry (a recode).
* Fields are generated from the dataset's schema: a field with `x-list-ref` is a
  dropdown of the referenced dataset's entries in its **published version in
  effect** (a referenced dataset's draft is never offered, because the API accepts
  only published entries); enums are selects, numbers, booleans and text are
  inputs. A dataset without a schema takes its fields as free JSON.
* Entries are never deleted: **Retire** retires an entry in the draft (an entry
  added in the same draft is removed instead), optionally with its child entries;
  **Reactivate** brings a retired entry back.
* The **Schema** tab becomes editable: a JSON editor that checks the schema as you
  type (valid JSON, an object schema, known field types, required names, and that
  every `x-list-ref` names an existing dataset), with *Insert example*, *Reset* and
  *Remove schema*. *Save schema to draft* saves it into the draft.

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

A user with the publish permission finds submitted versions under **Pending work
→ Awaiting approval** on the home page, by their **Submitted** badge on the
Datasets page (and the geography's on Geography), or in Activity.

## Geography

The geography is one dataset with one version bar, the same as other datasets':
version selector, badge, the country, publisher and administrative-unit count of
the version on screen, and the same lifecycle buttons (with `geo:edit` and
`geo:publish`). Editing is possible only on the open draft while it is `DRAFT`.
The page has three groups of tabs: **Data**, **Lineage** and **History**.

Under the title, a **Public** or **Private** badge and the licence show the
geography's publication settings; users with `geo:edit` change them with
**Publication settings** (see [Visibility and licence](#visibility-and-licence)).

**Data** has three sub-tabs:

| Sub-tab | Shows |
|---|---|
| **Hierarchy** | The tree of administrative units level by level, with an *Include retired* switch. On the draft: **Manage levels** (add, edit, remove levels), add, edit and retire units; otherwise **View levels** |
| **Administrative units** | A flat, searchable table of units: filter by level and parent P-code, search by code or name, include retired. Shows each unit's level, parent, status and validity dates. On the draft: edit, **Retire** and **Reactivate** |
| **Boundaries** | Shown only when the boundary store is configured (`boundary_store_enabled`). For each level, the boundary object key of the version on screen (marked when it is shared, unchanged, from an earlier version) and a **Download** link. On the draft: **Upload GeoJSON** per level |

**Lineage** shows two panels side by side (one above the other on a narrow
screen):

| Panel | Shows |
|---|---|
| **Change events** | The change events of the version on screen, or of all versions, filterable by P-code, with type, from and to units, effective date, note, who recorded it and when, and an **Auto** badge for events MDS generated. On the draft: a form to **record a change event** (type, from units, to units, effective date, note, with the rule for each type) and to remove a recorded event |
| **Crosswalk** | A lookup: a unit code, a published from-version and a to-version (latest, the draft, or a published version); shows the successor (or predecessor) units, units without one, and the change events followed |

**History** works as for a dataset: **Versions** lists every geography version,
with its unit count, and each row expands to that version's activity timeline;
**All activity** is the full change feed for the geography. Recording or removing
a change event appears there too, for example *SPLIT recorded: ET040611 →
ET040612, ET040613*.

Unit changes left without a recorded event are not blocked: the Change events panel
says that MDS adds automatic events for them on submit, and once submitted they
appear with the **Auto** badge. The UI does not preview them before submit.

A boundary upload must be a GeoJSON `FeatureCollection`; the UI checks that the file
is JSON and a FeatureCollection, and the API matches features to units (by
`properties.pcode`). The UI does not preview the shapes. A boundary of a published
version cannot be replaced.

## Visibility and licence

The dataset dialog (**Edit dataset details**, and **Add** for a new dataset) and the
geography's **Publication settings** have the same two controls:

* **Visibility**: *Private* (the default) or *Public*. Public datasets and a public
  geography are shown, at their **published** versions only, by the opt-in
  [public catalogue](public-catalogue.md) for other websites and open-data
  portals. When the public catalogue is switched off in the deployment, choosing
  *Public* shows a note that nothing is published until an administrator enables
  it.
* **Licence** and **Licence URL**: free text, with suggestions (CC BY 4.0, CC BY-SA
  4.0, CC0 1.0, CC BY-IGO, ODbL 1.0); picking a suggestion fills the URL when it is
  empty.

Both apply at once and are not versioned; a change appears in the activity feed
(`list.updated`, `geo.settings.updated`). There is no public MDS website: the
public catalogue is an API that other sites read.

## Releases

The Releases page lists catalogue releases (code, title, status, number of
datasets, geography version, and when and by whom it was published). A user with
`referenceData:edit` can **create a release** (code, title, note) and **set its
members**: a published version of each chosen dataset (with *Pin all versions in
effect* as a shortcut) and optionally a published geography version.

**Publish** is shown to a user with `referenceData:publish` who is **neither the
release's creator nor whoever last set its members**; to such a maker the page
says that another person must publish it. A draft release can be deleted (with
`referenceData:delete`); a published release shows its members and cannot be
changed.

## Activity

The Activity page shows the catalogue change feed, newest first: when, the
event, the subject (dataset, geography or release, and which), the version, who
did it and the details, as a readable summary (for example *SPLIT recorded: D1 →
D1A, D1B* for a recorded change event; otherwise the detail fields as
`name: value`, with the raw JSON on hover). It can be filtered by subject type and
by text (event, subject or user name or id), and is paged. The **History** tab of
each dataset and of the geography shows the same feed for that subject, in full
and per version, and the home page shows its ten newest events.

## Permissions in the UI

Every page is in the menu for every signed-in user. Buttons that change something
appear only for users who hold the matching permission (`referenceData:*`,
`geo:*`); see [Change control and approvals](change-control.md#permissions). The
API enforces the same rules, including maker ≠ checker, so a hidden button is a
convenience, not the control.
