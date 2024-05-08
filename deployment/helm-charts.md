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

1. &#x20;Create Helm packaged zip files by executing the following command in the folder that contains your charts source code.

```
helm package charts/<chart name>
```

2. You will see packaged `.tgz` files created in the current directory.
3. Clone [https://github.com/OpenG2P/openg2p-helm](https://github.com/OpenG2P/openg2p-helm) repo and switch to `gh-pages` branch. Copy the above `.tgz` files to root folder of the repo (where you will see several `.tgz` files).&#x20;
4. Make sure you have direct check-in permissions to the `openg2p-helm` repo.
5. Run&#x20;

```
./publish.sh
```

## Publish Helm charts as Rancher apps

To have your charts available in Rancher Apps and be able to install from Rancher UI follow guide given [here](https://ranchermanager.docs.rancher.com/how-to-guides/new-user-guides/helm-charts-in-rancher/create-apps).  See [example](https://github.com/OpenG2P/openg2p-spar-deployment/tree/develop/charts/spar) of Helm chart configured for Rancher.

To publish a chart on Rancher Apps in step 3 above, copy the chart zip to  `/rancher` folder of the repo.  Run `./index.sh.`This will generate and `index.yaml` file in the folder. This file will be read by Rancher to display in the catalogue (refer [Installation using Rancher UI](../spar/deployment.md#installation-using-rancher-ui) on how to add this repository).&#x20;

## Helm chart versions

The chart version is mentioned as `version` attribute in the `Chart.yaml` file (see [example](https://github.com/OpenG2P/openg2p-spar-deployment/blob/1.0.0/charts/spar/Chart.yaml)).  For version numbers we adhere to [Semantic Versioning 2.0](https://semver.org/spec/v2.0.0.html) with "Simple 1-1 versioning" convention as described [here](https://codefresh.io/docs/docs/ci-cd-guides/helm-best-practices/#simple-1-1-versioning).  Here, chart version is kept same as docker version (app version). &#x20;

<table><thead><tr><th width="166">Chart State</th><th width="245">Chart version</th><th>Docker version (app version)</th></tr></thead><tbody><tr><td><strong>Released</strong></td><td>Same as docker version (app version)</td><td>Same as chart version</td></tr><tr><td><strong>Development</strong></td><td><code>0.0.0-develop</code></td><td><code>develop</code></td></tr></tbody></table>

> Since chart version matches docker version (app version) it is recommended that `appVersion` attribute is removed from `Chart.yaml` as it is redundant.&#x20;



