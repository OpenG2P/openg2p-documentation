# G2P ODK Importer

### Module name

g2p\_odk\_importer

### Module title

G2P ODK Importer

### Technology base

[Odoo](https://www.odoo.com/)

### Functionality

The **ODK Importer** module facilitates the import of records from Open Data Kit (ODK) into the OpenG2P system. It provides seamless integration with ODK Central, allowing users to import data submitted through ODK forms directly into the system.

### Features

* **Record Import**: Enables the import of records from ODK forms into the OpenG2P system.
* **Scheduled Import**: Supports scheduled imports based on configurable intervals.
* **Connection Testing**: Provides functionality to test the connection with ODK Central.
* **Import Status Monitoring**: Allows monitoring of import job status and logs.

### Design notes

* The module is designed to integrate smoothly with ODK Central for efficient data transfer.
* Emphasis is placed on robust error handling and status monitoring to ensure reliable import processes.



### Dependencies

* **pyjq**: Python library for JSON querying.
* **Base**: Core module providing fundamental functionality.
* **Web**: Module for web interface components.
* **Queue Job**: Dependency for managing asynchronous jobs.

### User interface

Menu Added

* **Submenu**: ODK -> Configuration&#x20;

### Configuration

The module requires configuration of the following parameters:

* **Base URL**: The base URL of the ODK Central instance.
* **Username/Password**: Credentials for authentication with ODK Central.
* **Project ID**: The ID of the ODK project from which data will be imported.
* **Form ID**: The ID of the ODK form containing the data to be imported.
* **JSON Formatter**: Optional JSON formatter for customizing data mapping.
* **Target Registry**: Specifies whether imported records will be associated with individual or group registries.
* **Interval in Hours**: Configurable interval for scheduled imports.

### Usage

1. Configure the ODK connection settings in the **ODK Configuration** menu.
2. Test the connection to ODK Central to ensure successful authentication.
3. Schedule imports or manually trigger imports using the provided actions.
4. Monitor import job status and logs for any errors or warnings.

Example of Household Data JSON Formatter:

\[Example JSON formatter configuration]

`{ "name":.enumerator_details.data_enumerator_name, "region":.enumerator_details.region, "hh_history_with_relief_pro": .household_info.household_history, "no_of_pregnant_women": .household_info.no_of_visibly_pregnant, "no_of_breastfeeding_women": .household_info.no_of_breastfeeding_women, "no_of_younger_children": .household_info.no_of_children, "no_of_malnourished_children": .household_info.no_of_malnourished_childrens, "no_of_chronically_ill_individuals": .household_info.no_of_chronically_ill_individuals, "is_the_hh_head_disable": .household_info.head_persion_with_disability , "no_of_disable_hh_members": .household_info.no_of_pwd, "is_hh_head_above_60": .household_info.is_household_head_age_above_60 , "is_female_a_hh_head": .household_info.is_female_headed_household, "is_child_a_hh_head": .household_info.is_child_headed_household, "is_the_hh_under_the_status_of_IDP": .household_info.is_household_under_status_of_idp, "is_the_hh_a_returnee_hh": .household_info.household_returnee, "condition_of_constructed_house": .household_info.house_constructed, "no_of_rooms_rented_out": .household_info.no_of_rooms_rented_in_house, "no_of_rooms_rented_in_by_hh": .household_info.no_of_rooms_in_house, "transport_related_costs": .household_info.transport_related_costs, "size_of_owned_farmland": .household_info.size_of_farmland_owned_by_household, "size_of_rented_farmland": .household_info.size_of_farmland_rented_or_ploughed, "no_of_hh_members_engaged_in_mining": .household_info.no_of_members_engaged_in_mining, "hh_involved_in_other_natural_sources_of_income": .household_info.income_generating_activities, "no_of_ox_owned_by_hh": .household_info.no_of_oxen_owned, "no_of_cattle_owned_by_hh": .household_info.no_of_cattle_owned, "no_of_ship_or_goats_owned_by_hh": .household_info.no_of_sheep_or_goats_owned, "no_of_camels_owned_by_hh": .household_info.no_of_camels_or_equine_owned, "no_of_chickens_owned_by_hh": .household_info.no_of_chickens_owned, "is_hh_involved_in_any_trade": .household_info.is_involved_in_trade, "no_of_beehives_owned_by_hh": .household_info.no_of_beehives_owned, "hh_own_a_three_leg_motor_bike": .household_info.own_bike_three_leg, "hh_own_a_two_leg_motor_bike": .household_info.own_bike_two_leg, "hh_earn_from_renting_construction_tools": .household_info.earn_from_renting_tool, "hh_own_cart": .household_info.own_cart, "hh_have_a_member_living_abroad": .household_info.member_living_abroad, "hh_have_a_member_living_in_urban_and_provides_finanical_support": .household_info.member_living_in_city, "involved_in_any_manufacturing_activity": .household_info.involved_in_manufacturing_activities, "sum_amount_of_liquid_cash": .household_info.total_asset, "hh_qualify_for_loan": .household_info.qualify_for_loan_or_credit, "no_of_unskilled_members": .household_info.no_of_able_men_educated_or_skilled, "no_of_skilled_members": .household_info.no_of_able_female_or_men_educated_or_skilled, "how_long_the_hh_use_the_inkind_assistance": .household_info.assistance_recieved_in_last_three_years, "group_membership_ids": .household_info.household_members }`

### Error codes

NA

### Source code

[https://github.com/OpenG2P/openg2p-importers/tree/17.0-develop/g2p\_odk\_importer](https://github.com/OpenG2P/openg2p-importers/tree/17.0-develop/g2p\_odk\_importer)

### Installation

Standard odoo package installation

###
