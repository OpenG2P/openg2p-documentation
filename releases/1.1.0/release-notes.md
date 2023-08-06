# Release Notes

### Release version: 1.1.0

### Release date: 7th August 2023

## Summary

OpenG2P 1.1.0 is a public benefits delivery platform based on [Odoo 15.0](https://www.odoo.com/documentation/15.0/). This release comes with improved user experience through intuitive development and multiple rounds of testing and inculcates feedback collated from various pilot and test runs across different countries.

OpenG2P 1.1.0 focuses on the core needs of our stakeholders from start to finish. Many more changes are underway, but here is a quick list of all the key features and functionalities covered in this release.

## Features of this release

<table><thead><tr><th width="258.66666666666663">Function</th><th>Features</th></tr></thead><tbody><tr><td>Registration</td><td><ul><li>Registry with security and privacy features</li><li>Tokenization of identifiers (foundational ID)</li><li>Bulk import and export</li><li>Deduplication using MOSIP ID or any ID platform</li><li>Offline registration using ODK</li><li>Registration over REST API</li></ul></td></tr><tr><td>Program Management</td><td><ul><li>Creation and configuration of multiple programs</li><li>Configuration of eligibility and other managers within a program</li><li>Proxy Means Test plugin</li><li>Rule-based eligibility</li><li>Multi-stage approval based on user role configuration</li><li>Role-based access control for program administrators</li></ul></td></tr><tr><td>Payments</td><td><ul><li>Payments integration with Mojaloop (Technology demonstration)</li><li>Cyclical and cycle-less payments</li></ul></td></tr><tr><td>Voucher based benefit delivery</td><td><ul><li>Digitally signed QR Code</li><li>Template-based voucher design</li><li>Voucher scanner Android app (reference implementation)</li></ul></td></tr><tr><td>Immediate individual assistance on-demand workflow</td><td><ul><li>Configuration mult-stage approval process from application to delivery of benefit</li></ul></td></tr><tr><td>Self service portal</td><td><ul><li>Login using e-Signet and MOSIP ID</li><li>Self-enrolment into a program (on-demand assistance)</li><li>Multi device UI</li><li>Support for upload of documents</li><li>Interactive dashboard</li><li>Real-time status updates</li></ul></td></tr><tr><td>Service provider portal (<em>reference implementation)</em></td><td><ul><li>Reimbursements to service providers against a voucher</li><li>Generation of payments instructions</li></ul></td></tr><tr><td>Document management</td><td><ul><li>Upload and view</li></ul></td></tr><tr><td>Notifications</td><td><ul><li>SMS</li><li>Email</li></ul></td></tr><tr><td>i18n support</td><td><ul><li>Back office application configured for multiple languages</li></ul></td></tr><tr><td>Monitoring and reporting</td><td><ul><li>Debezium-Kafka-Elasticsearch-Kibana pipeline</li><li>Customisable dashboards</li><li>Real-time updation of data</li></ul></td></tr><tr><td>Kubernetes based production deployment infrastructure</td><td><ul><li>Helm charts</li><li>Instructions and scripts to deploy on Kubernetes</li></ul></td></tr></tbody></table>

## Release contents

* [OpenG2P Odoo package docker](https://hub.docker.com/layers/openg2p/openg2p-odoo-package/1.1.0/images/sha256-d9f39eb05ff11e00d5c31df045d1bcb164f8b9eaab124ec2b596cb959e29d43b?context=explore) (_see repositories listed below)_
* Non-odoo modules:
  * [Reporting](https://github.com/OpenG2P/openg2p-reporting/tree/1.1.0)
  * [Voucher scan Android app](https://github.com/OpenG2P/openg2p-voucher-scanner-app/releases/tag/v0.5.0)
* Deployment components:
  * [Helm charts](https://github.com/OpenG2P/openg2p-helm/tree/1.1.0)
  * [Scripts](https://github.com/OpenG2P/openg2p-deployment/tree/1.1.0)
* [Documentation](https://docs.openg2p.org/v/1.1)

## Source code

<table><thead><tr><th width="297.3333333333333">Github repository</th><th width="153" align="center">Version/Tag</th><th>Base</th></tr></thead><tbody><tr><td><a href="https://github.com/OpenG2P/openg2p-program/tree/v1.1.0">openg2p-program</a></td><td align="center">v1.1.0</td><td>Odoo 15.0</td></tr><tr><td><a href="https://github.com/OpenG2P/openg2p-registry/tree/v1.1.0">openg2p-registry</a></td><td align="center">v1.1.0</td><td>Odoo 15.0</td></tr><tr><td><a href="https://github.com/OpenG2P/openg2p-self-service-portal/tree/v1.1.0">openg2p-self-service-portal</a></td><td align="center">v1.1.0</td><td>Odoo 15.0</td></tr><tr><td><a href="https://github.com/OpenG2P/openg2p-auth/tree/v1.1.0">openg2p-auth</a></td><td align="center">v1.1.0</td><td>Odoo 15.0</td></tr><tr><td><a href="https://github.com/OpenG2P/openg2p-theme/tree/v1.1.0">openg2p-theme</a></td><td align="center">v1.1.0</td><td>Odoo 15.0</td></tr><tr><td><a href="https://github.com/OpenG2P/openg2p-notifications/tree/v1.1.0">openg2p-notifications</a></td><td align="center">v1.1.0</td><td>Odoo 15.0</td></tr><tr><td><a href="https://github.com/OpenG2P/openg2p-documents/tree/v1.1.0">openg2p-documents</a></td><td align="center">v1.1.0</td><td>Odoo 15.0</td></tr><tr><td><a href="https://github.com/OpenG2P/odoo-json-field/tree/v1.1.0">odoo-json-field</a></td><td align="center">v1.1.0</td><td>Odoo 15.0</td></tr><tr><td><a href="https://github.com/OpenG2P/openg2p-mts/tree/v1.1.0">openg2p-mts</a></td><td align="center">v1.1.0</td><td>Odoo 15.0</td></tr><tr><td><a href="https://github.com/OpenG2P/openg2p-security/tree/v1.1.0">openg2p-security</a></td><td align="center">v1.1.0</td><td>Odoo 15.0</td></tr><tr><td><a href="https://github.com/OpenG2P/openg2p-packaging">openg2p-packaging</a></td><td align="center">Latest 'main'</td><td>Shell scripts</td></tr><tr><td><a href="https://github.com/OpenG2P/openg2p-helm/tree/v1.1.0">openg2p-helm</a></td><td align="center">v1.1.0</td><td>Helm charts</td></tr><tr><td><a href="https://github.com/OpenG2P/openg2p-deployment/tree/v1.1.0">openg2p-deployment</a></td><td align="center">v1.1.0</td><td>Shell scripts, Python</td></tr><tr><td><a href="https://github.com/OpenG2P/openg2p-voucher-scanner-app/releases/tag/v0.5.0">openg2p-voucher-scanner-app</a></td><td align="center">v0.5.0</td><td>Android</td></tr><tr><td><a href="https://github.com/OpenG2P/openg2p-reporting/tree/v1.1.0">openg2p-reporting</a></td><td align="center">v1.1.0</td><td>Shell scripts</td></tr></tbody></table>

## Build and deploy

* To build and run this release as a developer refer to the guide [here](<../../guides/developer-guides/getting-started (1).md>).
* To deploy this release on Kubernetes refer to the guide [here](../../guides/deployment-guide/deployment-on-kubernetes/).

## Test report

## Limitations and known issues
