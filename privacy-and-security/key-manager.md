# Key Manager

## Introduction

OpenG2P recognizes the critical importance of securing sensitive databases, including registrant data and voucher generation. The inclusion of a dedicated Key Manager ensures the protection of private and public keys, enhancing overall system security.

## Key Manager integration

<img src="../.gitbook/assets/file.excalidraw (4).svg" alt="The workflow of keymanager" class="gitbook-drawing">

### Purpose

The Key Manager in OpenG2P serves as a centralized entity responsible for the secure storage, generation, and distribution of cryptographic keys. Its primary functions include:

### Securing databases

* Safeguarding databases containing registrant data and voucher generation records.
* Protecting against unauthorized access and ensuring data confidentiality.

### Private and public key management

* Storing and managing private keys used for encryption and digital signatures.
* Distributing public keys for secure communication and verification.

### Key generation and storage

* Utilize the Key Manager to generate strong cryptographic keys.
* Safely store keys, potentially leveraging Hardware Security Modules (HSMs) for added protection.

### Database encryption

* Employ keys from the Key Manager to encrypt sensitive data in databases.
* Ensure that only authorized entities with the appropriate keys can access and decrypt the data.

### Voucher generation security

* Implement secure voucher generation processes using keys managed by the Key Manager.
* Protect against fraudulent activities by securing voucher generation operations.

### Private/public key pair handling

* Manage private keys securely to prevent unauthorized access.
* Distribute public keys for use in secure communication channels within the OpenG2P ecosystem.

## Security best practices

### Key rotation

* Regularly rotate cryptographic keys to mitigate the risk of compromise.
* Ensure a seamless transition during key rotation to avoid disruptions.

## HSM integration

Consider integrating with Hardware Security Modules for enhanced physical and logical key protection.

## Integration process&#x20;

The integration process involves making calls to the KeyManager service deployed in the Kubernetes cluster of OpenG2P. Keycloak provides an access token, which is used as a header for each API request. The primary functionalities are encapsulated within the `g2p_encryption` module.

### **Key Components:**

1. **Keycloak  access token:**
   * Obtained from keycloak authentication.
   * Serves as an authorization header for API requests
2. **KeyManager service:**
   * Deployed in the kubernetes cluster of openG2P.
   * Exposes various API endpoints for cryptographic operations.
3. **g2p\_encryption module:**
   * Central module handling cryptographic functionalities.
   * Initiates API calls to the KeyManager service.**Process Steps:**

### **Process steps:**

1. **Obtain keycloak access token:**
   * Authentication with keycloak to acquire an access token.
2. **Initialize g2p\_encryption module:**
   * Set up an instance of the `g2p_encryption` module within the openG2P environment.
3. **API requests to KeyManager:**
   * Utilize the access token as a header for API requests.
   * Make calls to various KeyManager API endpoints for cryptographic operations.
4. **KeyManager api endpoints:**
   * The KeyManager service, deployed in the kubernetes cluster, exposes endpoints for tasks like JWT signing and certificate retrieval.
5. **Integration with odoo:**
   * The `g2p_encryption` module acts as a bridge between KeyManager and odoo.
   * Provides an interface for odoo to perform secure operations using the services offered by KeyManager.

### **Advantages:**

* **Centralized cryptographic operations:**
  * All cryptographic operations are centralized within the `g2p_encryption` module, promoting modular and maintainable code.
* **Secure communication:**
  * Utilizing keycloak access tokens ensures secure communication between openG2P and KeyManager.
* **Scalability:**
  * Kubernetes deployment facilitates scalability and efficient management of the KeyManager service.

## Code module

The system employs a key manager to handle the encryption of registry data. All registry information is stored in an encrypted form, represented as a string. To access the original data, admin must utilize the "decrypt fields" option available in the settings. The key manager is responsible for generating, storing, and managing the encryption keys required for securing and decrypting the registry information. This approach enhances security by ensuring that sensitive data remains unreadable without the appropriate decryption process.&#x20;

### **Future Considerations:**

* **Error handling:**
  * Implement robust error handling mechanisms to gracefully manage exceptions during API calls.
* **Logging and Monitoring:**
  * Incorporate logging and monitoring features for tracking API requests and identifying potential issues.

## Documentation

Refer the following links for deeper understanding of the API's structure [Kernel api's](https://docs.mosip.io/1.1.5/apis/kernel-apis) and [Mosip api documentation](https://mosip.github.io/documentation/1.2.0/kernel-keymanager-service.html)

## Source Code

[openg2p-security](../pbms/development/repositories/openg2p-security.md)

## Conclusion

Integrating the Key Manager into OpenG2P provides a robust foundation for securing crucial databases and managing cryptographic keys. By following best practices and leveraging the capabilities of the Key Manager, OpenG2P ensures the confidentiality, integrity, and authenticity of sensitive information.
