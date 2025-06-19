---
description: Work in Progress
---

# Change Management

### Introduction

The Change Management module provides a structured approach to managing modifications to registry records. It ensures that all changes to records go through a proper approval process before being implemented, maintaining data integrity and providing an audit trail.

### &#x20;Features

* Change Request Creation: Users can initiate change requests for existing registry records
* Draft Record Management: System creates a copy of the original record for modification
* Document Upload: Support for uploading documents to substantiate changes
* Approval Workflow: Structured approval process with approver comments
* Change History: Complete audit trail of all changes and approvals
* Status Tracking: Clear visibility of change request status throughout the process

## State

DRAFT

* Initial state when change request is created
* User can edit changes, reason, and supporting documents
* User can submit for approval

PENDING\_APPROVAL

* Change request is submitted and waiting for approver review
* User cannot make further modifications
* Approver can approve or reject the change

APPROVED/PUBLISHED

* Change request has been approved by the approver
* Original record will be updated with draft data
* Change request is permanently closed

REJECTED

* Change request has been rejected by the approver
* Change request is closed
* User must create a new change request if needed

### User Roles

Data Entry User

* Can view registry records
* Can initiate change requests
* Can edit draft change requests
* Can submit change requests for approval

Approver

* Can view pending change requests
* Can review change details, reasons, and supporting documents
* Can approve change requests
* Can reject change requests with comments

System Administrator

* Can view all change requests and their history
* Can manage user roles and permissions
* Can access audit logs

### Workflow

Step 1: Change Initiation

* User navigates to a registry record
* User clicks "Request Change" button
* System opens change request form

Step 2: Change Request Creation

* User specifies what changes are needed
* User provides reason for the change
* User uploads supporting documents (if required)
* User saves the change request
* System creates change request record in DRAFT status
* System copies original record to draft table

Step 3: Submission for Approval

* User reviews the change request
* User clicks "Submit for Approval"
* System changes status to PENDING\_APPROVAL
* System notifies approver of new change request

Step 4: Approval Process

* Approver receives notification
* Approver reviews change details, reason, and documents
* Approver has three options:
* Approve (triggers automatic publishing of draft to original record)
* Approve with comments (triggers automatic publishing of draft to original record)
* Reject with comments (closes the change request)

Step 5: Outcome

* If APPROVED: Draft record automatically overwrites the original record
* If REJECTED: Change request is closed, no changes made
* System maintains complete audit trail
* User receives notification of outcome

## Change Request Interfaces

There would be multiple entry points through which a registry record change or addition might be requested. It can be mainly categorized into two channel.

1. Odoo based channels
   * Social Registry Admin: Direct UI within Odoo
   * CSV/Excel Import: Bulk import with change request generation
   * Agent Portal: Field agent interface within Odoo
   * ODK Import: Mobile data collection integration
2. API based channels
   * Self-Service Portal: External web interface
   * External Systems: Third-party integrations
   * DCI interfaces: API's exposed as per the DCI specifications\


{% embed url="https://miro.com/app/board/uXjVImzoRgY=/?share_link_id=278785513081" %}

\


