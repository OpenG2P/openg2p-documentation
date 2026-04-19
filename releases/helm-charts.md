# Helm Charts

For deployment on Kubernetes OpenG2P provides Helm charts for all its components. Instructions to install a module/component using Helm are provided in the respective deployment guides.

## Source code

Charts may be found here:

| Module                                                            | Location                                                                                                                         |
| ----------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| [Social Registry](../products/registry/registry/social-registry/) | [https://github.com/OpenG2P/openg2p-social-registry-deployment/](https://github.com/OpenG2P/openg2p-social-registry-deployment/) |
| [PBMS](../pbms/)                                                  | [https://github.com/OpenG2P/openg2p-pbms-deployment](https://github.com/OpenG2P/openg2p-pbms-deployment)                         |
| [SPAR](../spar/)                                                  | [https://github.com/OpenG2P/openg2p-spar-deployment/](https://github.com/OpenG2P/openg2p-spar-deployment/)                       |
| [G2P Bridge](../g2p-bridge/)                                      | [https://github.com/OpenG2P/openg2p-g2p-bridge-deployment](https://github.com/OpenG2P/openg2p-g2p-bridge-deployment)             |

## Published repository

All charts are published to this public website: https://openg2p.github.io/openg2p-helm. This website is automatically created by Github with contents on [`gh-pages`](https://github.com/OpenG2P/openg2p-helm/tree/gh-pages) branch of openg2p-helm repository. Charts are automatically published via Github action given [here](https://github.com/OpenG2P/openg2p-deployment/blob/main/.github/workflows/push_trigger.yml).

Charts may be published manually with the procedure given below:

1. Create Helm packaged zip files by executing the following command in the folder that contains your charts source code.

```
helm package charts/<chart name>
```

2. You will see packaged `.tgz` files created in the current directory.
3. Clone [https://github.com/OpenG2P/openg2p-helm](https://github.com/OpenG2P/openg2p-helm) repo and switch to `gh-pages` branch. Copy the above `.tgz` files to root folder of the repo (where you will see several `.tgz` files).
4. Make sure you have direct check-in permissions to the `openg2p-helm` repo.
5. Run

```
./publish.sh
```

## Publish Helm charts as Rancher apps

To have your charts available in Rancher Apps and be able to install from Rancher UI follow guide given [here](https://ranchermanager.docs.rancher.com/how-to-guides/new-user-guides/helm-charts-in-rancher/create-apps). See [example](https://github.com/OpenG2P/openg2p-social-registry-deployment/tree/develop/charts/openg2p-social-registry) of Helm chart configured for Rancher.

### Automatic publishing

To have your chart published automatically to be available in Rancher, add the following annotation to `Chart.yaml` in your helm chart.

```yaml
annotations:
  openg2p.org/add-to-rancher: ""
```

### Manual publishing

To publish a chart on Rancher Apps in step 3 above,

* copy the chart zip to `/rancher` folder of the repo.
* cd /rancher
* Run command `helm repo index --url ../ . --merge index.yaml`
* Delete the chart zip in `/rancher` - its no longer required.

This will update `index.yaml` file in the .`/rancher` folder. This file will be read by Rancher to display in the catalogue (refer [Installation using Rancher UI](../spar/deployment/#installation-using-rancher-ui) on how to add this repository).

{% hint style="info" %}
If in [annotations](https://ranchermanager.docs.rancher.com/how-to-guides/new-user-guides/helm-charts-in-rancher/create-apps#chartyaml-annotations) for the chart fixed name and namespace of the Helm chart is specified, then only one instance of the application will be installed and further attempts to install will only update the application. Example, Monitoring app on Rancher.
{% endhint %}

## Helm chart versions

The Helm chart version is mentioned under the `version` attribute in the `Chart.yaml` file (see [example](https://github.com/OpenG2P/openg2p-spar-deployment/blob/1.0.0/charts/spar/Chart.yaml)). Important to note that the version of Helm chart MAY NOT match the primary Docker version of the app inside the chart. However, generally, the major and minor versions would be same. For example, Helm chart version 1.4.2 of Social Registry may contain 1.4.0 of the Social Registry Odoo Docker. The chart version may have moved forward due to some other changes in the chart like change in dependencies, their version, or even any other minor fixes in the chart.

A 3 digit version of a chart is considered 'frozen'. See more details about versioning [here](versioning.md#frozen-versions). Charts that are not frozen will have `-develop` tag. Examples:

* `1.4.0-develop`: Non-frozen chart on 1.4 branch of the deployment repository. \`
* `0.0.0-develop`: Non-frozen chart on `develop`branch of deployment repository.

## Helm chart size limitation

{% hint style="warning" %}
**Helm chart size limitation**

Due to 1 MB limit of Kubernetes ETCD secrets, we have split a large chart into parts. This split is purely to address this limitation. See some discussions here on this topic:

[https://github.com/helm/helm/issues/11493](https://github.com/helm/helm/issues/11493)

[https://azure.github.io/azure-service-operator/design/adr-2023-02-helm-chart-size-limitations/](https://azure.github.io/azure-service-operator/design/adr-2023-02-helm-chart-size-limitations/)
{% endhint %}
