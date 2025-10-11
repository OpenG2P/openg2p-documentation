# Packaging Concepts

A pacakge of Registry module is offered as a Helm Chart that contains several other dependencies.

Refer to the packaging hierarchy here:

<figure><img src="../../../.gitbook/assets/module-packaging (1).jpg" alt=""><figcaption></figcaption></figure>

At the highest level a package is synonymous to a Helm chart that collates all dependencies for a   "single-click" installation.  This "Module Package Helm Chart" contains several other dependent charts.  Each Helm chart typically contains one Docker (there may be more, but for simplicity let's consider a single Docker per Helm).  A Docker is a package in itself that may contain code from several Git repositories. A single Git repository may house multiple components like Odoo modules, FastAPI modules etc.&#x20;

## Dockers

Helm chart contain Dockers for various components. The Dockers for top-level modules like Social Regsitry, PBMS, are created with a [Docker package file](https://github.com/OpenG2P/openg2p-packaging/blob/main/packaging/packages/social-registry/1.2.0.txt).  Learn more about packaging and uploading such Dockers in the following guides:

* [Automatic Build and Upload of Private Dockers](../../../deployment/deployment-guide/automatic-build-and-upload-of-private-dockers.md)
* [Packaging Odoo based Docker](../../../deployment/deployment-guide/packaging-openg2p-docker.md)

