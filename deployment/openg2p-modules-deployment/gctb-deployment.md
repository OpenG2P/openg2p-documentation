# GCTB Deployment

## Introduction

Refer to [GCTB Concepts](../../platform/modules/g2p-cash-transfer-bridge/) to understand more.

## Prerequisites

* The following utilities/tools must be present on the user's machine.
  * `kubectl`, `istioctl`, `helm`, `jq`, `curl`, `wget`, `git`, `bash`, `envsubst`.
* [PostgreSQL](./#postgresql)

## Installation

* Clone the [https://github.com/openg2p/openg2p-deployment](https://github.com/openg2p/openg2p-deployment) repo and navigate to [kubernetes/g2p-cash-transfer-bridge](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/g2p-cash-transfer-bridge) directory.
*   Run: (This installs the reference package dockers)

    ```bash
    SANDBOX_HOSTNAME=openg2p.sandbox.net \
        ./install.sh
    ```
*   Clone the [https://github.com/OpenG2P/g2p-cash-transfer-bridge](https://github.com/OpenG2P/g2p-cash-transfer-bridge/) repo and navigate to [gctb-mojaloop-sdk-payment-backend](https://github.com/OpenG2P/g2p-cash-transfer-bridge/tree/develop/gctb-mojaloop-sdk-payment-backend). And run:

    ```bash
    kubectl -n gctb create cm gctb-mojaloop-scripts --from-file=payment_backend.py
    kubectl apply -f k8s-mojaloop-payment-backend.yaml
    ```
*   Navigate to [gctb-simple-mpesa-payment-backend](https://github.com/OpenG2P/g2p-cash-transfer-bridge/tree/develop/gctb-simple-mpesa-payment-backend).

    ```bash
    kubectl -n gctb create cm gctb-simple-mpesa-scripts --from-file=payment_backend.py
    kubectl apply -f k8s-simple-mpesa-payment-backend.yaml
    ```

## Post-installation

TODO
