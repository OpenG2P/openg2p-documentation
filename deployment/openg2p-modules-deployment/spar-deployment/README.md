---
cover: ../../../.gitbook/assets/SPAR banner-on-light-background.png
coverY: 0
layout:
  cover:
    visible: true
    size: hero
  title:
    visible: true
  description:
    visible: true
  tableOfContents:
    visible: true
  outline:
    visible: true
  pagination:
    visible: true
---

# SPAR Deployment

## Introduction

SPAR deployment comprises deploying the following services on [Kubernetes cluster infrastructure](../../infrastructure-setup/).

* [SPAR Service](../../../platform/modules/social-payments-account-registry-spar.md#spar-service)&#x20;
* [SPAR ID Account Mapper](../../../platform/modules/social-payments-account-registry-spar.md#id-account-mapper)&#x20;
* [SPAR Self Service Portal](../../../platform/modules/social-payments-account-registry-spar.md#spar-self-service-portal) &#x20;

## Prerequisites

* The following utilities/tools must be present on the user's machine.
  * `kubectl`, `istioctl`, `helm`, `jq`, `curl`, `wget`, `git`, `bash`, `envsubst`.
* This module requires kubernetes infrastructure to be setup. For details, [click here](../../infrastructure-setup/)
* [PostgreSQL](../../../guides/deployment-guide/deployment-on-kubernetes/postgresql-server.md)
* SPAR Self Service Portal needs an e-Signet instance to allow login through national ID. To install eSignet on the OpenG2P K8s cluster with mock ID system, use the [eSignet guide](../../external-components-setup/esignet-deployment.md).

## Installation

* Clone the [https://github.com/openg2p/openg2p-deployment](https://github.com/openg2p/openg2p-deployment) repo and navigate to [kubernetes/social-payments-account-registry](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/social-payments-account-registry) directory.
* Configure the values.yaml in this folder according to the components needed. Go over the comments to check what can be added/edited/removed.
*   Run:

    ```bash
    SANDBOX_HOSTNAME=openg2p.sandbox.net \
        ./install.sh
    ```

## Post-installation

After installation, SPAR Self Service portal will be accessible at https://spar.openg2p.sandbox.net, SPAR Service APIs will be accessible at https://spar.openg2p.sandbox.net/spar/v1, and SPAR ID Mapper APIs will be accessible at https://spar.openg2p.sandbox.net/mapper/v1, depending on the hostname given above.

Follow [SPAR Post Installation](spar-post-installation-configuration.md) Guide to finish setup.
