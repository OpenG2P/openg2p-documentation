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

# Individual APIs

OpenG2P Social Registry APIs are CRUD APIs that allow the end-user to create, read, and update the Individual registry data.

The Individual APIs contain the following CRUD operations.

* **Create**: Allows the creation of a new individual entity.
* **Read**: Enables the fetching of details about an individual entity.
* **Update**: Supports modifying existing individual entities.

{% hint style="danger" %}
Delete API is not supported. Contact the Administrator to delete an individual registrant.
{% endhint %}

The endpoints of Individual APIs and their definitions are given below.

<table><thead><tr><th width="111">Method</th><th width="225">API End Point</th><th>API Functionality</th></tr></thead><tbody><tr><td>POST</td><td>/registry/individual</td><td>This endpoint allows the end-user to create a new individual.</td></tr><tr><td>GET</td><td>/registry/individual/{_id}</td><td>This endpoint allows the end-user to retrieve the partner's information by a specific ID.</td></tr><tr><td>GET</td><td>/registry/individual</td><td>This endpoint allows the end-user to search the individual based on a specific ID or name.</td></tr></tbody></table>

{% hint style="danger" %}
The API request and response values used in the below sections are only an example for understanding. Do not use the example values in an API call.
{% endhint %}

## Authentication

The Individual APIs use a session-based authentication mechanism provided by Odoo. This involves initiating a session using login credentials. The end-user must authenticate by calling the `/web/session/authenticate` endpoint with the appropriate parameters in the request body. Successfully authenticated sessions generate a session ID, which is then used to authenticate subsequent API requests.

Subsequent API requests must include the session ID in the header to maintain the authenticated session.

### Session authentication endpoint

| Name   | Value                                           |
| ------ | ----------------------------------------------- |
| Method | GET                                             |
| URL    | \<openg2p.sandbox.net>/web/session/authenticate |

### Body parameters

| Parameter Name | Description                          | Mandatory/Optional | Data Type |
| -------------- | ------------------------------------ | ------------------ | --------- |
| jsonrpc        | The version of the JSON-RPC protocol | Mandatory          | String    |
| db             | The name of the database             | Mandatory          | String    |
| login          | The user's login name                | Mandatory          | String    |
| password       | The user's password                  | Mandatory          | String    |

### **Sample cURL request**

```
curl --location --request GET '<openg2p.sandox.net>/web/session/authenticate' \
--header 'Content-Type: application/json' \
--header 'Cookie: frontend_lang=en_US; session_id=c7b75ddb25f94ced204b78e6d7ea115c4a7c0f7e' \
--data '{
    "jsonrpc": "2.0", 
    "params": {
        "db": <db-name>, 
        "login": <login>, 
        "password": <password>
    }
}
'
```

### Sample request

```json
{
    "jsonrpc": "2.0", 
    "params": {
        "db": <db-name>, 
        "login": <login>, 
        "password": <password>
    }
}
```



## Create individual registry

This endpoint allows the end-user to create a new individual.

### Key request parameters

| Name   | Value                                              |
| ------ | -------------------------------------------------- |
| Method | `POST`                                             |
| URI    | `<openg2p.sandbox.net>/api/v1/registry/individual` |
| Cookie | session\_id=\<session\_id>                         |

### Request body parameters

<table><thead><tr><th width="177">Parameter Name</th><th width="205">Description</th><th width="187">Mandatory/Optional</th><th>Data Type</th></tr></thead><tbody><tr><td>name </td><td>The name of an individual</td><td>Mandatory</td><td>String</td></tr><tr><td>id_type</td><td>The type of the ID</td><td>Mandatory</td><td>String</td></tr><tr><td>value</td><td>The value of the ID</td><td>Mandatory</td><td>String</td></tr><tr><td>expiry_date</td><td>The date of expiry of an individual registry</td><td>Mandatory</td><td><p>Date </p><p>Format: YYYY-MM-DD</p></td></tr><tr><td>registration_date</td><td>The date of an individual registration</td><td>Optional</td><td><p>Date </p><p>Format: YYYY-MM-DD</p></td></tr><tr><td>phone_no</td><td>The contact number of an individual </td><td>Mandatory</td><td>String</td></tr><tr><td>date_collected</td><td>The date on which an individual data is collected</td><td>Optional</td><td>String</td></tr><tr><td>email</td><td>The email ID of an individual</td><td>Optional</td><td>String</td></tr><tr><td>address</td><td>The address of an individual</td><td>Optional</td><td>String</td></tr><tr><td>bank_name</td><td>The bank name of an individual</td><td>Optional </td><td>String</td></tr><tr><td>acc_number</td><td>The account number of an individual</td><td>Optional</td><td>String</td></tr><tr><td>given_name</td><td>The given name of an individual</td><td>Mandatory</td><td>String</td></tr><tr><td>addl_name</td><td>The additional name of an individual</td><td>Mandatory</td><td>String</td></tr><tr><td>family_name</td><td>The family name of an individual</td><td>Mandatory</td><td>String</td></tr><tr><td>gender</td><td>The gender of an individual</td><td>Mandatory</td><td>String</td></tr><tr><td>birthdate</td><td>The date of birth of an individual</td><td>Mandatory</td><td><p>Date </p><p>Format: YYYY-MM-DD</p></td></tr><tr><td>birth_place</td><td>The place of birth of an individual</td><td>Mandatory</td><td><p>Date </p><p>Format: YYYY-MM-DD</p></td></tr><tr><td>is_group</td><td>It defines whether the individual belongs to a group or not</td><td>Mandatory</td><td><p>Boolean </p><p>True </p><p>False</p><p></p><p>Note: </p><p>The default values is false.</p></td></tr></tbody></table>

### **Sample cURL request**

```
curl --request POST
--url https://openg2p.stoplight.io/api/v1/registry/individual/
--header 'Accept: application/json'
--header 'Accept-Language: '
--header 'Content-Type: application/json'
--header 'Cookie: session_id=<session_id>'
--data '{ "name": "string", "ids": [ { "id_type": "string", "value": "string", "expiry_date": "2019-08-24" } ], "registration_date": "2019-08-24", "phone_numbers": [ { "phone_no": "string", "date_collected": "2019-08-24" } ], "email": "string", "address": "string", "bank_ids": [ { "bank_name": "string", "acc_number": "string" } ], "given_name": "string", "addl_name": "string", "family_name": "string", "gender": "string", "birthdate": "2019-08-24", "birth_place": "string", "is_group": false }'
```

### Sample request

<pre class="language-json"><code class="lang-json"><strong>{ 
</strong><strong> "name": "string",
</strong><strong>  "ids": [ { "id_type": "string", 
</strong><strong>             "value": "string",
</strong><strong>             "expiry_date": "2019-08-24" } ],
</strong><strong>  "registration_date": "2019-08-24",
</strong><strong>  "phone_numbers": [ { "phone_no": "string",
</strong><strong>                       "date_collected": "2019-08-24" } ],
</strong><strong>  "email": "string",
</strong><strong>  "address": "string",
</strong><strong>  "bank_ids": [ { "bank_name": "string",
</strong><strong>                  "acc_number": "string" } ],
</strong><strong>  "given_name": "string",
</strong><strong>  "addl_name": "string",
</strong><strong>  "family_name": "string",
</strong><strong>  "gender": "string",
</strong><strong>  "birthdate": "2019-08-24",
</strong><strong>  "birth_place": "string",
</strong><strong>  "is_group": false
</strong><strong>  }
</strong></code></pre>

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
  "is_group": false,
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
  "given_name": "string",
  "addl_name": "string",
  "family_name": "string",
  "gender": "string",
  "birthdate": "2019-08-24",
  "age": "string",
  "birth_place": "string"
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

## Get individual registry

This endpoint allows the end-user to retrieve the individual registry data based on a specific ID.

### Key request parameters

| Name   | Value                                                    |
| ------ | -------------------------------------------------------- |
| Method | `GET`                                                    |
| URI    | `<openg2p.sandbox.net>/api/v1/registry/individual/{_id}` |
| Cookie | session\_id=\<session\_id>                               |



<table><thead><tr><th width="177">Parameter Name</th><th width="205">Description</th><th width="217">Mandatory/Optional</th><th>Data Type</th></tr></thead><tbody><tr><td>id</td><td>The ID of an individual</td><td>Mandatory</td><td><p>Number </p><p>Example: 124567</p></td></tr></tbody></table>

### **Sample cURL request**

```
curl --request GET
--url https://openg2p.stoplight.io/api/v1/registry/group/_id
--header 'Accept: application/json'
--header 'Accept-Language: '
--header 'Cookie: session_id=<session_id>'
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
  "is_group": false,
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
  "given_name": "string",
  "addl_name": "string",
  "family_name": "string",
  "gender": "string",
  "birthdate": "2019-08-24",
  "age": "string",
  "birth_place": "string"
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

## Search individual registry

This endpoint allows the end-user to search the individuals based on a specific ID or name.

### Key request parameters

| Name   | Value                                                                                                                                                                      |
| ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Method | `GET`                                                                                                                                                                      |
| URI    | <p><code>&#x3C;openg2p.sandbox.net>/api/v1/registry/individual/{_id}</code></p><p>(or)</p><p><code>&#x3C;openg2p.sandbox.net>/api/v1/registry/individual/{name}</code></p> |
| Cookie | session\_id=\<session\_id>                                                                                                                                                 |

<table><thead><tr><th width="177">Parameter Name</th><th width="205">Description</th><th width="217">Mandatory/Optional</th><th>Data Type</th></tr></thead><tbody><tr><td>id</td><td>The ID of an individual</td><td>Optional</td><td><p>Number </p><p>Example: 4356789</p></td></tr><tr><td>name</td><td>The name of an individual</td><td>Optional</td><td><p>String </p><p>Example: John Miller</p></td></tr></tbody></table>

### **Sample cURL request**

```
curl --request GET
--url https://openg2p.stoplight.io/api/v1/registry/individual
--header 'Accept: application/json'
--header 'Accept-Language: '
--header 'Cookie: session_id=<session_id>'
```

### **Sample response**

{% tabs %}
{% tab title="200" %}
Successful response

```json
[
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
    "is_group": false,
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
    "given_name": "string",
    "addl_name": "string",
    "family_name": "string",
    "gender": "string",
    "birthdate": "2019-08-24",
    "age": "string",
    "birth_place": "string"
  }
]
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

## API specification

The Individual APIs are available in Stoplight at the following link.

[openg2p-crud-apis](https://openg2p.stoplight.io/docs/openg2p-social-registry/branches/main/m2g8egugf4nrf-open-g2-p-crud-ap-is)
