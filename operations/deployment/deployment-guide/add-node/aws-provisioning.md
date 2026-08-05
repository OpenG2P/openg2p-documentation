---
description: >-
  Optional AWS EC2 provisioning for a new OpenG2P cluster node — creates a
  single Ubuntu instance in an existing VPC and writes provision-output.yaml.
---

# AWS Add-Node Provisioning

The bundled AWS add-node provisioner is an **optional prerequisite** for [Add Node](README.md). Use it when you need a **new EC2 instance** in an existing AWS VPC and want an interactive, repeatable way to launch it.

{% hint style="info" %}
**When to skip this page:** you already have a VM (on-prem, another cloud, manually created EC2, or a hypervisor clone). Go straight to [Add Node → Step 1](README.md#step-1-gather-cluster-details-from-the-control-plane).
{% endhint %}

{% hint style="info" %}
**Source code:** [`automation/add-node/aws/`](https://github.com/OpenG2P/openg2p-deployment/tree/main/automation/add-node/aws) in the `openg2p-deployment` repository.
{% endhint %}

This script **only provisions the VM**. Joining the cluster is a separate step — [Add Node](README.md) — run **on the new instance** after SSH is working.

## What it does

| Creates | Does not create |
| --- | --- |
| 1 × Ubuntu 24.04 LTS EC2 instance | Security groups (reuses an existing SG in your VPC) |
| Encrypted gp3 root volume | VPC, subnets, or route tables |
| `provision-output.yaml` (IPs, SSH paths) | Key pairs (reuses existing, or creates one if you choose) |
| Tags: `Project`, `ManagedBy=openg2p-aws-add-node`, `Name` | Cluster join / RKE2 install |

The destroy script removes **only** the instance this tool created. It never touches production cluster nodes (`ManagedBy=openg2p-aws-provision`), shared security groups, VPCs, or pre-existing key pairs.

## Prerequisites

| | Requirement |
| --- | --- |
| **Where to run** | Your laptop (same as [production AWS provisioning](../../infrastructure-setup/production-automation/aws-provisioning.md)) |
| **AWS CLI** | v2 — `aws --version` |
| **Credentials** | Configured via `aws configure`, `AWS_PROFILE`, or environment variables |
| **Bash** | 4+ (`bash --version`) |
| **Existing AWS resources** | VPC, subnet (with public IP if you SSH from the internet), security group, EC2 key pair |
| **IAM permissions** | `ec2:Describe*`, `ec2:RunInstances`, `ec2:TerminateInstances`, `ec2:CreateTags`, `sts:GetCallerIdentity` |

Use the **same `project` tag value** as your production AWS config so resources stay grouped.

### Security group

Reuse the production **Compute** security group (`<project>-k8s-node`) or any SG that allows:

* SSH (TCP 22) from your admin CIDR
* **All intra-VPC traffic** (the production SG opens the full VPC CIDR — required for RKE2 ports 9345, 6443, 10250, etc.)

The add-node provisioner does **not** create or modify security group rules.

### Default sizing

| Setting | Default | Config key |
| --- | --- | --- |
| Instance type | `t3a.2xlarge` (8 vCPU, 32 GB) | `instance_type` |
| Root disk | 128 GiB gp3, encrypted | `disk_gb` |
| OS | Ubuntu 24.04 LTS (latest Canonical AMI) | `ubuntu_ami` (auto-resolve if blank) |

Match or exceed the [Compute node minimums](../../prerequisites-procurement.md#compute-the-four-vms) for production workloads.

---

## Workflow

```bash
cd automation/add-node/aws
cp aws-config.example.yaml aws-config.yaml
# Edit project + region at minimum

./openg2p-aws-provision.sh --config aws-config.yaml
```

The script is **interactive** when config keys are blank. It prompts for (and saves back to `aws-config.yaml`):

1. EC2 instance type (default `t3a.2xlarge`)
2. Root EBS volume size (default 128 GiB gp3)
3. VPC
4. Availability Zone (AZs that have subnets in the VPC)
5. Subnet in that AZ (prefers `MapPublicIpOnLaunch=true`)
6. Security Group in the VPC
7. EC2 key pair (existing or create new)
8. Instance Name tag

After launch it waits for:

* EC2 status checks **ok**
* SSH reachable (unless `--skip-ssh-wait`)

Then it writes `provision-output.yaml` next to the script.

### Continue with cluster join

Return to the main guide:

➡️ **[Add Node](README.md)**

Use values from `provision-output.yaml`:

| `provision-output.yaml` | `add-node-config.yaml` |
| --- | --- |
| `private_ip` | `node_ip` |
| `instance_name` | `node_name` |

You still need `server_url`, `rke2_token`, and `rke2_version` from an existing control-plane node — see [Add Node → Step 1](README.md#step-1-gather-cluster-details-from-the-control-plane).

---

## Configuration reference

`aws-config.example.yaml` documents every key. Minimum to set before the first run:

```yaml
project: "openg2p-prod"    # match production AWS config
region: "ap-south-1"
```

Leave placement keys blank for interactive selection on first run:

```yaml
vpc_id:    ""
az:        ""
subnet_id: ""
sg_id:     ""
```

Key pair (typical for add-node — reuse the production key):

```yaml
key_mode: "existing"
key_name: "openg2p-prod-key"
key_path: "/home/you/.ssh/openg2p-prod-key.pem"
```

---

## CLI options

### Provision

```bash
./openg2p-aws-provision.sh --config aws-config.yaml [options]
```

| Option | Purpose |
| --- | --- |
| `--non-interactive` | Fail instead of prompting (all required keys must be in config) |
| `--skip-ssh-wait` | Skip SSH wait after status checks |
| `--ssh-timeout <sec>` | SSH wait timeout (default 600) |
| `--force` | Terminate an existing add-node instance with the same Name, then launch fresh |
| `--help` | Show usage |

**`--force`** is useful when a previous launch failed mid-way (instance stuck, wrong subnet, etc.). It only replaces instances tagged `ManagedBy=openg2p-aws-add-node` (or listed in `provision-output.yaml`).

### Destroy

```bash
./openg2p-aws-destroy.sh --config aws-config.yaml [options]
```

| Option | Purpose |
| --- | --- |
| `--instance-id <id>` | Target a specific instance (skips auto-detect) |
| `--yes` / `-y` | Skip confirmation (type instance name) |
| `--help` | Show usage |

**Target resolution** (first match):

1. `--instance-id` if provided
2. `instance_id` in `provision-output.yaml`
3. `instance_name` in `aws-config.yaml` (with `ManagedBy=openg2p-aws-add-node`)
4. Interactive menu of add-node instances in the project

Confirmation requires typing the instance **Name** tag (unless `--yes`).

---

## `provision-output.yaml`

Written automatically after a successful provision. Example:

```yaml
instance_id:     "i-0acf756d167187715"
instance_name:   "openg2p-cluster-node-2"
instance_type:   "t3a.2xlarge"
private_ip:      "172.29.11.168"
public_ip:       "13.201.50.158"
ssh_host:        "13.201.50.158"
ssh_user:        "ubuntu"
ssh_key:         "/path/to/key.pem"
```

SSH to the instance:

```bash
ssh -i /path/to/key.pem ubuntu@<ssh_host>
```

---

## Teardown

When you no longer need the EC2 instance (before or after removing it from Kubernetes):

```bash
cd automation/add-node/aws
./openg2p-aws-destroy.sh --config aws-config.yaml
```

This terminates the add-node instance and removes `provision-output.yaml`. It does **not**:

* Delete the security group, VPC, or subnet
* Delete your SSH key pair
* Remove the node from the Kubernetes cluster (run `openg2p-remove-node.sh` on the control-plane first — see [Add Node → Removing a node](README.md#removing-a-node))

Recommended order when decommissioning:

1. [Remove from cluster](README.md#removing-a-node) (`openg2p-remove-node.sh` on control-plane)
2. Clean up RKE2 on the node (commands printed by remove script)
3. [Destroy EC2 instance](#teardown) (`openg2p-aws-destroy.sh` on laptop)

---

## Troubleshooting

### Key file not found locally

If a previous interactive run saved `key_path` to a default under `aws/keys/` but your `.pem` lives elsewhere, either:

* Update `key_path` in `aws-config.yaml` to the real location, or
* Re-run — the script re-prompts for the local `.pem` when the saved path is missing

### `Cannot reach //<ip>:9345` during cluster join

That error comes from the **join script** on the node, not this AWS provisioner. See [Add Node → Troubleshooting](README.md#troubleshooting).

### Instance launched but no public IP

Pick a subnet with `MapPublicIpOnLaunch=true`, or SSH via a bastion / VPN using the private IP from `provision-output.yaml`.

### Re-provision after failure

```bash
./openg2p-aws-provision.sh --config aws-config.yaml --force
```

---

## Related guides

* [Add Node](README.md) — main cluster join guide
* [Production AWS provisioning](../../infrastructure-setup/production-automation/aws-provisioning.md) — initial three-node fleet
* [Prerequisites & Procurement](../../prerequisites-procurement.md)
