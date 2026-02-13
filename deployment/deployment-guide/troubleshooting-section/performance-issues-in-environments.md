---
description: >-
  This document explains how to troubleshoot performance issues in the
  environments.
---

# Performance Issues in Environments

### Symptoms <a href="#symptoms" id="symptoms"></a>

Consider the following scenario:

1. When accessing any UI in the OpenG2P environment, pages may load slowly when clicking different buttons to view records.
2. When using `curl` or `ping` on the URL, responses may not be immediate.

### Cause

1. One of the nodes in your Kubernetes cluster may have network-related issues or may not be reachable by other nodes within the network.
2. You might have missed updating the Nginx upstream configuration after adding or removing a node in your Kubernetes cluster.

### Solution <a href="#solution" id="solution"></a>

1. Ping all your Kubernetes nodes from the Nginx node to identify any of that are not reachable. If you find any unreachable nodes, restart them and try pinging again.
2. Whenever you add or remove a node in your Nginx upstream configuration file, make sure to keep it updated.

<br>
