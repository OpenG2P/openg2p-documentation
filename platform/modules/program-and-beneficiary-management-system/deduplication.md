# Deduplication

## Introduction

Deduplication refers to the process of removing duplicate entries in the program, thus avoiding double-dipping, and merging all the demographic fields associated with an individual/group into a single record.

The OpenG2P registry allows multiple entries for the same registrant. Hence once the registrants are enrolled in the program as beneficiaries, they should be deduplicated. OpenG2P Deduplication Managers can deduplicate the beneficiaries based on foundational/functional IDs, and phone numbers.

Note:&#x20;

* Each program in the OpenG2P platform should have at least one Deduplication Manager configured
* A separate Deduplication Manager must be created and configured for a program

## Deduplication Manager types

OpenG2P platform supports three types of Deduplication Managers.

1. Default Deduplication Manager
2. ID Deduplication Manager
3. Phone number Deduplication Manager

#### Default Deduplication Manager

This Deduplication Manager is assigned to each program by default. The Program administrators run the Deduplication Manager if they are sure of unique registration entries, as it is mandatory to configure at least one Deduplication Manager.

#### ID Deduplication Manager

ID Deduplication Manager deduplicates the registrants based on the their ID. The Program administrators should configure the ID type that will be used for deduplication.&#x20;

#### Phone number Deduplication Manager

Phone number Deduplication Manager deduplicates the registrants based on their phone numbers. This Deduplication Manager is often configured along with the ID Deduplication Manager.

## Deduplication Manager configuration

In OpenG2P program, the two-step process to configure a Deduplication Manager in a program are:

1. Program administrator must create at least one Deduplication Manager for each Deduplication Manager type required.&#x20;
2. After Deduplication Manager(s) is created, Program administrators add Deduplication Manager to a program.&#x20;

## Deduplicating registrants

Deduplication of registrants is a one-click operation once Deduplication Managers are added to the program. The Deduplication Manager does not distinguish between original and duplicate records, and all beneficiaries with the same field value - as configured for duplicate detection - are listed as duplicates.

The figure below shows two duplicate entries.

\<image to be incorporated>

## Deduplicating Individuals

The Deduplication Manager also supports deduplication for the scenario in which the program administrator or approving authorities approve the [entitlement ](entitlement.md)of a single individual. The demographics of the individual will be deduplicated against that of every enrolled beneficiary.

If the program supports multiple entitlements for the same individual, then this deduplication can be skipped. It is assumed that in such a case, there are other mechanisms to ensure that double-dipping is prevented.

On the whole, these features provide flexibility for the Program administrators to implement a wide variety of social protection programs.

## Related links

[Configure ID Types](https://github.com/OpenG2P/openg2p-documentation/blob/1.2.1/platform/modules/guides/user-guides/configure-id-types.md)

[Create Deduplication Manager Types](https://github.com/OpenG2P/openg2p-documentation/blob/1.2.1/platform/modules/guides/user-guides/create-deduplication-manager-types/README.md)

[Create Deduplication Manager under Program](https://github.com/OpenG2P/openg2p-documentation/blob/1.2.1/platform/modules/guides/user-guides/create-deduplication-manager.md)

##
