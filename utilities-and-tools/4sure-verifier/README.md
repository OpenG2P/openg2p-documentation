---
description: Alpha version
layout:
  title:
    visible: true
  description:
    visible: true
  tableOfContents:
    visible: true
  outline:
    visible: true
  pagination:
    visible: true
---

# 4Sure Verifier

The 4Sure App securely verifies identities offline. It simplifies the verification process by transferring information from a digital wallet like INJI using Bluetooth technology and uses facial recognition to ensure the person's identity matches their credentials. The application is seamlessly integrated with the MOSIP Platform for National ID, enhancing its functionality and usability and is designed to facilitate various features like facial authentication and identity verification, all without the need for an internet connection.

The application features a user-friendly interface that guides agents through the authentication process step-by-step. It provides clear instructions for scanning and capturing live photos and displays the scanned certificates once they are shared by beneficiaries. Some of the features provided by 4Sure are:

* Offline identity verification
* Secure information transfer from digital wallets
* Facial recognition for accurate identity confirmation
* National ID Integration with the MOSIP Platform
* Step-by-step guided authentication process

## Feature and functionality

<table><thead><tr><th width="225">Feature </th><th>Functionality</th></tr></thead><tbody><tr><td><strong>Secure transfer of credentials</strong></td><td>Utilises BLE technology for the secure and encrypted transfer of digital credentials</td></tr><tr><td><strong>National ID  integration</strong></td><td>Fully integrated with the MOSIP platform, ensuring compatibility and interoperability with a wide range of identity solutions</td></tr><tr><td><strong>User-friendly interface</strong></td><td>Designed with a focus on ease of use, ensuring accessibility for users of varying technical proficiencies</td></tr><tr><td><strong>Face verification</strong></td><td><p>Incorporates a robust face verification SDK to enhance identity authentication, adding an extra layer of security and trustworthiness to </p><p>the verification process</p></td></tr><tr><td><strong>Authentication process</strong></td><td><p></p><p>The 4Sure application uses a two-step authentication process to verify individuals. First, the national ID of the individual is scanned and then authenticated by capturing it with a live photo. And then, the beneficiary ID is scanned or entered to complete the authentication process.</p></td></tr><tr><td><strong>VC matching</strong></td><td><p></p><p>The application compares the national ID and beneficiary ID provided by the individual to ensure they match. This matching process is done by verifying the UIN which helps to authenticate the individual's identity and verify their VC details.</p></td></tr><tr><td><strong>Offline authentication</strong></td><td><p> </p><p>One of the key features of the 4Sure application is its ability to perform authentication processes offline. This ensures that users can verify their identity even in areas where there is no connectivity.</p></td></tr><tr><td><strong>Integration</strong></td><td><p></p><p>The 4Sure application can be integrated with other systems or applications to enhance its functionality. For example, it can be integrated with ODK to collect the authenticated data of the beneficiaries, Such as the national ID and beneficiary ID data are passed to ODK central and from there moved to the social registry and programs.</p></td></tr><tr><td><strong>Facial authentication</strong></td><td>The application provides facial recognition technology to authenticate individuals, providing a secure and efficient method for verifying identity. Users can simply capture a live photo, which is then compared against the images present on the national ID.</td></tr><tr><td><strong>Identity verification</strong></td><td><p></p><p>With MOSIP integration, the application enables comprehensive identity verification processes. Users can scan and upload IDs such as National ID and Beneficiary ID, which are verified against each other for accuracy and validity.</p></td></tr><tr><td><strong>Security features</strong></td><td><p></p><p>The 4Sure application includes security features to protect the authenticity of the verification process. These features may include encryption of VC details, secure storage of verification certificates, and secure transmission of data.</p></td></tr></tbody></table>

## **Operational modes**

### **Standalone mode**

In standalone mode, the app functions independently to verify an individual's identity. It does not require an internet connection, making it ideal for use in remote or offline environments. In this mode, the app ensures data privacy and security by not storing any personal information post-verification, aligning with best practices in data protection.

{% embed url="https://miro.com/app/board/uXjVNkRnD6w=/?share_link_id=732459129683" %}
4Sure Standalone Flow
{% endembed %}

**Key features**

* Identity verification
* Offline process&#x20;
* No storage of personal data

**Use cases**

* Verifying identities in remote locations
* Checking eligibility for benefits or services in offline settings

### Intent mode

When the app is activated through intent, such as being opened via another application (e.g., ODK Collect), it operates in a connected manner, allowing for the exchange of information between the 4Sure App and the calling application. This mode is particularly useful for applications that require a seamless flow of data and wish to incorporate identity verification within their operational processes.

{% embed url="https://miro.com/app/board/uXjVNyZUxF4=/?share_link_id=58368165436" %}
4Sure Intent Flow
{% endembed %}

#### Key features

* Data exchange with calling applications
* Seamless integration with other apps
* Enhanced functionality for interconnected operations
* Offline process

#### Use cases

* Gathering and returning verification details to a primary application
* Enhancing data flow in applications that require embedded verification processes

> The dual-mode functionality of the 4Sure App provides versatile solutions catering to various operational needs and environments, ensuring users have access to reliable and secure verification services regardless of their internet connectivity status.

## Components

The 4Sure App is built with several key technical components that enable its functionality, especially in terms of offline data transfer and identity verification. These components are integral to the app's operation, ensuring it delivers a secure and efficient verification process.

### **BLE Verifier SDK**

The [Bluetooth Low-Energy](https://developer.android.com/develop/connectivity/bluetooth/ble/ble-overview) (BLE) Verifier SDK is a critical component that enables the 4Sure App to receive Verifiable Credentials (VCs) via BLE technology. This SDK is a wrapper built on top of Tuvali, a React Native library, which simplifies the API and enhances the app's ability to facilitate offline VC transfers between mobile devices.

**Key features**

* Secure VC transfer via BLE.
* Simplified API for ease of integration.
* Dependency on Tuvali for core functionality.
* Active development and maintenance by MOSIP.

**Considerations**

* Limited support for iOS devices in initiating BLE exchanges, affecting VC transfer between iOS devices.

### **Camera SDK**

The Camera SDK integrates with the react-native-camera-kit camera to enable the app to access and use the device's camera. This feature is crucial for capturing live photos of individuals during the verification process.

**Key features**

* Access and control over the device's camera.
* Integration with react-native-vision for enhanced camera functionality.

**Use cases**

* Capturing live photos for real-time identity verification.

### **Face match SDK**

The Face Match SDK is a sophisticated component that leverages [TensorFlow](https://www.tensorflow.org/) and [Google ML Kit](https://developers.google.com/ml-kit) to perform facial recognition and verification. It is built with native functionalities for Android ensuring compatibility and reliable performance.

**Key features**

* Advanced facial recognition using TensorFlow and Google ML Kit.
* Utilizes a tflite model trained on faces
* Essential for offline face authentication, providing an additional layer of security.

**Considerations**

* The tflite model requires creation and training by the integrating party, demanding specific technical expertise.

## Technical concepts

[See technical documentation of 4Sure](../../pbms/development/repositories/4sure.md)

## Workflow

{% embed url="https://miro.com/app/board/uXjVNrBMX8o=/?share_link_id=416645137148" %}
4Sure App Workflow
{% endembed %}

## User guides

[Verify Digital Credentials using 4Sure Application](https://app.gitbook.com/o/bnTr6Kp4z4CXR4QVIPSa/s/JZcdob2emEcLMvLyIxqT/\~/changes/79/utilities-and-tools/user-guides/verify-digital-credentials-using-4sure-application)

[Verify and Populate the form in ODK Collect using 4Sure Application](https://app.gitbook.com/o/bnTr6Kp4z4CXR4QVIPSa/s/JZcdob2emEcLMvLyIxqT/\~/changes/79/utilities-and-tools/user-guides/verify-and-populate-the-form-in-odk-collect-using-4sure-application)

## Source code

4Sure source code - [https://github.com/OpenG2P/4sure](https://github.com/OpenG2P/4sure)
