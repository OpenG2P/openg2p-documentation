# Logging & OpenSearch Deployment

## Introduction

Logs from different components present on the cluster will be pulled into OpenSearch to display dashboards and compute reports. Fluentd is used to pull capture logs and put into OpenSearch.

## Prerequisites

* The following utilities/tools must be present on the user's machine.
  * `kubectl`, `istioctl`, `helm`, `jq`, `curl`, `wget`, `git`, `bash`, `envsubst`.
* [Keycloak](keycloak-deployment.md) for Authentication and Sign-in to UI

## Installation

Clone the [https://github.com/openg2p/openg2p-deployment](https://github.com/openg2p/openg2p-deployment) repo and navigate to [kubernetes/logging](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/logging) directory.

### Install OpenSearch (and related components)

*   Run this to install OpenSearch and related components.

    ```bash
    SANDBOX_HOSTNAME="openg2p.sandbox.net" \
        ./install.sh
    ```
* After installation is successful, OpenSearch Dashboards will be accessible at https://opensearch.openg2p.sandbox.net, depending on the hostname given above.

### Install Rancher Logging (Fluentd)

1. On Rancher UI, navigate to Apps (or Apps & Marketplace) -> Charts
2. Search and install Logging from the list, with default values.

### Add _Index State Policy_ on OpenSearch

*   Run this to add ISM Policy (This is responsible for automatically deleting logstash indices after 3 days. Configure the minimum age to delete indices, in the same script below.)

    ```
    ./opensearch-ism-script.sh
    ```

### Configure Rancher FluentD

*   Run this to create _ClusterOutput_ (This is responsible for redirecting all logs to OpenSearch.)

    ```
    kubectl apply -f clusterflow-opensearch.yaml
    ```
*   Run this to create a _ClusterFlow_ (This is responsible for filtering OpenG2P service logs, from the logs of all pods.)

    ```
    kubectl apply -f clusterflow-all.yaml
    ```

### Filters

Note the filters applied in [clusterflow-all.yaml](https://github.com/OpenG2P/openg2p-deployment/blob/main/kubernetes/logging/clusterflow-all.yaml). You may update the same for your install if required, and rerun the apply command.

### Dashboards

* TODO

### TraceId

* TODO

### Troubleshooting

* TODO
