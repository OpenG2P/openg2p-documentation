# Eligibility Assessment

## Introduction

For a given program, there are certain criteria by which individuals are eligible for that program. Assuming that eligibility can be expressed unambiguously based on an individual's demographic data, a program administrator can apply the criteria in the registry to create a list of beneficiaries.

## Eligibility Manager

In OpenG2P, Eligibility Manager is a separate software module for configuring eligibility to a program. The module provides both simple filters and more sophisticated filters, such as the [Proxy Means Test](proxy-means-test.md), to define most eligibility requirements. Program administrators can also write their own custom plugins and add them to the Eligibility Manager.

## Configuring eligibility criteria in a program

In the OpenG2P program, configuring eligibility criteria is a two-step process. Program administrators need to first create Eligibility Manager(s) based on type. In the second step, these Eligibility Managers are added to the program.

#### Creating Eligibility Manager type

OpenG2P supports three types of Eligibility Managers.

1. Default Eligibility Manager
2. ID document Eligibility Manager
3. Phone number Eligibility Manager

One Eligibility Manager can be associated with only one program. To learn the steps to create an Eligibility Manager, click [here](../guides/user-guides/create-eligibility-manager-1/).

#### Adding an Eligibility Manager to a program

A program can have multiple Eligibility Managers. To learn the steps to add the Eligibility Managers, click [here](../guides/user-guides/create-eligibility-manager.md).

## Eligibility filters

The image here shows eligibility criteria with two filters: first for checking that the registrant is part of exactly one program, and second for checking that the registrant is unemployed.

<figure><img src="../.gitbook/assets/eligibility-criteria-filters (1).PNG" alt=""><figcaption></figcaption></figure>

## How-To Guides:

[Create Eligibility Manager Types](../guides/user-guides/create-eligibility-manager-1/)

[Create an Eligibility Manager Under the Program](../guides/user-guides/create-eligibility-manager-1/)
