---
description: >-
  Step-by-step tasks for catalogue administrators in the Master Data admin UI:
  change, retire and recode entries, add a dataset, schedule and approve
  changes, change geography, load a newer country pack, make a dataset public
---

# Admin Guide

Common tasks for catalogue administrators in the Master Data admin UI. Each task
uses the same flow: **open a draft → edit → submit → another person approves**
(see [Change Control and Approvals](change-control.md)). The screens are described
on [Admin UI](ui.md).

You need the right role: `MASTER_DATA_ADMIN` to edit and submit,
`MASTER_DATA_APPROVER` (or the publish permission) to approve. See
[Permissions](change-control.md#permissions).

## Add or change an entry

1. Open **Datasets** and click the dataset.
2. If there is no open draft, click **Open draft** and give a change note. If
   there is one, click **View draft**.
3. On the **Entries** tab, click **Add entry**, or **Edit** on an existing entry.
4. Fill in the code, label, labels by language, parent (for a hierarchical
   dataset) and fields. Save.
5. Click **Submit for approval**, check the change note, and submit.
6. Ask an approver to approve it (see [Approve or reject](#approve-or-reject)).

The code of an entry that has been published cannot be changed; see
[Recode an entry](#recode-an-entry).

## Retire an entry

1. Open the dataset's draft (steps 1–2 above).
2. On the **Entries** tab, click **Retire** on the entry. Choose whether to retire
   its child entries too.
3. Submit for approval.

A retired entry is not offered for new records, but records that hold it still
show it. **Reactivate** in a draft brings it back. See
[Retired entries](concepts.md#retired-entries).

## Recode an entry

A published code never changes. To replace it:

1. Open the dataset's draft.
2. **Retire** the old entry.
3. **Add entry** with the new code (and the same label, if it is unchanged).
4. Say in the change note that this is a recode, from which code to which.
5. Submit for approval.

Records that hold the old code keep it; map them if needed. See
[Codes are fixed once published](concepts.md#codes-are-fixed-once-published).

## Add a dataset

1. Open **Datasets** and click **New dataset**.
2. Give its code, label, labels by language, description, publisher, theme, and
   whether it is hierarchical. Save. The dataset opens on its first draft
   (version 1).
3. Optionally, on the **Schema** tab, define the fields each entry carries and
   click **Save schema to draft**. See [Typed attributes](concepts.md#typed-attributes).
4. Add its entries on the **Entries** tab.
5. Submit for approval.

A dataset that was never published can be deleted from the Datasets list. A
published one cannot; retire its entries instead.

## Schedule a change for a future date

1. Make the change in a draft as above.
2. When you open the draft (**Open draft**) or submit it (**Submit for
   approval**), set **Effective from** to the date.
3. Submit. An approver can still change the date when approving.

Once approved, the version is published but **not in effect** until the date: the
Datasets list shows **Changes pending**, and consumers keep reading the current
version until then. See [Effective dates](concepts.md#effective-dates).

## Approve or reject

1. On **Home**, look under **Pending work → Awaiting approval**, or find the
   **Submitted** badge on the Datasets or Geography page.
2. Open the version. Check the **Compare versions** tab for what changed, and the
   change note.
3. Click **Approve and publish** (optionally changing the effective date), or
   **Reject** with a note.

You cannot approve a draft you created, edited or submitted. If the deployment
uses the Approval Workflow Engine, there are no approve buttons in MDS: approve in
AWE, and the page shows the result. To rework a rejected version, open it and
click **Rework as new draft**.

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
   type, the from units and the to units, and add a note (for example, the decision
   that made the change).
5. Set **Effective from** if the change takes effect later, and submit.

Record splits and merges yourself: MDS adds automatic events for other changes,
but those do not link old units to new ones. Use **Lineage → Crosswalk** to check
how an old code maps. See [Geography and Boundary Changes](geography.md).

## Load a newer country pack version

1. Ask the deployment administrator to set the new pack and re-run the install
   (see [Deployment](deployment.md)). The loader creates a **draft** for each
   dataset, and for the geography, that differs from the published version.
2. On **Home**, open each draft under **Pending work → Drafts in progress**.
3. Check the **Compare versions** tab: entries added, changed and retired.
4. For the geography, record the real change events (split, merge, recode)
   unless the pack provided them.
5. Submit each draft. Submit and approve datasets that others refer to first (for
   example, crops before seed varieties).

See [Country Packs and Migration](country-packs-and-migration.md).

## Make a dataset public

1. Open the dataset and click **Edit dataset details** (for the geography:
   **Publication settings** on the Geography page).
2. Set **Visibility** to *Public*, and give a **Licence** and **Licence URL**.
3. Save. This applies at once; no approval is needed.

Only published versions are shown. Nothing is served until the deployment switches
the public catalogue on; the dialog says so when it is off. See
[Public Catalogue](public-catalogue.md).
