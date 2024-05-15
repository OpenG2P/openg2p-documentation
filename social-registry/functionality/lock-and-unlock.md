---
layout:
  title:
    visible: true
  description:
    visible: false
  tableOfContents:
    visible: true
  outline:
    visible: true
  pagination:
    visible: true
---

# Lock and Unlock

\
Lock&#x20;
----------

On Social Registry (SR), the lock feature is pivotal in preventing data from being multiple edits.  When the records are loaded on SR, the limit is set to edit the data only once. If the records are edited once, then the particular records will be locked.&#x20;

## Unlock

The locked records are unlocked for the next edit only. In order to re-edit the record, The user must send a request to Super Admin to unlock the record with a valid reason.\
\
Super Admin validates the user request to unlock the record. After validating, he/she approves/rejects the request to edit the record.

Once the Super Admin approves the request, the user can edit the record. The rejected request remains locked.

## Notification

On Social Registry, if there are corrections in the records, then a super admin user will send a push and an email notification to the user.  The user is notified about the information of a record that needs correction.

## Log

The log captures  the information of change in status of the records, user requesting for unlock, edit details, notification sent for the records, approval/rejection of a request.
