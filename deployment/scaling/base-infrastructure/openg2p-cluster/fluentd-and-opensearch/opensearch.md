---
description: OpenSearch Deployment
---

# DEPRECATED - OpenSearch

{% hint style="warning" %}
This guide is no longer relevant as OpenSearch is now directly installable with OpenG2P Modules. This guide will soon be removed.
{% endhint %}

Logs captured by [Fluentd](./) from different components are pushed to [OpenSearch](https://opensearch.org/) for search, display, and reports.

## Prerequisites

* The following utilities/tools must be present on the user's machine.
  * `kubectl`, `istioctl`, `helm`, `jq`, `curl`, `wget`, `git`, `bash`, `envsubst`.
* [Keycloak](broken-reference) for Authentication and Sign-in to UI

## Installation

Clone the [https://github.com/openg2p/openg2p-deployment](https://github.com/openg2p/openg2p-deployment) repo and navigate to [kubernetes/logging](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/logging) directory.

### Install OpenSearch (and related components)

*   Run this to install OpenSearch and related components.

    ```bash
    SANDBOX_HOSTNAME="openg2p.sandbox.net" \
        ./install.sh
    ```
* After successful installation, OpenSearch dashboards can be accessed using the hostname given above.

### Add _Index State Policy_ on OpenSearch

*   Run this to add [ISM](https://opensearch.org/docs/latest/im-plugin/ism/index/) Policy (This is responsible for automatically deleting `logstash` indices after 3 days. Configure the minimum age to delete indices, in the same script below.)

    ```bash
    ./opensearch-ism-script.sh
    ```

### Dashboards&#x20;

_TBD_

#### Access control on dashboards:

_TBD_

### TraceId

_TBD_
