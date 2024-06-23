---
description: WORK IN PROGRESS
---

# Fayda ID Integration

{% @jira/embed url="https://openg2p.atlassian.net/browse/OE-133" %}

## **API-1: Fetch  Registration IDs**

**Route**: `/get/rids`

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

**Route**: `/update/partner`

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
* `address`: (String) The physical address of the person.

**Example Request Body**:

```json
[
  {
    "registrationId": "INID123456",
    "faydaId": [
      {
        "id_type": "fayda",
        "value": "A12345678"
      }
    ],
    "name": "John Doe",
    "birthdate": "1990-01-01",
    "birth_place": "New York",
    "email": "johndoe@example.com",
    "address": "123 Main St, New York, NY 10001"
  }
]
```

**Response**:\
Example

```json
[
  {
    "faydaId": "A12345678",
    "registrationId": "INID123456",
    "status": "Success",
    "message": "Partner data's updated successfully"
  }
]
```

* Returns an array of objects indicating the status of each update.



