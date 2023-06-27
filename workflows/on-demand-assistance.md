# On-Demand Assistance

## Introduction

On-demand assistance is especially useful for scenarios like urgent surgeries, treatments, and other crisis situations. However, to prevent instances of fraud, it is imperative to do a thorough assessment of beneficiary entitlement. This section details one reference implementation for providing assistance using multiple stages of approvals.

## Process

## Multi-stage approval

This example shows multi-stage approval with three stages. The program manager/administrator can custom-assign an assessment officer for each stage. Though this example shows three stages, the number of stages can be customized.

The assessment can be rejected at any stage. In either case, the assessing officer needs to add the reason for the acceptance/rejection in the assessment.

If the assessment is rejected by any officer, then the process stops.

The entitlement is prepared by the Senior Officer after three assessments in this example.

The entitlement voucher can be communicated digitally or printed on paper. The voucher contains a QR code, which can be scanned to view and digitally verify the entitlement details.

After successful submission, the service provider can view the status and details of reimbursement on the _Service Provider Portal._

<figure><img src="../.gitbook/assets/image (2).png" alt=""><figcaption></figcaption></figure>
