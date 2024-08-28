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

## Concepts

Periodic biometric authentications will be used to ensure legitimacy, validity and liveness of beneficiaries.&#x20;

## Need of this feature&#x20;

This process aims to enhance security by verifying recipients' identities on a regular basis, preventing fraud, and ensuring the right people receive benefits.

## High level diagram 1

<img src="../../../.gitbook/assets/file.excalidraw (1).svg" alt="" class="gitbook-drawing">

## High level diagram 2

<img src="../../../.gitbook/assets/file.excalidraw (3).svg" alt="" class="gitbook-drawing">

## To be discussed

1. Who are the users using this functionality

* User roles
* What are various operations for each user role

### Monitoring and reporting

1. Are any reports required for the administrators?
2. Any frequent monitoring required?

Frequency of authentication - 2 or 6 months (configurable)

Current Modes of Authentication

* SSP
* VC based authentication

3. Can existing reporting framework be used for the same?

### Privacy and security&#x20;

1. Is the data stored PII?
2. Any considerations related to data privacy?
3. How will the privacy of data handled at rest and in flight?
4. Any encryption required&#x20;

### Required features

* Notifying User
* Frequency of authentication- 2 or 6 months (configurable)

### Technical design

1. Is it an Odoo module? Or fastapi or anything else
2. Is the database involved

* Tables
* Fields
* Insert/update

Scalability - how do we handle scale?

### Source code location

* Repository name
* Branch

### Install/Deployment

1. How will the feature/module deployed with the rest of software
2. How will a developer install the feature

### Dependencies

1. Is the feature dependent on external libraries or projects?
2. What are the licenses of the external software?

### Test design

1. What the important points related to testing that we must keep in mind
2. Location of test case document
3. Is there automation involved? &#x20;
4. Plan for automation (if any)
5. Is a scale testing required. How?

### Development plan

1. Are there phases in which the feature will be developed
2. Release versioning
3. Scope of various releases
4. Rough timelines
5. Git Branch name
6. Task breakdown (pointer to Jira)

### Solution - long term

Odoo-based system might not scale. Hence develop and separate Portal (API + UI) which handles agents login and facilitates, beneficiary authentication.
