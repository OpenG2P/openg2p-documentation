# Deployment of Novu

The instructions here pertain to the deployment of Novu and associated components on the Kubernetes cluster using [Novu helm chart](https://github.com/OpenG2P/openg2p-deployment/tree/main/charts/novu). All the components are installed in the same namespace.

## Prerequisites

Before you deploy, make sure the following are in place:

* ✅ [Infrastructure setup](../../operations/deployment/infrastructure-setup/three-node-automation/README.md) is completed.
* ✅ [Environment](../../operations/deployment/environment-setup-multi-node.md) has been setup with common resources installed.
* ✅ Domain name `novu.<your environment>.<your domain name>` (e.g. `novu.qa.openg2p.org`) is available along with SSL certificate for the domain (_the wild certificate should have already been loaded during Infrastructure setup_)
* ✅ **Project Owner access** on the OpenG2P namespace

## Installation using Rancher UI

1. Log in to Rancher admin console.
2. Select your cluster.
3. Under **Apps -> Repositories** click on Create to add a repository.
4.  Provide Name as `openg2p` and target HTTPS Index URL as [https://openg2p.github.io/openg2p-helm/rancher](https://openg2p.github.io/openg2p-helm/rancher) and click Create.

    <figure><img src="../../.gitbook/assets/image (2) (1).png" alt=""><figcaption></figcaption></figure>
5.  To display prerelease versions of OpenG2P apps, click on your user avatar in the upper right corner of the Rancher dashboard. Then click on `Include Prerelease Versions` under Preferences under Helm Charts.

    <figure><img src="../../.gitbook/assets/image (3) (2).png" alt=""><figcaption></figcaption></figure>
6. Select the namespace in which you would like to install novu, from the namespace filter on the top-right.
7.  Navigate to **Apps->Charts** page on Rancher. You should see `novu` Helm charts listed.

    <figure><img src="../../.gitbook/assets/image (88).png" alt=""><figcaption></figcaption></figure>
8. Proceed to Install `novu` chart select the latest version to be installed, and click Install.
9. On the next screen, choose a name for installation, like `novu`. Select the checkbox `Customise Helm options` before install, and click Next.
10. Go through each app's configuration page, and configure the following:
    1. Configure a hostname for each app in the following way. `<appname>.<base-hostname>` , where base host name is the environment's wildcard base domain set up during the [Environment](../../operations/deployment/environment-setup-multi-node.md) stage (the Istio `Gateway` for `*.<base_domain>`). Example: `novu-api.qa.openg2p.org`, etc. `<appname>` is arbitrary - default names have been provided.
11. Click Next to reach Helm Options page. Disable `wait` flag. Click on Install.
12. Wait for all the pods to get into **Running state**. This may take several minutes.

    <div align="left"><figure><img src="../../.gitbook/assets/image (5).png" alt=""><figcaption></figcaption></figure></div>

## Post Installation

### Accessing the novu

On the browser connect to URL

https://novu.dev.your.org/

#### Configuring the novu (TODO)<br>
