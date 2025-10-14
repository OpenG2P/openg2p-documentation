# Packaging Concepts

A pacakge of Registry module is offered as a Helm Chart that contains several other dependencies.

Refer to the packaging hierarchy here:

<figure><img src="../../../../.gitbook/assets/module-packaging (1).jpg" alt=""><figcaption></figcaption></figure>

At the highest level a package is synonymous to a Helm chart that collates all dependencies for a   "single-click" installation.  This "Module Package Helm Chart" contains several other dependent charts.  Each Helm chart typically contains one Docker (there may be more, but for simplicity let's consider a single Docker per Helm).  A Docker is a package in itself that may contain code from several Git repositories. A single Git repository may house multiple components like Odoo modules, FastAPI modules etc.&#x20;

The depencies are listed in `Chart.yaml` file of the Helm Chart.

## Dockers

The Registry Helm Chart uses Registry Docker.  The Docker itself is a package of several repositories (refer to the diagram above). [Lean more on Registry Docker >> ](docker-packaging-guide.md)

