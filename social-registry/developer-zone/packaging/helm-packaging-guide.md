# 📘 Helm Packaging Guide

## Concepts

Social Registry and all its dependencies are installed using a single packaged [Helm chart](https://github.com/OpenG2P/openg2p-social-registry-deployment/tree/develop/charts).  The contents of the package may be found in the [Docker package files](https://github.com/OpenG2P/openg2p-packaging/tree/main/packaging/packages/social-registry).  Learn more on Helm charts, versioning and packaging [here](../../../deployment/helm-charts.md#helm-chart-versions).

{% hint style="info" %}
\* The chart has been split into parts to address the Kubernetes ETCD limitation. [Learn more >>](../../../deployment/helm-charts.md#helm-chart-size-limitation)
{% endhint %}

Helm package is the highest level of package that is offered for module installation.  The Helm package contains all dependencies and is intended to be installed "single click" from Rancher or the command line.

The package hierarchy is depicted below.

{% embed url="https://miro.com/app/board/uXjVKoUYG7g=/" %}

## Steps

### Tagging Helm repo

The charts are located in [this](https://github.com/OpenG2P/openg2p-social-registry-deployment/) repo.

1. Decide on which branch you would like to create the tag.
2. On the marked branch create another branch with same name as the version, e.g. 1.3.1.
3. On this branch make the necessary changes in the chart:
   1. Update `Chart.yaml` file. Make sure 3 digit version without any suffix is updated in the file.
   2. Update any dependency chart versions. Make sure all the versions of other charts are frozen versions.
   3. Update `values.yaml` with the tagged version of the docker image.&#x20;
4. Check in the changes on this branch
5. Create a tag following tagging conventions. E.g. `v1.3.1`. &#x20;
6. The Github workflow action to package Helm and push on `openg2p-helm` repo's `gh-pages` branch should be triggered automatically and the chart published.
7. Update the [Versions](../../versions.md) page on this documentation.

{% hint style="warning" %}
The Github workflow triggers only if the branch already exists and changes are applied on the branch. So create the branch first on Github directly and push the Helm changes.
{% endhint %}

### Making package availabe on Rancher
