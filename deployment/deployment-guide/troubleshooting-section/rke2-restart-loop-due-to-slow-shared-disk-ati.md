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

Without a controller cache, every write waits for the consumer SSDs. etcd needs writes to finish in about 10 ms, but writes stalled for **300–400 ms**, so etcd timed out, rke2 lost its leader election and restarted (78 times in one day), and every restart killed all pods on the node.

**Why it started after about a year:** consumer SSDs are fast when new. After ~13 months of continuous writes (~67 TB per drive), they have no clean blocks left and must erase before writing. The E208i-a controller does **not pass TRIM** to the drives, so they never learn which space is free, and there is no cache to hide these pauses. The disk now shows 100% busy at only **~1 MB/s**.

{% hint style="info" %}
The drives are healthy (SMART `PASSED`, ~92% life left, no errors, 20–23 °C). The hardware is **too slow** for this workload, not faulty. Deleting VMs, freeing space, or rebooting does **not** fix it.
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
iostat -x sda 5 3          # %util 100% at ~1 MB/s, w_await 300-400 ms
xentop -b -i 2 -d 5        # VBD_WR / VBD_WSECT show which VM writes most
xe sr-list params=name-label,physical-size,physical-utilisation
dmesg -T | grep -i 'write cache'   # "Write cache: disabled"
```

**3. On the XCP-ng host: identify the controller and drives (no extra tools needed)**

```bash
cat /proc/scsi/scsi                                  # controller model (E208i-a)
cat /sys/class/scsi_disk/*/cache_type                # "none" = no write cache
for i in 0 1 2 3 4 5; do
  smartctl -i -H -A -d cciss,$i /dev/sda | grep -iE 'Device Model|Rotation|overall-health|Percent_Lifetime|Total_LBAs_Written|Reallocat|Uncorrect|Temperature'
done
cat /sys/block/sda/queue/discard_max_bytes          # 0 = TRIM not supported
```

**4. Inside the cluster VM: confirm the VM itself is not the heavy writer**

```bash
apt install -y sysstat && pidstat -d 5 3             # etcd only ~100 KB/s, rest negligible
```

## Solution <a href="#solution" id="solution"></a>

### Temporary fix (reduce disk writes)

1. Scale down Rancher Monitoring (Prometheus) on both clusters:

   ```bash
   kubectl -n cattle-monitoring-system scale sts prometheus-rancher-monitoring-prometheus --replicas=0
   ```
2. Move Xen Orchestra backup / snapshot jobs to off-hours.
3. In a maintenance window: shut down all VMs, keep the host **powered on and idle for 1–2 hours** (lets the SSDs clean up internally), then start VMs one by one, Kubernetes control-plane VMs first. Relief lasts hours to days only.
4. If another server is available, move the `rancher` VM and OpenG2P control-plane VMs there until new disks arrive.

{% hint style="warning" %}
"Reclaim freed space" in Xen Orchestra does not help here, because TRIM is not supported by this controller.
{% endhint %}

### Permanent fix

1. Add 2 **data-center SSDs with power-loss protection** (for example Samsung PM893, Micron 5400 PRO, Solidigm D3-S4520, ~960 GB) as a separate SR, and move the Kubernetes control-plane VMs (`rancher`, OpenG2P etcd nodes) onto it. This needs one short host reboot (all VMs down). Later, replace all 6 consumer SSDs.
2. Optionally upgrade the controller to one **with cache** (for example HPE P408i-a with Smart Storage Battery).
3. Keep heavy writers (monitoring, DB, MinIO, NFS) off the disk used by etcd.
4. Re-check SSD wear monthly (`Percent_Lifetime_Remain`, `Total_LBAs_Written`); BX500 1 TB is rated for 360 TB written.
