---
description: >-
  Step-by-step guide to add a new Ubuntu 24.04 node to an existing OpenG2P
  RKE2 cluster — run from your admin laptop over SSH.
---

# Add Node

This guide walks through adding a **new Kubernetes node** to an existing OpenG2P RKE2 cluster. The automation runs on your **admin laptop**: it SSHes into the new Ubuntu 24.04 machine, stages the join scripts, and installs RKE2 as either a **worker** (most common) or a **server** (HA control-plane).

{% hint style="info" %}
**Source code:** [`automation/add-node/`](https://github.com/OpenG2P/openg2p-deployment/tree/main/automation/add-node) in the `openg2p-deployment` repository.
{% endhint %}

{% hint style="success" %}
**Run from your laptop — do not use `sudo` on the laptop.** The orchestrator connects as `ubuntu` (or your `ssh_user`) and uses passwordless sudo **on the remote node**. Running `sudo ./openg2p-add-node.sh` on an Ubuntu 22.04 laptop will fail the OS check incorrectly — that check now runs on the remote node only.
{% endhint %}

## Sub-pages

* [AWS provisioning (optional)](aws-provisioning.md) — provision a new EC2 instance before joining

## Overview

| Phase | Where it runs | Script / action |
| --- | --- | --- |
| **0. Provision VM** (optional) | Laptop | [AWS add-node provisioning](aws-provisioning.md) — `openg2p-aws-provision.sh` |
| **1. Configure** | Laptop | Edit `add-node-config.yaml` (SSH + join fields) |
| **2. Join cluster** | Laptop → SSH → new node | `./openg2p-add-node.sh --config add-node-config.yaml` |
| **3. Verify** | Control-plane | `kubectl get nodes` |
| **4. Post-install** (optional) | Control-plane / RP | Nginx upstream, Istio ingress |

The laptop orchestrator:

1. Loads config (+ optional `aws/provision-output.yaml` overlay)
2. Probes SSH + passwordless sudo on the new node
3. Stages `roles/join/` + libs + config to `/tmp/openg2p-add-node` on the node
4. Runs the remote join under sudo (ufw, RKE2 install, cluster join)

## Before you start

### Cluster must already be running

You need a working RKE2 cluster with at least one control-plane (`rke2-server`) node.

### Hardware (new node)

| | Minimum (worker) |
| --- | --- |
| OS | Ubuntu Server **24.04 LTS** amd64 |
| vCPU / RAM / disk | Match [Compute minimums](../../prerequisites-procurement.md#compute-the-four-vms) (16 / 64 GB / 128 GB) |
| Network | Same VPC as the cluster; TCP **9345** to a control-plane private IP |

### Optional: provision the VM on AWS

➡️ **[AWS add-node provisioning (optional)](aws-provisioning.md)**

After AWS provision succeeds, `aws/provision-output.yaml` supplies `ssh_host`, `ssh_user`, `ssh_key`, `private_ip`, and `instance_name` automatically when you run the join script from `automation/add-node/`.

---

## Step 1: Gather cluster details from a control-plane

On any existing **control-plane** node:

```bash
systemctl is-active rke2-server
sudo cat /var/lib/rancher/rke2/server/node-token
rke2 --version
```

Note the control-plane **private IP** for `server_url` (`https://<private-ip>:9345`).

---

## Step 2: Configure `add-node-config.yaml` (on the laptop)

```bash
cd automation/add-node
cp add-node-config.example.yaml add-node-config.yaml
vi add-node-config.yaml
```

Minimum fields:

```yaml
# How THIS laptop reaches the NEW node
ssh_host: "13.x.x.x"          # public IP (or private if on VPN)
ssh_user: "ubuntu"
ssh_key:  "/home/you/sshkeys/openg2p.pem"

# Join parameters
server_url: "https://172.29.0.198:9345"
rke2_token: "K10…::server:…"
rke2_version: "v1.33.6+rke2r1"
node_ip: "172.29.4.176"
node_name: "worker"
node_role: "worker"
vpc_subnet: "172.29.0.0/16"
wireguard_subnet: "10.15.0.0/16"
```

{% hint style="warning" %}
**`server_url` format:** exactly `https://<ip>:9345` — no extra slashes.
{% endhint %}

For remove-node later, also set `primary_ssh_host` (SSH to a control-plane).

---

## Step 3: Probe SSH (optional)

From the **laptop** (no sudo):

```bash
./openg2p-add-node.sh --config add-node-config.yaml --probe
```

Confirms SSH + passwordless sudo on the new node.

---

## Step 4: Join the cluster (from the laptop)

```bash
# Preview
./openg2p-add-node.sh --config add-node-config.yaml --dry-run

# Join
./openg2p-add-node.sh --config add-node-config.yaml
```

| Flag | Purpose |
| --- | --- |
| `--role worker` / `--role server` | Override `node_role` |
| `--force` | Re-run remote steps (clear markers on the node) |
| `--dry-run` | Probe SSH; print what would be staged/run; change nothing |
| `--probe` | SSH + sudo check only |
| `--help`, `-h` | Show help |

Remote steps (on the node): validate → apt tools → ufw → RKE2 join → verify.

Logs on the laptop: `automation/add-node/logs/add-node-*.log`.

---

## Step 5: Verify

On a control-plane:

```bash
export KUBECONFIG=/etc/rancher/rke2/rke2.yaml
export PATH="$PATH:/var/lib/rancher/rke2/bin"
kubectl get nodes -o wide
```

---

## Removing a node

From the **laptop** (needs `primary_ssh_*` in config):

```bash
./openg2p-remove-node.sh --config add-node-config.yaml --node worker --dry-run
./openg2p-remove-node.sh --config add-node-config.yaml --node worker
```

The script asks for confirmation before cordoning / draining / deleting the node. Type `yes` to proceed, or pass `--yes` (`-y`) to skip the prompt (CI / automation).

Then clean RKE2 on the removed machine (commands printed by the script). If it was an AWS add-node instance:

➡️ [AWS add-node provisioning → Tearing down](aws-provisioning.md#tearing-down)

---

## Troubleshooting

### `Unsupported Ubuntu version: 22.04` on the laptop

You ran an **old** on-node script with `sudo` on your laptop. Use the current laptop orchestrator **without** `sudo`:

```bash
./openg2p-add-node.sh --config add-node-config.yaml
```

The Ubuntu 24.04 check runs on the **remote** node.

### SSH / sudo probe failed

```bash
ssh -i /path/to/key.pem ubuntu@<ssh_host>
sudo -n true
```

Ensure the security group allows SSH from your laptop and the user has NOPASSWD sudo.

### `Cannot reach <ip>:9345` (on the remote node)

From the new node (or after join starts failing):

```bash
nc -zv 172.29.11.236 9345
```

Fix SG / ufw on the control-plane so TCP 9345 is allowed from the VPC CIDR.

### Missing `ssh_host` / `ssh_key`

Set them in `add-node-config.yaml`, or re-run AWS provision so `aws/provision-output.yaml` exists next to the script.

---

## Related guides

* [AWS add-node provisioning (optional)](aws-provisioning.md)
* [Prerequisites & Procurement](../../prerequisites-procurement.md)
* [Adding and Removing Nodes in Cluster](../adding-and-removing-nodes-in-cluster.md) (legacy manual)
