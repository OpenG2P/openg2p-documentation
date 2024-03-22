---
layout:
  title:
    visible: true
  description:
    visible: true
  tableOfContents:
    visible: true
  outline:
    visible: true
  pagination:
    visible: true
---

# Social Registry

Social Registry (SR) is an independent module offered by OpenG2P to enable the creation of **registries** of individuals and groups of people with demographic data with advanced features that make the SR interoperable and easily fit into the digital public infrastructure (DPI) infrastructure of a country.&#x20;

The registry can host demographic data of both individuals and groups (family/household) and this data is privacy protected.  SR offers the unique feature of issuing digitally signed credentials - Verifiable Credentials - to the beneficiaries.

{% embed url="https://miro.com/app/board/uXjVN3lWhUg=/?share_link_id=305024808834" %}

## Functionality and features

<table><thead><tr><th width="268">Feature</th><th width="348">Description </th><th>Status</th><th data-type="number"></th></tr></thead><tbody><tr><td>Registry population mechanisms  </td><td><ul><li>CSV</li><li><a href="functionality/api.md">APIs</a></li><li>Login based direct data entry</li><li>Operators uploading data</li><li>ODK (Android, agent, offline)</li></ul></td><td></td><td>null</td></tr><tr><td>Data share</td><td><ul><li>CSV</li><li>APIs (G2P Connect, GraphQL, REST)</li></ul></td><td></td><td>null</td></tr><tr><td>Individuals and Groups</td><td><ul><li>Registry of individuals</li><li>Registry of household and families</li><li>Entities with group of people, like school, community</li></ul></td><td></td><td>null</td></tr><tr><td><a href="privacy-and-security.md">Privacy and security</a></td><td><ul><li>Encryption of PII</li></ul></td><td></td><td>null</td></tr><tr><td>Search</td><td><ul><li>Fast data search based on parameters of registrants.</li></ul></td><td></td><td>null</td></tr><tr><td><a href="functionality/languages-support.md">Languages support</a></td><td></td><td></td><td>null</td></tr><tr><td>Notifications</td><td><ul><li>SMS</li><li>Email</li></ul></td><td></td><td>null</td></tr><tr><td><a href="functionality/administration.md">Administration</a></td><td><ul><li>RBAC</li><li>Roles</li><li>Users</li></ul></td><td></td><td>null</td></tr><tr><td><a href="monitoring-and-reporting/">Reporting</a></td><td><ul><li>Dashboards</li><li>Real-time data monitoring</li></ul></td><td></td><td>null</td></tr><tr><td>Logging</td><td><ul><li>Change logs</li><li>Audit logs</li><li>System logs</li></ul></td><td></td><td>null</td></tr><tr><td>Verifiable Credentials Issuance</td><td><ul><li>Mobile wallet</li><li>Paper (QR code)</li></ul></td><td></td><td>null</td></tr><tr><td>Domain specific registries </td><td></td><td></td><td>null</td></tr></tbody></table>

## Design

### Change log

Change log can be build using the Odoo OCA package [Audit Log](https://github.com/OCA/server-tools/tree/16.0/auditlog). This would be set of changes in any field(s) for the registry.

### Multiple versions of data

Multiple version of a person's record might come in the following scenarios

* Change in field value
* New updated record coming in for the person which would be termed as a named version (typically surveys)
* Feedback call from the connected applications

**Proposed solution:** Utilizing Elasticsearch as the backbone, we aim to implement a robust solution for managing multiple versions efficiently. Below are the key technology components and strategies discussed:

* **Debezium configuration:** Debezium will be configured to capture real-time changes from the database's Write-Ahead Logs (WALs), ensuring that any modifications or additions to the data are promptly recorded.
* **Elasticsearch setup:** Elasticsearch will serve as the primary destination for streaming the captured changes. Leveraging its indexing capabilities, Elasticsearch will efficiently organize and store the data, facilitating quick retrieval and analysis.
* **Indexing strategy:** An indexing strategy will be devised to optimize the storage and retrieval of captured data. This strategy will accommodate multiple versions of records, ensuring that historical data remains accessible and searchable.
* **Authorization implementation:** Authorization mechanisms will be implemented within Elasticsearch. This will control access to the API endpoints, ensuring that only authorized users can interact with the data.&#x20;
* **API Endpoints configuration:** API endpoints will be configured in Elasticsearch to expose the captured data to authorized users. These endpoints will provide seamless access to multiple versions of records, enabling users to retrieve and analyze data as needed. Client should be in a position to fetch based on named version or any other parameter like timeframe.

### Relationships between people

Relationship functionality would primarily address the family relationship.

#### Parent info for a registrant

* Parent1Id
* Parent2Id
* IsAdopted
* GaurdianId

**Spouse Relationship (new table)**

* Person1Id
* Person2Id
* IsMarried
* MarriedOn
* IsSeperated
* SeperatedOn

Current thought process is to set all possible relations with the above data structure.

### Groups and Households

### Attestation

**Attestation table**

* id of the field
* status (NEW, ATTESTED, REJECTED ..)
* attested by
* attestation datetime
* comments

The `status` fields will come from business processes and real use cases.

## User interface

UI required for the following:

* Person to log in, view and update records
* Admin to view and attest fields with comments
* Download of CSV for chosen fields of registry
* Upload of attested CSV

## Bulk attestation

We should be able to download a CSV from the registry, apply bulk attestation, and upload back the CSV. The upload should trigger an update of registry, change log and attestation table

* **Attestation table**
  * id of the field
  * status (NEW, ATTESTED, REJECTED ..)
  * attested by
  * attestation datetime
  * comments

## API

The SR exposes the following REST APIs:

_TBD_
