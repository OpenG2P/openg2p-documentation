---
description: >-
  Stage 2 of the production deployment — provision the four VMs that the
  infrastructure automation will install onto.
---

# Provisioning

This is **Stage 2** of the production deployment: bringing up the four Ubuntu 24.04 VMs (Reverse Proxy, Compute, Storage, Backup) that Stage 3 will install onto. You should arrive here once the items in [Stage 1 — Prerequisites & Procurement](../prerequisites-procurement.md) have been requested.

{% hint style="info" %}
**Production deployment flow:**  [1. Procurement](../prerequisites-procurement.md)  →  **2. Provisioning** (this page)  →  [3. Infrastructure](production-automation/)  →  [4. Environment](../environment-setup-multi-node.md)  →  [5. Modules](../environment-setup-multi-node.md#next-install-your-openg2p-modules)
{% endhint %}

## Operator's workstation

The operator (you) drives the install from a workstation — your laptop or a jump host. Everything from this stage onward runs there. Set it up **once**, before Stage 2; the same machine is used through Stages 2, 3, 4, and 5.

### Supported operating systems

| OS                      | Status                                                                                                                                                       |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Ubuntu 22.04+ / Debian 12+** | Best supported — orchestrator and all tooling install cleanly via `apt`.                                                                              |
| **Fedora / RHEL / Rocky 9+** | Fully supported via `dnf`. All required tools are in the default repos.                                                                                  |
| **macOS 12+ (Intel or Apple Silicon)** | Supported **after** upgrading bash. macOS ships `/bin/bash 3.2`; the orchestrator requires **bash 4+** and will refuse to start otherwise. Install with `brew install bash`. See the [macOS gotcha](#macos-gotcha-default-bash-is-too-old) below. |
| **Windows 10/11**       | Supported via **WSL2 + Ubuntu**. Run all commands from inside the WSL Ubuntu shell. Native PowerShell / cmd is **not** supported.                            |

### Required tools

| Tool                | All stages | Stage 2 (AWS only) | Stage 4 onward | Why                                                                  |
| ------------------- | :--------: | :----------------: | :------------: | -------------------------------------------------------------------- |
| `bash` ≥ 4.0        | ✓          |                    |                | Orchestrator uses `mapfile`, associative arrays, process substitution |
| `ssh` / `scp`       | ✓          |                    |                | All node-side work runs over SSH                                     |
| `rsync`             | ✓          |                    |                | Pushes role scripts and config to each node                          |
| `openssl`           | ✓          |                    |                | Validates customer-supplied TLS certs locally before upload          |
| `git`               | ✓          |                    |                | To clone the `openg2p-deployment` repo                               |
| Wireguard client    | ✓ (after install) | |                | To log in to Rancher (and, after the environment stage, the app UIs — Keycloak, MinIO, Superset, …) over the VPN. GUI client recommended — Tunnelblick-style apps don't work; use the official **WireGuard.app** (macOS), **WireGuard for Windows**, or `wg-quick` (Linux). |
| **AWS CLI v2**      |            | ✓                  |                | Used by `openg2p-aws-provision.sh`. Skip if not on AWS.              |
| `kubectl`           |            |                    | ✓              | `env-cluster.sh` and module installs target the cluster              |
| `helm` ≥ 3.x        |            |                    | ✓              | Module Helm-chart installs                                           |

### Install commands by OS

{% tabs %}
{% tab title="Ubuntu / Debian / WSL" %}
```bash
# Stage 2 (always) + Stage 3 (always)
sudo apt update
sudo apt install -y bash openssh-client rsync openssl git wireguard-tools

# Stage 2 — AWS path only
sudo apt install -y unzip curl
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o awscli.zip && unzip awscli.zip && sudo ./aws/install

# Stage 4 onward
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" && sudo install kubectl /usr/local/bin/
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```
{% endtab %}

{% tab title="Fedora / RHEL / Rocky" %}
```bash
# Stage 2 (always) + Stage 3 (always)
sudo dnf install -y bash openssh-clients rsync openssl git wireguard-tools

# Stage 2 — AWS path only
sudo dnf install -y unzip
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o awscli.zip && unzip awscli.zip && sudo ./aws/install

# Stage 4 onward
sudo dnf install -y kubectl helm   # via Kubernetes / Helm yum repos; see upstream docs if not enabled
```
{% endtab %}

{% tab title="macOS (Homebrew)" %}
```bash
# Bash 4+ is mandatory — macOS default is 3.2
brew install bash

# Stage 2 (always) + Stage 3 (always)
brew install rsync openssl@3 git
# ssh, openssh: bundled with macOS — no install needed
# Wireguard GUI: install from the App Store (search "WireGuard") OR
brew install --cask wireguard-tools

# Stage 2 — AWS path only
brew install awscli

# Stage 4 onward
brew install kubectl helm
```

**After `brew install bash`**, confirm the Homebrew bash is first in PATH:

```bash
which bash      # should print /opt/homebrew/bin/bash (Apple Silicon) or /usr/local/bin/bash (Intel)
bash --version  # should print 5.x
```
{% endtab %}

{% tab title="Windows (WSL2)" %}
```powershell
# In PowerShell as Administrator — one-time WSL install
wsl --install -d Ubuntu
# Reboot if prompted, then launch Ubuntu from the Start menu.
```

Then **inside the Ubuntu WSL shell**, follow the **Ubuntu / Debian / WSL** tab above.

For the Wireguard client, install **WireGuard for Windows** natively (from `wireguard.com/install`) — admin UIs open in your Windows browser, so the VPN runs on the Windows side, not inside WSL.
{% endtab %}
{% endtabs %}

### macOS gotcha: default bash is too old

macOS ships `/bin/bash 3.2`. The orchestrator uses `mapfile` and other bash-4 features and will refuse to start with:

```
[FATAL] bash 4 or later required (detected 3.2.57(1)-release).
[FATAL] macOS: 'brew install bash', then re-open the shell.
```

The fix is `brew install bash` — but the script invokes itself with `#!/usr/bin/env bash`, so the **PATH-lookup** bash is the one that runs. After install, open a fresh terminal (so `/opt/homebrew/bin` is on PATH) and verify `bash --version` prints 5.x. The original `/bin/bash` stays at 3.2 — that's fine, the env shebang resolves to whichever `bash` is first on PATH.

### Verify your workstation is ready

Before running any installer:

```bash
bash --version | head -1     # must be 5.x or 4.x — not 3.x
ssh -V                       # any OpenSSH 8.x+
rsync --version | head -1    # any 3.x
openssl version              # any 1.1.x / 3.x
git --version                # any 2.x

# AWS path only
aws --version                # aws-cli/2.x

# Stage 4 onward
kubectl version --client     # any 1.28+
helm version                 # any 3.x
```

If any required line errors or shows the wrong version, install/fix it before continuing — the install scripts hard-fail on missing tools.

## What you need before provisioning

* Compute specs decided — see [Procurement → Compute](../prerequisites-procurement.md#compute-the-four-vms) (RP, Compute, Storage minimums + backup node).
* Network plan in place — one private subnet for all four VMs; the RP needs an internet-reachable address (public IP, NAT/DNAT, or AWS Elastic IP).
* SSH key ready — the install orchestrator on your laptop needs SSH + passwordless sudo to each VM. On the AWS path, blank `admin_cidr` defaults to `0.0.0.0/0` so SSH survives public-IP changes; lock it down for long-lived production (see [AWS Provisioning → admin_cidr](production-automation/aws-provisioning.md#admin_cidr--ssh--ping-from-the-admin-laptop)).

## On-prem provisioning

There is no bundled on-prem provisioning automation — you provision on your hypervisor with whatever tooling your organisation uses (vSphere, KVM, Proxmox, Hyper-V, Terraform against a private cloud, etc.). The implementer's responsibilities are:

1. Four Ubuntu Server 24.04 LTS VMs at the sizes in [Procurement → Compute](../prerequisites-procurement.md#compute-the-four-vms).
2. All four VMs on the **same private subnet**.
3. The Reverse Proxy VM has either:
   * a directly-bound public IP on its NIC, or
   * a NAT/DNAT address on an upstream firewall that maps incoming Wireguard UDP + admin SSH to the RP's private IP.
4. SSH access with passwordless sudo from the deployer's workstation, restricted to the admin CIDR from Stage 1.
5. Internet egress from all four VMs during install (apt, RKE2, Helm chart downloads).

Once the four VMs are up and you can SSH into each as `ubuntu` (or another sudo-enabled user) without a password prompt, you're done with Stage 2 — proceed to [Stage 3 — Infrastructure Automation](production-automation/).

## AWS provisioning

OpenG2P bundles an AWS provisioning script that creates the EC2 instances (Reverse Proxy, Compute, Storage, and — with `backup_node.enabled: true` — the Backup node), security groups, key pair, and the Elastic IP for the Reverse Proxy. Use it if you're on AWS and don't have your own Terraform / CloudFormation / console-driven flow already.

→ See [**AWS Provisioning**](production-automation/aws-provisioning.md) for the full procedure (prerequisites, IAM permissions, what gets created, workflow, costs, and teardown).

If you have your own AWS provisioning tooling, treat AWS like an on-prem case above — bring the four VMs up yourself and proceed to Stage 3.

## After provisioning

You now have four Ubuntu VMs reachable from the deployer's laptop. Continue with [**Stage 3 — Infrastructure Automation**](production-automation/) to install RKE2, Istio, Rancher, Wireguard, Nginx, NFS, and host PostgreSQL across them.
