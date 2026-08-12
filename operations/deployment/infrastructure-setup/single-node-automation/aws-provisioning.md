---
description: >-
  Optional AWS provisioning for the single-node sandbox — creates one EC2
  instance (m5a.4xlarge), security group, Elastic IP, and writes
  provision-output.yaml for the single-node install
---

# AWS Provisioning

The bundled AWS provisioning is a separate, optional step that creates a **single** Ubuntu 24.04 EC2 instance (`m5a.4xlarge` by default) and the supporting AWS resources, then writes `provision-output.yaml` for the single-node install scripts to consume. Lives at `automation/single-node/aws/`.

Use it if you don't already have a VM. If you have your own VM (other clouds, on-prem, manual EC2), skip this page and go straight to [Quick Start](./#quick-start) on the sandbox page.

{% hint style="info" %}
**Flow:** optional AWS provisioning (this page) → [laptop orchestrator `openg2p-single-node.sh`](./) → on-box infra + environment scripts over SSH. Creates one EC2 instance; you drive the install from your laptop.
{% endhint %}

## Prerequisites

|                     |                                                                                                                                                                                                                                                                                 |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **AWS CLI**         | v2 installed on your laptop. `aws --version` should print `aws-cli/2.x`.                                                                                                                                                                                                        |
| **AWS credentials** | Configured via `aws configure`, environment variables, or an `AWS_PROFILE`. The script honours `AWS_REGION`, `AWS_PROFILE`, and `AWS_DEFAULT_REGION`.                                                                                                                           |
| **`jq`**            | Not required (we deliberately avoid the dependency).                                                                                                                                                                                                                            |
| **Permissions**     | The IAM user/role needs the EC2 permissions listed below.                                                                                                                                                                                                                       |
| **EIP quota**       | Prefer **one free Elastic IP** in the target region (default quota is 5). The provisioner allocates one EIP for Wireguard endpoint stability. If quota is exhausted, it falls back to the instance's ephemeral public IP and continues with a warning.                        |

## IAM permissions

Minimum EC2 IAM permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "ec2:DescribeVpcs",
      "ec2:DescribeSubnets",
      "ec2:DescribeImages",
      "ec2:DescribeInstances",
      "ec2:DescribeInstanceStatus",
      "ec2:DescribeKeyPairs",
      "ec2:DescribeSecurityGroups",
      "ec2:DescribeAddresses",
      "ec2:DescribeNetworkInterfaces",
      "ec2:CreateKeyPair",
      "ec2:DeleteKeyPair",
      "ec2:CreateSecurityGroup",
      "ec2:DeleteSecurityGroup",
      "ec2:AuthorizeSecurityGroupIngress",
      "ec2:RevokeSecurityGroupIngress",
      "ec2:AllocateAddress",
      "ec2:ReleaseAddress",
      "ec2:AssociateAddress",
      "ec2:DisassociateAddress",
      "ec2:RunInstances",
      "ec2:TerminateInstances",
      "ec2:ModifyInstanceAttribute",
      "ec2:CreateTags",
      "sts:GetCallerIdentity",
      "tag:GetResources"
    ],
    "Resource": "*"
  }]
}
```

`AmazonEC2FullAccess` plus `sts:GetCallerIdentity` and `tag:GetResources` also works.

## What gets created

All resources are tagged with `Project=<project>` and `ManagedBy=openg2p-aws-single-node` so destroy only removes this provisioner's resources.

| Resource       | Default name                   | Configurable    | Notes                                                                                                                                 |
| -------------- | ------------------------------ | --------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| Key pair       | `openg2p-sandbox-key`          | `key_name`      | Created if missing; .pem saved to `aws/keys/` mode 0400                                                                               |
| Security group | `openg2p-sandbox-single-node`  | `sg_name`       | Admin SSH (`admin_cidr`), Wireguard UDP, private 80/443 (or public if `public_web: true`), all intra-VPC. Reused if exists; rules added if missing. |
| **Elastic IP** | tagged `Role=single-node-eip`  | —               | Preferred for Wireguard endpoint stability. Soft-fallback to ephemeral public IP if EIP quota is exhausted.                           |
| Instance       | `openg2p-sandbox-single-node`  | `instance_name` | `m5a.4xlarge`, 128 GB gp3, source/dest check disabled (Wireguard)                                                                    |

## Default sizing

Matches the OpenG2P [single-node resource requirements](https://docs.openg2p.org/deployment/resource-requirements#single-node).

| Role        | Instance type | vCPU | RAM   | Root disk (gp3) |
| ----------- | ------------- | ---- | ----- | --------------- |
| Single-node | `m5a.4xlarge` | 16   | 64 GB | 128 GB          |

Configurable via `instance_type`, `disk_gb`, `disk_iops`, `disk_throughput` in `aws-config.yaml`. Larger is fine; smaller will fail the infra script's prerequisite check.

## About the Elastic IP

The single-node instance gets an Elastic IP when quota allows. **Why?** The Wireguard `Endpoint` in every peer config is this public IP. An EIP survives instance stop/start; a dynamic IP would change and break peer configs.

**When EIP quota is exhausted:** the provisioner logs a warning and continues with the auto-assigned public IP. Free an unused EIP (or raise the quota) and re-run later if you want a stable endpoint:

```bash
aws ec2 describe-addresses --query 'Addresses[?AssociationId==null].[AllocationId,PublicIp]' --output table
aws ec2 release-address --allocation-id <alloc-id>
```

## Workflow

```bash
# On your laptop — provision (optional):
cd automation/single-node/aws
cp aws-config.example.yaml aws-config.yaml
# Edit aws-config.yaml — minimum: project, region.
# Leave vpc_id, subnet_id, key_mode blank to be prompted interactively.
# Prefer project: "openg2p-sandbox".

./openg2p-aws-provision.sh --config aws-config.yaml
# ~5–8 minutes. Creates resources, waits for status checks AND SSH.
# Writes ../provision-output.yaml

# Still on your laptop — install (orchestrator SSHes into the VM):
cd ..
cp single-node-config.example.yaml single-node-config.yaml
cp env-config.example.yaml   env-config.yaml
# Optional: install_environment: false  — infra only; install env later
./openg2p-single-node.sh --config single-node-config.yaml --probe
./openg2p-single-node.sh --config single-node-config.yaml
# Writes setup-output/SETUP-SUMMARY.txt (env URLs if install_environment: true)
# Stages automation/single-node/ to /tmp/openg2p-deploy/ on the VM,
# runs roles/infra/run.sh then openg2p-environment.sh under sudo,
# pulls peer1.conf / CA / kubeconfig into ./artifacts/

# Later — remove one environment (keeps infra):
#   ./openg2p-environment-uninstall.sh --config env-config.yaml
# Tear down all infra (keeps the VM / EC2):
#   ./openg2p-single-node-uninstall.sh --config single-node-config.yaml
# Destroy the EC2 resources:
#   cd aws && ./openg2p-aws-destroy.sh --config aws-config.yaml
```

## `admin_cidr` and `public_web`

| Key | Blank / false | Explicit |
| --- | ------------- | -------- |
| `admin_cidr` | Defaults to `0.0.0.0/0` (SSH from any IP) | Office/VPN CIDR locks SSH/ICMP |
| `public_web` | `false` — 80/443 only from VPC CIDR | `true` — 80/443 open to `0.0.0.0/0` (pair with `public_access: true` in `single-node-config.yaml`) |

Intra-VPC traffic is always allowed separately (covers K8s API, RKE2, NFS, Wireguard-decapsulated access).

## Interactive selection (default)

When `vpc_id`, `subnet_id`, or `key_mode` are blank, the script queries AWS and presents a numbered menu. Selections are written back to `aws-config.yaml`. For CI, pass `--non-interactive` and pre-fill all required values.

## Reusing an existing security group

Set `sg_name` to an existing SG name in the VPC. The script reuses it, adds any missing ingress rules, and never removes rules.

If you already have an EC2 instance and only need the SG, the standalone helper still exists:

```bash
./create-security-group.sh --vpc-id vpc-xxxxxxxxx
```

Prefer `openg2p-aws-provision.sh` for new sandboxes.

## `provision-output.yaml` — what the orchestrator consumes

After provisioning succeeds, `provision-output.yaml` sits next to `single-node-config.yaml`:

```yaml
# AUTO-GENERATED by aws/openg2p-aws-provision.sh
node_ip:   "10.0.1.50"
node_name: "openg2p-sandbox-single-node"
wireguard:
  endpoint: "13.x.x.x"
public_ip:  "13.x.x.x"
private_ip: "10.0.1.50"
ssh_host:   "13.x.x.x"
ssh_user:   "ubuntu"
ssh_key:    "./aws/keys/openg2p-sandbox-key.pem"
```

`openg2p-single-node.sh` (and on-box `roles/infra/run.sh`) auto-detect this file next to `single-node-config.yaml` and load it as an overlay — AWS-derived keys win on conflict. Your hand-edited preferences in `single-node-config.yaml` (`cluster_name`, `local_domain`, etc.) are never overwritten by the provisioner.

## Tearing down

```bash
cd automation/single-node/aws
./openg2p-aws-destroy.sh --config aws-config.yaml
```

Confirms by asking you to type the project name back, then deletes resources tagged `Project=<project>` **and** `ManagedBy=openg2p-aws-single-node`:

| # | Resource | How it gets deleted |
| - | -------- | ------------------- |
| 1 | EC2 instance | `terminate-instances` + wait |
| 1 | Root EBS / primary ENI | Auto-deleted with the instance |
| 2 | Elastic IP | `release-address` |
| 3 | Security group | `delete-security-group` |
| 4 | Key pair | Only if script-created (`ManagedBy=openg2p-aws-single-node`). Keep with `--keep-key`. |
| 5 | Stray volumes / snapshots / ENIs | Explicit delete |
| 6 | `../provision-output.yaml` | Removed |
| 7 | Final sweep | Lists anything still tagged |

{% hint style="warning" %}
Destroy only touches resources tagged `ManagedBy=openg2p-aws-single-node`. Prefer a distinct `project:` (e.g. `openg2p-sandbox`).
{% endhint %}

## Costs (rough, us-east-1, on-demand)

| Item | $/hour | $/month (730 h) |
| ---- | ------ | --------------- |
| `m5a.4xlarge` | $0.688 | \~$502 |
| EIP (attached) | free | $0 |
| EBS gp3 128 GB | $0.08/GB-month | \~$10 |
| **Total** | | **\~$512/month** if running 24/7 |

Stop the instance when not using it to drop EC2 charges (you still pay for EBS). Keep the EIP attached so the Wireguard endpoint survives stop/start.

## Troubleshooting

**SSH times out after changing Wi‑Fi / ISP** — with default `admin_cidr` (`0.0.0.0/0`) this should not happen. If you locked `admin_cidr` to a previous `/32`, update it and re-run the provisioner (adds missing ingress; never removes rules).

**VPC not found** — create a default VPC, set `vpc_id` / `subnet_id`, or leave them blank and pick interactively.

**EIP `AddressLimitExceeded`** — soft-fallback to ephemeral public IP. Free an unused EIP and re-run if you want a stable Wireguard endpoint.

**Infra script can't find `node_ip`** — ensure `provision-output.yaml` is next to `single-node-config.yaml` on the laptop (orchestrator merges it when staging), or set `node_ip` / `wireguard.endpoint` / `ssh_*` by hand.

**Orchestrator SSH probe fails** — confirm `ssh_key` points at the `.pem`, security group allows your IP on TCP/22, and the instance passed status checks. Re-run `./openg2p-single-node.sh --config single-node-config.yaml --probe`.

## Related documentation

* [Sandbox — Single-Node](./) — install / uninstall from the laptop (`openg2p-single-node.sh`, `openg2p-environment.sh`, and their `*-uninstall.sh` counterparts)
