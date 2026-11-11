---
description: >-
  Step-by-step tasks for catalogue administrators in the Master Data admin UI:
  set up an approver, change, recode or add a dataset, approve and publish,
  schedule a change, change geography, load a newer country pack, create a
  catalogue release, make a dataset public and follow what changed
---

# Admin Guide

This page gives the steps for each task in the Master Data admin UI. Why things
work this way is explained elsewhere: [Concepts](concepts.md) (datasets,
versions, catalogue releases) and [Change Control and Approvals](change-control.md)
(drafts, approval, permissions).

The menu has **Home**, **Datasets**, **Geography**, **Releases** and **Activity**.
Every signed-in user can see everything; a button that changes something appears
only for users with the matching [permission](change-control.md#permissions).

## Set up a second person to approve

Every change is approved by someone other than the person who made it
(**maker ≠ checker**). The install gives the role `MASTER_DATA_ADMIN` only to the
`admin` user, so before the first approval:

1. In Keycloak, realm `staff`, create a user (or pick an existing one).
2. Under **Role mapping**, assign the client role `MASTER_DATA_APPROVER` of the
   client `master-data` (approves only), or `MASTER_DATA_ADMIN` (can also edit).
3. That person signs in to the Master Data admin UI.

## Change a dataset's entries

A published version never changes, so a change is made in a new version (see
[Versions](concepts.md#versions)).

1. Open **Datasets** and the dataset.
2. Click **Start new version**. This opens a **draft**, an editable copy of the
   version in effect. If a draft is already open, click **Go to draft** and work
   in it: a dataset has one draft at a time.
3. On **Entries**, use **Add entry**, **Edit** or **Retire**. **Include retired**
   shows retired entries; **Reactivate** brings one back.
4. On **Compare versions**, check the draft against the version it started from.
5. Click **Submit for approval**, give a **Change note** and, if the change takes
   effect later, **Effective from** (see [Schedule a change](#schedule-a-change-for-a-future-date)).
   The draft is checked and can no longer be edited.
6. Another person approves it: [Approve and publish](#approve-and-publish-or-reject-a-draft).

Good to know:

* The entry code of a published entry is read-only; to change it, [recode](#recode-an-entry).
* Retiring an entry asks whether to retire its child entries too. Retiring an
  entry added in the same draft removes it instead. See
  [Retired entries](concepts.md#retired-entries).
* A field that refers to another dataset offers only that dataset's version in
  effect, never its draft: publish the referenced dataset first (see
  [Typed fields](concepts.md#typed-fields)).
* **Discard draft** drops the draft; it is kept as *Discarded* for the record.

## Recode an entry

A published entry code never changes
([why](concepts.md#entry-codes-and-p-codes-are-fixed-once-published)). To replace it:

1. Open the dataset and **Start new version** (or **Go to draft**).
2. **Retire** the old entry.
3. **Add entry** with the new entry code (and the same label, if unchanged).
4. **Submit for approval**, saying in the change note that it is a recode, from
   which entry code to which.

Records that hold the old entry code keep it; map them if needed.

## Change a dataset's details

1. Open the dataset and click **Dataset settings**.
2. Change what you need:
   * **Settings (apply at once)**: description, publisher, theme, visibility and
     licence. They apply when saved, with no approval
     ([why](change-control.md#details-that-change-without-a-new-version)).
   * **Name and structure**: dataset code, label, labels by language, hierarchy
     flag. These are part of the data: they are saved into the draft and published
     on approval.
3. Click **Save**. For **Name and structure**, then submit the draft as in
   [Change a dataset's entries](#change-a-datasets-entries).

The schema (typed fields) is changed on the dataset's **Schema** tab, in a draft:
click **Save schema to draft**.

## Add a dataset

1. Open **Datasets** and click **New dataset**.
2. Give the dataset code, label and, optionally, the settings (description,
   publisher, theme, visibility, licence) and a change note. Click **Save**. The
   dataset opens on its first draft, version 1.
3. Optionally, define typed fields on **Schema** and click **Save schema to
   draft**. Without a schema, fields are free JSON.
4. Add the entries on **Entries**.
5. **Submit for approval**; another person approves it.

A dataset that was never published can be deleted. A published one cannot: retire
its entries instead.

## Approve and publish (or reject) a draft

1. Open **Home**. Under **Pending work → Awaiting approval**, click **Review** on
   the draft. (Everyone sees the list; *Review* appears only for users who may act.)
2. Check the draft, using **Compare versions**.
3. Click **Approve and publish**. Optionally set **Effective from** (it overrides
   the draft's date; leave it empty to keep it, or to publish now). Or click
   **Reject** and give a **Decision note** (required).

The published version is fixed from then on, and consumers reading the latest
version get it from its effective date. To rework a rejected version, open it and
click **Rework as new draft**.

If the deployment approves through the Approval Workflow Engine, MDS has no
approve buttons: the version shows the AWE request reference, and the approval is
made in AWE ([Approval modes](change-control.md#approval-modes)).

## Schedule a change for a future date

1. Make the change as in [Change a dataset's entries](#change-a-datasets-entries).
2. Set **Effective from** to the date, when submitting (or in **Draft details**).
   The approver can still change it.
3. Once approved, the version is published but not yet in effect: the Datasets
   list shows **Changes pending**, and consumers keep reading the current version
   until that date ([Effective dates](concepts.md#effective-dates)).

Good to know:

* The date can only move forward, never earlier than the latest published
  version's. So publish a future-dated version **close to its date**, and make
  urgent corrections **before** staging one. If an urgent correction is needed
  while one is pending, publish it with the **same effective date**, so the two
  take effect together.

## Change geography (split, merge, rename)

1. Open **Geography**. Click **Start new version** and give a change note.
2. Under **Data → Administrative units**, edit the units:
   * **split**: add the new units, move the old unit's children to their new
     parents, then **Retire** the old unit;
   * **merge**: move the children to the surviving (or new) unit, then retire the
     others;
   * **rename**: **Edit** the unit's name; the P-code stays.
3. Under **Data → Boundaries**, click **Upload GeoJSON** for each level whose
   shapes changed. (**Boundaries** appears only when the deployment has a boundary
   store.)
4. Under **Lineage → Change events**, click **Record change event**: choose the
   type, the from and to units, and add a note (for example, the decision that
   made the change).
5. Set **Effective from** if the change takes effect later, and **Submit for
   approval**.

Good to know:

* **Record splits and merges yourself.** For unit changes without a recorded
  event, MDS adds automatic events on submit (marked **Auto**), but those do not
  link old units to new ones.
* A boundary file must be a GeoJSON `FeatureCollection`; features are matched to
  units by `properties.pcode`. A published version's boundaries cannot be replaced.
* **Lineage → Crosswalk** shows how an old P-code maps to the new units.

See [Geography and Boundary Changes](geography.md).

## Load a newer country pack version

1. Ask the deployment administrator to set the new pack and re-run the install
   (see [Deployment](deployment.md)). The loader opens a **draft** for each
   dataset, and for the geography, that differs from the published version.
2. On **Home**, open each draft under **Pending work → Drafts in progress**.
3. Check **Compare versions**: entries added, changed and retired.
4. For the geography, record the real change events (split, merge, recode)
   unless the pack provided them.
5. Submit and approve the drafts **in order**: first a dataset that others refer
   to (for example, crops before seed varieties).

See [Country Packs](country-packs.md).

## Create a catalogue release

A [catalogue release](concepts.md#catalogue-release) names one version of each
dataset it includes, and of the geography, under one code, so consumers can read
them together.

1. Open **Releases** and click **Create release**. Give a **Release code** (for
   example `2027.1`), a title and a note.
2. Click **Set members**. Add a row per dataset with **Add dataset** and choose a
   published version, or click **Pin all versions in effect**. Choose the
   **Geography version**. Save.
3. Another person clicks **Publish**. The release is then fixed.

Name every dataset its consumers use: a dataset not in the release cannot be read
by that release. A draft release can be deleted; a published one cannot.

## Make a dataset public

1. Open the dataset and click **Dataset settings** (for the geography:
   **Publication settings**).
2. Set the visibility to **Public** and, if it applies, the licence. Save. It
   applies at once.

A public dataset carries a **Public** badge in the Datasets list and on its page.
Nothing is served until the deployment switches the public catalogue on; the
dialog says so when it is off. See [Public Catalogue](public-catalogue.md).

## Follow what changed

* **Activity** lists every step of every dataset, the geography and releases,
  newest first: the catalogue's change feed.
* A dataset's or the geography's **History** tab shows the same for that subject,
  per version, including changes that apply at once.
* The UI shows who did something by display name, or by user id when there is no
  name (for example, the country-pack loader).
