# Eligibility

## Introduction

Eligibility is a list of criteria/requirement that an individual/group must possess to eligible for a given program. A program administrator can apply the criteria in the registry to create a list of beneficiaries, assuming that eligibility can be expressed unambiguously based on an individual's demographic data.

## Eligibility Manager

In OpenG2P, Eligibility Manager is an independent Odoo module for configuring eligibility to a program. The module provides both simple filters and advanced filters, such as the [Proxy Means Test](proxy-means-test.md), to define most eligibility requirements. Program administrators can also script their own custom plugins and add them to the Eligibility Manager.

OpenG2P supports three types of Eligibility Managers.

| Eligibility Manager                                                                                                                                                                                                                                                                   | Description                                                                                                                                                                                                                                                                        |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Default Eligibility Manager](https://app.gitbook.com/o/bnTr6Kp4z4CXR4QVIPSa/s/CwMntokukpQZjoCcqMwL/\~/changes/151/guides/user-guides/eligibility-and-program-enrollment/program/create-manager-type/create-eligibility-manager-1/create-default-eligibility-manager)                 | Default Eligibility Manager  is assigned to each program by default. The program manager runs the Default Eligibility Manager if the registrants are to be filter based on his/her eligibility criteria, as it is mandatory to configure at least one Default Eligibility Manager. |
| [ID Document Eligibility Manager](https://app.gitbook.com/o/bnTr6Kp4z4CXR4QVIPSa/s/CwMntokukpQZjoCcqMwL/\~/changes/151/guides/user-guides/eligibility-and-program-enrollment/program/create-manager-type/create-eligibility-manager-1/copy-of-create-id-document-eligibility-manager) | ID Document Eligibility Manager verifies the valid registrants based on his/her ID document. The program manager should configure the ID type that will be used to verify the eligibility of the registrants.                                                                      |
| [Phone Number Eligibility Manager](https://app.gitbook.com/o/bnTr6Kp4z4CXR4QVIPSa/s/CwMntokukpQZjoCcqMwL/\~/changes/151/guides/user-guides/eligibility-and-program-enrollment/program/create-manager-type/create-eligibility-manager-1/create-phone-number-eligibility-manager)       | Phone number Eligibility Manager verifies the valid registrants based on his/her phone numbers. This Phone Number Eligibility Manager is often configured along with the ID Document Eligibility Manager.                                                                          |

## Eligibility Manager Configuration

In the OpenG2P program, the process involved to configure eligibility manager are:&#x20;

1. Program manager must configure Eligibility Manager(s) from the three types of Eligibility Manager supported by OpenG2P
2. After Eligibility Manager is configured, program manager adds Eligibility Manager to a program

Note:

* One Eligibility Manager can be associated with only one program
* A program can have multiple Eligibility Managers

### Eligibility criteria

Program manager configures eligibility criteria to enroll the eligible registrants in the program. The filters used in configuring eligibility criteria are:

| Filter           | Description                                                                                                                                                                                                                                               |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Domain Filter    | OpenG2P supports a variety of domain filters to set criteria for age, gender, household size, composition, and location. Program manager can use these filters to define eligibility criteria.                                                            |
| Proxy Means Test | The Proxy Means Test (PMT) is considered the most effective approach to reduce the error of exclusion. PMT is available as a separate plug-in in the OpenG2P platform. Using this plug-in, program manager can configure the regression analysis formula. |
| Computer fields  | Computed fields are a powerful tool for abstracting information from a set of fields. Program manager can use these fields in PMT and domain filters to configure complex eligibility criteria.                                                           |

For example, the image here shows eligibility criteria with two filters: first for checking that the registrant is part of exactly one program, and second for checking that the registrant is unemployed.

<figure><img src="../../../../.gitbook/assets/eligibility-criteria-filters (1).PNG" alt=""><figcaption><p>Eligibility filters</p></figcaption></figure>

## Related user guides

[Create Eligibility Manager Types](../../../../user-guides/eligibility-and-program-enrollment/program/create-manager-type/create-eligibility-manager-1/)

[Create an Eligibility Manager Under the Program](../../../../user-guides/eligibility-and-program-enrollment/program/create-eligibility-manager.md)

[Create Default Eligibility Manager](https://app.gitbook.com/o/bnTr6Kp4z4CXR4QVIPSa/s/CwMntokukpQZjoCcqMwL/\~/changes/151/guides/user-guides/eligibility-and-program-enrollment/program/create-manager-type/create-eligibility-manager-1/create-default-eligibility-manager)

[Create ID Document Eligibility Manager](https://app.gitbook.com/o/bnTr6Kp4z4CXR4QVIPSa/s/CwMntokukpQZjoCcqMwL/\~/changes/151/guides/user-guides/eligibility-and-program-enrollment/program/create-manager-type/create-eligibility-manager-1/copy-of-create-id-document-eligibility-manager)

[Create Phone Number Eligibility Manager](https://app.gitbook.com/o/bnTr6Kp4z4CXR4QVIPSa/s/CwMntokukpQZjoCcqMwL/\~/changes/151/guides/user-guides/eligibility-and-program-enrollment/program/create-manager-type/create-eligibility-manager-1/create-phone-number-eligibility-manager)
