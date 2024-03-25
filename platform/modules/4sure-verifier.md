# 4Sure Verifier

## Introduction

The 4Sure App is a user-friendly tool designed to make verifying identities quick and easy, even without an internet connection. It's perfect for situations where you need to confirm someone's credentials securely and reliably. By using technology similar to what's found in everyday devices, the app allows for a straightforward transfer of necessary information from a secure digital wallet, ensuring that the verification process is smooth and efficient. With its face verification feature, the app allows agents to take a person's photo and compare it with the image on their credential, ensuring accurate identity confirmation. Whether you're in a remote area or need to check identities in a busy environment, the 4Sure App ensures a smooth and secure verification process.

The 4Sure application is a VC (Verification Certificate) application designed to authenticate individuals by comparing and matching their VC details, such as national ID and beneficiary ID. The 4Sure application is seamlessly integrated with the MOSIP Platform, enhancing its functionality and usability. The application is designed to facilitate various features like facial authentication, identity verification, and offline authentication.

The application features a user-friendly interface that guides agents through the authentication process step-by-step. It provides clear instructions for scanning and capturing live photos and displays the scanned certificates once they are shared by beneficiaries.\


### **Operational Modes**

**Standalone Mode**

In standalone mode, the app functions independently to verify an individual's identity or confirm their eligibility for a specific program. It does not require an internet connection, making it ideal for use in remote or offline environments. In this mode, the app ensures data privacy and security by not storing any personal information post-verification, aligning with best practices in data protection.

**Key Features:**

* Identity verification
* Eligibility confirmation for programs
* Offline operation
* No storage of personal data

**Use Cases:**

* Verifying identities in remote locations
* Checking eligibility for benefits or services in offline settings

**Intent Mode**

When the app is activated through intent, such as being opened via another application (e.g., ODK Collect), it operates in a connected manner, allowing for the exchange of information between the 4Sure App and the calling application. This mode is particularly useful for applications that require a seamless flow of data and wish to incorporate identity verification within their operational processes.

Key Features:

* Data exchange with calling applications
* Seamless integration with other apps
* Enhanced functionality for interconnected operations

Use Cases:

* Gathering and returning verification details to a primary application
* Enhancing data flow in applications that require embedded verification processes

The dual-mode functionality of the 4Sure App provides versatile solutions catering to various operational needs and environments, ensuring users have access to reliable and secure verification services regardless of their internet connectivity status.

## Functionality and features

<table><thead><tr><th width="225">Feature </th><th>Functionality</th></tr></thead><tbody><tr><td><strong>Secure transfer of credentials</strong></td><td>Utilizes BLE technology for the secure and encrypted transfer of digital credentials</td></tr><tr><td><strong>MOSIP integration</strong></td><td>Fully integrated with the MOSIP platform, ensuring compatibility and interoperability with a wide range of identity solutions</td></tr><tr><td><strong>User-friendly interface</strong></td><td>Designed with a focus on ease of use, ensuring accessibility for users of varying technical proficiencies</td></tr><tr><td><strong>Face verification</strong></td><td><p>Incorporates a robust face verification SDK to enhance identity authentication, adding an extra layer of security and trustworthiness to </p><p>the verification process</p></td></tr><tr><td>Authentication Process</td><td><p></p><p>The 4Sure application uses a two-step authentication process to verify individuals. First, the national ID of the individual is scanned and then authenticated by capturing it with a live photo. And then, the beneficiary ID is scanned or entered to complete the authentication process.</p></td></tr><tr><td>VC Matching</td><td><p></p><p>The application compares the national ID and beneficiary ID provided by the individual to ensure they match. This matching process is done by verifying the UIN which helps to authenticate the individual's identity and verify their VC details.</p></td></tr><tr><td>Offline Authentication</td><td><p> </p><p>One of the key features of the 4Sure application is its ability to perform authentication processes offline. This ensures that users can verify their identity even in areas where there is no connectivity.</p></td></tr><tr><td>Integration</td><td><p></p><p>The 4Sure application can be integrated with other systems or applications to enhance its functionality. For example, it can be integrated with ODK to collect the authenticated data of the beneficiaries, Such as the national ID and beneficiary ID data are passed to ODK central and from there moved to the social registry and programs.</p></td></tr><tr><td>Facial Authentication</td><td>The application provides facial recognition technology to authenticate individuals, providing a secure and efficient method for verifying identity. Users can simply capture a live photo, which is then compared against the images present on the national ID.</td></tr><tr><td>Identity Verification</td><td><p></p><p>With MOSIP integration, the application enables comprehensive identity verification processes. Users can scan and upload IDs such as National ID and Beneficiary ID, which are verified against each other for accuracy and validity.</p></td></tr><tr><td>Security Features</td><td><p></p><p>The 4Sure application includes security features to protect the authenticity of the verification process. These features may include encryption of VC details, secure storage of verification certificates, and secure transmission of data.</p></td></tr></tbody></table>

## Concepts - all entities/sub modules

**National ID:** The national ID, also known as a national identification ID card, is a unique identifier assigned to individuals by their government for the purpose of identification. It can be used for availing various facilities. The format and use of national IDs may vary from country to country.

**Beneficiary ID:** A beneficiary ID is a unique identifier assigned to a person or entity who is the recipient of benefits, funds, or assets from a particular program. Even a Beneficiary ID is a unique identifier assigned to individuals. The format and use of national IDs may vary from country to country.

**Authentication**: Authentication is the process of verifying the identity of a user. In the 4Sure application, the authentication of the beneficiary is done by capturing the live photo of the beneficiary and then comparing it with the photo present on the National ID. The verified ID is then marked as authenticated.



## Components

The 4Sure App is built with several key technical components that enable its functionality, especially in terms of offline data transfer and identity verification. These components are integral to the app's operation, ensuring it delivers a secure and efficient verification process.

### **BLE Verifier SDK**

The BLE Verifier SDK is a critical component that enables the 4Sure App to receive Verifiable Credentials (VCs) via Bluetooth Low Energy (BLE) technology. This SDK is a wrapper built on top of Tuvali, a React Native library, which simplifies the API and enhances the app's ability to facilitate offline VC transfers between mobile devices.

**Key Features:**

* Secure VC transfer via BLE.
* Simplified API for ease of integration.
* Dependency on Tuvali for core functionality.
* Active development and maintenance by MOSIP.

**Considerations:**

* Limited support for iOS devices in initiating BLE exchanges, affecting VC transfer between iOS devices.

### **Camera SDK**

The Camera SDK integrates with the react-native-camera-kit camera to enable the app to access and use the device's camera. This feature is crucial for capturing live photos of individuals during the verification process.

**Key Features:**

* Access and control over the device's camera.
* Integration with react-native-vision for enhanced camera functionality.

**Use Cases:**

* Capturing live photos for real-time identity verification.

### **Face Match SDK**

The Face Match SDK is a sophisticated component that leverages Tensorflow and Google ML Kit to perform facial recognition and verification. It is built with native functionalities for Android ensuring compatibility and reliable performance.

**Key Features:**

* Advanced facial recognition using Tensorflow and Google ML Kit.
* Utilizes a tflite model trained on faces
* Essential for offline face authentication, providing an additional layer of security.

**Considerations:**

* The tflite model requires creation and training by the integrating party, demanding specific technical expertise.

## Technical Concepts

[See technical documentation of 4Sure](../../developer-zone/repositories/4sure.md)

## Workflow

<figure><img src="../../.gitbook/assets/4sure-work-flow.jpg" alt=""><figcaption></figcaption></figure>

## User guides

TODO

## Source Code

4Sure Source Code - [https://github.com/OpenG2P/4sure](https://github.com/OpenG2P/4sure)

##
