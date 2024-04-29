# Beneficiary Registry Configurations

## Introduction

OpenG2P platform provides configurations to define values (enumerations) for a field. These fields are related to the registrant's identity and association with other registrants. Once defined, these values are available for selection in a dropdown list for that field. This is the list of currently available configurations:

### ID Types

ID Type is a reference name given by the OpenG2P platform user to refer to a registrant identity such as driver's license, MOSIP ID, Aadhar, etc. Users can define multiple ID Types. Once defined, users can select the ID Type from a dropdown list. Each registrant's ID Type has an ID Number (identifier) associated with it. Therefore, ID Type is also used by the[ ID Deduplication Manager](../../../features/deduplication/user-guides/create-deduplication-manager-types/create-id-deduplication-manager.md) to select the ID Type for deduplicating registrants.

### Registrant Tags

Registrant tags are used to define the categories for Individuals and groups such as indigenous, solo parents, minors, unemployed, disabled, mentally challenged, etc. These tags can be used by the Eligibility Manager to enroll registrants for targeted programs.

### District Configuration

The District configuration is typically used to define a particular place within a state or country. Districts can be configured according to the county's requirements. The configured district will appear as a drop-down menu when selecting the district for any registrant.

### Gender Types

Gender types are used to define the gender of individuals and members in groups. Users can create gender types from the configurations, which will appear as a drop-down menu for selecting the gender type. This allows for easy categorization and identification of individuals and group members based on their gender.

### Relationships

Relationship is used to record the relation between registrants such as father and son, mother and daughter, and village head and villagers. Relationships can be established between individuals and groups. Some common examples are:

* Individual<>Individual: Father<>Son, Mother<>Daughter, etc.
* Individual<>Group: Village head<>Villagers, Social worker<>Group of beneficiaries, etc.
* Group<>Individual: School<>Principal, Children<>Mother, etc.
* Group<>Group: Class<>School, Schools<>Districts, etc.

OpenG2P platform provides options for directionality in relationships, i.e. bi-directional or uni-directional based on context. Some examples are:

* The father can authenticate the minor child, but the minor child cannot authenticate the father.
* A representative from a group of beneficiaries can receive benefits on behalf of a beneficiary, but the beneficiary cannot receive benefits on behalf of the representative.

The exact interpretation of relationships can vary according to the context and environment of the social protection program. OpenG2P provides all the necessary configurations to the Program Administrator to define complex relationships.

### Group Types

Group Types define the association among a group of registrants. Some common examples of Group Types are family, household, village, and company.

### Group Membership Kind

The Group Membership Kind establishes the role of an individual in a group. For example, the individual could be a member or head of the group. This field is especially useful for programs that disburse the benefits to only the head of the group but also record the list of other members in the group.

## Related user guides

:notebook\_with\_decorative\_cover:[Configuration](user-guides/configuration/)

