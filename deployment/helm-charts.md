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

For deployment on Kubernetes OpenG2P provides Helm charts for all its components. Instructions to install a module/component using Helm are provided in the respective deployment guides.&#x20;

## Source code&#x20;

Charts may be found here:

| Module                    | Location                                                                                                   |
| ------------------------- | ---------------------------------------------------------------------------------------------------------- |
| [SPAR](../spar/)          | [https://github.com/OpenG2P/openg2p-spar-deployment/](https://github.com/OpenG2P/openg2p-spar-deployment/) |
| All modules (except SPAR) | [https://github.com/OpenG2P/openg2p-helm](https://github.com/OpenG2P/openg2p-helm)                         |

## Published repository

All charts are published to this public website: [https://openg2p.github.io/openg2p-helm](https://openg2p.github.io/openg2p-helm). This website is automatically created by Github with contents on `gh-pages` branch of openg2p-helm repository. Charts are automatically published via Github action given [here](https://github.com/OpenG2P/openg2p-helm/blob/main/.github/workflows/push\_trigger.yml).  Charts may be published manually with the procedure given below:

To publish charts manually follow these steps:

* &#x20;Run the following command from the folder that contains your Helm charts

```
helm package charts/<chart name>
```

* You will see packaged `.tgz` files created in the current directory.
* Clone [https://github.com/OpenG2P/openg2p-helm](https://github.com/OpenG2P/openg2p-helm) repo and switch to `gh-pages` branch. Copy the above `.tgz` files root folder of the repo (where you will see server `.tgz` files.&#x20;
* Run

```
./publish.sh
```
