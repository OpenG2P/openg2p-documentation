# Reference Design - Farmer Registry

The OpenG2P Farmer Registry is designed to streamline the identification, registration, and verification of farmers in a structured and scalable manner. It aligns with the use case documented in [OpenG2P Farmer Registry Use Case](https://docs.openg2p.org/use-cases/farmer-registry) and provides a reference implementation based on OpenG2P principles. This reference design can be a base to start off your farmer registry implementation and further you may modify as per your farmer registry specification.&#x20;

## Use case&#x20;

Refer [Farmer Registry](./)

## Components&#x20;

Included The Farmer Registry solution comprises the following components, as reflected in the OpenG2P Reference Designs GitHub repository:&#x20;

* `g2p_farmer`: Core farmer registry model.
* `g2p_farmer_rest_api`: REST API for accessing and managing farmer data.
* `g2p_farmer_service_provider_portal`: Portal for service providers to manage farmer and household in their respective administrative area.
* `g2p_lock_unlock`: Functionality for locking and unlocking farmer records.
* `g2p_odk_importer_farmer`: Component for importing data collected via ODK (Open Data Kit).

## Source code

The entire source code for the reference design can be found in the GitHub [repository](https://github.com/OpenG2P/openg2p-reference-designs/tree/develop/farmer-registry)

## How to setup

Follow the developer installation guide provided for setting up OpenG2P on Linux: [Developer Install Guide](https://docs.openg2p.org/social-registry/developer-zone/developer-install/developer-install-of-openg2p-package-on-linux).

Once the OpenG2P setup is completed, proceed with the following steps specific to the Farmer Registry:

1.  Navigate to the OpenG2P addons directory

    ```
    cd ~/odoo/custom-addons/
    ```
2.  Clone the farmer registry repository

    ```
    git clone https://github.com/OpenG2P/openg2p-reference-designs.git
    ```
3.  Adjust Odoo configuration

    * Update the `odoo.conf` file to include the Farmer Registry module path:

    ```
    addons_path = /home/odoo/odoo/addons,/home/odoo/custom-addons/openg2p-reference-designs/farmer-registry
    ```
4.  Restart odoo

    ```
    sudo systemctl restart odoo
    ```
5. Activate the farmer registry module
   * Log into Odoo and navigate to **Apps**.
   * Enable Developer Mode.
   * Search for `Farmer Registry` and install the module.
6. Configure farmer registry settings
   * Set up deduplication rules and ODK integration under module settings.

## Deployment
