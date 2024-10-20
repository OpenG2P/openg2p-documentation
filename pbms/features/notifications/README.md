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

# Notifications

## Introduction

Notifications to beneficiaries and administrators are a must, especially when there are multiple stages of a delivery chain, usually with long time intervals between the different stages. Beneficiaries must be notified of their enrollment status, entitlements, payouts, exits, etc. Multiple channels such as SMS, email, and messaging apps can be used for notifications.

OpenG2P provides configuration of email, SMS, and Fast2SMS notifications in a few simple steps. Depending on the implementation needs of a program, notifications can be triggered for specific events in the delivery chain.

The figure below shows example notifications configured for two events - enrolling in the program and sending OTP.

<figure><img src="../../../.gitbook/assets/notification-events.png" alt=""><figcaption></figcaption></figure>

## Notification Manager

OpenG2P manages notifications via Notification Managers. Each program has at least one Notification Manager configured. The platform defines a different Notification Manager for each type of notification - SMS, email, Fast2SMS. These are the most commonly used Notification Managers:

* SMS Notification Manager
* Email Notification Manager
* Fast2SMS

OpenG2P uses the in-built [Qweb Templates](https://www.odoo.com/documentation/16.0/developer/reference/frontend/qweb.html) and [Inline Templates](https://apps.odoo.com/apps/modules/10.0/mail\_inline\_css/) for configuring the HTML pages and fragments. Notifications are sent based on the event and application configurations.

<figure><img src="../../../.gitbook/assets/notification-template (1).png" alt=""><figcaption></figcaption></figure>

The two steps to configure the notifications are:

1. The program administrator must create at least one Notification Manager for each Notification Manager type required.&#x20;
2. After the Notification Manager is created, the Program administrator adds the Notification Manager to the program.&#x20;

## Send notifications

Sending the notifications is a one-click operation. Based on the state of the program - enrolment, entitlement, payment, etc. - the corresponding notification is sent by the Notification Manager types configured for the program.

## Related user guides

:notebook\_with\_decorative\_cover:[Create Notification Manager Types](user-guides/create-notification-manager-types/)

:notebook\_with\_decorative\_cover:[Create Notification Manager under Program](user-guides/configure-notification-manager.md)

:notebook\_with\_decorative\_cover:[Send Notifications to Individual Registrants](user-guides/send-notifications-to-individual-registrants.md)
