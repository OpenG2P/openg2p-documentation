# Module Packaging

A module like Social Registry, PBMS, or SPAR is offered as [Helm Chart](helm-charts.md) package. The Helm Chart collates all dependencies and offers a single package for installing a module with a near "on-click" advantage.

Refer to the packaging hierarchy here:

{% embed url="https://miro.com/app/board/uXjVKoUYG7g=/?share_link_id=625991316183" %}

At the highest level a package is synonymous to a Helm chart that collates all dependencies into a near  "single-click" installation.  This "Module Package Helm Chart" contains several other dependent charts.  Each Helm chart typically contains one Docker (there may be more, but for simplicity let's consider a single Docker per Helm).  A Docker is a package in itself that may contain code from several Git repositories. A single Git repository may house multiple components like Odoo modules, FastAPI modules etc.





