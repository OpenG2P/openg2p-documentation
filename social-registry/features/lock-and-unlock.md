---
layout:
  title:
    visible: true
  description:
    visible: true
  tableOfContents:
    visible: true
  outline:
    visible: true
  pagination:
    visible: true
---

# Lock and Unlock

In Social Registry (SR) huge volumes of data are recorded. There is a need to set a limit to prevent the data from being edited multiple times. If the limit is set, it improves the accuracy of the data. The Social Registry has the Lock and Unlock feature which plays a pivotal role in maintaining the integrity of the recorded data. &#x20;

## Lock&#x20;

The Lock feature prevents data from being edited inadvertently or without appropriate permissions. When the records are loaded on SR and SPP, the limit is set to edit the data only once. If the records are edited once, the Lock feature disables the record from being edited again.

## Unlock

Records may be unlocked to be edited following the below process:

* The user must send a request with a valid reason to the Admin (with permissions to allow lock/unlock)
* The  Admin validates the reason and approves the request.&#x20;
* The user can then edit/update the records.
* If the request is rejected, the record remains locked.

## Notification

If there are updates to the records, Admin will send a push and an email notification to the user.  The email contains the information on the record that needs to be edited/updated.&#x20;

## Log

The Log feature captures the status of the records such as the information on the&#x20;

* records the user has requested for unlock.
* edited record details.
* notifications sent for a record.
* approved/rejected record requests.
