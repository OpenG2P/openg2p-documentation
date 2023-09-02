# Deduplication

## Introduction

Deduplication refers to the process of removing duplicate entries in the program, thus avoiding double-dipping, and merging all the demographic fields associated with an individual or a group into a single record.

Each program in the OpenG2P program should have at least one Deduplication Manager configured. A separate Deduplication Manager must be created and configured for a program.

## Deduplication Manager types

OpenG2P platform supports three types of Deduplication Managers:

#### Default Deduplication Manager

This Deduplication Manager is assigned by default to each program. Since it is mandatory to configure at least one Deduplication Manager, program administrators can use this Deduplication Manager if they are sure of unique registration entries or do not want to run the deduplication.

#### ID Deduplication Manager

This Deduplication Manager will deduplicate the registrants based on the ID of the registrants. The program administrators should configure the ID type that will be used for deduplication. To learn more about ID type configuration, click [here](../guides/user-guides/configure-id-types.md).

#### Phone Number Deduplication Manager

The registrants can be deduplicated based on their phone numbers. This Deduplication Manager is often configured along with the ID Deduplication Manager.

## Deduplication Manager configuration

Configuring a Deduplication Manager in a program is a two-step process.

#### Create a Deduplication Manager type

The program administrator must create at least one Deduplication Manager for each Deduplication Manager type required. To learn more about this step, click [here](../guides/user-guides/create-deduplication-manager-types/).

#### Add the Deduplication Manager to a program

The program administrator needs to add the Deduplication Manager(s) created in the first step to the program. To learn more about this step, click [here](../guides/user-guides/create-deduplication-manager.md).

## Deduplicating registrants

Deduplication of registrants is a one-click operation once Deduplication Managers are added to the program. The Deduplication Manager does not distinguish between original and duplicate records, and all beneficiaries with the same field value - as configured for duplicate detection - are listed as duplicates.

The figure below shows two duplicate entries.&#x20;

<figure><img src="../.gitbook/assets/deduplicate-beneficiaries.png" alt=""><figcaption></figcaption></figure>

## Deduplicating Individuals

The Deduplication Manager also supports deduplication for the scenario in which the program administrator or approving authorities approve the [entitlement ](entitlement.md)of a single individual. The demographics of the individual will be deduplicated against that of every enrolled beneficiary.&#x20;

If the program supports multiple entitlements for the same individual, then this deduplication can be skipped. It is assumed that in such a case, there are other mechanisms to ensure that double-dipping is prevented.

Together, these features provide flexibility for program administrators to implement a wide variety of social protection programs.

## How-To Guides

[Configure ID Types](../guides/user-guides/configure-id-types.md)

[Create Deduplication Manager Types](../guides/user-guides/create-deduplication-manager-types/)

[Create Deduplication Manager under Program](../guides/user-guides/create-deduplication-manager.md)

##
