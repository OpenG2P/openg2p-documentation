---
description: >-
  Stage 2 of the production deployment — provision the three VMs that the
  infrastructure automation will install onto.
---

# Provisioning

This is **Stage 2** of the production deployment: bringing up the three Ubuntu 24.04 VMs (Reverse Proxy, Compute, Storage) that Stage 3 will install onto. You should arrive here once the items in [Stage 1 — Prerequisites & Procurement](../prerequisites-procurement.md) have been requested.

{% hint style="info" %}
**Production deployment flow:**  [1. Procurement](../prerequisites-procurement.md)  →  **2. Provisioning** (this page)  →  [3. Infrastructure](three-node-automation/)  →  [4. Environment](../environment-setup-multi-node.md)  →  [5. Modules](../environment-setup-multi-node.md#next-install-your-openg2p-modules)
{% endhint %}

## What you need before provisioning

* Compute specs decided — see [Procurement → Compute](../prerequisites-procurement.md#compute-the-three-vms) (RP, Compute, Storage minimums + backup node).
* Network plan in place — one private subnet for all three VMs; the RP needs an internet-reachable address (public IP, NAT/DNAT, or AWS Elastic IP).
* SSH key + admin CIDR ready — the install orchestrator on your laptop needs SSH + passwordless sudo to each VM.

## On-prem provisioning

There is no bundled on-prem provisioning automation — you provision on your hypervisor with whatever tooling your organisation uses (vSphere, KVM, Proxmox, Hyper-V, Terraform against a private cloud, etc.). The implementer's responsibilities are:

1. Three Ubuntu Server 24.04 LTS VMs at the sizes in [Procurement → Compute](../prerequisites-procurement.md#compute-the-three-vms).
2. All three VMs on the **same private subnet**.
3. The Reverse Proxy VM has either:
   * a directly-bound public IP on its NIC, or
   * a NAT/DNAT address on an upstream firewall that maps incoming Wireguard UDP + admin SSH to the RP's private IP.
4. SSH access with passwordless sudo from the deployer's workstation, restricted to the admin CIDR from Stage 1.
5. Internet egress from all three VMs during install (apt, RKE2, Helm chart downloads).

Once the three VMs are up and you can SSH into each as `ubuntu` (or another sudo-enabled user) without a password prompt, you're done with Stage 2 — proceed to [Stage 3 — Infrastructure Automation](three-node-automation/).

## AWS provisioning

OpenG2P bundles an AWS provisioning script that creates the three EC2 instances, security groups, key pair, and the Elastic IP for the Reverse Proxy. Use it if you're on AWS and don't have your own Terraform / CloudFormation / console-driven flow already.

→ See [**AWS Provisioning**](three-node-automation/aws-provisioning.md) for the full procedure (prerequisites, IAM permissions, what gets created, workflow, costs, and teardown).

If you have your own AWS provisioning tooling, treat AWS like an on-prem case above — bring the three VMs up yourself and proceed to Stage 3.

## After provisioning

You now have three Ubuntu VMs reachable from the deployer's laptop. Continue with [**Stage 3 — Infrastructure Automation**](three-node-automation/) to install RKE2, Istio, Rancher, Keycloak, Wireguard, Nginx, NFS, and host PostgreSQL across them.
