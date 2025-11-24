---
description: >-
  This document outlines the process for scaling down an environment in a
  Kubernetes cluster.
---

# Scaling Down an Environment to Optimize Resource Usage

In cloud environments, resource optimization is crucial to reduce costs and improve efficiency. Scaling down unused or idle environments can significantly save computational resources, such as CPU, memory, and storage, without impacting application availability during inactive periods. By scaling down Kubernetes workloads like **Deployments** and **StatefulSets**, you can effectively manage resource usage and only scale them back up when required.

Here’s an example script that automates this process. The script identifies all Deployments and StatefulSets in a specific namespace and scales them to **0 replicas** when the environment is idle. When the environment is needed again, it scales them back up to **1 replica**.

### **Scaling down**

The script iterates through all Deployments and StatefulSets in the namespace and sets their replicas to `0`. This effectively stops all workloads, freeing up resources such as CPU, memory, and storage.

{% code fullWidth="false" %}
```sh
#!/bin/bash

# Namespace to scale resources (set to 'default' if not specified)
NAMESPACE=${1:-default}

echo "Scaling all Deployments and StatefulSets in the namespace: $NAMESPACE to 0 replicas."

# Scale Deployments to 0 replicas
kubectl -n $NAMESPACE get deployments -o name | while read deployment; do
  echo "Scaling $deployment to 0 replicas."
  kubectl -n $NAMESPACE scale $deployment --replicas=0
done

# Scale StatefulSets to 0 replicas
kubectl -n $NAMESPACE get statefulsets -o name | while read statefulset; do
  echo "Scaling $statefulset to 0 replicas."
  kubectl -n $NAMESPACE scale $statefulset --replicas=0
done

echo "All Deployments and StatefulSets in the namespace: $NAMESPACE have been scaled to 0 replicas."
```
{% endcode %}

### Scaling up

When needed, the script can scale the replicas back to `1`, restoring the environment's operational state. This is particularly useful for testing, staging, or development environments.

{% code fullWidth="false" %}
```sh
#!/bin/bash

# Namespace to scale resources (set to 'default' if not specified)
NAMESPACE=${1:-default}

echo "Scaling all Deployments and StatefulSets in the namespace: $NAMESPACE back to 1 replica."

# Scale Deployments to 1 replica
kubectl -n $NAMESPACE get deployments -o name | while read deployment; do
  echo "Scaling $deployment to 1 replica."
  kubectl -n $NAMESPACE scale $deployment --replicas=1
done

# Scale StatefulSets to 1 replica
kubectl -n $NAMESPACE get statefulsets -o name | while read statefulset; do
  echo "Scaling $statefulset to 1 replica."
  kubectl -n $NAMESPACE scale $statefulset --replicas=1
done

echo "All Deployments and StatefulSets in the namespace: $NAMESPACE have been scaled back to 1 replica."

```
{% endcode %}

### How to use:

1. Ensure you have the permission to access cluster and `kubectl` is installed and properly configured to communicate with your Kubernetes cluster.
2. Save the script to a file, for example, scale\_down\_k8s\_replicas\_to\_one.sh or scale\_down\_k8s\_replicas\_to\_zero.sh.
3. Make the script executable:\
   chmod +x scale\_k8s\_replicas\_to\_one.sh
4. Run the script, specifying the namespace:\
   `./scale_k8s_replicas_to_one.sh <namespace>`
5. Replace \<namespace> with the desired namespace. If no namespace is specified, it defaults to default.\
   Example: `./scale_k8s_replicas_to_one.sh dev`

<br>
