---
description: >-
  For catalogue administrators: the Master Data admin UI, who can do what, and
  the common tasks: change, retire and recode entries, add a dataset, schedule
  and approve changes, change geography, load a newer country pack, make a
  dataset public
---

# Admin Guide

This page is for the people who manage reference data in the Master Data admin
UI. Every change follows the same flow: **open a draft → edit → submit → another
person approves**. The ideas behind it are in [Concepts](concepts.md) and
[Change Control and Approvals](change-control.md). The UI says "dataset" and
"entry"; for the names the API uses, see
[Names in the API](api-reference.md#names-in-the-api).

## The pages

| Page | What it is for |
|---|---|
| **Home** | Overview: datasets by theme, the geography in effect, pending work and recent activity |
| **Datasets** | Every dataset, with its versions, entries, schema and history |
| **Geography** | Administrative units, boundaries, change events and the crosswalk |
| **Releases** | Named sets of pinned dataset and geography versions |
| **Activity** | The change feed for the whole catalogue |

## Who can do what

Every signed-in user sees every page and can read everything. A button that
changes something appears only for a user with the matching permission.

| To | You need |
|---|---|
| Create a dataset | `referenceData:create` |
| Open, edit, submit or discard a dataset draft; change dataset details (theme, visibility, licence); create a release and set its members | `referenceData:edit` |
| Retire entries; delete a never-published dataset or a draft release | `referenceData:delete` |
| Approve or reject a dataset draft; publish a release | `referenceData:publish` |
| Open, edit, submit or discard the geography draft; set its visibility and licence | `geo:edit` |
| Retire administrative units | `geo:delete` |
| Approve or reject a geography draft | `geo:publish` |

The role `MASTER_DATA_ADMIN` has all of these. `MASTER_DATA_APPROVER` has only
the two publish permissions: it approves but cannot edit. Full details are in
[Permissions](change-control.md#permissions).

* **Maker ≠ checker.** You cannot approve or reject a draft you created, last
  edited or submitted. You cannot publish a release you created or whose members
  you last set. Ask someone else.
* The API enforces the same rules. A hidden button is a convenience, not the
  control.

## Add or change an entry

1. Open the dataset. Click **Open draft** and give a change note, or **View
   draft** if one is open.
2. On **Entries**, click **Add entry**, or **Edit** on an entry. Save.
3. Click **Submit for approval**, check the change note, and submit.
4. Ask an approver to approve it (see [Approve or reject](#approve-or-reject)).

Good to know:

* You can edit only the open draft, and only while it is in `DRAFT`. Other
  versions are read-only.
* A dataset has at most one open draft. If someone else has one open, work in it
  or wait.
* The code of a published entry is read-only (see
  [Recode an entry](#recode-an-entry)). The code of an entry added in this draft
  can still change.
* A field that refers to another dataset offers only that dataset's **published
  version in effect**, never its draft. See
  [Load a newer country pack version](#load-a-newer-country-pack-version) for the
  order this implies.
* Use **Compare versions** to review the draft against its base before you
  submit.

## Retire an entry

1. Open the dataset's draft.
2. On **Entries**, click **Retire** on the entry. Choose whether to retire its
   child entries too.
3. Submit for approval.

Entries are never deleted. A retired entry is not offered for new records, but
records that hold it still show it. Retired entries are shown struck through,
with **Include retired**. **Reactivate** in a draft brings one back. Retiring an
entry that was added in the same draft removes it instead. See
[Retired entries](concepts.md#retired-entries).

## Recode an entry

A published code never changes. To replace it:

1. Open the dataset's draft.
2. **Retire** the old entry.
3. **Add entry** with the new code (and the same label, if unchanged).
4. In the change note, say it is a recode, from which code to which.
5. Submit for approval.

Records that hold the old code keep it; map them if needed. See
[Codes are fixed once published](concepts.md#codes-are-fixed-once-published).

## Add a dataset

1. On **Datasets**, click **New dataset**. Fill in its details and save. It opens
   on its first draft (version 1).
2. Optionally, on **Schema**, define the fields each entry carries and click
   **Save schema to draft**. See [Typed attributes](concepts.md#typed-attributes).
3. Add its entries on **Entries**.
4. Submit for approval.

Good to know:

* In **Edit dataset details**, description, publisher, theme, visibility and
  licence apply **at once** and are not versioned. Code, label, labels by
  language and the hierarchy flag go into the draft.
* A dataset without a schema takes its fields as free JSON.
* A dataset that was never published can be deleted. A published one cannot;
  retire its entries instead.

## Schedule a change for a future date

1. Make the change in a draft.
2. Set **Effective from** when you open the draft or submit it. An approver can
   still change the date when approving.
3. Submit.

The date can only move forward: never earlier than the latest published
version's. Once approved, the version is published but **not in effect** until
that date. The Datasets list shows **Changes pending**, and consumers keep
reading the current version until then. See
[Effective dates](concepts.md#effective-dates).

## Approve or reject

1. On **Home**, look under **Pending work → Awaiting approval**.
2. Open the version. Read the change note and check **Compare versions**.
3. Click **Approve and publish** (optionally changing the effective date), or
   **Reject** with a note.

Good to know:

* Everyone sees the pending list. It says *Review* only to users who may act.
* If the deployment uses the Approval Workflow Engine (`awe` mode), MDS has no
  approve buttons. The version shows the AWE request reference; approve in AWE,
  and MDS shows the result. See [Approval modes](change-control.md#approval-modes).
* To rework a rejected version, open it and click **Rework as new draft**.
* A discarded draft is kept as **Discarded**, and its number is not reused.

## Change geography (split, merge, rename)

1. Open **Geography**. Click **Open draft** and give a change note.
2. Under **Data**, edit the units:
   * **split**: add the new units, move the old unit's children to their new
     parents, then **Retire** the old unit;
   * **merge**: move the children to the surviving (or new) unit, then retire the
     others;
   * **rename**: **Edit** the unit's name; the code stays.
3. Under **Data → Boundaries**, click **Upload GeoJSON** for each level whose
   shapes changed.
4. Under **Lineage → Change events**, click **Record change event**: choose the
   type, the from and to units, and add a note (for example, the decision that
   made the change).
5. Set **Effective from** if the change takes effect later, and submit.

Good to know:

* **Record splits and merges yourself.** For unit changes without a recorded
  event, MDS adds automatic events on submit (marked **Auto**), but those do not
  link old units to new ones. They are not previewed before submit.
* A boundary file must be a GeoJSON `FeatureCollection`. Features are matched to
  units by `properties.pcode`. The shapes are not previewed. A published
  version's boundaries cannot be replaced.
* **Boundaries** appears only when the deployment has a boundary store.
* Use **Lineage → Crosswalk** to check how an old code maps to the new units.

See [Geography and Boundary Changes](geography.md).

## Load a newer country pack version

1. Ask the deployment administrator to set the new pack and re-run the install
   (see [Deployment](deployment.md)). The loader creates a **draft** for each
   dataset, and for the geography, that differs from the published version.
2. On **Home**, open each draft under **Pending work → Drafts in progress**.
3. Check **Compare versions**: entries added, changed and retired.
4. For the geography, record the real change events (split, merge, recode)
   unless the pack provided them.
5. Submit and approve the drafts **in order**: a dataset that others refer to
   first (for example, crops before seed varieties). A reference is checked
   against the published version, so a dataset that uses another's new entries
   can only be approved after that one.

See [Country Packs and Migration](country-packs-and-migration.md).

## Make a dataset public

1. Open the dataset and click **Edit dataset details** (for the geography:
   **Publication settings**).
2. Set **Visibility** to *Public*, and give a **Licence** and **Licence URL**.
3. Save.

This applies at once; no approval is needed. Only published versions are shown.
Nothing is served until the deployment switches the public catalogue on; the
dialog says so when it is off. There is no public MDS website: the public
catalogue is an API that other sites read. See
[Public Catalogue](public-catalogue.md).

## Good to know

* **Names, not ids.** The UI shows who did something by display name. It shows
  the user id when there is no name, for example for the country-pack loader or
  older records.
* **Activity** is the catalogue change feed. Each dataset's and the geography's
  **History** tab shows the same feed for that subject, per version. Changes that
  apply at once (theme, visibility, licence) appear there too.
* A dataset's **theme** comes from the country pack. You can change it in the
  dataset details.
