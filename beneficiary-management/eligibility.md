# Eligibility Assessment

## Introduction

For a given program, there are certain criteria by which individuals are eligible for that program. Assuming that eligibility can be expressed unambiguously based on an individual's demographic data, a program administrator can apply the criteria in the registry to create a list of beneficiaries.&#x20;

## Eligibility Manager

In OpenG2P, Eligibility Manager is a separate software module for configuring eligibility to a program. The module provides both simple filters and more sophisticated filters, such as the [Proxy Means Test](proxy-means-test.md), to define most eligibility requirements. Program administrators can also write their own custom plugins and add them to the Eligibility Manager.

## Configuring eligibility criteria in a program

In the OpenG2P program, configuring eligibility criteria is a two-step process. Program administrators need to first create eligibility manager(s) based on type. In the second step, these eligibility managers are added to the program.

#### Creating eligibility manager type

OpenG2P supports three types of eligibility managers.&#x20;

1. Default eligibility manager
2. ID document eligibility manager
3. Phone number eligibility manager

One eligibility manager can be associated with only one program. To learn the steps to create an eligibility manager, click [here](../guides/user-guides/create-eligibility-manager-1/).

#### Adding an eligibility manager to a program

A program can have multiple eligibility managers. To learn the steps to add the eligibility managers, click [here](../guides/user-guides/create-eligibility-manager.md).

## Eligibility filters

The image here shows eligibility criteria with two filters.&#x20;

<figure><img src="../.gitbook/assets/eligibility-filters.png" alt=""><figcaption></figcaption></figure>

## How-To Guides:

[Create Eligibility Manager Types](../guides/user-guides/create-eligibility-manager-1/)

[Create Eligibility Manager Under Program](../guides/user-guides/create-eligibility-manager-1/)

