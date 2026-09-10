# Documents

Staff attach files to a register section. Identity copies, certificates, household photos. Each file is stored once. A change request or an intake submission points at it. After approval, the live record shows those files. Opening a file uses a short-lived link.

Templates, bulk import files, and register exports use the same store. They are not the files on a section.

### Three places files show up

The same filename can appear in more than one place. Those places are not the same list.

| On screen            | Where                                                                                                                   | After approval                                                                                    |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| File fields          | Inside the section panels. In this register they are labelled `national_id`, `birth_certificate`, `passport`, and so on | Become the live files for that part of the record                                                 |
| Supporting Documents | Extra upload slots at the bottom of the section editor (`cert1`, `cert2`). Not on intake                                | Stay on that change request. Never copied onto the live record                                    |
| Attached Documents   | Header column on a change request or an intake submission                                                               | On a change request, this is Supporting Documents again. On intake, this is the section File list |
| Record photo         | Upload / Delete on the header-section silhouette, Individual Info                                                       | Stored on the record itself, not as a File field in `individual_documents`                        |

If you only remember one thing, remember this. File fields are the documents of the record. Supporting Documents / Attached Documents on a change request are evidence for the request. Approving does not turn that evidence into live File fields.

The editor below has both. File fields in the yellow panel, Supporting Documents under the divider.

<figure><img src="../../../../.gitbook/assets/image (9).png" alt=""><figcaption></figcaption></figure>

### The File field

Each File field is one slot. Label on the left, control on the right. The label is whatever Configuration set. In the screens here that is the field id, such as `national_id` or `birth_certificate`.

#### Edit

Open a live record, find the section, click **Edit Details**. Or fill the field on an intake draft.

Empty. A rounded **Upload** button with an upload icon and a dashed border. Required fields show a red asterisk next to the label. Required Supporting Documents slots (here `Birth Certificate`) use a full-width Upload. If you leave a required field empty and try to save, the dashed border turns error-coloured and the slot can show **This document is required**.

<figure><img src="../../../../.gitbook/assets/image (91).png" alt=""><figcaption></figcaption></figure>

Filled. Paperclip, truncated filename, X to clear. Supporting Documents use the same control, full width. Example of both in the same section shown below.

<figure><img src="../../../../.gitbook/assets/image (13).png" alt=""><figcaption></figcaption></figure>

Click **Upload** and pick a file from disk. Allowed types and max size come from that field. PDF and common images are typical. If the file does not appear after you pick it, it is usually the wrong type or larger than that field allows. Try another file.

The X clears the slot. Save after that if you mean to drop the file from the proposed set.

#### View

On the live record, and on the change request **New & Old Values** tab, the same field is read-only. Label on the left. Filename and a paperclip on the right, or `-` if empty. There is no X.

<figure><img src="../../../../.gitbook/assets/image (92).png" alt=""><figcaption></figcaption></figure>

The paperclip opens a short-lived link in a new tab. If an old tab stops opening the file, go back to the record and click again. The link expires.

A stored file shows under the File field whose label matches the label saved with the file. A file saved as `national_id` fills the `national_id` field.

### Upload, then save

The form never puts file bytes into the change request or the intake payload. **Save** does this in order.

1. New files from File fields, Supporting Documents, and the record photo are uploaded.
2. The server returns an id for each.
3. Save sends that id and a label. The label is the field title, such as `national_id` or `cert1`.
4. On a change request, files that were already on the section and were not changed keep their ids. They are not uploaded again.

When new files go up, you get **3 file(s) uploaded successfully!** (the count matches how many you just added). Then **Change request created successfully!** If upload fails, you see **File upload failed** and the change request is not created.

<figure><img src="../../../../.gitbook/assets/image (17).png" alt=""><figcaption></figcaption></figure>

You can replace a file, add one, or clear a slot. Untouched File fields on a change request stay attached.

**Save** on the section editor stays disabled until something changed. **Cancel** closes the editor without creating a request.

### Change a live record

Every edit to a live section goes through a change request, including file-only edits.

#### Open the editor

1. Open the register (here Individuals), open the record.
2. Use the tabs to reach the section that holds the File fields.
3. The section is read-only. Click **Edit Details** at the bottom of the section.
4. The section editor overlay opens on top of the record. Yellow background, dashed border.

The overlay has the section title (`individual_documents`), then the File fields in columns. Supporting Documents sit **below** a divider, under a collapsible **Supporting Documents** heading, above **Cancel** and **Save**. Click the chevron to collapse or expand that block. Those extra slots are not File fields. They do not become live section files.

<figure><img src="../../../../.gitbook/assets/image (20).png" alt=""><figcaption></figcaption></figure>

#### What to put where

Use the File fields for the documents that belong on the record. `national_id`, `birth_certificate`, household photo, passport.

Use Supporting Documents for extras the reviewer should see. Here `cert1` and `cert2`. A cover letter, a note from the field, a scan that explains the change. Those stay on the request. After save they show as **Attached Documents** on the change request, not under New.

The record photo is on Individual Info, not in `individual_documents`. See Record photo.

#### Save the request

Click **Save**. New files upload first. Then the portal creates a pending change request. The two toasts above appear in that order.

The record page can show **Pending changes awaiting review** when that record has pending requests. If it has none, it shows **No pending change requests**.

Only one pending request is allowed for that record and section. A second **Save** on the same section fails with **A pending change request already exists for this record and section**. Open the existing request, or wait until it is approved or rejected.

### Review the change request

Open the request from the record, or from **Change Request**. The list shows cards. Each card has **Attached Documents** on the right. That column is Supporting Documents from the editor (`cert1:` and a filename link). It is not the File fields.

**View details** opens the request. Breadcrumb looks like Individuals > Person 34808 > Change Request > Details. Partner and other channels that create a request land on this same screen.

<figure><img src="../../../../.gitbook/assets/image (21).png" alt=""><figcaption></figcaption></figure>

#### Details header

The yellow header has Register, Tab, Section, Created By, Created At, Source, Approval Status, then **Attached Documents**.

**Attached Documents** is Supporting Documents from the editor. In the shot below, `cert1:` links to `openg2p.pdf`. It is not `national_id` or `birth_certificate`. Those sit under **New & Old Values**.

If the column is empty (a dash), the requester did not add supporting files. The File fields can still have proposed files under New.

The filename is a link. The header shows the first three. Extra files use **View More**, which opens a popup titled **Attached Documents**.

#### New & Old Values

The body has tabs. **New & Old Values** is selected by default. Next to it, **CR Possible Duplicates** and **Register Possible Duplicates**. Those duplicate tabs do not list files.

New is on top, with a green **NEW** badge on the section title. That is the proposed File fields. Old is underneath, with an **OLD** badge. That is what is live today. Both are read-only. There is no **Edit Details** on this tab.

**Approvals** sits on the right. If you have no task, it says **No approval tasks assigned to you for this record.**

<figure><img src="../../../../.gitbook/assets/image (25).png" alt=""><figcaption></figcaption></figure>

Compare File fields the same way you compare text. New has a filename, Old has `-`. That is an add. New and Old both have filenames. That is a keep or a replace. New is `-` and Old has a filename. That is a clear.

When the live record already had files, Old is filled. New is what this request proposes. In the shot below, New dropped `household_photo` and `other_document` (those are `-`). Old still has them.

<figure><img src="../../../../.gitbook/assets/image (39).png" alt=""><figcaption></figcaption></figure>

If New File fields look empty and nobody removed files, treat New as same as Old. The requester left those slots alone. An intentional clear shows `-` on New.

#### Approve or reject

**Approve** writes the proposed File fields onto the live record. Supporting Documents stay on the request. They do not move to the live section. After the request above is approved, the live `individual_documents` section gets `national_id` and `birth_certificate`. It does not get `cert1`.

**Reject** leaves live files as they were. The files on the request remain on the request. They are not written to the record.

You may see **Approval is blocked because there are earlier pending change requests for this record.** Finish those first, in order.

Toasts after a decision. **Change request approved successfully** or **Change request rejected**.

### List sections

A list section is several rows in one table. Each row can have its own File fields. Change one child's certificate without touching the others.

A single-record section has one set of File fields for that record. `individual_documents` in the shots is that kind of section.

When you edit a list, check you are on the right row before you **Save**. The change request payload is per row. Approving applies that row's files to that row.

### Intake

Intake creates **new** records. It does not edit a live one. Files are saved with the **section** of the submission.

Intake does **not** show Supporting Documents. Only File fields in the form panels. There is nothing to attach as request-only evidence on this path.

#### Draft

Open **Intake Form**, start a new submission. Sections are accordions. Expand the section that has File fields.

Fill the File fields the same way as in the live editor. **Upload**, filename, X. There is no Supporting Documents block under the panels. **Previous** and **Next** move between sections.

Save the section. A toast says **Section saved successfully**. The accordion shows a green **Saved** badge (Land in the shot below). If you change a field after that, it shows a red **Modified** badge (Location Details). Save again before submit.

<figure><img src="../../../../.gitbook/assets/image (41).png" alt=""><figcaption></figcaption></figure>

Submit is disabled until every section is saved. The warning is **Please save all modified sections before submitting**.

#### Submit

**Submit** asks you to confirm. **If you submit your application, you will not be able to modify it further.** After that, **Submitted successfully**.

The submission header lists **Attached Documents**. On intake, that list **is** the section File list (`national_id`, `birth_certificate`, `proof_of_address`, then **View More (+3)**). Same files as the File fields. That is different from a change request, where Attached Documents is only supporting evidence (`cert1`).

Breadcrumb looks like Individuals - Form Submissions > the submission id. Tabs are **Intake Forms**, **Intake Possible Duplicates**, **Register Possible Duplicates**. **Approvals** is on the right.

<figure><img src="../../../../.gitbook/assets/image (76).png" alt=""><figcaption></figcaption></figure>

#### After submit

<table><thead><tr><th width="232">Stage</th><th>What happens to the files</th></tr></thead><tbody><tr><td>Submitted</td><td>No further edits. Header Attached Documents and the section File fields still show them</td></tr><tr><td>Rejected</td><td>Files stay on the submission. They are not written to the registry</td></tr><tr><td>Approved, then processed</td><td>Files from each section are written onto the new live record or records for that section</td></tr></tbody></table>

Approving the submission does not by itself put files on the registry. That happens when the approved submission is **processed** into live records.

On a repeating (list) section, the section's files apply to **every** row in that section when the record is created. Intake does not give each row its own File set. If two children need different certificates, that is a change request after the records exist, or a section design that is not a shared list.

Remove a file in draft and save before submit if it should never reach the live record.

### After approval

Open the register record and the same section. File fields are read-only. Label, filename, paperclip. **Edit Details** is still at the bottom of the section.

<figure><img src="../../../../.gitbook/assets/image (60).png" alt=""><figcaption></figcaption></figure>

To change a live file, **Edit Details** again. That creates another change request. View has no X.

A pending request still on that section means the live File fields have not changed yet. Look at **New & Old Values** on that request for the proposal.

### Record photo

The photo is on the Individual Info header, not in `individual_documents`. Click **Edit Details** on that header-section. The yellow overlay has a silhouette with **Upload** and **Delete**, then **Cancel** and **Save**. A dummy silhouette means no photo is stored yet.

<figure><img src="../../../../.gitbook/assets/image (77).png" alt=""><figcaption></figcaption></figure>

<figure><img src="../../../../.gitbook/assets/image (64).png" alt=""><figcaption></figcaption></figure>

Save still goes through a change request. The photo uploads with the other new files on that save. After approval, Browse Register and the record header show the photo next to the record name.

### Version history

On the record, open **Version History**. Pick a date, then **Select Section**, then **Select Version**. **Total Versions** shows how many exist.

The section renders read-only, same File fields as on a change request. Opening a past change request shows the File fields that request carried. Opening an intake version shows that submission section's files.

If the page says **No Version History**, nothing approved has been stored for that record yet.

The approval list on the right appears when the selected version is a change request. It is the decision trail for that request, not a second file list.

### Configure a section with file widget

<table><thead><tr><th width="198">Setting</th><th>Where</th><th>What staff then see</th></tr></thead><tbody><tr><td>File widget</td><td>Section Builder</td><td>One upload slot. Label, required, accept types, max size</td></tr><tr><td>Supporting document slots</td><td>Section schema</td><td>Extra slots in the section editor titled Supporting Documents. Header files on the change request</td></tr><tr><td>Documents Required</td><td>Add / Edit section modal</td><td>The section file list cannot be empty on save</td></tr><tr><td>Mixed vs files-only</td><td>Same section schema</td><td>Only File widgets, or File widgets next to text and tables</td></tr></tbody></table>

The on-screen form still blocks empty required File fields even when **Documents Required** is off. Turn **Documents Required** on when the section as a whole must have at least one file.

Labels on the change request and in File fields are the titles typed in Section Builder. If translations are missing, staff see the field id (`national_id`). If a stored file does not land in the field you expect, the field label and the saved label do not match. Fix the label in Configuration or save again with the same title.

Hide **Edit Details** on a section that should never change from the record screen. File fields on that section then stay view-only unless another channel creates a request.

### Limits

* One upload, many uses, until the file is deleted from storage.
* The same stored file cannot be attached to two sections of one record.
* Deleting a file from storage is permanent. It disappears everywhere that id was used.
* Allowed types and sizes are set per deployment. Typically PDF and common images, on the order of 10 MiB.
* Intake draft, a pending change request, and a rejected request do not change live files.
* Preview links are short-lived. Click again from the UI when one dies.
