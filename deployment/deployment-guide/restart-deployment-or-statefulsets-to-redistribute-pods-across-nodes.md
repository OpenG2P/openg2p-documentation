---
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

# Redistribute Pods across Nodes by Restarting Deployment/StatefulSets

The document explains how to redistribute pods across nodes by restarting deployment or StatefulSets.

While using Kubernetes, it may be necessary to redistribute pods across nodes to balance the load, apply updates, or manage resource usage. One way to achieve this is to restart the deployment or statefulsets, which will terminate the current pods and create new ones, causing them to be rescheduled across the available nodes.&#x20;

The steps to accomplish this task are given below.

### **Prerequisites**

* You need `kubectl` installed and configured to access your Kubernetes cluster.
* Ensure you have the necessary permissions to manage deployments and statefulsets in your cluster.

### Procedure

1.  Determine the name of the deployment or statefulset you want to restart. You can list them using command below.

    ```
    kubectl get deployments -n <namespace>
    kubectl get statefulsets -n <namespace>
    ```
2.  To restart a deployment, you can use the `kubectl rollout restart` command. This will update the deployment's pods to the latest state and cause them to be rescheduled.

    ```sh
    kubectl rollout restart deployment <deployment-name> -n <namespace>
    ```
3.  Restarting a statefulset is slightly different. You need to update the annotation to trigger a restart.

    ```sh
    kubectl patch statefulset <statefulset-name> -p '{"spec":{"template":{"metadata":{"annotations":{"date":"`date +'%s'`"}}}}}' -n <namespace>
    ```
4.  After restarting the deployment or statefulset, you should verify that the pods are being redistributed and running correctly.

    ```bash
    kubectl get pods -n <namespace>
    ```
5.  Check the status of the pods and ensure they are running on different nodes as expected.

