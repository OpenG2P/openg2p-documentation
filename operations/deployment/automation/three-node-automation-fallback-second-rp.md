---
description: Fallback layout when the Reverse Proxy VM cannot have two network interfaces — split into two RP VMs (public + private).
---

# Fallback: Two Nginx VMs (single-NIC each)

This page is a **fallback** to the standard [Three-Node Automation](three-node-automation.md). Use it only when you cannot add a second vNIC to the Reverse Proxy VM (rare — see the [hypervisor table](three-node-automation.md#id-2.-two-network-interfaces-on-the-reverse-proxy-vm) in the main doc; every common hypervisor supports it).

{% hint style="warning" %}
This is more moving parts than the standard layout (one more VM, two Nginx configs to keep aligned, two sets of cert deployments). Prefer the standard two-NIC RP whenever possible.
{% endhint %}

## Architecture

```
       internet                              internal mgmt / cluster network
          │                                              │
          ▼                                              ▼
     RP-public VM                                  RP-private VM
     ┌────────────────────────────┐               ┌────────────────────────────┐
     │ Single NIC (public IP)     │               │ Single NIC (internal IP)   │
     │ • Wireguard server         │               │ • Nginx (admin server      │
     │ • Nginx public server      │               │   blocks: rancher,         │
     │   blocks (env automation,  │               │   keycloak, grafana,       │
     │   citizen-facing services) │               │   prometheus)              │
     │                            │               │                            │
     │ Routes WG-tunneled traffic │ ────internal──▶                            │
     │ destined for admin IPs to  │                                            │
     │ the internal subnet        │                                            │
     └────────────────────────────┘               └────────────────────────────┘
                                                              │
                                                              ▼
                                                  Compute, Storage (same subnet)
```

Four VMs instead of three. Both RPs are on the same internal/management network.

## Differences from the standard layout

| Concern | Standard (single RP, 2 vNICs) | Fallback (two RPs, 1 vNIC each) |
|---|---|---|
| Number of VMs | 3 | 4 |
| Wireguard server location | RP node, bound to vNIC-public | RP-public VM |
| Public Nginx | RP node, bound to vNIC-public | RP-public VM |
| Admin Nginx | RP node, bound to vNIC-internal | RP-private VM |
| Routing | Trivially in-host between vNICs | WG → public NIC → internal network → admin NIC. Requires the internal network to route WG-source packets to RP-private's IP. |
| Cert deployment | One copy of admin certs on the RP | Admin certs deployed to RP-private; public certs to RP-public |
| Failure isolation | Single RP — if down, both channels down | Public + admin are decoupled at the VM level |

## Required prerequisites (in addition to the standard list)

Refer to [Prerequisites in the main doc](three-node-automation.md#prerequisites) for everything else. The fallback layout **adds** these:

1. **A fourth Ubuntu 24.04 VM** for RP-private. Same OS / minimum specs as the standard RP (2 vCPU, 4 GB RAM, 64 GB disk).
2. Both RP VMs on the **same internal/management subnet** as compute and storage. Layer-3 routing between RP-public's public network and the internal subnet is the customer's responsibility (typical setup: RP-public is dual-homed at the L2 level via the hypervisor — its single OS-visible NIC has the public IP, but the underlying virtual switch is on the management VLAN).
3. The customer's DNS resolves the four admin hostnames to **RP-private's internal IP**.
4. RP-public's security group / firewall opens UDP `wg_port` to the world, TCP 22 to the admin CIDR, and forwards WG-tunneled traffic to RP-private.

## Manual setup (provisioning automation comes later)

Until the orchestrator natively supports the dual-RP layout, this is a **manual setup** on top of the existing automation:

### Step 1 — Provision the fourth VM

Per the prerequisite above. Note the internal IP; you'll need it in step 4.

### Step 2 — Run the standard automation with `rp_role: private` on the existing RP node

The existing 3-node automation today configures Wireguard, dnsmasq, local CA, and Nginx on the RP. For the dual-RP layout, you point the orchestrator at the **RP-private VM** for the `rp` role:

```yaml
# prod-config.yaml (fallback layout)
rp_role: "private"          # tells the script to skip Wireguard setup
rp_public_ip: ""            # leave blank — no public IP on this node
rp_internal_ip: "172.29.0.42"
rp_ssh_host:  "172.29.0.42"
```

The orchestrator with `rp_role: private` installs only the admin-Nginx + cert pieces on this node, **skipping** Wireguard.

{% hint style="info" %}
The `rp_role` config key is not yet implemented in the orchestrator. Until it is, do step 2 manually: ssh into the fourth VM, follow the standard RP phase 1 by hand for cert + Nginx, skip the Wireguard sections.
{% endhint %}

### Step 3 — Install Wireguard on RP-public manually

On the RP-public VM (the one with the public IP):

```bash
sudo apt update && sudo apt install -y wireguard-tools
sudo mkdir -p /etc/wireguard /etc/wireguard/peers
# generate keys
wg genkey | sudo tee /etc/wireguard/server.key | wg pubkey | sudo tee /etc/wireguard/server.pub
# write /etc/wireguard/wg0.conf — use the same template as the standard RP phase 1
# Key thing: AllowedIPs in peer configs must cover RP-private's internal IP
sudo systemctl enable --now wg-quick@wg0
```

The full `wg0.conf` template lives at `automation/production/roles/reverse-proxy/phase1.sh` in the OpenG2P deployment repo — copy the relevant section.

### Step 4 — Configure routing so WG-tunneled traffic reaches RP-private

WG peer's tunneled packets terminate on RP-public. They must then route to RP-private's internal IP via the management network. This is typically automatic if both VMs share an L2 segment, but check:

```bash
# On RP-public
sudo sysctl -w net.ipv4.ip_forward=1
sudo iptables -A FORWARD -i wg0 -j ACCEPT
sudo iptables -A FORWARD -o wg0 -j ACCEPT
# MASQUERADE so RP-private sees source as RP-public's internal IP (else it can't reply)
sudo iptables -t nat -A POSTROUTING -s <wg_subnet> -j MASQUERADE
```

Persist these via `iptables-persistent` or netfilter-persistent.

### Step 5 — DNS and cert checks

* Customer's DNS resolves the four admin hostnames to **RP-private's internal IP**.
* Admin certs are uploaded to RP-private (`/etc/openg2p/certs/public/<hostname>/`).
* Admin laptops on Wireguard can reach `https://rancher.<your-domain>` → resolves to RP-private internal IP → routes through WG to RP-public → forwards to RP-private → Nginx → Istio.

## Roadmap for native support

When demand for this layout justifies it, the orchestrator will gain:

* A `rp_role` config key (`combined` | `public` | `private`) that selects which set of phase-1 steps to run on each RP VM.
* A `--role rp-public` / `--role rp-private` orchestrator flag.
* AWS provisioning + on-prem instructions for a four-VM layout.

Until then, the standard single-RP two-NIC layout is the supported path.

## Related

* [Three-Node Automation (main)](three-node-automation.md)
* [Private Access Channel (concept)](../../../deployment/deployment-guide/private-access-channel.md)
