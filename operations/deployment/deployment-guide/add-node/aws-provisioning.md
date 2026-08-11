---
description: >-
  Optional AWS EC2 provisioning for a new OpenG2P cluster node — creates a
  single Ubuntu instance in an existing VPC and writes provision-output.yaml.
---

# AWS Add-Node Provisioning

The bundled AWS add-node provisioner is a separate, optional step that creates **one** Ubuntu 24.04 LTS EC2 instance in an existing VPC / security group, then writes `provision-output.yaml` for the [Add Node](README.md) join workflow. Lives at `automation/add-node/aws/`.

Use it if you need a new EC2 instance. If you already have a VM (on-prem, another cloud, manually created EC2), skip this page and go straight to [Add Node → Step 1](README.md#step-1-gather-cluster-details-from-the-control-plane).

{% hint style="info" %}
**Add-node flow:** (optional) **AWS provision** (this page) → [Join cluster](README.md) (on the new node) → verify with `kubectl`
{% endhint %}

{% hint style="info" %}
**Source code:** [`automation/add-node/aws/`](https://github.com/OpenG2P/openg2p-deployment/tree/main/automation/add-node/aws) in the `openg2p-deployment` repository.
{% endhint %}

This script **only provisions the VM**. Joining the cluster is a separate step — [Add Node](README.md) — run from your **admin laptop** after SSH is working.

## Prerequisites

| | |
| --- | --- |
| **AWS CLI** | v2 installed on your laptop. `aws --version` should print `aws-cli/2.x`. |
| **AWS credentials** | Configured via `aws configure`, environment variables, or an `AWS_PROFILE`. Honours `AWS_REGION`, `AWS_PROFILE`. |
| **Bash** | 4+ (`bash --version`) |
| **Existing AWS resources** | VPC, subnet (public if you SSH from the internet), security group, EC2 key pair |
| **Permissions** | `ec2:Describe*`, `ec2:RunInstances`, `ec2:TerminateInstances`, `ec2:CreateTags`, `sts:GetCallerIdentity` |

Use a **`project` tag value** that matches the Project tag on your existing cluster resources so they stay grouped.

### Security group

Reuse your cluster **Compute** security group (`<project>-k8s-node`) or any SG that allows:

* SSH (TCP 22) from your admin CIDR
* **All intra-VPC traffic** (required for RKE2 ports 9345, 6443, 10250, etc.)

The add-node provisioner does **not** create or modify security group rules.

## What gets created

All resources are tagged with `Project=<project>` and `ManagedBy=openg2p-aws-add-node` so destroy / `--force` never touch instances tagged `ManagedBy=openg2p-aws-provision`.

| Resource | Notes |
| --- | --- |
| EC2 instance | Ubuntu 24.04 LTS, encrypted gp3 root volume |
| `provision-output.yaml` | IPs, SSH paths, suggested `node_name` |

**Never created:** VPC, subnets, security groups, Elastic IPs. Key pairs are reused (or created only if you choose “create new” in the interactive menu).

## Default sizing

| Setting | Default | Config key |
| --- | --- | --- |
| Instance type | `t3a.2xlarge` (8 vCPU, 32 GB) | `instance_type` |
| Root disk | 128 GiB gp3, encrypted | `disk_gb` |
| OS | Ubuntu 24.04 LTS (latest Canonical AMI) | `ubuntu_ami` (blank = auto-resolve) |

Match or exceed the [Compute node minimums](../../prerequisites-procurement.md#compute-the-four-vms) for your cluster workloads.

## Workflow

```bash
cd automation/add-node/aws
cp aws-config.example.yaml aws-config.yaml
# Edit aws-config.yaml — minimum: project, region.
# Leave vpc_id, az, subnet_id, sg_id, key_mode blank to be prompted interactively.

# Optional: preview without creating anything
./openg2p-aws-provision.sh --config aws-config.yaml --dry-run

./openg2p-aws-provision.sh --config aws-config.yaml
# Waits for status checks AND SSH (unless --skip-ssh-wait).
# Writes ./provision-output.yaml.
```

Then continue with the cluster join from your **laptop** (no sudo):

➡️ **[Add Node](README.md)**

```bash
cd automation/add-node
./openg2p-add-node.sh --config add-node-config.yaml --probe
./openg2p-add-node.sh --config add-node-config.yaml
```

`aws/provision-output.yaml` is auto-loaded for `ssh_host`, `ssh_user`, `ssh_key`, `node_ip`, and `node_name`. You still need `server_url`, `rke2_token`, and `rke2_version` from a control-plane — see [Add Node → Step 1](README.md#step-1-gather-cluster-details-from-a-control-plane).

## Interactive selection (default)

When placement / key / sizing keys are blank in `aws-config.yaml`, the script queries AWS and presents numbered menus. Selections are written back to `aws-config.yaml` so subsequent runs are stable.

Prompts cover: instance type, root disk size, VPC, Availability Zone, subnet, security group, key pair, and instance Name tag.

For CI / automation, pass `--non-interactive` and pre-fill all required values.

## Options reference

### Provision — `openg2p-aws-provision.sh`

| Option | Purpose |
| --- | --- |
| `--config <file>` | AWS add-node config (required) |
| `--non-interactive` | Never prompt — fail if any required value is unspecified |
| `--skip-ssh-wait` | Don't wait for SSH after status checks |
| `--ssh-timeout <sec>` | SSH wait timeout (default: 600) |
| `--force` | Terminate an existing add-node instance with the same Name, then launch fresh |
| `--dry-run` | Resolve selection and print what would be launched; create nothing |
| `--help`, `-h` | Show help |

**`--dry-run`**: still checks credentials and resolves VPC / SG / AMI / etc., then prints the planned launch and exits. Does not call `RunInstances`, terminate, wait for SSH, or write `provision-output.yaml`.

**`--force`** is useful when a previous launch failed mid-way. It only replaces instances tagged `ManagedBy=openg2p-aws-add-node` (or listed in `provision-output.yaml`).

### Destroy — `openg2p-aws-destroy.sh`

| Option | Purpose |
| --- | --- |
| `--config <file>` | AWS add-node config (required) |
| `--instance-id <id>` | Explicit instance to terminate (skips auto-detect) |
| `--yes` / `-y` | Skip confirmation (type instance Name) |
| `--dry-run` | Resolve the target and print what would be deleted; change nothing |
| `--help`, `-h` | Show help |

**Target resolution** (first match):

1. `--instance-id` if provided
2. `instance_id` in `provision-output.yaml`
3. `instance_name` in `aws-config.yaml` (with `ManagedBy=openg2p-aws-add-node`)
4. Interactive menu of add-node instances in the project

## `provision-output.yaml`

Written automatically after a successful provision. Example:

```yaml
# AUTO-GENERATED by aws/openg2p-aws-provision.sh — overwritten on every run.
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

## Tearing down

```bash
cd automation/add-node/aws

# Preview
./openg2p-aws-destroy.sh --config aws-config.yaml --dry-run

./openg2p-aws-destroy.sh --config aws-config.yaml
# Confirm by typing the instance Name tag (or pass --yes)
```

This terminates the add-node instance and removes `provision-output.yaml`. It does **not**:

* Delete the security group, VPC, or subnet
* Delete your SSH key pair
* Remove the node from the Kubernetes cluster (run `openg2p-remove-node.sh` on the control-plane first — see [Add Node → Removing a node](README.md#removing-a-node))

Recommended order when decommissioning:

1. [Remove from cluster](README.md#removing-a-node) (`openg2p-remove-node.sh` on control-plane)
2. Clean up RKE2 on the node (commands printed by remove script)
3. Destroy EC2 instance (`openg2p-aws-destroy.sh` on laptop)

## Troubleshooting

### Key file not found locally

If a previous interactive run saved `key_path` to a default under `aws/keys/` but your `.pem` lives elsewhere, either:

* Update `key_path` in `aws-config.yaml` to the real location, or
* Re-run — the script re-prompts for the local `.pem` when the saved path is missing

### Instance launched but no public IP

Pick a subnet with `MapPublicIpOnLaunch=true`, or SSH via a bastion / VPN using the private IP from `provision-output.yaml`.

### Re-provision after failure

```bash
./openg2p-aws-provision.sh --config aws-config.yaml --force
```

### Cluster join errors after AWS provision

See [Add Node → Troubleshooting](README.md#troubleshooting). The AWS script only creates the VM.

## Related guides

* [Add Node](README.md) — main cluster join guide
* [Prerequisites & Procurement](../../prerequisites-procurement.md)
