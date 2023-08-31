# Entitlement

## Introduction

Entitlement is the quantity of benefit that a beneficiary is entitled to receive. This is the money that a beneficiary will receive via either direct bank transfer, mobile wallet, cash at the counter, vouchers or other disbursement mechanisms. Entitlement is defined for each [cycle](disbursement-cycles.md).

## Entitlement manager

Entitlement Manager is a software module provided by the OpenG2P platform. The module provides a human-centric design for configuring the entitlement and approval process. Configuring an entitlement manager in a program is a three-step process:

#### Configure the entitlement manager role

Each entitlement manager has one or more approving authority roles. The approving authority role is played by a group of users who can approve the entitlements. Hence the approving authority role is configured as a group in the OpenG2P platform. OpenG2P provides a large variety of pre-defined groups. Additionally, program administrators can create custom groups that can be configured from scratch or inherited from pre-defined groups. To learn the steps to configure an approving authority role, click [here](../guides/user-guides/create-entitlement-manager-role.md).

#### Create entitlement manager type

OpenG2P supports two types of entitlement managers: default entitlement managers and voucher entitlement managers. The voucher entitlement manager provides the configuration of an [entitlement voucher](../eligibility-and-enrolment/payment-types/voucher.md) in addition to the configurations provided by the default entitlement manager. To learn the steps to create the entitlement manager type, click [here](broken-reference).

#### Configure entitlement manager in a program

In this step, the program administrators add the entitlement managers created in the second step to a program. To learn the steps to configure entitlement managers in a program, click [here](broken-reference).

## Entitlement details

OpenG2P entitlement managers allow program administrators to configure entitlement details under these broad categories.&#x20;

#### Entitlement amount

These configurations include entitlement amounts, transfer fees, currency, amount per person for a group, and the maximum number of individuals in a group. These configurations allow program administrators to set rules for entitlement amounts for individuals and groups.

#### Approving authority

The entitlement manager can have one or more stages of approval, and the program administrators can assign one of the approving authorities for each stage of approval. [Immediate Individual Assistance On-Demand](../workflows/on-demand-assistance.md) workflow describes an example involving multi-stage approval.

#### Entitlement voucher

OpenG2P provides an easy-to-use UI for creating an [entitlement voucher](../eligibility-and-enrolment/payment-types/voucher.md) template along with a QR code configuration. Once the entitlement is approved, a voucher file is generated according to the voucher template and QR code configuration.

The entitlement manager provides an option to auto-generate the entitlement voucher file upon entitlement approval. By default, these files are stored in the cloud. Program administrators can also configure the storage type - cloud, OpenG2P storage, or external storage - for the entitlement voucher files. To learn the steps to configure an entitlement voucher, click [here](broken-reference).

## Approval process

The approval process can be single-stage or multi-stage based on the approval settings in the entitlement manager. The figure below shows the entitlement approval for a program.

<figure><img src="../.gitbook/assets/approval-process.png" alt=""><figcaption></figcaption></figure>

The multi-stage approval typically follows this process:

* The first approving authority inspects and verifies documents, enrols the beneficiary based on eligibility, and adds an assessment.
* Subsequent approving authorities will skip the process of enrolment. However, they also inspect and verify beneficiary documents, and add their assessments.
* The last approving authority completes the approval process and generates an entitlement voucher.

To learn the steps for multi-stage approval, click [here](../guides/user-guides/multi-stage-approval.md).

## How-To Guides

[Create Entitlement Manager Role](../guides/user-guides/create-entitlement-manager-role.md)

[Create Entitlement Manager Type](broken-reference)&#x20;

[Configure Entitlement Manager in the Program](broken-reference)

[Configure Entitlement Voucher](broken-reference)

[Multi-Stage Approval](../guides/user-guides/multi-stage-approval.md)

