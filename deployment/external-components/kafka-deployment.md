# Kafka Deployment

## Introduction

Skip this if the [realtime reporting framework](https://github.com/openg2p/openg2p-reporting) is not being used.

## Prerequisites

* The following utilities/tools must be present on the user's machine.
  * `kubectl`, `istioctl`, `helm`, `jq`, `curl`, `wget`, `git`, `bash`, `envsubst`.

## Installation

* Clone the [https://github.com/openg2p/openg2p-deployment](https://github.com/openg2p/openg2p-deployment) repo and navigate to [kubernetes/kafka](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/kafka) directory.
*   Run:

    ```bash
    SANDBOX_HOSTNAME="openg2p.sandbox.net" \
        ./install.sh
    ```

## Post-installation

After installation is successful, Kafka UI can be accessed at https://kafka.openg2p.sandbox.net, depending on the hostname given above.
