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

# Helm Charts

For deployment on Kubernetes OpenG2P provides Helm charts for all its components. Instructions to install a module/component using Helm are provided in the respective deployment guides. The location of the charts is given below:

| Module                    | Location                                                                                                   |
| ------------------------- | ---------------------------------------------------------------------------------------------------------- |
| [SPAR](../spar/)          | [https://github.com/OpenG2P/openg2p-spar-deployment/](https://github.com/OpenG2P/openg2p-spar-deployment/) |
| All modules (except SPAR) | [https://github.com/OpenG2P/openg2p-helm](https://github.com/OpenG2P/openg2p-helm)                         |

## Publishing of Helm charts

All charts are published to this public website: [https://openg2p.github.io/openg2p-helm](https://openg2p.github.io/openg2p-helm).  Charts are automatically published via Github action given [here](https://github.com/OpenG2P/openg2p-helm/blob/main/.github/workflows/push\_trigger.yml).  Charts may be published manually with the procedure given below:

TBD
