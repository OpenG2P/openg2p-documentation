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

# Rerun Jobs in Kubernetes Cluster

This guide provides instructions on how to rerun jobs in Kubernetes cluster.

In Kubernetes, Jobs are used to rerun tasks that are expected to terminate or end. Sometimes, it may be necessary to rerun a job, either because it failed or because you need to run the task again.&#x20;

Below are the steps to rerun jobs in a Kubernetes cluster.

## **Prerequisites**

* You need `kubectl` installed and configured to access your Kubernetes cluster.
* Ensure you have the necessary permissions to manage jobs in your cluster.

## Procedure&#x20;

1.  Determine the name of the job you want to rerun. You can list the jobs in a namespace.

    ```bash
    kubectl get jobs -n <namespace>
    ```
2.  Delete the current job to rerun a job. This will also delete the associated pods.

    ```bash
    kubectl delete job -n <namespace>
    ```
3.  After deleting the current job, you need to recreate it. You can use the same YAML file or command that was used to create the job initially.

    ```sh
    kubectl apply -f <job-definition-file>.yaml -n <namespace>
    ```
4.  After recreating the job, you should verify that the job has been recreated and is running as expected.

    ```bash
    kubectl get jobs -n <namespace>
    ```
5.  You can monitor the logs of the job's pod to ensure that it is running correctly and completing the task.

    ```sh
    kubectl logs -f job/<job-name> -n <namespace>
    ```
