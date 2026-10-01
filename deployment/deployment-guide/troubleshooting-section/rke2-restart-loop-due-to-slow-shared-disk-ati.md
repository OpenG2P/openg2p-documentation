---
description: >-
  ATI environment: rke2-server restart loop and cattle-system pod restarts on
  both the OpenG2P and Rancher clusters, caused by slow shared storage on the
  XCP-ng host.
---

# RKE2 Restart Loop due to Slow Shared Disk (ATI Environment)

## Problem <a href="#problem" id="problem"></a>

Both clusters in the ATI environment (OpenG2P cluster `openg2pati` and Rancher cluster `rancher`) kept failing at the same time:

* `rke2-server` restarted every few minutes (systemd restart counter kept increasing).
* `cattle-system` pods (`rancher`, `rancher-webhook`) showed 90+ restarts, exit code `255`, startup probe failures.
* `kubectl` intermittently failed with `connection refused` on `127.0.0.1:6443`.
* RKE2 logs showed:

  ```text
  etcdserver: request timed out / context deadline exceeded
  leaderelection lost for rke2 / rke2-etcd
  ```

## Root cause <a href="#root-cause" id="root-cause"></a>

All VMs (17 in total, including both clusters, DB, MinIO, and NFS) run on **one XCP-ng host** and share **one RAID volume**:

| Component       | Details                                                                     |
| --------------- | --------------------------------------------------------------------------- |
| RAID controller | HPE **E208i-a** (entry level, **no write cache**)                           |
| Drives          | 6 × **Crucial BX500 1 TB** (consumer SSD, no DRAM cache) in RAID 10         |
| Free space      | Only ~33 GiB free out of 2.69 TiB on `Local storage` SR                     |

Without a controller cache, every write waits for the consumer SSDs. Under heavy load from all the VMs, writes stalled for **100 ms or more**. etcd needs writes to finish in about 10 ms, so it timed out, rke2 lost its leader election and restarted, and every restart killed all pods on the node.

{% hint style="info" %}
The drives were healthy (SMART `PASSED`, ~92% life remaining). The hardware is **too slow** for this workload, not faulty.
{% endhint %}

## How we checked <a href="#how-we-checked" id="how-we-checked"></a>

**1. On the cluster nodes: confirm rke2 restarts and disk stalls**

```bash
systemctl status rke2-server --no-pager | head -5
journalctl -u rke2-server --since "3 hours ago" --no-pager | grep -iE 'fatal|leaderelection|deadline'
cat /proc/pressure/io     # "full" avg60/avg300 of 15-25% = processes stuck waiting on disk
vmstat 1 5                # high "wa", CPU mostly idle
```

etcd itself was ruled out: DB size was small (~35 MB vs 2.1 GB quota) and there were no alarms. Memory and CPU were also fine.

**2. On the XCP-ng host: check the shared disk and per-VM writes**

```bash
iostat -x sda 5 3          # %util ~100%, w_await up to ~116 ms
xentop -b -i 2 -d 5        # VBD_WR / VBD_WSECT show which VM writes most
xe sr-list params=name-label,physical-size,physical-utilisation
dmesg -T | grep -i 'write cache'   # "Write cache: disabled"
```

**3. On the XCP-ng host: identify the controller and drives (no extra tools needed)**

```bash
cat /proc/scsi/scsi                                  # controller model (E208i-a)
cat /sys/class/scsi_disk/*/cache_type                # "none" = no write cache
for i in 0 1 2 3 4 5; do
  smartctl -i -H -A -d cciss,$i /dev/sda | grep -iE 'Device Model|Rotation|overall-health|Percent_Lifetime|Total_LBAs_Written'
done
```

## Solution <a href="#solution" id="solution"></a>

### Temporary fix (reduce disk writes)

1. Scale down Rancher Monitoring (Prometheus) on both clusters:

   ```bash
   kubectl -n cattle-monitoring-system scale sts prometheus-rancher-monitoring-prometheus --replicas=0
   ```
2. Move Xen Orchestra backup / snapshot jobs to off-hours.
3. Free up space on the `Local storage` SR.

### Permanent fix

1. Replace the consumer SSDs with **data-center SSDs with power-loss protection** (for example Samsung PM893, Micron 5400 PRO, Solidigm D3-S4520), or give etcd a **dedicated enterprise SSD/NVMe**.
2. Optionally upgrade the controller to one **with cache** (for example HPE P408i-a with Smart Storage Battery).
3. Keep heavy writers (monitoring, DB, MinIO, NFS) off the disk used by etcd.
4. Re-check SSD wear monthly (`Percent_Lifetime_Remain`, `Total_LBAs_Written`); BX500 1 TB is rated for 360 TB written.
