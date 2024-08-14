---
description: WORK IN PROGRESS
---

# Fayda ID Integration

## User stories

{% @jira/embed url="https://openg2p.atlassian.net/browse/OE-133" %}

In Social Registry (SR), the registrants' data are dynamically populated. There is a requirement to update the registrants' information with Fayda ID\* along with their Registration ID (RID).

## FaydaIDConnector

&#x20;The FaydaIDConnector component in the backend enables SR to retrieve and update Fayda IDs with their RIDs using APIs in the relevant registrants' data.

{% hint style="info" %}
\*Fayda ID is a 12-digit unique identification number issued by NIDP (National ID Program) of Ethiopia to residents who fulfill the required procedures put in place by NIDP digital identification number.
{% endhint %}

## Feature and functionality&#x20;

| Feature                                 | Functionality                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Automatic retrieval and synchronization | FayaIDConnector automatically retrieves data in sync with the Registration IDs.                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| APIs                                    | <ul><li>Initiates the periodic task that retrieves a list of Registration IDs that first authenticates with an <strong>OpenG2P API</strong><em>.</em>  </li><li>Uses the retrieved list of Registration IDs to call the <strong>Fayda Number API</strong> to get the data from <strong>Fayda API</strong>.</li><li>It updates the Fayda ID and additional information using the <strong>OpenG2P API</strong>.</li><li>At last, data from the response is processed and transformed to update the relevant records with Fayda ID in OpenG2P system.</li></ul> |
| Reliability and consistency             | The service's comprehensive **error handling**, **logging systems**, and **continuous operation** **design** ensure trustworthy and consistent data updates.                                                                                                                                                                                                                                                                                                                                                                                                 |
| Maintenance                             | FaydaIDConnector is an essential component of maintaining current registration information  by automating these processes and enhancing data accuracy and operational efficiency.                                                                                                                                                                                                                                                                                                                                                                            |

## Source code

* [https://github.com/OpenG2P/openg2p-eth-nidp](https://github.com/OpenG2P/openg2p-eth-nidp)
* [https://github.com/OpenG2P/openg2p-registry/tree/15.0-develop/g2p\_registry\_rest\_api](https://github.com/OpenG2P/openg2p-registry/tree/15.0-develop/g2p\_registry\_rest\_api)

## **Error handling**&#x20;

* **HTTP Errors**: Handling and logging of HTTP errors during API calls.
* **General Exceptions**: Logging and raising exceptions in the `job_runner` method.

## &#x20;**Logging**&#x20;

The logs are captured in different levels. The various levels and their purposes are given below.

<table><thead><tr><th width="132">Logs</th><th>Purpose</th></tr></thead><tbody><tr><td>Info</td><td>Info log level indicates that something happened, causing the application to enter a certain state. For example, an Info log level in the authorisation API holds information about the user requesting authorisation and whether or not it was approved.</td></tr><tr><td>Debug</td><td>Debug log level provides details on the identified issues or troubleshooting </td></tr><tr><td>Error</td><td>Error log level provides information on the application issue preventing one or more functionalities from properly functioning.</td></tr></tbody></table>
