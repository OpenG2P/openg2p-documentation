---
description: Firewall setup for Kubernetes cluster nodes
---

# Firewall

To set up the Kubernetes cluster, you need to open a few ports on all nodes as mentioned below.&#x20;

## Firewall rules

Set up firewall rules on each node according to the following table.&#x20;

<table><thead><tr><th width="126">Protocol</th><th width="144">Port</th><th width="272">Access</th><th>Purpose</th></tr></thead><tbody><tr><td>TCP</td><td>22</td><td>Public/Internet</td><td>SSH</td></tr><tr><td>TCP</td><td>80</td><td>Public/Internet</td><td>HTTP</td></tr><tr><td>TCP</td><td>443</td><td>Public/Internet</td><td>HTTPS</td></tr><tr><td>TCP</td><td>5432</td><td>Intranet</td><td>Postgres</td></tr><tr><td>TCP</td><td>9345</td><td>Intranet</td><td>RKE</td></tr><tr><td>TCP</td><td>6443</td><td>Intranet</td><td>K8s API</td></tr><tr><td>UDP</td><td>8472</td><td>Intranet</td><td>K8s Flannel VXLAN</td></tr><tr><td>TCP</td><td>10250</td><td>Intranet</td><td>kubelet</td></tr><tr><td>TCP</td><td>2379</td><td>Intranet</td><td>etcd client</td></tr><tr><td>TCP</td><td>2380</td><td>Intranet</td><td>etcd peer </td></tr><tr><td>TCP</td><td>9796</td><td>Intranet</td><td>Prometheus </td></tr><tr><td>TCP</td><td>30000:32767</td><td>Intranet</td><td>K8s NodePort </td></tr></tbody></table>

### Firewall setup&#x20;

The exact method to set up the firewall rules will vary from cloud to cloud and on-prem. (For example on AWS, EC2 security groups can be used. For on-prem cluster, ufw can be used and so on)

#### Using Ansible

* On your machine install `ansible`
* Make sure you have SSH access to all nodes of the cluster
* Create `hosts.ini` file. Sample given [here](https://github.com/OpenG2P/openg2p-deployment/tree/main/ansible).
* Copy [`ports.yaml`](https://github.com/OpenG2P/openg2p-deployment/blob/main/ansible/ports.yaml) file and inspect for any changes w.r.t to above table.
* Run

```shell-session
ansible-playbook -i hosts.ini ports.yaml
```

#### Manual

* You can use `ufw` to set up the firewall on each cluster node.
  * SSH into each node, and change to superuser
  *   Run the following command for each rule in the above table

      ```
      ufw allow from <from-ip-range-allowed> to any port <port/range> proto <tcp/udp>
      ```
  *   Example:

      ```
      ufw allow from any to any port 22 proto tcp
      ufw allow from 10.3.4.0/24 to any port 9345 proto tcp
      ```
  *   Enable ufw:

      ```
      ufw enable
      ufw default deny incoming
      ```
* Additional Reference: [RKE2 Networking Requirements](https://docs.rke2.io/install/requirements#networking)

