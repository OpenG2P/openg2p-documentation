# Reference Design: Farmer Registry

The OpenG2P Farmer Registry is designed to streamline the identification, registration, and verification of farmers in a structured and scalable manner. It aligns with the use case documented in [OpenG2P Farmer Registry Use Case](https://docs.openg2p.org/use-cases/farmer-registry) and provides a reference implementation based on OpenG2P principles. This reference design can be a base to start off your farmer registry implementation and further you may modify as per your farmer registry specification.&#x20;

## Use case&#x20;

Refer [Farmer Registry](./)

## Source code

The entire source code for the reference design can be found in the GitHub [repository](https://github.com/OpenG2P/openg2p-reference-designs/tree/develop/farmer-registry).

## Components&#x20;

Included The Farmer Registry solution comprises the following components, as reflected in the OpenG2P Reference Designs GitHub repository:&#x20;

* `g2p_farmer`: Core farmer registry model.
* `g2p_farmer_rest_api`: REST API for accessing and managing farmer data.
* `g2p_farmer_service_provider_portal`: Portal for service providers to manage farmer and household in their respective administrative area.
* `g2p_lock_unlock`: Functionality for locking and unlocking farmer records.
* `g2p_odk_importer_farmer`: Component for importing data collected via ODK (Open Data Kit).

## Farmer model

(_Some of the fields are inherited from the OpenG2P core, so please refer to the base repositories to find them_)

| **Category**                | **Field Name**                       | **Type**                | **Description**                                         |
| --------------------------- | ------------------------------------ | ----------------------- | ------------------------------------------------------- |
| **Basic information**       | name                                 | Char                    | Farmer's full name                                      |
|                             | unique\_id                           | Numeric                 | Farmer ID                                               |
|                             | gender                               | Selection               | Gender of the farmer                                    |
|                             | date\_of\_birth                      | Date                    | Farmer's date of birth                                  |
|                             | phone\_number                        | Char                    | Contact phone number                                    |
|                             | email                                | Char                    | Email address                                           |
|                             | address                              | Text                    | Residential address                                     |
|                             | registration\_date                   | Date                    | Date of registration                                    |
|                             | tags\_ids                            | Many2many               | Tags associated with the registrant                     |
|                             | civil\_status                        | Char                    | Marital status of the registrant                        |
|                             | reg\_ids                             | One2many                | IDs for the farmer                                      |
|                             | phone\_number\_ids                   | One2many                | List of phone numbers                                   |
| **Socio-economic data**     | education\_level                     | Selection               | Highest level of education attained                     |
|                             | employment\_status                   | Selection               | Farmer's employment status                              |
|                             | household\_income                    | Float                   | Total household income                                  |
|                             | hh\_income\_type                     | Selection               | Income type                                             |
| **Membership**              | cooperative\_id                      | Many2one                | Cooperative membership                                  |
|                             | is\_member\_of\_primary\_cooperative | Selection               | Whether the farmer is a member of a primary cooperative |
|                             | primary\_cooperatives                | Many2one                | Primary cooperative the farmer belongs to               |
|                             | is\_member\_of\_cooperative\_union   | Selection               | Whether the farmer is a member of a cooperative union   |
|                             | cooperative\_unions                  | Many2one                | Cooperative union the farmer belongs to                 |
|                             | is\_member\_in\_farmer\_cluster      | Selection               | Whether the farmer is a member of a farmer cluster      |
|                             | primary\_commodity                   | Many2one                | Primary commodity the farmer produces                   |
|                             | role\_in\_farmer\_cluster            | Selection               | Role of the farmer in the cluster                       |
|                             | state                                | Selection               | State of the membership                                 |
| **Land information**        | total\_land\_area                    | Float                   | Size of land owned/leased                               |
|                             | land\_certificate                    | Many2one                | Certificate file upload                                 |
|                             | land\_id                             | Char                    | Land ID as per land administration records              |
|                             | ownership\_type                      | <p></p><p>Selection</p> | Owner or rented                                         |
| **Crop information**        | crop                                 | Selection               | Type of crops grown                                     |
|                             | collected\_gc                        | Date                    | Date of plantation                                      |
|                             | season                               | Selection               | Season                                                  |
| **Livestock information**   | livestock\_type                      | Selection               | Type of livestock raised                                |
|                             | livestock\_count                     | Integer                 | Number of livestock owned                               |
| **Agricultural input**      | do\_you\_use\_fertilizer             | Boolean                 | Whether fertilizer is used                              |
|                             | amount\_fertilizer\_utilized         | Float                   | The amount Of fertilizer                                |
|                             | do\_you\_use\_pesticide              | Boolean                 | Whether pesticide is used                               |
|                             | amount\_pesticide\_utilized          | Float                   | The amount Of pesticide                                 |
|                             | do\_you\_use\_insecticide            | Boolean                 | Whether insecticide is used                             |
|                             | amount\_insecticide\_utilized        | Float                   | The amount Of insecticide                               |
|                             | do\_you\_use\_improved\_seed         | Boolean                 | Whether improved seed is used                           |
|                             | amount\_improved\_seed\_utilized     | Float                   | The amount Of improved seed used                        |
| **Access to resources**     | crop\_water\_source                  | Selection               | Primary water source for crops                          |
|                             | livestock\_water\_sources            | Selection               | Water source for livestock                              |
|                             | access\_to\_machinery                | Selection               | Access to machinery                                     |
|                             | type\_of\_machinery                  | Selection               | Type to machinary                                       |
| **Access to finance**       | has\_finance\_access                 | Boolean                 | Has finance access                                      |
|                             | finance\_accesses                    | Selection               | Types of finances                                       |
| **Household**               | individual\_membership\_ids          | One2many                | Household membership                                    |
| **Other household members** | household\_members                   | One2many                | List of other household members                         |

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
