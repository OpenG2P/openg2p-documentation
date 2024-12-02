---
description: Work in progress
---

# Draft and Publish

### Overview

The Draft and Publish functionality allows users to create, modify, and finalize data entries before making them publicly available or integrating them into the main system. It ensures that users can work on data iteratively while maintaining control over visibility and approval workflows.

### **Key Features**

1. **Draft Mode:**
   * Users can create new entries in a private workspace.
   * Drafts are accessible only to the creator until submitted for approval.
   * Auto-save or manual save options ensure no data loss during editing.
2. **Approval Workflow:**
   * Once ready, users can submit drafts for review.
   * Administrators or approvers verify and approve drafts before publishing.
   * Rejected drafts can be revised and resubmitted.
3. **Publishing:**
   * Approved drafts are finalized and stored in the main system.
   * Notifications keep users informed about the approval and publishing status.
   * **Unique ID** is created and assigned
4. **Audit Trail:**
   * Tracks all changes, approvals, and publishing actions with timestamps and user details.
5. **Access Control:**
   * Only the creator can edit drafts in progress.
   * Approvers have visibility of submitted drafts.

### **Benefits**

1. **Improved Data Accuracy:**
   * Enables users to iteratively refine data before submission, reducing errors.
2. **Enhanced Collaboration:**
   * Structured approval workflows ensure high-quality data with accountability.
3. **Controlled Data Publishing:**
   * Only approved entries are published, ensuring consistency in the main database.
4. **Better User Experience:**
   * Users can work on drafts at their own pace without immediate publishing pressure.
5. **Secure and Private Editing:**
   * Access controls limit visibility to authorized personnel only.
6. **Auditability:**
   * Comprehensive logs improve transparency and help with compliance.

### **Workflow: Draft and Publish Process**

1. **Start: Initiate Draft**
   * A user starts by creating a new draft record for the entity (e.g., a Registrant).
   * The draft is stored in a temporary workspace specific to the user.
2. **Modify Draft**
   * The user updates and modifies the draft as needed.
   * Changes are auto-saved or manually saved in the temporary workspace.
3. **Review Draft**
   * The user reviews the draft to ensure all required information is complete and accurate.
   * The status of the draft remains as "In Progress" during this stage.
4. **Submit for Approval**
   * Once the user is satisfied with the draft, they submit it for approval.
   * The status of the draft changes to "Submitted."
   * Notifications are sent to administrators or approvers.
5. **Approval Process**
   * The administrator or approver reviews the submitted draft.
     * If the draft meets the required standards, it is approved.
     * If the draft requires changes, it is sent back to the user with comments, and the status reverts to "In Progress."
6. **Publish Draft**
   * Once the draft is approved:
     * The draft data is finalized and stored in the main database (e.g., `res.partner`).
     * The status of the draft changes to "Published."
     * Notifications are sent to the user confirming the publication.
7. **End: Finalized Data**
   * The approved and published data becomes part of the main records, visible and usable by the system.

{% embed url="https://miro.com/app/board/uXjVL8ldqpM=/?share_link_id=986712128228" %}

## Low level design

### **Entities and Models**

1. **`res.partner` (Main Model for Registrant)**
   * **Purpose:** Stores finalized and published data for registrants.
   * **Key Fields:**
     * `name` (Char): Name of the registrant.
     * `email` (Char): Email address.
     * `phone` (Char): Contact number.
     * Additional fields extended by the `registrant` model.
2. **`registrant` (Extension of `res.partner`)**
   * **Purpose:** Adds specific fields for registrants.
   * **Key Fields:**
     * `registration_number` (Char): Unique identifier for the registrant.
     * `additional_info` (Text): Extended information specific to the registrant.
3. **Transient Draft Model**
   * **Purpose:** Holds draft data during editing.
   * **Structure:**
     * Inherits from `res.partner`.
     * Temporary, non-persistent storage.
4. **Draft Metadata Table**
   * **Purpose:** Tracks draft records and metadata.
   * **Key Fields:**
     * `user_id` (Many2one): Links to the user creating/editing the draft.
     * `last_modified` (Datetime): Timestamp of the last edit.
     * `status` (Selection): Draft, Submitted, or Published.
     * `data` (JSON): Stores serialized draft data.

### **Workflows**

1. **Draft Creation**
   * User initiates a new draft.
   * A new record is created in the transient model.
   * Initial metadata entry is added to the draft metadata table.
2. **Draft Modification**
   * User edits the draft record via a form view.
   * Changes are saved in the transient model.
   * `last_modified` timestamp in metadata is updated.
3. **Draft Submission**
   * User submits the draft for approval.
   * Metadata `status` changes to "Submitted."
   * Draft becomes visible to the approver.
4. **Approval Workflow**
   * Approver reviews the draft.
     * **If Approved:** Metadata `status` changes to "Published."
     * **If Rejected:** Metadata `status` changes back to "Draft," and the user is notified.
5. **Publishing**
   * Approved draft data is transferred to `res.partner`.
   * A unique identifier (`registration_number`) is generated.
   * Draft data in transient model and metadata table are archived.

### **Access Control**

1. **Draft Visibility**
   * **User:** Can only view and edit their own drafts.
   * **Approver:** Can view submitted drafts.
2. **Approval Rights**
   * Only users with the "Approver" role can approve or reject drafts.

### **States**

1.  **Draft**

    The initial state of a new or in-progress draft created by the user.
2.  **Submitted**

    The draft has been completed by the user and submitted for review.
3.  **Approved**

    The draft has been reviewed and approved by the approver.
4.  **Rejected**

    The approver has reviewed the draft and decided it needs revisions.
5.  **Published**

    The approved draft has been published as a registrant record in `res.partner`.

### **State Transitions Overview**

| **Current State** | **Action**          | **Next State** |
| ----------------- | ------------------- | -------------- |
| Draft             | Submit for Approval | Submitted      |
| Draft             | Delete              | Removed (End)  |
| Submitted         | Approve             | Approved       |
| Submitted         | Reject              | Rejected       |
| Rejected          | Modify and Resubmit | Submitted      |
| Approved          | Publish             | Published      |

