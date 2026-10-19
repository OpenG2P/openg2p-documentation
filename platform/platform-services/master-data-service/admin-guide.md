---
description: >-
  For catalogue administrators: how changes are made in the Master Data admin
  UI, who can do what, steps to recode an entry, change geography and load a
  newer country pack, and what to know when adding, retiring, scheduling,
  approving or publishing data
---

# Admin Guide

This page is for the people who manage reference data in the Master Data admin
UI. Every change follows the same flow: **open a draft → edit → submit → another
person approves**. The ideas behind it are in [Concepts](concepts.md) and
[Change Control and Approvals](change-control.md).

## Who can do what

Every signed-in user can read everything; a button that changes something
appears only for a user with the matching permission (see
[Permissions](change-control.md#permissions)). **Maker ≠ checker:** you cannot
approve or reject a draft you created, last edited or submitted, nor publish a
release you created or whose members you last set. Ask someone else.

## Add or change an entry

Good to know:

* You can edit only the open draft, and only while it is in `DRAFT`. A dataset
  has at most one open draft: if someone else has one open, work in it or wait.
* The code of a published entry is read-only (see
  [Recode an entry](#recode-an-entry)). The code of an entry added in this draft
  can still change.
* A field that refers to another dataset offers only that dataset's published
  version in effect, never its draft. Publish the referenced dataset first (see
  [Typed fields](concepts.md#typed-fields)).
* Use **Compare versions** to review the draft against its base before you
  submit.

## Retire an entry

Good to know:

* Retiring asks whether to retire the entry's child entries too.
* **Include retired** shows retired entries, struck through. **Reactivate** in a
  draft brings one back.
* Retiring an entry that was added in the same draft removes it instead.

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

Good to know:

* A new dataset opens on its first draft (version 1). Define its typed fields on
  **Schema** and click **Save schema to draft**; without a schema, fields are
  free JSON.
* In **Edit dataset details**, some details apply at once (see
  [Settings that apply at once](change-control.md#settings-that-apply-at-once));
  code, label, labels by language and the hierarchy flag go into the draft.
* A dataset that was never published can be deleted. A published one cannot;
  retire its entries instead.

## Schedule a change for a future date

Good to know:

* Set **Effective from** when you open the draft or submit it; an approver can
  still change it when approving. Until that date the Datasets list shows
  **Changes pending**, and consumers keep reading the current version.
* The date can only move forward: never earlier than the latest published
  version's. So:
  * publish a future-dated version **close to its date**, not months ahead,
    unless the dataset rarely changes;
  * make urgent corrections **before** staging a future-dated version;
  * if an urgent correction is needed while one is pending, publish it with the
    **same effective date**, so the two take effect together.

## Approve or reject

Good to know:

* Pending drafts are on **Home → Pending work → Awaiting approval**. Everyone sees
  the list; it says *Review* only to users who may act.
* A rejection needs a note.
* If the deployment uses the Approval Workflow Engine, MDS has no approve
  buttons: the version shows the AWE request reference; approve in AWE. See
  [Approval modes](change-control.md#approval-modes).
* To rework a rejected version, open it and click **Rework as new draft**.

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
   first (for example, crops before seed varieties); see
   [Typed fields](concepts.md#typed-fields).

See [Country Packs](country-packs.md).

## Make a dataset public

Good to know:

* Visibility and licence are in **Edit dataset details** (for the geography:
  **Publication settings**). They apply at once; no approval is needed.
* Nothing is served until the deployment switches the public catalogue on; the
  dialog says so when it is off. See [Public Catalogue](public-catalogue.md).

## Good to know

* **Names, not ids.** The UI shows who did something by display name. It shows
  the user id when there is no name, for example for the country-pack loader.
* **Activity** is the catalogue change feed. Each dataset's and the geography's
  **History** tab shows the same feed for that subject, per version, including
  changes that apply at once.
* A dataset's **theme** comes from the country pack. You can change it in the
  dataset details.
