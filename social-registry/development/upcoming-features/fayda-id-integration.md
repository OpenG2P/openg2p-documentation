---
description: WORK IN PROGRESS
---

# Fayda ID Integration

{% @jira/embed url="https://openg2p.atlassian.net/browse/OE-133" %}

## **API-1: Fetch  Registration IDs**

**Route**: `/get_ids`

**Method**: GET

**Description**: This API fetches  all the registrant RID

**Request Parameters**:

* `id_type`: (String) The type of ID to fetch.

**Response**:

```json
[
  "INID123456",
  "INID134567",
  "125",
  "grp12345"
]
```

* Returns an array of registration IDs.



## **API-2: Update Registration Information in Social Registry**

**Route**: `/update_individual`

**Method**: PUT

**Description**: This API updates the registrant information using registration IDs.

**Request Parameters**:

* `registrationId`: (String) The registration ID to update.
* `faydaId`: (Array) An array of objects with the following fields:
  * `id_type`: (String) The type of the ID. For example, "fayda".
  * `value`: (String) The ID value.
* `name`: (String) The name of the person.
* `birthdate`: (String) The birthdate of the person in `YYYY-MM-DD` format.
* `birth_place`: (String) The birthplace of the person.
* `email`: (String) The email address of the person.
* gender: (String) The physical address of the person.
* is\_group: (String) The physical address of the person.
* image\_1920: (String) The physical address of the person.

**Example Request Body**:

```json
[
  {
    "updateId": "INID123456",
    "name": "Jacop",
    "ids": [
      {
        "id_type": "Fayda",
        "value": "123456789",
         "expiry_date": "2024-10-10"
      }
    ],
    "registration_date": "2024-06-24",
    "phone_numbers": [
      {
        "phone_no": "+919876543210",
        "date_collected": "2024-06-23"
      }
    ],
    "email": "Jacop.email@example.com",
    "address": "Jacop Address",
    "given_name": "Jacop Given Name",
    "addl_name": "Jacop Additional Name",
    "family_name": "Jacop Family Name",
    "gender": "Male",
    "birthdate": "1990-01-01",
    "birth_place": "Jacop Birth Place",
    "is_group": false,
    "image_1920":"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"
  }
]
```

**Response**:\
Example

```json
[
  {
    "id": 71,
    "name": "test",
    "reg_ids": [
      {
        "id": 70,
        "id_type_as_str": "fayda",
        "value": "123456789",
        "expiry_date": "2024-10-10"
      },
      {
        "id": 5,
        "id_type_as_str": "new",
        "value": "INID123456",
        "expiry_date": "2024-06-25"
      }
    ],
    "is_group": false,
    "registration_date": "2024-06-23",
    "phone_number_ids": [
      {
        "id": 56,
        "phone_no": "+919876543210",
        "phone_sanitized": "+919876543210",
        "date_collected": "2024-06-23"
      },
    
    ],
    "email": null,
    "address": null,
    "create_date": "2024-06-18T13:54:00.631383",
    "write_date": "2024-06-24T10:51:13.943845",
    "given_name": "Test",
    "addl_name": null,
    "family_name": "Test Family Name",
    "gender": null,
    "birthdate": null,
    "age": "34",
    "birth_place": null
  }
]
```

* Returns an array of objects indicating the status of each update.



