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

# Audit Log

**Audit logs** are an essential component of any system that stores sensitive data. They help in monitoring user activity, recording actions such as login attempts, changing user accounts, updating  records, any message added to the record, notification pushed to the record, request sent and accessing sensitive data. This document provides an overview of audit logs, their importance, and best practices for their implementation.

The basic events logging available in Odoo are:

* **Login attempts:** Recording successful and failed login which helps in monitoring user access to the system.
* **Changes to user accounts:** Tracking the changes made to user accounts which helps in maintaining the integrity of user profiles and detecting unauthorized modifications.
* **Access to sensitive data:** Recording access to sensitive data which ensures that only authorized users can access confidential information.
