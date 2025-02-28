---
description: Testing at OpenG2P
---

# Testing

## Overview

To ensure the reliability, security, and performance of the OpenG2P platform we follow a structured testing approach primarily focusing on [Sanity Testing](./#sanity-testing) and [Regression Testing](./#regression-testing).  Testing is conducted on versioned/tagged Dockers from the end-to-end (black box) perspective.  All test cases and planned and documented for manual execution (see the Excel sheet below).  The test results for a particular release are well documented [(example)](https://docs.openg2p.org/releases/1.1.0/release-notes#test-report).

### Sanity testing

Sanity testing ensures that new builds, bug fixes, or minor changes in the OpenG2P system do not introduce new defects and that the core functionalities work as expected.

#### Key focus areas

* Verification of critical workflows such as user authentication, beneficiary enrollment, and program management.
* Quick validation of database integrity after updates.
* Basic UI and API response checks to confirm stability.

#### Execution

* Performed on new releases or patches.
* Limited scope, focusing only on recent changes and their direct impact.
* If sanity tests pass, the system moves to deeper regression testing.

***

### Regression testing

Regression testing ensures that existing functionalities continue to work correctly after system modifications, updates, or enhancements.

#### Key Focus Areas:

* Validation of end-to-end workflows, including beneficiary registration, payment processing, and reporting.
* Testing of database transactions to ensure data consistency and security.
* Verification of API integrations with third-party financial systems.

#### Execution

* Performed after major updates, feature additions, or bug fixes.
* Manual test cases executed across various system modules.

[https://docs.google.com/spreadsheets/d/1wDvw2GdXGKBEchBPIUslTeIaJWf\_cEG9G9EK8PyuAAY/edit?gid=1675241385#gid=1675241385](https://docs.google.com/spreadsheets/d/1wDvw2GdXGKBEchBPIUslTeIaJWf_cEG9G9EK8PyuAAY/edit?gid=1675241385#gid=1675241385)

* Detailed test reports generated to track defect trends and system stability.

[https://docs.google.com/spreadsheets/d/1wDvw2GdXGKBEchBPIUslTeIaJWf\_cEG9G9EK8PyuAAY/edit?gid=1675241385#gid=1675241385](https://docs.google.com/spreadsheets/d/1wDvw2GdXGKBEchBPIUslTeIaJWf_cEG9G9EK8PyuAAY/edit?gid=1675241385#gid=1675241385)&#x20;

## Testing process for a release

Release testing ensures that the final product is fully functional, secure, and meets the requirements before deployment.

#### Key focus areas:

* Comprehensive validation of all functionalities under real-world conditions.
* Final integration testing with all system components and external services.
* User acceptance testing (UAT) to verify compliance with user needs and expectations.
* Performance and security testing under production-like environments.
* Deployment testing to ensure smooth installation and rollback capabilities.

#### Execution

* Conducted in a staging environment that mimics production.
* Test cases cover all aspects of system functionality, security, and usability.
* Final approval is based on test results and stakeholder feedback.&#x20;

## How to write a test case

Writing test cases for testing functionality involves defining clear, structured steps to validate that a feature or module of OpenG2P works as expected. Here’s a structured approach:

Each test case should include the following fields:

* Story ID            &#x20;
* Story  &#x20;
* Test Case No &#x20;
* Scenario          &#x20;
* Prerequisites&#x20;
* Test Case        &#x20;
* Expected Result          &#x20;
* Actual Result&#x20;
* Test Execution Env (Result)                                  &#x20;
* Exec #1 Date  &#x20;

Bug ID&#x20;
