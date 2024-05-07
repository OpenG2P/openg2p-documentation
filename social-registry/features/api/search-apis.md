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

The search APIs has implemented the [G2P Connect Registry Core APIs](https://g2p-connect.github.io/specs/release/html/registry\_core\_api\_v1.0.0.html) specification. These APIs are designed to offer comprehensive searching capabilities across the registry, utilizing advanced query options for precise results. The API facilitates querying across all registrants within the social registry. It leverages **GraphQL** to handle complex queries efficiently, ensuring that only the requisite data for a specific query is retrieved.

## Query Type

The `search api` utilizes **GraphQL** for its queries, significantly enhancing the efficiency and flexibility of data retrieval. When crafting a GraphQL query for the API, you must consider the following parameters:

* **Query Filters**: Define specific criteria to filter the data you are requesting. These filters can be based on various attributes of the registrants in the social registry, such as age, location, or status.
* **Fields Selection**: GraphQL allows you to specify exactly which fields of data you wish to receive in response to your query. This means you can tailor the response to include only the data that is relevant to your needs, making the API response more lightweight and focused.
* **Pagination Parameters**: For queries that could return large datasets, it's essential to implement pagination. GraphQL supports pagination parameter like `limit` (the number of records to return).
* **Sort Order**: You can specify the order in which you want the records to be returned, such as ascending or descending based on a specific field.

**Example GraphQL Query:**

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

This example query would return the `name`, `age`, `gender` and `address` of the first 10 registrants who are 18 years or older and located in New York, sorted by their name in ascending order.

APIs are available in Stoplight at the following links

[openg2p-social-registry-search-apis](https://openg2p.stoplight.io/docs/openg2p-social-registry/branches/main/yh3dm5ylwbwq7-g2-p-connect-registry-sync)
