# Eligibility

## Introduction

Eligibility is a list of criteria/requirement that an individual/group must possess to eligible for a given program. A program administrator can apply the criteria in the registry to create a list of beneficiaries, assuming that eligibility can be expressed unambiguously based on an individual's demographic data.

## Eligibility Manager

In OpenG2P, Eligibility Manager is an independent Odoo module for configuring eligibility to a program. The module provides both simple filters and advanced filters, such as the [Proxy Means Test](proxy-means-test.md), to define most eligibility requirements. Program administrators can also script their own custom plugins and add them to the Eligibility Manager.

OpenG2P supports three types of Eligibility Managers.

* Default Eligibility Manager
* ID document Eligibility Manager
* Phone number Eligibility Manager

\<Define the functionality of each type of Eligibility Manager>

## Create Eligibility Manager

In the OpenG2P program, the two steps process to configure eligibility criteria are:&#x20;

1. Program administrators must create Eligibility Manager(s) from the three types of Eligibility Manager supported by OpenG2P
2. After Eligibility Manager is created, Program administrators add Eligibility Manager to a program

Note:

* One Eligibility Manager can be associated with only one program.
* A program can have multiple Eligibility Managers.

## Eligibility filters

The image represents eligibility criteria with two filters to check, if the,

1. registrant is part of exactly one program
2. registrant is unemployed.

\<image to be incorporated>

## Related links

[Create Eligibility Manager Types](https://github.com/OpenG2P/openg2p-documentation/blob/1.2.1/platform/modules/guides/user-guides/create-eligibility-manager-1/README.md)

[Create an Eligibility Manager Under the Program](https://github.com/OpenG2P/openg2p-documentation/blob/1.2.1/platform/modules/guides/user-guides/create-eligibility-manager-1/README.md)
