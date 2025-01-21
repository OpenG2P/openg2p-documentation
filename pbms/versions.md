---
description: PBMS versions
---

# Versions

## PBMS Helm Package

<table><thead><tr><th width="145">Helm Version</th><th width="173">PBMS Core Version</th><th width="133">Created on</th><th>Contents</th></tr></thead><tbody><tr><td><a href="https://github.com/OpenG2P/openg2p-pbms-deployment/tree/v1.2.0">1.2.0</a></td><td></td><td>18-Oct-2024</td><td>Update for Docker 1.2.0 of PBMS. Reporting versions changed to tagged versions.</td></tr><tr><td><a href="https://github.com/OpenG2P/openg2p-pbms-deployment/tree/v1.2.2">1.2.2</a></td><td></td><td>22-Dec-2024</td><td>Update for Docker 1.2.2 of PBMS</td></tr><tr><td><a href="https://github.com/OpenG2P/openg2p-pbms-deployment/tree/v1.2.3">1.2.3</a></td><td>1.2.3</td><td>28-Dec-2024</td><td>Update for Docker 1.2.3 of PBMS</td></tr><tr><td><a href="https://github.com/OpenG2P/openg2p-pbms-deployment/tree/v2.0.0">2.0.0</a></td><td>1.2.4</td><td>03-Jan-2025</td><td>MAJOR, INCOMPATIBLE changes w.r.t 1.x Helm version. The packaging has been significantly modified. Only one instance of DB, Kafka, OpenSearch installed and wired accordingly. Previous 1.x Helm charts cannot be easily upgraded to this version. Hence it is advised to install this version fresh. Part 2 is no longer required with this packaging - entire PBMS can be installed from one package.</td></tr><tr><td><a href="https://github.com/OpenG2P/openg2p-pbms-deployment/tree/v2.0.1">2.0.1</a></td><td>1.2.6</td><td>21-Jan-2025</td><td>PBMS Core version upgraded to 1.2.6</td></tr></tbody></table>

## PBMS Docker

Repository on Docker Hub:

* [openg2p-pbms-odoo-package](https://hub.docker.com/r/openg2p/openg2p-pbms-odoo-package/tags) (legacy)

<table><thead><tr><th width="95">Tag</th><th width="137">Created on</th><th>Description</th></tr></thead><tbody><tr><td><a href="https://github.com/OpenG2P/openg2p-packaging/blob/main/packaging/packages/pbms/1.2.0.txt">1.2.0</a></td><td>17-Oct-2024</td><td>Latest on branch 17.0-1.2</td></tr><tr><td><a href="https://github.com/OpenG2P/openg2p-packaging/blob/main/packaging/packages/pbms/1.2.1.txt">1.2.1</a></td><td>21-Oct-2024</td><td><p>Fixed getting total no. of beneficiaries from cycle, instead of program.</p><p>UI improvements: Renamed <code>Print Summary</code> to<code>Envelope Summary</code></p><p>Fixed an issue where <code>batch_has_completed</code> was not getting updated.<br></p></td></tr><tr><td><a href="https://github.com/OpenG2P/openg2p-packaging/blob/main/packaging/packages/pbms/1.2.2.txt">1.2.2</a></td><td>22-Dec-2024</td><td>Changes in ODK import to support multiple programs.</td></tr><tr><td><a href="https://github.com/OpenG2P/openg2p-packaging/blob/main/packaging/packages/pbms/1.2.3.txt">1.2.3</a></td><td>22-Dec-2024</td><td>Background import for ODK</td></tr></tbody></table>

* [openg2p-pbms-core](https://hub.docker.com/r/openg2p/openg2p-pbms-core/tags) (renamed the above docker).

The new name of this Docker shall be used starting 1.2.4 version.

<table><thead><tr><th width="95">Tag</th><th width="137">Created on</th><th>Description</th></tr></thead><tbody><tr><td><a href="https://github.com/OpenG2P/openg2p-packaging/blob/main/packaging/packages/pbms/1.2.4.txt">1.2.4</a></td><td>03-Jan-2025</td><td>ODK Import Documents update.</td></tr><tr><td><a href="https://github.com/OpenG2P/openg2p-packaging/blob/main/packaging/packages/pbms/1.2.6.txt">1.2.6</a></td><td>21-Jan-2025</td><td>SR pull changed to job queue<br>Bug fixes<br>community addons updated</td></tr></tbody></table>
