# Immediate Assistance On Demand

## Introduction

Immediate assistance is especially useful for scenarios like urgent surgeries, treatments, and other crises. However, to prevent instances of fraud, it is imperative to do a thorough assessment of beneficiary entitlement. This section details one reference implementation using multiple stages of approvals.

## Process <a href="#process" id="process"></a>

1. The beneficiary logs into the [Self Service Portal](https://app.gitbook.com/o/bnTr6Kp4z4CXR4QVIPSa/s/5qS01vi3dugd1B0cF8Ma/secure-registry/registration-methods/self-service-portal) and provides details of assistance such as the type and cost of treatment along with the name, address, gender, age, occupation, and family information.
2. The assistance application is reviewed and assessed in multiple stages by the officers designated by the program administrator/manager. At each stage, the designated officer will either approve/reject the application with a valid reason. If the application is rejected at any one of the stages, the approval process stops.
3. After all the designated officers approve the application, the final approving officer will also issue an entitlement voucher. The entitlement voucher has a QR code that can be scanned to view beneficiary entitlement and prove the authenticity of the entitlement voucher.
4. The beneficiary takes the entitlement voucher to the service provider. The service provider scans the entitlement voucher. If the QR scan is valid, the service provider assists the beneficiary.

## Reference scenario <a href="#reference-scenario" id="reference-scenario"></a>

This example describes on-demand assistance with multi-stage approval.

<figure><img src="https://github.com/OpenG2P/openg2p-documentation/raw/8a03d5f1c4c2808fdb9c6725f32442f21b6de7cf/.gitbook/assets/on-demand-assistance.png" alt=""><figcaption></figcaption></figure>

## Customizations <a href="#customizations" id="customizations"></a>

* The program manager/administrator can custom-assign an assessment officer for each stage.
* Though this example shows three stages, the number of stages can be customized.
* The entitlement voucher can be communicated digitally or printed on paper.
