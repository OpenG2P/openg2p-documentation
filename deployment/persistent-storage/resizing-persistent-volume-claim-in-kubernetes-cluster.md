---
description: Guide on Resizing PVC (Persistent Volume Claim) in Kubernetes Cluster
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

# Resizing Persistent Volume Claim in Kubernetes Cluster

When you require additional storage for your application, you may need to resize a Persistent Volume Claim (PVC) in the Kubernetes cluster. This document provides step-by-step instructions to resize a PVC in a Kubernetes cluster.

## **Prerequisites**

* Your PVC's StorageClass has to support volume expansion. Verify that your StorgeClass has `allowVolumeExpansion: true`&#x20;
* Ensure you have the necessary permissions to edit PVCs and resize volumes.

## Resizing a PVC

There may be downtime when resizing a PVC in Kubernetes, especially when transferring data or resizing file systems. To securely resize a PVC, turn off the related service and follow the instructions below.&#x20;

1.  Identify the PVC you want to resize. Run the below command.

    ```bash
    kubectl get pvc -n <namespace>
    ```
2.  Identify the pods that are using this PVC.

    ```bash
    kubectl get pods -n <namespace> --field-selector=spec.volumes.persistentVolumeClaim.claimName=<pvc-name>
    ```

    You must end the running application in order to safely resize the PVC. If the PVC is attached to a Deployment, StatefulSet, or another workload, scale it down to zero replicas.\
    **For a Deployment**

    ```bash
    kubectl scale deployment <deployment_name> --replicas=0 -n <namespace>
    ```

    **For a StatefulSet**

    ```bash
    kubectl scale statefulset <statefulset_name> --replicas=0 -n <namespace>
    ```
3.  Confirm that the pods have been scaled down.

    ```bash
    kubectl get pods -n <namespace>
    ```
4.  Edit the PVC to update the `spec.resources.requests.storage` field with the new size. Run the following command.

    ```bash
    kubectl edit pvc <pvc-name> -n <namespace>
    ```
5.  Edit the storage field to Increase the storage size. For example, change 10GB to 20GB.

    ```yaml
    resources:
      requests:
        storage: 10Gi
    ```
6.  After updating the PVC, check the status to ensure the resize operation succeeds.

    ```shell
    kubectl get pvc <pvc-name> -n <namespace>
    ```
7.  After resizing the PVC and verifying that everything is in order, scale the deployment or stateful set back to its initial number of replicas.\
    **For a Deployment**

    ```
    kubectl scale deployment <deployment-name> --replicas=<desired-count> -n <namespace>
    ```

    **For a StatefulSet**

    ```
    kubectl scale statefulset <statefulset-name> --replicas=<desired-count> -n <namespace>
    ```
8.  Verify that the pods are running

    ```
    kubectl get pods -n <namespace>
    ```

Note:

You can use the Rancher UI to resize the PVC by following the procedures listed above.
