---
description: WIP
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

In Social Registry (SR) huge volumes of data are recorded. There is a need to set a limit to prevent the data from being edited multiple times. If the limit is set, it improves the accuracy of the data. The Social Registry has the Lock, Unlock, and Update features which play a pivotal role in maintaining the efficiency of the recorded data.  \


## Lock&#x20;

The Lock feature prevents data from being edited multiple times. When the records are loaded on SR and SPP, the limit is set to edit the data only once. If the records are edited once, the Lock feature disables the record from being edited again.

## Unlock

The Super Admin performs the below activities to unlock/lock the record.

* If there is a need to edit/update the record, the user must send a request with a valid reason to Super Admin.
* The Super Admin validates the reason. If the reason is valid, he/she approves the request.&#x20;
* Once the Super Admin approves the request, the user can edit/update the records.
* If the Super Admin rejects the request, the record remains locked.



## Notification

If there are corrections in the records, then a Super Admin user will send a push and an email notification to the user.  The email contains the information on the record that needs to be edited/updated.&#x20;

## Log

The Log feature captures the status of the records such as the information on the&#x20;

* records the user has requested for unlock.
* edited record details.
* notifications sent for a record.
* approved/rejected record requests.
