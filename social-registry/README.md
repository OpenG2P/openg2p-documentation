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

# Social Registry

Social Registry (SR) is an independent module offered by OpenG2P to enable the creation of **registries** of individuals and groups of people with demographic data with advanced features that make the SR interoperable and easily fit into the digital public infrastructure (DPI) infrastructure of a country.&#x20;

The registry can host demographic data of both individuals and groups (family/household) and this data is privacy protected.  SR offers the unique feature of issuing digitally signed credentials - Verifiable Credentials - to the beneficiaries.

## Functional architecture

{% embed url="https://miro.com/app/board/uXjVN3lWhUg=/?share_link_id=305024808834" %}
Social Registry Functional Architecture
{% endembed %}

## Feature and functionality

<table><thead><tr><th width="326">Feature</th><th>Functionality</th></tr></thead><tbody><tr><td><a href="features/administration/">Administration/User Management</a></td><td><ul><li>RBAC</li><li>Roles</li><li>Users</li></ul></td></tr><tr><td><a href="features/api/">API</a></td><td><ul><li><a href="features/api/search-apis.md">Search APIs</a></li><li><a href="features/api/individual-apis.md">Individual APIs</a></li><li><a href="features/api/group-apis.md">Group APIs</a></li></ul></td></tr><tr><td><a href="features/attestation.md">Attestation</a></td><td></td></tr><tr><td><a href="features/score-computation.md">Benefit Targeting Methods</a></td><td></td></tr><tr><td><a href="features/configurations/">Configurations</a></td><td>Configuration of ID Types, Registrant Tags, Gender Types, Relationships, Group Types, and Group Membership Kind are required to define values (enumerations) for the associated fields.</td></tr><tr><td><a href="features/consent.md">Consent</a></td><td></td></tr><tr><td><a href="features/data-share.md">Data Share</a></td><td><ul><li>CSV</li><li>APIs (G2P Connect, GraphQL, REST)</li></ul></td></tr><tr><td><a href="features/deduplication/">Deduplication</a></td><td><ul><li>Identifies and stores the duplicate entries of the recorded registrants' data.</li><li>Manages duplicate records within separate groups and individual registries.</li></ul></td></tr><tr><td><a href="features/document-upload.md">Document Upload</a></td><td><ul><li>Assists in uploading the mandatory documents required to register for a program</li></ul></td></tr><tr><td><a href="features/domain-specific-registries.md">Domain Specific Registries</a></td><td></td></tr><tr><td><a href="features/registry-update-mechanisms.md">Dynamic Updates</a></td><td><p></p><ul><li>CSV</li><li><a href="features/api/">APIs</a></li><li>Login-based direct data entry</li><li>Operators uploading data</li><li>ODK (Android, agent, offline)</li></ul></td></tr><tr><td><a href="features/enumerator/">Enumerator</a></td><td></td></tr><tr><td><a href="features/fayda-id-integration.md">Fayda ID Integration</a></td><td></td></tr><tr><td><a href="features/geographic.md">Geographic</a></td><td></td></tr><tr><td><a href="features/id-creation.md">ID Creation</a></td><td></td></tr><tr><td><a href="development/upcoming-features/tokenisation.md">ID Validation and Tokenisation</a></td><td></td></tr><tr><td><a href="features/individuals-and-groups/">Individual and Groups</a></td><td><ul><li>Registry of individuals</li><li>Registry of household and families</li><li>Entities with group of people, like school, community</li></ul></td></tr><tr><td><a href="features/interoperability.md">Interoperability</a></td><td></td></tr><tr><td><a href="features/logging/">Logging</a></td><td><ul><li>Change logs</li><li>Audit logs</li><li>System logs</li></ul></td></tr><tr><td><a href="features/lock-and-unlock.md">Lock and Unlock</a></td><td><ul><li>Lock record for edit</li><li>Suggest for edit/update</li><li>Request for edit/update</li><li>Unlock for edit/update</li></ul></td></tr><tr><td><a href="features/languages-support/">Language Support</a></td><td></td></tr><tr><td><a href="features/monitoring-and-reporting/">Monitoring and Reporting</a></td><td><ul><li>Dashboards</li><li>Real-time data monitoring</li></ul></td></tr><tr><td><a href="features/notifications.md">Notifications</a></td><td><ul><li>SMS</li><li>Email</li></ul></td></tr><tr><td><a href="features/odk-importer/">ODK Importer</a></td><td></td></tr><tr><td><a href="features/privacy-and-security.md">Privacy and Security</a></td><td><ul><li>Encryption of PII</li></ul></td></tr><tr><td><a href="features/record-revision-history.md">Record  Revision History</a></td><td></td></tr><tr><td><a href="features/monitoring-and-reporting/">Reporting</a></td><td><ul><li></li></ul></td></tr><tr><td><a href="features/registration-portal/">Registration Portal</a></td><td></td></tr><tr><td><a href="features/search.md">Search</a></td><td><ul><li>Fast data search based on parameters of registrants</li></ul></td></tr><tr><td><a href="features/search-opensearch.md">Search - Open Search</a></td><td></td></tr><tr><td><a href="features/self-service-registration-portal.md">Self Service Registration Portal</a></td><td></td></tr><tr><td><a href="features/single-sign-on.md">Single Sign-On</a></td><td></td></tr><tr><td>Social Registry ID</td><td></td></tr><tr><td><a href="features/spar-update-for-offline-enumerations.md">SPAR Update for Offline Enumerations</a></td><td></td></tr><tr><td><a href="features/unique-reference-id.md">Unique Reference ID</a></td><td></td></tr><tr><td><a href="features/verifiable-credentials-issuance.md">Verifiable Credentials Issuance</a></td><td><ul><li>Mobile wallet</li><li>Paper (QR code)</li></ul></td></tr></tbody></table>

