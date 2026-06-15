---
description: >-
  Optional AWS provisioning for the production infrastructure — creates the
  EC2 instances (Reverse Proxy, Compute, Storage, and the Backup node),
  security groups, Elastic IP, and writes provision-output.yaml for the
  orchestrator to consume.
---

# AWS Provisioning (optional)

The bundled AWS provisioning is a separate, optional step that creates the EC2 instances — Reverse Proxy, Compute, Storage, and (with `backup_node.enabled: true`) the Backup node — and the supporting AWS resources, then writes `provision-output.yaml` for the orchestrator to consume. Lives at `automation/production/aws/`.

Use it if you don't already have VMs. If you have your own VMs (other clouds, on-prem, manual EC2), skip this page and go straight to [Step 1 of the infrastructure automation](README.md#step-1-clone-and-configure).

{% hint style="info" %}
**Production deployment flow:**  [1. Procurement](../../prerequisites-procurement.md)  →  **2. Provisioning** ([overview](../provisioning.md) · AWS path = this page)  →  [3. Infrastructure](README.md)  →  [4. Environment](../../environment-setup-multi-node.md)  →  [5. Modules](../../environment-setup-multi-node.md#next-install-your-openg2p-modules)
{% endhint %}

## Prerequisites

|                     |                                                                                                                                                                                                                                                                                                                                                                                                            |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **AWS CLI**         | v2 installed on your laptop. `aws --version` should print `aws-cli/2.x`.                                                                                                                                                                                                                                                                                                                                   |
| **AWS credentials** | Configured via `aws configure`, environment variables, or an `AWS_PROFILE`. The script honours `AWS_REGION`, `AWS_PROFILE`, and `AWS_DEFAULT_REGION`.                                                                                                                                                                                                                                                      |
| **`jq`**            | Not required (we deliberately avoid the dependency).                                                                                                                                                                                                                                                                                                                                                       |
| **Permissions**     | The IAM user/role needs the EC2 permissions listed below.                                                                                                                                                                                                                                                                                                                                                  |
| **EIP quota**       | At least **one Elastic IP free** in the target region. AWS's default per-region quota is 5 EIPs. The provisioner allocates one EIP for the RP (Wireguard endpoint stability across stop/start — see [About the Elastic IP](#about-the-elastic-ip)). If you're at quota, free one first (see [About the Elastic IP](#about-the-elastic-ip)) before running the provisioner. |

## IAM permissions

The provisioning script needs a moderately broad set of EC2 permissions. The minimal set:

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

If you have full EC2 admin (`AmazonEC2FullAccess` managed policy + `sts:GetCallerIdentity` + `tag:GetResources`), that works too.

## What gets created

All resources are tagged with `Project=<project>` so the destroy script can find and remove them later.

| Resource          | Default name                    | Configurable      | Notes                                                                                                                                                                                                                 |
| ----------------- | ------------------------------- | ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Key pair          | `openg2p-prod-key`              | `key_name`        | Created if missing; .pem saved to `aws/keys/` mode 0400                                                                                                                                                               |
| SG: RP            | `openg2p-prod-reverse-proxy`    | `rp_sg_name`      | Single SG: admin SSH (`admin_cidr`), Wireguard UDP, and all intra-VPC. Public `80/443` are **not** opened here — admin tools stay private; env automation opens them later. Reused if exists; rules added if missing. |
| SG: Compute       | `openg2p-prod-k8s-node`         | `compute_sg_name` | Same                                                                                                                                                                                                                  |
| SG: Storage       | `openg2p-prod-storage`          | `storage_sg_name` | Same                                                                                                                                                                                                                  |
| **Elastic IP**    | tagged `Role=reverse-proxy-eip` | —                 | One EIP allocated and associated with the RP. Script **hard-fails** on `AddressLimitExceeded`. See below for why.                                                                                                     |
| Instance: RP      | `openg2p-prod-reverse-proxy`    | `rp_name`         | `t3a.medium`, 64 GB gp3, **single ENI**                                                                                                                                                                               |
| Instance: Compute | `openg2p-prod-k8s-node-1`       | `compute_name`    | `m5a.4xlarge`, 128 GB gp3                                                                                                                                                                                             |
| Instance: Storage | `openg2p-prod-storage`          | `storage_name`    | `t3a.2xlarge`, 256 GB gp3                                                                                                                                                                                             |

## Default sizing

Matches the OpenG2P resource minimums.

| Role          | Instance type | vCPU | RAM   | Root disk (gp3) |
| ------------- | ------------- | ---- | ----- | --------------- |
| Reverse Proxy | `t3a.medium`  | 2    | 4 GB  | 64 GB           |
| Compute / K8s | `m5a.4xlarge` | 16   | 64 GB | 128 GB          |
| Storage       | `t3a.2xlarge` | 8    | 32 GB | 256 GB          |

All sizes are configurable in `aws-config.yaml` via `*_instance_type`, `*_disk_gb`, `*_disk_iops`, `*_disk_throughput`. Larger is fine; smaller may fail the orchestrator's preflight.

## About the Elastic IP

Only the reverse-proxy node gets an Elastic IP. Compute and storage use AWS's auto-assigned dynamic public IPs (which is fine — those public IPs are only used for SSH from your laptop).

**Why an EIP, not a dynamic public IP?** The Wireguard `Endpoint` line in every peer config is the RP's public IP. An EIP survives instance stop/start; a dynamic IP would change after any stop/start and break every peer config you've already distributed. AWS single-NIC launches _do_ technically support auto-assigned public IPs, but for production stability we always use an EIP.

**Behaviour when the EIP quota is exhausted:** if your AWS account is at the default 5-EIP per-region limit, `AllocateAddress` returns `AddressLimitExceeded` and the provisioner **hard-fails** at step 2 ("Allocating Elastic IP for RP"). No instances have been launched yet, so there's nothing to clean up — just free an EIP (or request a quota increase) and re-run.

**To check your current EIP usage and free unused ones:**

```bash
# How many EIPs are allocated in this region (compared to the quota of 5):
aws ec2 describe-addresses --query 'length(Addresses)'

# List EIPs that are allocated but not associated with any instance (these are safe to release):
aws ec2 describe-addresses --query 'Addresses[?AssociationId==null].[AllocationId,PublicIp]' --output table

# Release one:
aws ec2 release-address --allocation-id <alloc-id>
```

**During teardown**, `openg2p-aws-destroy.sh` automatically releases every EIP tagged `Project=<project>` (step 2 of the destroy flow), so the EIP returns to your pool for reuse on the next provision. No manual cleanup needed.

## Workflow

```bash
cd automation/production/aws
cp aws-config.example.yaml aws-config.yaml
# Edit aws-config.yaml — minimum: project, region.
# Leave vpc_id, subnet_id, key_mode blank to be prompted interactively.

./openg2p-aws-provision.sh --config aws-config.yaml
# ~5–8 minutes. Creates resources, waits for status checks AND SSH on
# all 3 instances before declaring done. Writes ../provision-output.yaml.

cd ..
cp prod-config.example.yaml prod-config.yaml
# Edit prod-config.yaml — only USER PREFERENCES (no IPs needed).

./openg2p-prod.sh --probe     --config prod-config.yaml
./openg2p-prod.sh --preflight --config prod-config.yaml
./openg2p-prod.sh             --config prod-config.yaml
```

## Interactive selection (default)

When `vpc_id`, `subnet_id`, or `key_mode` are blank in `aws-config.yaml`, the script queries AWS and presents a numbered menu — no need to leave the terminal to look anything up. Example:

```
[INFO] No vpc_id in config — querying available VPCs...
[INFO] Multiple VPCs available in region ap-south-1:
  [1] vpc-0a1b2c3d4e5f67890  10.0.0.0/16 (default)
  [2] vpc-0123456789abcdef0  10.10.0.0/16 — staging
  [3] vpc-abcdef0123456789a  10.20.0.0/16 — prod
  Select [1-3] or paste VPC ID:
```

Your selection is written back to `aws-config.yaml`, so the next run is fully non-interactive. The same applies to subnet selection and key-pair selection (existing AWS key pairs are listed alongside a "Create new" option).

For CI / automation, pass `--non-interactive` and pre-fill all required values. The script will fail loudly (with a list of options) on anything ambiguous.

## Reusing existing security groups

If your infra team has already created security groups, point the `*_sg_name` fields in `aws-config.yaml` at their names. The script:

1. **Reuses** the existing SG (no new SG created).
2. **Verifies** the required ingress rules — adds any that are missing, leaves the rest alone.
3. **Never removes** rules.

Per-rule status is logged so you can see what was added vs already present:

```
+ TCP/22  from 203.0.113.5/32: added
· ICMP    from 203.0.113.5/32: already present
· UDP/51820 (Wireguard) from 0.0.0.0/0: already present
```

## `provision-output.yaml` — what the orchestrator consumes

After AWS provisioning succeeds, the orchestrator's `prod-config.yaml` does not need any IPs or SSH paths. Those live in a sibling file `provision-output.yaml`:

```yaml
# AUTO-GENERATED by aws/openg2p-aws-provision.sh — overwritten on every run.
rp_public_ip:    "13.x.x.x"
rp_private_ip:   "10.0.1.50"
rp_ssh_host:     "13.x.x.x"
rp_ssh_user:     "ubuntu"
rp_ssh_key:      "./aws/keys/openg2p-prod-key.pem"
compute_private_ip:  "10.0.1.51"
compute_ssh_host:    "<dynamic-public>"
# ... etc
private_subnet:  "10.0.0.0/16"
admin_cidr:      "203.0.113.5/32"
wg_endpoint:     "13.x.x.x"
```

The orchestrator auto-detects this file next to `prod-config.yaml` and loads it as an overlay — its keys win on conflict. Re-running AWS provisioning regenerates it cleanly (single `.prev` archive, no timestamped backup churn). Your hand-edited `prod-config.yaml` is never touched.

## Tearing down

```bash
cd automation/production/aws
./openg2p-aws-destroy.sh --config aws-config.yaml
```

Confirms by asking you to type the project name back, then deletes everything tagged `Project=<project>`:

| # | Resource                                                          | How it gets deleted                                                                                                                                                              |
| - | ----------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1 | EC2 instances                                                     | `terminate-instances` + wait for `terminated`                                                                                                                                    |
| 1 | Root EBS volumes                                                  | Auto-deleted with the instance (created with `DeleteOnTermination: true`)                                                                                                        |
| 1 | Primary ENI                                                       | Auto-deleted with the instance                                                                                                                                                   |
| 2 | Elastic IPs                                                       | `release-address`                                                                                                                                                                |
| 3 | Security groups                                                   | `delete-security-group`                                                                                                                                                          |
| 4 | Key pair                                                          | **Only deleted if WE created it** (tagged `Project=<project>` `ManagedBy=openg2p-aws-provision`). Pre-existing keys imported by the user are kept. Force-keep with `--keep-key`. |
| 5 | **Stray EBS volumes** in `available` / `creating` / `error` state | Explicit `delete-volume` — catches volumes detached from instances or extras attached after provisioning                                                                         |
| 5 | **Stray snapshots** owned by you, tagged with the project         | Explicit `delete-snapshot`                                                                                                                                                       |
| 5 | **Stray ENIs** in `available` state, tagged                       | Explicit `delete-network-interface`                                                                                                                                              |
| 6 | `../provision-output.yaml`                                        | Removed (stale after teardown)                                                                                                                                                   |
| 7 | Final sweep                                                       | Lists anything **still** tagged `Project=<project>` so leaks are visible                                                                                                         |

A clean teardown ends with `Nothing left tagged Project=<project>`.

{% hint style="warning" %}
The destroy script only touches resources tagged `Project=<project>`. If you've created VPC peering, NAT gateways, EFS file systems, or anything else that you tagged with the same project, those will appear in the final sweep — review the list before assuming "all clean."
{% endhint %}

{% hint style="info" %}
**Before re-provisioning into the same config directory:** the teardown removes `provision-output.yaml`, but it does **not** clear the orchestrator's laptop-side state under `automation/production/.state/`. If you provision new VMs and re-run the install with the same `prod-config.yaml`, those stale markers will make the orchestrator skip every phase. Run `./openg2p-prod.sh --reset-laptop --config prod-config.yaml` after teardown (or before the next install) to start clean.
{% endhint %}

## Costs (rough, us-east-1, on-demand)

| Item                                      | $/hour         | $/month (730 h)                  |
| ----------------------------------------- | -------------- | -------------------------------- |
| `t3a.medium` (RP)                         | $0.0376        | \~$27                            |
| `m5a.4xlarge` (Compute)                   | $0.688         | \~$502                           |
| `t3a.2xlarge` (Storage)                   | $0.301         | \~$220                           |
| EIP (attached)                            | free           | $0                               |
| EIP (released-but-unattached)             | $0.005         | \~$3.65                          |
| EBS gp3 storage (64 + 128 + 256 = 448 GB) | $0.08/GB-month | \~$36                            |
| **Total**                                 |                | **\~$785/month** if running 24/7 |

Stop instances when not using them to drop EC2 charges to near-zero (you still pay for EBS). The EIP stays attached to the (stopped) RP, so the Wireguard endpoint survives stop/start when present.

## Troubleshooting

**AWS provision: "VPC not found"** — some accounts have no default VPC. Either create one (`aws ec2 create-default-vpc`), set `vpc_id` and `subnet_id` explicitly in `aws-config.yaml`, or run with the default `vpc_id: ""` and pick interactively.

**AWS provision: EIP `AddressLimitExceeded`** — the script **hard-fails** at step 2 (no instances launched yet). The provisioner allocates one EIP for the RP so the Wireguard endpoint IP survives instance stop/start. Free an unused EIP and re-run, or request a quota increase:

```bash
# List EIPs that are allocated but unassociated (safe to release):
aws ec2 describe-addresses --query 'Addresses[?AssociationId==null].[AllocationId,PublicIp]' --output table
aws ec2 release-address --allocation-id <alloc-id>

# Or request a quota increase (default is 5 EIPs/region):
aws service-quotas request-service-quota-increase \
    --service-code ec2 --quota-code L-0263D0A3 --desired-value 10
```

See [About the Elastic IP](#about-the-elastic-ip) for why we use an EIP.

**Multiple environments on the same AWS account** — use a different `project:` value in each `aws-config.yaml` (e.g., `openg2p-prod`, `openg2p-staging`). Resources are isolated by tag; the destroy script only touches the configured project.
