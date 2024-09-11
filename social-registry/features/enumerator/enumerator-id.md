# Enumerator ID

Enumerators are created in the Social Registry (SR) using the Registration Portal. Enumerators are field employees or agents who assist in gathering information from registrants/applicants. Each time an Enumerator is added to the Registration Portal, a unique ID is automatically generated and assigned to them. The assigned ID is the Enumerator ID (EID) which serves as a unique identifier for each enumerator in the SR.

The Data Administrator and the System Administrator have the authority to create Enumerators in SR using the Registration Portal.

## Purpose of EID

The EID plays a significant role such as

* The EID distinguishes each Enumerator within the SR, enabling efficient tracking and managing of data collected by different Enumerators.

## Characteristics of EID

* Each Enumerator has a unique EID.
* The EID is generated using a sequencer on the Odoo platform. It has a 5-digit sequence with a configurable prefix. For example, it could be formatted as `EID-00001`.
* Since EID is a read-only attribute throughout the system, it cannot be changed, once they are generated.
* The admin portal allows for the deactivation of Enumerators, but not the deletion of EID.

## Appearance of EID

* The EID is displayed in the user profile of the Enumerators that is saved in the Registration Portal of SR.
* Every record that the Enumerator collects has their EID in the Enumerator information section.

## Technical concept

### EID generation process

#### **EID field definition**

The EID field is defined as a Char field on the partner model with the following attributes:

* string='EID': Displays the field label as "EID."&#x20;
* copy=False: Prevents the EID from being duplicated when a partner record is copied.&#x20;
* readonly=True: Ensures the EID cannot be manually edited, maintaining its integrity.&#x20;
* index=True: Optimizes database queries for searches involving EIDs.

#### **Automatic EID generation**

* When a new enumerator is created, the create method of the G2PRegistrant model checks if an EID is provided. If not, the EID is temporarily set to 'New.'
* After the record is created, the create method calls the generate\_eid method to automatically generate and assign the next unique EID.

#### **EID sequence configuration**

The generate\_eid method utilises an Odoo sequence named 'Enumerator Code' to generate EIDs. This sequence is configured as follows:

* code: enumeratorCode.
* prefix: EID-.
* padding: 5.

This configuration ensures that each EID starts with "EID-" followed by a 5-digit padded number, for example, EID-00025.

#### **EID  view integration**

* The EID field is integrated into relevant views (form/tree view), providing a clear and readily accessible display of the Enumerator's unique identifier.&#x20;

## Development phase

The following deliverables for the Enumerator module are planned for development and release at the appropriate phase.

<table><thead><tr><th width="117">Phase</th><th>Deliverable</th><th>Status</th></tr></thead><tbody><tr><td>Phase 2</td><td><ul><li>Enumerators use their EID to log in to Registration Portal.</li><li>In SR, Data Administrator able to search Enumerator by their EID.</li></ul></td><td></td></tr></tbody></table>
