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
