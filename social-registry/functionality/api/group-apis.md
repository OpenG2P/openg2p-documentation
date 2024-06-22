---
layout:
  title:
    visible: true
  description:
    visible: false
  tableOfContents:
    visible: true
  outline:
    visible: true
  pagination:
    visible: true
---

# Group APIs

OpenG2P Social Registry APIs are CRUD APIs that allow the end-user to create, read, and update the group registry data.

The Group APIs contain the following CRUD operations.

* **Create**: Allows the creation of a new group entity.
* **Read**: Enables the fetching of details about a group entity.
* **Update**: Supports modifying existing group entities.

{% hint style="danger" %}
Delete API is not supported. Contact the Administrator to delete a group registrant.
{% endhint %}

The endpoints of Group APIs and their definitions are given below.

<table><thead><tr><th width="111">Method</th><th width="225">API End Point</th><th>API Functionality</th></tr></thead><tbody><tr><td>POST</td><td>/registry/group</td><td>This endpoint allows the end-user to create a new group.</td></tr><tr><td>GET</td><td>/registry/group/{_id}</td><td>This endpoint allows the end-user to retrieve the partner's information by a specific ID.</td></tr><tr><td>GET</td><td>/registry/group</td><td>This endpoint allows the end-user to search the group based on a specific ID or name.</td></tr></tbody></table>

{% hint style="danger" %}
The API request and response values used in the below sections are only an example for understanding. Do not use the example values in an API call.
{% endhint %}

## Authentication

A basic authentication mechanism secures OpenG2P Social Registry CRUD API.  It uses login credentials, i.e., User name and Password to allow the end-user to access the Social Registry database.

### Key request parameters - basic authentication

| Name     | Value                  |
| -------- | ---------------------- |
| URL      | \<openg2p.sandbox.net> |
| UserName | \*\*\*\*\*\*\*         |
| Password | \*\*\*\*\*\*\*         |

## Create group registry

This endpoint allows the end-user to create a new group.

### Key request parameters

| Name   | Value                                         |
| ------ | --------------------------------------------- |
| Method | `POST`                                        |
| URI    | `<openg2p.sandbox.net>/api/v1/registry/group` |

### Body parameters

<table><thead><tr><th width="177">Parameter Name</th><th width="205">Description</th><th width="187">Mandatory/Optional</th><th>Data Type</th></tr></thead><tbody><tr><td>name </td><td>The name of a group</td><td>Mandatory</td><td>String</td></tr><tr><td>ids</td><td>It contains the list of ID details of a group</td><td></td><td>array</td></tr><tr><td>id_type</td><td>The type of the ID of a group</td><td>Mandatory</td><td>String</td></tr><tr><td>value</td><td>The value of the ID of a group</td><td>Mandatory</td><td>String</td></tr><tr><td>expiry_date</td><td>The date of expiry of a group registry</td><td>Mandatory</td><td><p>Date </p><p>Format: YYYY-MM-DD</p></td></tr><tr><td>registration_date</td><td>The date on which a group is registered</td><td>Optional</td><td><p>Date </p><p>Format: YYYY-MM-DD</p></td></tr><tr><td>phone_numbers</td><td>It contains the list of contact details of a group</td><td></td><td>array</td></tr><tr><td>phone_no</td><td>The contact number of a group</td><td>Mandatory</td><td>String</td></tr><tr><td>date_collected</td><td>The date on which a group data is collected</td><td>Optional</td><td>String</td></tr><tr><td>email</td><td>The email ID of a group</td><td>Optional</td><td>String</td></tr><tr><td>address</td><td>The address of a group</td><td>Optional</td><td>String</td></tr><tr><td>bank_ids</td><td>It contains the list of bank details of a group</td><td></td><td>array</td></tr><tr><td>bank_name</td><td>The bank name of a group</td><td>Optional </td><td>String</td></tr><tr><td>acc_number</td><td>The account number of a group</td><td>Optional</td><td>String</td></tr><tr><td>is_group</td><td>It defines whether the member belongs to group or not</td><td>Mandatory</td><td><p>Boolean </p><p>True </p><p>False </p><p></p><p>Note: </p><p>The default values is true.</p></td></tr><tr><td>members</td><td>It contains the details of a member belongs to a group</td><td></td><td>array</td></tr><tr><td>name</td><td>The name of a member</td><td>Mandatory</td><td>String</td></tr><tr><td>given_name</td><td>The given name of a member</td><td>Optional</td><td>String</td></tr><tr><td>addl_name</td><td>The additional name of a member</td><td>Optional</td><td>String</td></tr><tr><td>family_name</td><td>The family name of a member</td><td>Optional</td><td>String</td></tr><tr><td>ids</td><td>It contains the ID details of a member belongs to a group</td><td></td><td>array</td></tr><tr><td>id_type</td><td>The type of the ID of a member</td><td>Mandatory</td><td>String</td></tr><tr><td>value</td><td>The value of the ID of a member</td><td>Mandatory</td><td>String</td></tr><tr><td>expiry_date</td><td>The date of expiry of a member registry</td><td>Mandatory</td><td><p>Date </p><p>Format: YYYY-MM-DD</p></td></tr><tr><td>registration_date</td><td>The registration date of a member</td><td>Optional</td><td><p>Date </p><p>Format: YYYY-MM-DD</p></td></tr><tr><td>phone_numbers</td><td>It contains the contact details of a member</td><td></td><td>array</td></tr><tr><td>email</td><td>The email id of a member</td><td>Mandatory</td><td></td></tr><tr><td>address</td><td>The address of a member</td><td>Mandatory</td><td></td></tr><tr><td>gender</td><td>The gender of a member</td><td>Mandatory</td><td>String</td></tr><tr><td>birthdate</td><td>The date of birth of a member</td><td>Mandatory</td><td><p>Date </p><p>Format: YYYY-MM-DD</p></td></tr><tr><td>birth_place</td><td>The place of birth of a member</td><td>Mandatory</td><td><p>Date </p><p>Format: YYYY-MM-DD</p></td></tr><tr><td>is_group</td><td>It defines whether the member belongs to group or not</td><td>Optional</td><td><p>Boolean </p><p>True </p><p>False </p><p></p><p>Note: </p><p>The default values is true.</p></td></tr><tr><td>kind</td><td>It contains list of the name of the kind allocated to a member</td><td></td><td>array</td></tr><tr><td>name</td><td>The name of the kind allocated to a member</td><td>Mandatory</td><td>String</td></tr><tr><td>bank_ids</td><td>It contains the list of bank details of a member</td><td></td><td>array</td></tr><tr><td>bank_name</td><td>The bank name of a member</td><td>Optional</td><td>String</td></tr><tr><td>acc_number</td><td>The account number of a member</td><td>Optional</td><td>String</td></tr><tr><td>kind</td><td>It contains the name of the kind allocated to a group</td><td>Mandatory</td><td></td></tr><tr><td>is_partial_group</td><td></td><td>Mandatory</td><td></td></tr></tbody></table>

### **Sample cURL request**

```
curl --request POST
--url https://openg2p.stoplight.io/api/v1/registry/group/
--header 'Accept: application/json'
--header 'Accept-Language: '
--header 'Content-Type: application/json'
--data '{ "name": "string", "ids": [ { "id_type": "string", "value": "string", "expiry_date": "2019-08-24" } ], "registration_date": "2019-08-24", "phone_numbers": [ { "phone_no": "string", "date_collected": "2019-08-24" } ], "email": "string", "address": "string", "bank_ids": [ { "bank_name": "string", "acc_number": "string" } ], "is_group": true, "members": [ { "name": "string", "given_name": "string", "addl_name": "string", "family_name": "string", "ids": [ { "id_type": "string", "value": "string", "expiry_date": "2019-08-24" } ], "registration_date": "2019-08-24", "phone_numbers": [ { "phone_no": "string", "date_collected": "2019-08-24" } ], "email": "string", "address": "string", "gender": "string", "birthdate": "2019-08-24", "birth_place": "string", "is_group": false, "kind": [ { "name": "string" } ], "bank_ids": [ { "bank_name": "string", "acc_number": "string" } ] } ], "kind": "string", "is_partial_group": true }'
```

### Sample request

```json
{
  "name": "string",
  "ids": [
    {
      "id_type": "string",
      "value": "string",
      "expiry_date": "2019-08-24"
    }
  ],
  "registration_date": "2019-08-24",
  "phone_numbers": [
    {
      "phone_no": "string",
      "date_collected": "2019-08-24"
    }
  ],
  "email": "string",
  "address": "string",
  "bank_ids": [
    {
      "bank_name": "string",
      "acc_number": "string"
    }
  ],
  "is_group": true,
  "members": [
    {
      "name": "string",
      "given_name": "string",
      "addl_name": "string",
      "family_name": "string",
      "ids": [
        {
          "id_type": "string",
          "value": "string",
          "expiry_date": "2019-08-24"
        }
      ],
      "registration_date": "2019-08-24",
      "phone_numbers": [
        {
          "phone_no": "string",
          "date_collected": "2019-08-24"
        }
      ],
      "email": "string",
      "address": "string",
      "gender": "string",
      "birthdate": "2019-08-24",
      "birth_place": "string",
      "is_group": false,
      "kind": [
        {
          "name": "string"
        }
      ],
      "bank_ids": [
        {
          "bank_name": "string",
          "acc_number": "string"
        }
      ]
    }
  ],
  "kind": "string",
  "is_partial_group": true
}
```

### **Sample response**

{% tabs %}
{% tab title="200" %}
Successful response

```json
{
  "id": 0,
  "name": "string",
  "reg_ids": [
    {
      "id": 0,
      "id_type_as_str": "string",
      "value": "string",
      "expiry_date": "2019-08-24"
    }
  ],
  "is_group": true,
  "registration_date": "2019-08-24",
  "phone_number_ids": [
    {
      "id": 0,
      "phone_no": "string",
      "phone_sanitized": "string",
      "date_collected": "2019-08-24"
    }
  ],
  "email": "string",
  "address": "string",
  "create_date": "2019-08-24T14:15:22Z",
  "write_date": "2019-08-24T14:15:22Z",
  "bank_ids": [
    {
      "bank_name": "string",
      "acc_number": "string"
    }
  ],
  "group_membership_ids": [],
  "is_partial_group": true
}
```
{% endtab %}

{% tab title="422" %}
Validation error

```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}
```
{% endtab %}
{% endtabs %}

## Get group registry

This endpoint allows the end-user to retrieve the group registry data based on a specific ID.

### Key request parameters

| Name   | Value                                               |
| ------ | --------------------------------------------------- |
| Method | `GET`                                               |
| URI    | `<openg2p.sandbox.net>/api/v1/registry/group/{_id}` |

<table><thead><tr><th width="177">Parameter Name</th><th width="205">Description</th><th width="217">Mandatory/Optional</th><th>Data Type</th></tr></thead><tbody><tr><td>id</td><td>The ID of a group</td><td>Mandatory</td><td><p>Number </p><p>Example: 124567</p></td></tr></tbody></table>

### **Sample cURL request**

```
curl --request GET
--url https://openg2p.stoplight.io/api/v1/registry/group/_id
--header 'Accept: application/json'
--header 'Accept-Language: '
```

### **Sample response**

{% tabs %}
{% tab title="200" %}
Successful response

```json
{
  "id": 0,
  "name": "string",
  "reg_ids": [
    {
      "id": 0,
      "id_type_as_str": "string",
      "value": "string",
      "expiry_date": "2019-08-24"
    }
  ],
  "is_group": true,
  "registration_date": "2019-08-24",
  "phone_number_ids": [
    {
      "id": 0,
      "phone_no": "string",
      "phone_sanitized": "string",
      "date_collected": "2019-08-24"
    }
  ],
  "email": "string",
  "address": "string",
  "create_date": "2019-08-24T14:15:22Z",
  "write_date": "2019-08-24T14:15:22Z",
  "bank_ids": [
    {
      "bank_name": "string",
      "acc_number": "string"
    }
  ],
  "group_membership_ids": [],
  "is_partial_group": true
}
```
{% endtab %}

{% tab title="422" %}
Validation error

```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}
```
{% endtab %}
{% endtabs %}

## Search group registry

This endpoint allows the end-user to search the group based on a specific ID or name.

### Key request parameters

| Name   | Value                                                                                                                                                            |
| ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Method | `GET`                                                                                                                                                            |
| URI    | <p><code>&#x3C;openg2p.sandbox.net>/api/v1/registry/group/{_id}</code></p><p>(or)</p><p><code>&#x3C;openg2p.sandbox.net>/api/v1/registry/group/{name}</code></p> |

<table><thead><tr><th width="177">Parameter Name</th><th width="205">Description</th><th width="217">Mandatory/Optional</th><th>Data Type</th></tr></thead><tbody><tr><td>id</td><td>The ID of the individual</td><td>Optional</td><td><p>Number </p><p>Example: 4356789</p></td></tr><tr><td>name</td><td>The name of the individual</td><td>Optional</td><td><p>String </p><p>Example: John Miller</p></td></tr></tbody></table>

### **Sample cURL request**

```
curl --request GET
--url https://openg2p.stoplight.io/api/v1/registry/group
--header 'Accept: application/json'
--header 'Accept-Language: '
```

### **Sample response**

{% tabs %}
{% tab title="200" %}
**\<WIP>**
{% endtab %}

{% tab title="422" %}
Validation error

```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}
```
{% endtab %}
{% endtabs %}

## API specification

The Group APIs are available in Stoplight at the following link.

[openg2p-crud-apis](https://openg2p.stoplight.io/docs/openg2p-social-registry/branches/main/m2g8egugf4nrf-open-g2-p-crud-ap-is)
