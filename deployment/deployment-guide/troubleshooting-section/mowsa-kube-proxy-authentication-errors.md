---
description: >-
  Troubleshooting PostgreSQL connection timeouts caused by Kubernetes
  ClusterIP Service routing issues and kube-proxy API authentication
  errors observed in the MOWSA environment.
---

# MOWSA: Kubernetes ClusterIP Service Routing Timeouts After Kube-Proxy API Authentication Errors
## 1. Problem Description
During deployment in the MOWSA environment, pods running in the `nsr-v2` namespace, particularly `commons-keycloak` and PostgreSQL initialization jobs, experienced connection timeouts when attempting to access PostgreSQL through the Kubernetes ClusterIP Service `commons-postgresql:5432`.

The `commons-keycloak-0` pod showed readiness issues and repeated restarts. Its logs indicated that connections to PostgreSQL were repeatedly timing out.

Further investigation identified Kubernetes API authentication errors in the `kube-proxy` logs on the affected worker node, `kubernet2`.

## 2. Inspect Keycloak Logs

Check the logs of the `commons-keycloak-0` pod in the `nsr-v2` namespace:

```bash
kubectl logs -n nsr-v2 commons-keycloak-0 -c keycloak --tail=100
```

The logs showed that Keycloak was attempting to establish a connection to PostgreSQL:

```text
Trying to connect to PostgreSQL server commons-postgresql...
```

However, the connection attempts repeatedly failed with the following error:

```text
timeout reached before the port went into state "inuse"
```

This message appeared multiple times, indicating that Keycloak could not establish a PostgreSQL connection within the configured timeout.

Although the logs confirmed the connection timeout, further investigation was necessary to determine the underlying cause.

## 3. Inspect Kube-Proxy Logs

To investigate the connectivity issue, check the `kube-proxy` pod running on the affected worker node, `kubernet2`.

Identify the `kube-proxy` pod:

```bash
kubectl get pods -n kube-system -o wide | grep kube-proxy-kubernet2
```

Follow the pod logs:

```bash
kubectl logs -n kube-system kube-proxy-kubernet2 -f
```

The logs showed repeated Kubernetes API authentication errors while `kube-proxy` attempted to access Services, EndpointSlices, and Nodes.

The following errors were observed:

```text
failed to list *v1.Service: Unauthorized
Failed to watch *v1.Service: failed to list *v1.Service: Unauthorized
failed to list *v1.EndpointSlice: Unauthorized
Failed to watch *v1.EndpointSlice: failed to list *v1.EndpointSlice: Unauthorized
failed to list *v1.Node: Unauthorized
Failed to watch *v1.Node: failed to list *v1.Node: Unauthorized
```

These errors indicated that `kube-proxy` was encountering authentication failures when communicating with the Kubernetes API server.

Since `kube-proxy` relies on these resources to maintain Kubernetes Service routing, the authentication failures suggested a possible connection to the observed PostgreSQL connectivity issue.

However, the available logs did not conclusively establish the underlying cause of the authentication failures.

## 4. Solution

### 4.1 Restart the RKE2 Agent

To address the issue, restart the RKE2 agent on the affected worker node, `kubernet2`:

```bash
sudo systemctl restart rke2-agent
```

> **Note:** Restarting the RKE2 agent may temporarily affect workloads running on the node. Perform this operation with appropriate precautions.

After the restart, verify that the RKE2 agent is running:

```bash
sudo systemctl status rke2-agent
```

The service reported the following status:

```text
Active: active (running)
```

This confirmed that the RKE2 agent restarted successfully and was running.

## 5. Verify Kube-Proxy Recovery

After restarting the RKE2 agent, check the latest `kube-proxy` logs from `kubernet1`:

```bash
kubectl logs -n kube-system kube-proxy-kubernet2 --tail=20
```

The logs showed successful `kube-proxy` initialization and cache synchronization:

```text
Using iptables Proxier
Caches are synced for service config
Caches are synced for node config
Caches are synced for endpoint slice config
```

These messages confirmed that `kube-proxy` successfully initialized and synchronized its Service, Node, and EndpointSlice configuration after the RKE2 agent restart.

## 6. Post-Restart Verification

After confirming that `kube-proxy` has synchronized successfully, verify the status of the affected node and workloads.

### 6.1 Check Node Status

Check the Kubernetes node status:

```bash
kubectl get nodes
```

Confirm that the affected worker node, `kubernet2`, reports a `Ready` status.

### 6.2 Check Affected Workloads

Check the pods running in the `nsr-v2` namespace:

```bash
kubectl get pods -n nsr-v2
```

Review the status and restart counts of `commons-keycloak` and the PostgreSQL initialization jobs to determine whether the affected workloads are operating normally.

Inspect the Keycloak logs again:

```bash
kubectl logs -n nsr-v2 commons-keycloak-0 -c keycloak --tail=100
```

Verify that Keycloak can establish a connection to PostgreSQL and that the previous connection timeout messages no longer occur.

Application recovery should only be considered confirmed after the affected workloads are healthy and PostgreSQL connectivity has been successfully verified.

---

**Note:** This troubleshooting guide documents an issue encountered in the MOWSA environment. The namespace, pod names, and node names are specific to this deployment and may differ in other OpenG2P environments.
