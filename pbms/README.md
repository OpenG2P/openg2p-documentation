---
description: Program and Beneficiary Management System
---

# PBMS

The Program and Beneficiary Management System (PBMS) is the core module of OpenG2P enabling the management of multiple programs and beneficiaries. The PBMS is based on [Odoo ERP/MIS](https://www.odoo.com/) and leverages Odoo's strength of easily extending modules to implement new functionality.  It offers user-friendly interfaces to create and administer social benefit programs.  Some of the key benefits for a country or an organisation using PBMS are:

* Manage **multiple** programs in one system
* **Share** beneficiary data with other systems/departments in an interoperable fashion
* Define eligibility and entitlement rules like [Proxy Means Test](features/eligibility/proxy-means-test.md) (**PMT)** to automatically create eligible beneficiaries
* Enable [**digital cash transfer**](../g2p-cash-transfer-bridge/) by seamlessly connecting to payment systems
* Offer [**self-service portal**](features/self-service-portal.md) to residents
* Send [**notifications**](features/notifications.md) to beneficiaries via SMS and email
* Issue digitally signed [**e-Vouchers**](features/disbursement-cycles/e-voucher.md) to beneficiaries
* Pull beneficiary data from other registries (departments) to avoid the collection of the same data multiple times

## Feature and Functionality&#x20;

<table><thead><tr><th width="201">Features</th><th>Functionality</th></tr></thead><tbody><tr><td><a href="features/program-management.md">Program management</a></td><td><ul><li>Program definition</li><li>Program lifecycle management</li><li>Managing multiple programs</li><li>Programs targeting both individuals and groups</li><li>Program disbursement cycles</li></ul></td></tr><tr><td><a href="features/beneficiary-management.md">Beneficiary Management</a></td><td><p></p><ul><li>Identifying beneficiaries</li><li>Enrolling beneficiaries</li><li>Maintaining <a href="features/beneficiary-registry.md">Beneficiary Registry</a></li><li>Deciding on entitlements</li><li>Disbursements</li><li>Notifications to beneficiaries</li></ul></td></tr><tr><td><a href="features/beneficiary-registry.md">Beneficiary Registry</a></td><td><ul><li>Data sharing of beneficiaries via APIs</li></ul></td></tr><tr><td><a href="features/self-service-portal.md">Self service portal</a></td><td><ul><li>Program application and discovery by beneficiaries</li><li>Program enrollment and disbursement status </li></ul></td></tr><tr><td><a href="features/document-management.md">Document Management</a></td><td></td></tr><tr><td><a href="features/id-verification.md">ID Verification</a></td><td><ul><li>Login using national ID via <a href="https://auth0.com/docs/authenticate/protocols/openid-connect-protocol">OpenID Connect</a> (OIDC)</li><li>MTS Connector</li></ul></td></tr><tr><td><a href="features/deduplication.md">Deduplication</a></td><td><ul><li>ID based deduplication </li><li>Phone number based deduplication</li></ul></td></tr><tr><td><a href="features/eligibility/">Eligibility</a></td><td><ul><li>Automatic computation of eligibility</li><li>Proxy Means Test</li></ul></td></tr><tr><td><a href="features/entitlement.md">Entitlement </a></td><td><ul><li>Differential entitlement</li><li>Entitlement in kind</li><li>e-Vouchers</li></ul></td></tr><tr><td><a href="features/disbursement-cycles/">Disbursement</a></td><td><ul><li>Disbursement cycles and batches</li><li>Digital cash transfer via bank or mobile</li><li>Voucher based disbursement</li><li>In-kind disbursement</li><li>Generation of disbursement list</li><li>Fund management</li></ul></td></tr><tr><td><a href="features/disbursement-cycles/e-voucher.md">e-Voucher</a></td><td><ul><li>Digital vouchers for goods or services</li><li>Voucher verification app</li><li>Voucher reimbursement </li></ul></td></tr><tr><td><a href="features/verifiable-credentials-issuance.md">Verifiable Credential Issuance</a></td><td><ul><li>Beneficiary e-Card</li></ul></td></tr><tr><td><a href="features/accounting.md">Accounting</a></td><td><ul><li>Fund management</li><li>Reconciliation</li></ul></td></tr><tr><td><a href="features/administration/">Administration</a></td><td><ul><li>Role-based access control (RBAC)</li><li>Multilevel approval </li><li>Fund management</li><li>Multi lingual - internationalisation (i18n)</li></ul></td></tr><tr><td><a href="features/notifications.md">Notifications</a></td><td><ul><li>Notifications to beneficiaries via SMS/Email</li></ul></td></tr><tr><td><a href="../interoperability.md">Interoperability</a></td><td><ul><li>Compliance with G2P Connect Registry APIs</li><li>Compliance with G2P Connect Disbursement APIs</li></ul></td></tr><tr><td><a href="features/multi-tenancy-in-pbms.md">Multi-tenancy</a></td><td><ul><li>Multiple departments using the same instance of OpenG2P</li><li>Separation of data, control and access.</li></ul></td></tr><tr><td><a href="../monitoring-and-reporting/">Monitoring and Reporting </a></td><td><ul><li>Monitor the status of the program and registries</li><li>User creates dashboard of their choice to visualise data</li></ul></td></tr><tr><td><a href="features/audit-logs.md">Audit Logs</a></td><td><ul><li>Odoo audit logs</li></ul></td></tr></tbody></table>

## Architecture

Refer to [Architecture](../#functional-architecture) for PBMS high level architecture and its relationship with other modules.

## Data sources

PBMS provides methods to pull data from OpenG2P's [Social Registry](../social-registry/) and other registries that are compliant with the G2P Connect API specifications.  The data is stored in internal cache DB and used to create beneficiary data. This cached data may be updated by administrators by pulling fresh data from the external registeries when desired.

## Data flow

{% embed url="https://miro.com/app/board/uXjVN3lF5oc=/?share_link_id=763340453780" %}

## Interoperability &#x20;

* G2P Connect interfaces
* Connection to payment systems
* Exposing beneficiary data via standard interfaces
* Pulling data using G2P Connect

## Technology

PBMS is based on Odoo which is an open source ERP software.  [Program & Beneficiary Program Management](features/program-management.md) (PBPM) extends modules of Odoo to tailor them from social protection needs.&#x20;

The underlying database is Postgres.

[Technical architecture](../#functional-architecture) diagram

## Privacy and security of data

Refer to[ Privacy and Security](../privacy-and-security/).

## User login and authorization

Users of PBMS system can login via following login providers

1. [Odoo](https://www.odoo.com/)&#x20;
2. [Keycloak ](https://www.keycloak.org/)
3. National ID (integration via [eSignet](https://docs.esignet.io/))

## Configuration

PBMS is highly configurable and several functionality and parameters can be enabled/disabled for your application.  Refer to configuration of each functionality under the respective topics.

## Use cases

## Related user guides
