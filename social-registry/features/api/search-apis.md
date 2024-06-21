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

# Search APIs

The Search APIs have implemented the [G2P Connect Registry Core APIs](https://g2p-connect.github.io/specs/release/html/registry\_core\_api\_v1.0.0.html) specification. These APIs are designed to offer comprehensive searching capabilities across individual and group registries. It utilizes advanced query options for precise results. The API facilitates querying across all Social Registry (SR) registrants. It leverages **GraphQL** to handle complex queries efficiently. It retrieves only the requisite data for a specific query.

## Authentication

OpenG2P Social Registry Search API is secured by OAuth 2.0. It uses Client Credentials Grant Type, i.e., Client ID and Secret to allow the end-user to access the Social Registry database.

### Key request parameters - authorization

Once you receive the Client ID and Secret, the next step is to call OAuth 2.0 endpoint to authenticate.

The key parameters are:

<table><thead><tr><th width="380">Name</th><th>Value</th></tr></thead><tbody><tr><td>Method</td><td><code>POST</code></td></tr><tr><td>Authorization type</td><td>Bearer Token</td></tr><tr><td>Auth URI</td><td>http://keycloak.keycloak/realms/openg2p/protocol/openid-connect/token</td></tr></tbody></table>

### Body request parameters

| Name           | Value                  |
| -------------- | ---------------------- |
| client\_id     | \<client\_id>          |
| client\_secret | \<client\_secret>      |
| grant\_type    | \<client\_credentials> |

### Sample cURL request

<pre><code><strong>curl --location 'https://keycloak.keycloak/realms/openg2p/protocol/openid-connect/token'
</strong>--header 'Content-Type: application/x-www-form-urlencoded'
--data-urlencode 'client_id=&#x3C;client_id>'
--data-urlencode 'client_secret=&#x3C;client_secret>'
--data-urlencode 'grant_type=client_credentials'
</code></pre>

On receiving the request, OpenG2P authorization system validates the parameters in the request. If the parameters are valid, it generates your access token and returns it in the response.

### Sample response

```json
{
    "access_token": "",
    "expires_in": 0,
    "refresh_expires_in": 0,
    "token_type": "",
    "not-before-policy": 0,
    "scope": ""
}
```

### HTTP status code

<table><thead><tr><th width="145">HTTP Code</th><th>Description</th></tr></thead><tbody><tr><td>200</td><td>The API call is successful.</td></tr><tr><td>400</td><td>Bad Request. The request is invalid, usually due to missing or incorrect parameters.</td></tr><tr><td>401</td><td>Unauthorized.  Authentication failed due to an invalid Client ID or Secret.</td></tr></tbody></table>

## Query type

The `search api` utilizes **GraphQL** query parameters. The query parameter enhances the search efficiency and eases the data retrieval.  You must consider the following parameters when crafting a GraphQL query parameters.

• **Query Filters:** When sending a request, you can define specific criteria to filter the data. You can filter based on various parameters such as age, location, or status of the registrants in the SR.

• **Fields Selection**: GraphQL allows you to specify the fields you need to receive in response based on your query. This means you can tailor the response to include only the relevant data that fulfills your needs. This makes the API response more lightweight and accurate.

• **Pagination Parameters**: For queries that return large data, it is mandatory to break into several pages through pagination. GraphQL uses the query parameter to set the limit to return the number of records per page.

• **Sort Order**: You can specify the order to organize the data that you need to receive in response. You can sort ascending or descending based on a specific field.

**Sample GraphQL query**

```graphql
{
  getregistrants(address: "New York", age_gte: 18, sort: "name_ASC", limit: 10) {
    name,
    age,
    gender,
    address
  }
}
```

For example, the query returns the name, age, gender, and address of the first 10 registrants of age >=18 years, residing in New York, and the names are sorted in ascending order.

## API specification

The Search APIs are available in Stoplight at the following link

[openg2p-social-registry-search-apis](https://openg2p.stoplight.io/docs/openg2p-social-registry/branches/main/yh3dm5ylwbwq7-g2-p-connect-registry-sync)
