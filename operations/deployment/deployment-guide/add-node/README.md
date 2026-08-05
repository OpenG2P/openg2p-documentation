---
description: >-
  Step-by-step guide to add a new Ubuntu 24.04 node to an existing OpenG2P
  production RKE2 cluster using the bundled add-node automation.
---

# Add Node

This guide walks through adding a **new Kubernetes node** to an existing OpenG2P production cluster. The bundled automation installs RKE2 on the new machine and joins it to the cluster as either a **worker** (data-plane — most common) or a **server** (control-plane — for HA).

{% hint style="info" %}
**Source code:** [`automation/add-node/`](https://github.com/OpenG2P/openg2p-deployment/tree/main/automation/add-node) in the `openg2p-deployment` repository.
{% endhint %}

{% hint style="warning" %}
**Run the join script on the new node — not on your laptop.** `openg2p-add-node.sh` must execute **on the machine you are adding**, with `sudo`. Your workstation is only used to SSH in, copy files, and (optionally) run the AWS provisioner.
{% endhint %}

## Sub-pages

* [AWS provisioning (optional)](aws-provisioning.md) — provision a new EC2 instance before joining the cluster

## Overview

| Phase | Where it runs | Script / action |
| --- | --- | --- |
| **0. Provision VM** (optional) | Your laptop | [AWS add-node provisioning](aws-provisioning.md) — only if you need a new EC2 instance |
| **1. Prepare config** | Your laptop → copy to new node | Edit `add-node-config.yaml` |
| **2. Join cluster** | **On the new node** | `sudo ./openg2p-add-node.sh --config add-node-config.yaml` |
| **3. Verify** | Control-plane node | `kubectl get nodes` |
| **4. Post-install** (optional) | Control-plane / RP | Nginx upstream, Istio ingress spread |

The join automation handles:

* Configuration validation and connectivity check to the RKE2 supervisor (TCP **9345**)
* `ufw` firewall rules aligned with the production cluster
* RKE2 install and cluster join
* Basic health verification

It does **not** install Wireguard, Nginx, NFS, Rancher, or Keycloak — those remain on the existing platform nodes.

## Before you start

### Cluster must already be running

This guide assumes you completed the [production infrastructure automation](../../infrastructure-setup/production-automation/) and have a working RKE2 cluster with at least one control-plane (`rke2-server`) node.

### Choose a role

| Role | RKE2 service | When to choose |
| --- | --- | --- |
| **worker** | `rke2-agent` | Scale application capacity. **Default choice** for most add-node operations. |
| **server** | `rke2-server` | Add a control-plane node for HA. Use an **odd** number of servers (3, 5, …). |

You can set `node_role` in the config file or let the script prompt interactively. Override on the CLI with `--role worker` or `--role server`.

### Hardware

Match or exceed the original [Compute node minimums](../../prerequisites-procurement.md#compute-the-four-vms):

| | Minimum (worker) | Notes |
| --- | --- | --- |
| OS | Ubuntu Server **24.04 LTS** amd64 | Required — the script hard-checks the version |
| vCPU | 16 | Same as the initial Compute node |
| RAM | 64 GB | Same as the initial Compute node |
| Root disk | 128 GB SSD | gp3 or equivalent |
| Network | Same VPC / private subnet as the cluster | Private IP reachability to the control-plane |

Smaller instances may work for light workloads but are not validated by OpenG2P preflight.

### Network access

From the **new node**, confirm:

* TCP **9345** to a control-plane node's **private IP** (RKE2 supervisor) — required for join
* TCP **6443**, **10250**, **2379**, **2380**, **8472** (UDP), **2049**, NodePort range — allowed by `ufw` rules the script applies within the VPC CIDR
* Outbound internet during install (apt, `get.rke2.io`, `dl.k8s.io`)

On **AWS**, the new instance must use a security group that allows intra-VPC traffic (reusing the production Compute SG is typical). See [troubleshooting](#troubleshooting) if the connectivity check fails.

### Optional: provision the VM on AWS

If you already have a VM (on-prem, another cloud, or manually created EC2), skip to [Step 1](#step-1-gather-cluster-details-from-the-control-plane).

If you need a new EC2 instance in an existing VPC, follow the optional guide first:

➡️ **[AWS add-node provisioning (optional)](aws-provisioning.md)**

That page provisions a single Ubuntu 24.04 instance and writes `provision-output.yaml` with the instance's private IP, SSH details, and suggested `node_name`. Return here when the instance is running and SSH-reachable.

---

## Step 1: Gather cluster details from the control-plane

SSH to **any existing control-plane node** (a machine where `rke2-server` is active):

```bash
# Confirm this is a server node
systemctl is-active rke2-server
# → active

# RKE2 join token (copy the full value, including the K10… prefix)
sudo cat /var/lib/rancher/rke2/server/node-token

# Installed RKE2 version — must match on the new node
rke2 --version
# e.g. rke2 version v1.33.6+rke2r1

# Private IP of this control-plane node (use for server_url when nodes share a VPC)
ip -4 addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | grep -v 127.0.0.1 | head -1
```

Also note:

| Value | Example | Where to use |
| --- | --- | --- |
| Control-plane private IP | `172.29.0.198` | `server_url` → `https://172.29.0.198:9345` |
| Join token | `K10abc…::server:…` | `rke2_token` |
| RKE2 version | `v1.33.6+rke2r1` | `rke2_version` |
| VPC CIDR | `172.29.0.0/16` | `vpc_subnet` |
| Wireguard peer subnet | `10.15.0.0/16` (default) | `wireguard_subnet` — must match the RP |

{% hint style="info" %}
**`server_url` uses port 9345, not 6443.** Port 9345 is the RKE2 supervisor (join protocol). Port 6443 is the Kubernetes API — do not put that in `server_url`.
{% endhint %}

To find the Wireguard subnet on the Reverse Proxy:

```bash
ip -br addr show wg0
# e.g. wg0  UNKNOWN  10.15.0.1/16  →  wireguard_subnet: 10.15.0.0/16
```

---

## Step 2: Copy the automation to the new node

From your **laptop**, copy the `add-node` directory onto the new machine:

```bash
# Replace <SSH_HOST> with the new node's public or private IP
# Replace <KEY> with your SSH private key path
scp -i <KEY> -r \
  /path/to/openg2p-deployment/automation/add-node \
  ubuntu@<SSH_HOST>:~/
```

SSH into the new node:

```bash
ssh -i <KEY> ubuntu@<SSH_HOST>
```

---

## Step 3: Configure `add-node-config.yaml`

On the **new node**:

```bash
cd ~/add-node
cp add-node-config.example.yaml add-node-config.yaml
vi add-node-config.yaml   # or your preferred editor
```

Fill in every required field:

```yaml
# Control-plane supervisor — private IP when in the same VPC
server_url: "https://172.29.0.198:9345"

# From: sudo cat /var/lib/rancher/rke2/server/node-token
rke2_token: "K10xxxxxxxx::server:xxxxxxxx"

# Must match the cluster exactly
rke2_version: "v1.33.6+rke2r1"

# This new node's private IP
node_ip: "172.29.11.168"

# Unique Kubernetes node name (kubectl get nodes)
node_name: "openg2p-cluster-node-2"

# worker (typical) or server (HA control-plane)
node_role: "worker"

# VPC CIDR for ufw inter-node rules
vpc_subnet: "172.29.0.0/16"

# Must match the RP Wireguard subnet
wireguard_subnet: "10.15.0.0/16"
```

{% hint style="warning" %}
**`server_url` format:** exactly `https://<host>:9345` — no extra slashes. `https:////172.29.0.198:9345` will fail validation.
{% endhint %}

If you used [AWS add-node provisioning](aws-provisioning.md), copy `private_ip` and `instance_name` from `aws/provision-output.yaml` into `node_ip` and `node_name`.

---

## Step 4: Run the join script (on the new node)

Still on the **new node**, as root:

```bash
cd ~/add-node
sudo ./openg2p-add-node.sh --config add-node-config.yaml
```

Optional flags:

| Flag | Purpose |
| --- | --- |
| `--role worker` / `--role server` | Override `node_role` from config |
| `--force` | Clear step markers and re-run all steps (after a partial failure) |
| `--reset` | Clear state markers and exit (does not join) |

The script runs five steps:

1. **Validate** — config fields, `server_url` format, TCP reachability to port 9345
2. **Tools** — apt packages (`curl`, `jq`, `nfs-common`, …); `kubectl` on server role only
3. **Firewall** — `ufw` rules for SSH, VPC inter-node ports, Wireguard subnet
4. **RKE2** — writes `/etc/rancher/rke2/config.yaml`, installs and starts `rke2-agent` or `rke2-server`
5. **Verify** — server nodes wait for `Ready` locally; worker nodes confirm `rke2-agent` is active

Logs are written to `/var/log/openg2p-add-node-<timestamp>.log`.

On success, a post-install guide is saved to `/root/openg2p-add-node-postinstall.txt`.

---

## Step 5: Verify from the control-plane

SSH to a **control-plane node** and confirm the new node appears:

```bash
export KUBECONFIG=/etc/rancher/rke2/rke2.yaml
export PATH="$PATH:/var/lib/rancher/rke2/bin"

kubectl get nodes -o wide
kubectl describe node <node_name>
kubectl get pods -A -o wide | grep <node_name>
```

The new node should reach **Ready** within one to two minutes. If it stays **NotReady**, check on the new node:

```bash
sudo journalctl -u rke2-agent -n 100 --no-pager   # worker
sudo journalctl -u rke2-server -n 100 --no-pager  # server
```

---

## Step 6: Post-install (optional)

These steps are **not** automated. Details are also in `/root/openg2p-add-node-postinstall.txt` on the new node.

### Redistribute workloads

After the node is Ready, restart Deployments or StatefulSets if you want pods spread onto the new capacity:

➡️ [Restart Deployment or StatefulSets to Redistribute Pods across Nodes](../../../../deployment/deployment-guide/redistribute-pods-across-nodes-by-restarting-deployment-statefulsets.md)

### Nginx upstream (load-balancing across nodes)

By default, Nginx on the Reverse Proxy forwards only to the original Compute node's Istio NodePort (`30080`). To load-balance across multiple nodes, add the new node's private IP to the upstream on the RP:

```bash
# On the Reverse Proxy
sudo vi /etc/nginx/sites-available/openg2p-infra.conf
```

```nginx
upstream istio_ingress {
    server <primary-compute-ip>:30080;
    server <new-node-ip>:30080;
}
```

```bash
sudo nginx -t && sudo systemctl reload nginx
```

This only helps if `istio-ingressgateway` pods can run on the new node — see the next section.

### Istio ingress on additional nodes (advanced HA)

The default Istio operator config pins ingress to nodes labelled `shouldInstallIstioIngress=true` (typically only the original Compute node). Running ingress on multiple nodes requires pod anti-affinity in the Istio operator config and labelling the new node. See the post-install guide on the node for the full procedure.

### NFS

No action needed on the new node — `nfs-common` is installed by the script so pods can mount PVCs from the Storage node's NFS export.

---

## Removing a node

Removal is a separate workflow. Run `openg2p-remove-node.sh` on a **control-plane node** (not on the node being removed):

```bash
cd ~/add-node   # copy the directory to the control-plane if needed
sudo ./openg2p-remove-node.sh --node <node_name>
```

This cordons, drains, and deletes the Kubernetes node object. The script prints manual cleanup commands to run on the removed machine (RKE2 uninstall, state cleanup, optional Nginx upstream edit).

If the node was provisioned with the optional AWS script, tear down the EC2 instance separately:

➡️ [AWS add-node provisioning → Teardown](aws-provisioning.md#teardown)

For the legacy manual RKE2 procedure, see [Adding and Removing Nodes in Cluster](../adding-and-removing-nodes-in-cluster.md).

---

## Troubleshooting

### `Unsupported Ubuntu version: 22.04`

You are running `openg2p-add-node.sh` on the wrong machine (e.g. your laptop). SSH to the **new Ubuntu 24.04 node** and run the script there.

### `Cannot reach <ip>:9345`

From the **new node**:

```bash
nc -zv 172.29.0.198 9345
ping -c2 172.29.0.198
```

On the **control-plane**:

```bash
systemctl is-active rke2-server
sudo ss -lntp | grep 9345
sudo ufw status
```

Common causes:

| Cause | Fix |
| --- | --- |
| Wrong `server_url` (extra `/`, wrong port, public IP when only private works) | Use `https://<private-ip>:9345` |
| AWS Security Group blocks 9345 from the new node | Allow TCP 9345 from the new node's IP or the VPC CIDR |
| `ufw` on control-plane blocks the new node's IP | Production nodes allow the full VPC CIDR — verify `vpc_subnet` in config |
| Pointed at a worker node | `server_url` must target a **server** (`rke2-server`), not an agent |

### `Configuration validation failed` / missing keys

Ensure every field in [Step 3](#step-3-configure-add-node-configyaml) is filled. Compare against `add-node-config.example.yaml`.

### `rke2-agent` / `rke2-server` failed to start

```bash
sudo journalctl -u rke2-agent -n 100 --no-pager
cat /etc/rancher/rke2/config.yaml
```

Check `rke2_token` and `rke2_version` match the cluster. A version mismatch prevents join.

### Re-run after a partial failure

```bash
sudo ./openg2p-add-node.sh --config add-node-config.yaml --force
```

If RKE2 was half-installed from a previous attempt:

```bash
sudo /usr/local/bin/rke2-killall.sh 2>/dev/null || true
sudo /usr/local/bin/rke2-uninstall.sh 2>/dev/null || true
sudo ./openg2p-add-node.sh --config add-node-config.yaml --force
```

### AWS instance provisioned but join still fails

Confirm you completed [Step 3](#step-3-configure-add-node-configyaml) with values from `provision-output.yaml` **and** the cluster join values from [Step 1](#step-1-gather-cluster-details-from-the-control-plane). The AWS script only creates the VM — it does not join the cluster.

---

## Related guides

* [AWS add-node provisioning (optional)](aws-provisioning.md)
* [Production infrastructure automation](../../infrastructure-setup/production-automation/)
* [Prerequisites & Procurement](../../prerequisites-procurement.md)
* [Private Access Channel](../private-access-channel.md)
* [Adding and Removing Nodes in Cluster](../adding-and-removing-nodes-in-cluster.md) (legacy manual procedure)
