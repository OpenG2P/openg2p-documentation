---
description: Work in progress
---

# Deployment on Kubernetes

## Prerequisites

* Kubernetes Cluster, with given [requirements](broken-reference). Use this guide to [setup the K8s Cluster](broken-reference).

## Installation

* This section assumes the OpenG2P docker is already packaged. See Packaging Instructions.
* Clone the [https://github.com/OpenG2P/openg2p-packaging](https://github.com/OpenG2P/openg2p-packaging)  and go to [charts/openg2p](https://github.com/OpenG2P/openg2p-packaging/tree/develop/charts/openg2p) directory
  *   Run, (This installs the ref-impl dockers):

      ```
      ./install.sh \
          --set global.hostname=openg2p.sandbox.net \
          --set global.selfServiceHostname=selfservice.openg2p.sandbox.net
      ```
  *   If use different docker image or tag use:

      ```
      ./install.sh \
          --set odoo.image.repository=<docker image name> \
          --set odoo.image.tag=<docker image tag> \
          --set global.hostname=openg2p.sandbox.net \
          --set global.selfServiceHostname=selfservice.openg2p.sandbox.net
      ```

## ODK Installation

*   From the [charts/odk-central](https://github.com/OpenG2P/openg2p-packaging/tree/develop/charts/odk-central) directory, run the following to install ODK helm chart.

    ```
    ./install.sh \
        --set global.hostname=openg2p.sandbox.net
    ```
*   Note: The above helm chart uses the following docker images built from [https://github.com/getodk/central/tree/v2023.1.0](https://github.com/getodk/central/tree/v2023.1.0), since ODK Central doesn't provide pre-built docker images for these.

    ```
    openg2p/odk-central-backend:v2023.1.0
    openg2p/odk-central-frontend:v2023.1.0
    openg2p/odk-central-enketo:v2023.1.0
    ```
* Post installation:
  *   Exec into the service pod, and create user (and promote if required).

      ```
      kubectl exec -it <service-pod> -- odk-cmd -u <email> user-create
      kubectl exec -it <service-pod> -- odk-cmd -u <email> user-promote
      ```
* Uninstallation:
  *   To uninstall, just delete the helm installation of odk-central. Example:

      ```
      helm -n odk delete odk-central
      ```
