---
description: Upcoming features - under development
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

# Periodic Biometric Authentication for Beneficiaries

In Program and Beneficiary Management System (PBMS) huge amount of beneficiaries' data are recorded. It is necessary to confirm that the information provided about the beneficiaries' identities are accurate and that they are currently receiving benefits from the applicable programs. With the ID Authentication feature, PBMS can check if each beneficiary has validated themselves using biometrics  within a specified time frame, allowing it to periodically verify each beneficiary's current status.

Only Registrars, Administrators, and Enumerators are authorised to use National IDs and biometrics or OTPs to authenticate applicants/registrants both in person and virtually.

Note:

The ID Authentication feature avoids the need for self-authentication via self-service portals.

## Authentication process

The PBMS retrieves the most recent date of successful authentication from the Social Registry module, which stores this data. The system determines whether the authentication happened within the necessary time limit (for example, during the last six months) after retrieving the date.

If the authentication is up-to-date, the beneficiary is considered "live," and their participation in the program is uninterrupted. The system initiates an action If the authentication date falls outside of the required period. Benefits may need to be temporarily suspended in this situation.
