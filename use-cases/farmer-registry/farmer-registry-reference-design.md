# Farmer Registry: Reference Design

The OpenG2P Farmer Registry is designed to streamline the identification, registration, and verification of farmers in a structured and scalable manner. It aligns with the use case documented in [OpenG2P Farmer Registry Use Case](https://docs.openg2p.org/use-cases/farmer-registry) and provides a ready-to-use implementation based on OpenG2P principles.

This document serves as a reference for understanding the implementation details, components, and setup process for the Farmer Registry solution.

## Use Case&#x20;

As outlined in the OpenG2P documentation, the primary use case for the Farmer Registry is to enable a country’s Department of Agriculture to:&#x20;

**Register Farmers**: Capture and maintain a centralized database of farmers, including demographics, agricultural activities, and service requirements.

**Target Support**: Enable agriculture programs to provide relevant support based on farmers’ needs.&#x20;

**Decision Support**: Empower policymakers with real-time data for informed decision-making.&#x20;

**Data Exchange**: Ensure seamless integration with other systems and data sources

## What We Did

The Farmer Registry was built to provide a digital-first approach to farmer identification and management. Key objectives achieved include:

* **Structured Registration**: A comprehensive registration system that captures essential farmer details such as personal information, land ownership, and farming activities.
* **ID Authentication**: The system supports biometric or OTP-based authentication to validate farmers.
* **ODK-Based Data Collection**: Offline and online data capture capabilities using ODK (Open Data Kit) for field-level data collection.
* **Configurable Deduplication**: Ensures unique farmer records through configurable deduplication based on IDs or biometric data.
* **Registration Portal:** An intuitive interface for the enrollment agents to enumerate farmer and their household data.
* **Interoperability**: Designed to integrate with other systems like payment gateways, subsidy management, and agriculture extension services.

## Components&#x20;

Included The Farmer Registry solution comprises the following components, as reflected in the OpenG2P Reference Designs GitHub repository:&#x20;

* `g2p_farmer`: Core farmer registry model.
* `g2p_farmer_rest_api`: REST API for accessing and managing farmer data.
* `g2p_farmer_service_provider_portal`: Portal for service providers to manage farmer and household in their respective administrative area.
* `g2p_lock_unlock`: Functionality for locking and unlocking farmer records.
* `g2p_odk_importer_farmer`: Component for importing data collected via ODK (Open Data Kit).

## Source code

The entire source code for the reference design can be found in the GitHub [repository](https://github.com/OpenG2P/openg2p-reference-designs/tree/develop/farmer-registry)\


## How to Set Up

Follow the developer installation guide provided for setting up OpenG2P on Linux: [Developer Install Guide](https://docs.openg2p.org/social-registry/developer-zone/developer-install/developer-install-of-openg2p-package-on-linux).

Once the OpenG2P setup is completed, proceed with the following steps specific to the Farmer Registry:

1.  **Navigate to the OpenG2P Addons Directory**

    ```
    cd ~/odoo/custom-addons/
    ```
2.  **Clone the Farmer Registry Repository**

    ```
    git clone https://github.com/OpenG2P/openg2p-reference-designs.git
    ```
3.  **Adjust Odoo Configuration**

    * Update the `odoo.conf` file to include the Farmer Registry module path:

    ```
    addons_path = /home/odoo/odoo/addons,/home/odoo/custom-addons/openg2p-reference-designs/farmer-registry
    ```
4.  **Restart Odoo**

    ```
    sudo systemctl restart odoo
    ```
5. **Activate the Farmer Registry Module**
   * Log into Odoo and navigate to **Apps**.
   * Enable Developer Mode.
   * Search for `Farmer Registry` and install the module.
6. **Configure Farmer Registry Settings**
   * Set up deduplication rules and ODK integration under module settings.



