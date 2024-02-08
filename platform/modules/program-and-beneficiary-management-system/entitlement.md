# Entitlement

## Introduction

Entitlement is the quantity of benefit that a beneficiary is entitled to receive. This is the money that a beneficiary will receive via either direct bank transfer, mobile wallet, cash at the counter, vouchers or other disbursement mechanisms. Entitlement is defined for each [cycle](disbursement-cycles/).

## Entitlement Manager

Entitlement Manager is a software module provided by the OpenG2P platform. The module provides a human-centric design for configuring the entitlement and approval process.&#x20;

OpenG2P supports two types of Entitlement Managers.

1. Default Entitlement Managers
2. Voucher Entitlement Managers.&#x20;

The three-step process to configure an Entitlement Manager in a program are:

1. Each Entitlement Manager has one or more approving authority roles. The approving authority role is played by a group of users who can approve the entitlements. Hence the approving authority role is configured as a group in the OpenG2P platform.

&#x20;       To learn the steps to configure an approving authority role, click [here](https://github.com/OpenG2P/openg2p-documentation/blob/1.2.1/platform/modules/guides/user-guides/create-entitlement-manager-role.md).

2. Voucher Entitlement Managers configure an [entitlement voucher](https://github.com/OpenG2P/openg2p-documentation/blob/1.2.1/platform/modules/eligibility-and-enrolment/payment-types/voucher.md) template in addition to the configurations provided by the Default Entitlement Managers.

&#x20;       To learn the steps to create an Entitlement Manager type, click [here](https://github.com/OpenG2P/openg2p-documentation/blob/1.2.1/platform/modules/program-and-beneficiary-management-system/broken-reference/README.md).

3. After the Entitlement Managers is created, Program administrators add the Entitlement Managers to a program.

&#x20;       To learn the steps to configure Entitlement Managers in a program, click [here](https://github.com/OpenG2P/openg2p-documentation/blob/1.2.1/platform/modules/program-and-beneficiary-management-system/broken-reference/README.md).

## Entitlement details

OpenG2P Entitlement Managers allow Program administrators to configure entitlement details under these broad categories.

1. Entitlement amount
2. Approving authority
3. Entitlement voucher

#### Entitlement amount

These configurations include entitlement amounts, transfer fees, currency, amount per person for a group, and the maximum number of individuals in a group. These configurations allow Program administrators to set rules for entitlement amounts for individuals and groups.

#### Approving authority

The Entitlement Manager can have one or more stages of approval, and the Program administrators can assign one of the approving authorities for each stage of approval. [Immediate Individual Assistance On-Demand](https://github.com/OpenG2P/openg2p-documentation/blob/1.2.1/platform/modules/workflows/on-demand-assistance.md) workflow describes an example involving multi-stage approval.

#### Entitlement voucher

OpenG2P provides an easy-to-use UI for creating an [entitlement voucher](https://github.com/OpenG2P/openg2p-documentation/blob/1.2.1/platform/modules/eligibility-and-enrolment/payment-types/voucher.md) template along with a QR code configuration. Once the entitlement is approved, a voucher file is generated according to the voucher template and QR code configuration. To understand the workflow for entitlement vouchers, click [here](https://github.com/OpenG2P/openg2p-documentation/blob/1.2.1/platform/modules/workflows/on-demand-assistance.md).

The Entitlement Manager provides an option to auto-generate the entitlement voucher file upon entitlement approval. By default, these files are stored in the cloud. Program administrators can also configure the storage type - cloud, OpenG2P storage, or external storage - for the entitlement voucher files.&#x20;

&#x20;To learn the steps to configure an entitlement voucher, click [here](https://github.com/OpenG2P/openg2p-documentation/blob/1.2.1/platform/modules/program-and-beneficiary-management-system/broken-reference/README.md).

## Approval process

The approval process can be single-stage or multi-stage based on the approval settings in the Entitlement Manager. The figure below shows the entitlement approval for a program.

\<image to be incorporated>

<figure><img src="https://github.com/OpenG2P/openg2p-documentation/blob/1.2.1/platform/modules/.gitbook/assets/approval-process.png" alt=""><figcaption></figcaption></figure>

The multi-stage approval typically follows this process:

* The first approving authority inspects and verifies documents, enrolls the beneficiary based on eligibility, and adds an assessment.
* Subsequent approving authorities will skip the process of enrolment. However, they also inspect and verify beneficiary documents, and add their assessments.
* The last approving authority completes the approval process and generates an entitlement voucher.

To learn the steps for multi-stage approval, click [here](https://github.com/OpenG2P/openg2p-documentation/blob/1.2.1/platform/modules/guides/user-guides/multi-stage-approval.md).

<table><thead><tr><th width="230">Configuration</th><th>Description</th></tr></thead><tbody><tr><td>Entitlement amount</td><td>Program administrators can configure entitlement amount, currency, and transfer fee. Further, the entitlement amount for each individual in a group and the maximum number of individuals in the group can be configured.</td></tr><tr><td>Entitlement vouchers</td><td>An entitlement voucher authorizes the intended beneficiary to claim the benefits at the service provider facility. The voucher has customized QR codes embedded. The QR code provides a digital signature that makes the voucher tamper-proof and establishes the authenticity of the voucher.</td></tr><tr><td>Multi-stage approvals</td><td>Program administrators can configure multiple stages and assign a role for each stage to avoid concentration of power and errors in deciding the entitlement amount</td></tr></tbody></table>

## Related links

[Create a Custom Group](https://github.com/OpenG2P/openg2p-documentation/blob/1.2.1/platform/modules/guides/user-guides/create-entitlement-manager-role.md)

[Create Entitlement Manager Type](https://github.com/OpenG2P/openg2p-documentation/blob/1.2.1/platform/modules/program-and-beneficiary-management-system/broken-reference/README.md)

[Configure Entitlement Manager in the Program](https://github.com/OpenG2P/openg2p-documentation/blob/1.2.1/platform/modules/program-and-beneficiary-management-system/broken-reference/README.md)

[Configure Entitlement Voucher](https://github.com/OpenG2P/openg2p-documentation/blob/1.2.1/platform/modules/program-and-beneficiary-management-system/broken-reference/README.md)

[Multi-Stage Approval](https://github.com/OpenG2P/openg2p-documentation/blob/1.2.1/platform/modules/guides/user-guides/multi-stage-approval.md)
