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

# Load Balancer

Load balancing (LB) is essential to ensure high availability, scalability, and reliability of applications running within the cluster. It involves distributing incoming network traffic across multiple pods or nodes to optimise resource utilisation and prevent any single point of failure. LB also isolates the internal network from the external world avoiding users directly accessing the nodes of the Kubernetes cluster.&#x20;

For a sandbox, to conserve resources LB may be skipped. See figure below.



{% embed url="https://miro.com/app/board/uXjVKOxj1TU=/" %}

<table><thead><tr><th width="203">Setup</th><th>LB type</th></tr></thead><tbody><tr><td>Sandbox</td><td>LB not required. Direct connection to nodes and traffic distribution via <a href="../cluster-setup.md#istio">Istio</a> Ingress Gateway.</td></tr><tr><td>Pilot/Production </td><td><a href="aws.md">Cloud LB</a> or <a href="nginx.md">Nginx </a></td></tr></tbody></table>
