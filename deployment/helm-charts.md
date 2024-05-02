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

All charts are published to this public website: [https://openg2p.github.io/openg2p-helm](https://openg2p.github.io/openg2p-helm). This website is automatically created by Github with contents on [`gh-pages`](https://github.com/OpenG2P/openg2p-helm/tree/gh-pages) branch of openg2p-helm repository. Charts are automatically published via Github action given [here](https://github.com/OpenG2P/openg2p-helm/blob/main/.github/workflows/push\_trigger.yml). The publishing process involves the following steps:

1. Create Helm packaged zip files.
2. Check-in the packaged zip in `gh-pages` branch of openg2p-helm repository.

&#x20;Charts may be published manually with the procedure given below:

* &#x20;Create Helm packaged zip files by executing the following command in the folder that contains your charts source code.

```
helm package charts/<chart name>
```

* You will see packaged `.tgz` files created in the current directory.
* Clone [https://github.com/OpenG2P/openg2p-helm](https://github.com/OpenG2P/openg2p-helm) repo and switch to `gh-pages` branch. Copy the above `.tgz` files to root folder of the repo (where you will see several `.tgz` files).&#x20;
* Make sure you have direct check-in permissions to the `openg2p-helm` repo.
* Run&#x20;

```
./publish.sh
```

## Helm chart versions

<mark style="color:red;">WORK IN PROGRESS</mark>

The chart version is mentioned as `version` attribute of the `Chart.yaml` file.  For version numbers Semantic Versioning 2.0 is followed.  The below conventions are followed:

Released charts:

Chart version:&#x20;

Branch

<table><thead><tr><th width="166">Chart State</th><th width="361">Chart version</th><th></th></tr></thead><tbody><tr><td>Released</td><td>Chart number == <code>appVersion</code> == released docker version</td><td> it is recommended that <code>appVersion</code> attribute is removed from <code>Chart.yaml</code> as it is redundant. </td></tr><tr><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td></tr></tbody></table>

For **released** charts:

Chart number == `appVersion` == released docker version

Because of above convention, it is recommended that `appVersion` attribute is removed from `Chart.yaml` as it is redundant.&#x20;

