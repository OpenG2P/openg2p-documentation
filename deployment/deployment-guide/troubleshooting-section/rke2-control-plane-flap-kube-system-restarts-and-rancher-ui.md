---
description: >-
  Runbook for RKE2 control-plane flaps (node1/node7), cascading kube-system
  restarts, NFS CSI FailedMount, and Rancher UI HTTP 504 Gateway Time-out.
---

# RKE2 Control Plane Flap: kube-system Restarts and Rancher UI 504

This runbook covers a real incident pattern on an OpenG2P RKE2 cluster where a control-plane node (`rke2-server`) became unstable, causing cluster-wide symptoms that looked like application or Canal/CoreDNS failures.

Use this guide when many namespaces restart at once, `kube-system` pods flap, NFS mounts fail, or Rancher UI shows **HTTP Error 504: Gateway Time-out**, while individual app configs look unchanged.

## Symptoms <a href="#symptoms" id="symptoms"></a>

Typical signs (often appearing together):

1. Pods across multiple namespaces restart or fail probes at the same time (for example `esignet`, Keycloak-dependent services, metrics/DNS consumers).
2. In `kube-system`, recent restarts on:
   - `kube-proxy-*`
   - `rke2-canal-*`
   - `rke2-coredns-*`
   - `rke2-metrics-server-*`
   - sometimes static pods such as `kube-apiserver-*`
3. Cluster events contain `Killing`, `Unhealthy`, or `FailedMount`.
4. NFS-backed pods fail with:
   ```text
   driver name nfs.csi.k8s.io not found in the list of registered CSI drivers
   ```
5. Rancher UI (`rancher2.<domain>`) shows fail-whale / **HTTP 504 Gateway Time-out** from nginx, even though `cattle-cluster-agent` pods show `Running`.
6. On peer control-plane nodes, RKE2 logs show failures talking to the bad node supervisor port `:9345`, for example:
   ```text
   dial tcp <node1-ip>:9345: connection refused
   Response status: 503 ... "message":"starting"
   websocket: close 1006 unexpected EOF
   ```
7. Node conditions may show high memory usage on a control-plane node (for example ~88% on `node7`), and some nodes may be `Ready,SchedulingDisabled` (cordoned).

## Root cause <a href="#root-cause" id="root-cause"></a>

### Primary cause

**`rke2-server` on a control-plane + etcd node became unstable and restarted** (observed on `node1`, with continued thrash involving `node7`).

When `rke2-server` drops:

1. Local apiserver / etcd / scheduler / controller-manager supervised by RKE2 are disrupted.
2. Remotedialer tunnels between control-plane nodes on port **9345** tear down.
3. Peer nodes see `:9345 connection refused` or `503 starting` while the node recovers.
4. Agents and controllers retry hard; kube-proxy, Canal, CoreDNS, and metrics-server may restart even though Canal itself was not the root bug.

### Why it often hits an older control-plane node

On the observed cluster:

| Finding | Meaning |
| --- | --- |
| `rke2-server` memory peak ~**9.4G** on `node1` | Control-plane process under heavy memory pressure |
| Node memory ~**88%** on `node7` | High risk of flaps / reconnect loops |
| Disk ~**80%** on control-plane roots | etcd sensitive to disk pressure / latency |
| Multiple nodes cordoned | Less capacity; recovery thrash concentrates on remaining nodes |

Most likely trigger class: **control-plane resource pressure (memory, with tight disk as a contributor)**, not a single application Helm chart.

### Cascade (what looked broken but was fallout)

| Observed issue | Actual relationship |
| --- | --- |
| Canal / kube-proxy / CoreDNS restarts | Symptom of CP flap / tunnel reconnect |
| NFS CSI `nfs.csi.k8s.io not found` | CSI pods/drivers briefly unregistered during CP recovery |
| Rancher UI 504 | Edge nginx timed out reaching Rancher API path; stuck `cattle-cluster-agent` subscribe websockets after API stress |
| App pod restarts | Probes/DNS/API dependencies failed while CP was flapping |

**Important:** Healthy-looking `cattle-cluster-agent` pods do **not** mean Rancher UI is healthy. The UI depends on the Rancher server path responding in time; agent websocket state can stay stuck after a CP incident.

## Diagnosis <a href="#diagnosis" id="diagnosis"></a>

Run these in order.

### 1. Confirm node and capacity state

```bash
kubectl get nodes -o wide
kubectl top nodes
kubectl describe node <suspect-cp-node> | egrep -A12 'Conditions:|Allocated resources:|Taints:|MemoryPressure|DiskPressure|PIDPressure'
```

Look for:

- Control-plane nodes that recently flipped Ready / NotReady
- High memory or disk
- `SchedulingDisabled` on overloaded CP nodes

### 2. Confirm which control-plane supervisor is bad

On a **healthy** CP node (or from journal of a peer):

```bash
sudo journalctl -u rke2-server --since "30 min ago" | egrep -i '9345|connection refused|503|starting|websocket|EOF|etcd'
```

On the **suspect** node (`node1` in the incident):

```bash
sudo systemctl status rke2-server --no-pager
sudo ss -lntp | egrep '9345|6443|2379'
free -h
df -h /
```

Key signals:

- `rke2-server` Active time recently reset → process restarted
- High `Memory: ... (peak: ...)` under the rke2 unit
- Ports `9345` / `6443` / `2379` missing while the unit is recovering

### 3. Confirm kube-system is flapping because of CP, not a CNI-only bug

```bash
kubectl -n kube-system get pods -o wide | grep -E 'coredns|metrics|canal|kube-proxy|apiserver'
kubectl get events -A --sort-by=.lastTimestamp | grep -iE 'Killing|Unhealthy|Failed' | tail -40
```

If restarts align with `:9345` errors on a CP IP, treat CNI as fallout.

### 4. Check CSI NFS after CP recovery

```bash
kubectl get csidrivers
kubectl -n kube-system get pods | grep -iE 'csi|nfs'
kubectl get events -A --sort-by=.lastTimestamp | grep -i 'nfs.csi.k8s.io' | tail -20
```

### 5. Check Rancher UI path (if 504)

```bash
kubectl -n cattle-system get deploy,pods,svc -o wide
kubectl -n cattle-system get endpoints rancher -o wide 2>/dev/null
kubectl -n cattle-system logs -l app=cattle-cluster-agent --tail=100 | egrep -i 'websocket|subscribe|stale GroupVersion|unable to handle|timeout'
```

Browser fail-whale with nginx `504` means the edge proxy timed out waiting for Rancher upstream, not that DNS for the Rancher hostname is down.

### 6. Capture root-cause evidence before it ages out

On the bad CP node:

```bash
sudo journalctl -u rke2-server --since "1 hour ago" | egrep -i 'oom|killed|fatal|panic|etcd|error|shutdown'
sudo dmesg -T | egrep -i 'oom|killed process|out of memory|I/O error|ext4'
```

This distinguishes OOM vs etcd/disk vs hard crash for post-incident review.

## Solution <a href="#solution" id="solution"></a>

### A. Stabilize the control plane (do this first)

1. Prefer fixing the unhealthy CP node rather than repeatedly restarting every node.
2. On the bad node, if `rke2-server` is stuck or peers still see `:9345 refused`:

   ```bash
   sudo systemctl restart rke2-server
   sudo systemctl status rke2-server --no-pager
   ```

3. Wait until:
   - `rke2-server` is `active (running)`
   - ports `9345`, `6443`, `2379` are listening
   - peer journals stop showing continuous `connection refused` / websocket EOF storms
4. If a second CP node (for example `node7`) keeps reconnecting (frequent cert resign / tunnel flaps), stabilize that node next the same way. Keep it **cordoned** until memory is comfortable:

   ```bash
   kubectl cordon <node>
   # after stable:
   kubectl uncordon <node>
   ```

5. Re-check kube-system:

   ```bash
   kubectl -n kube-system get pods -o wide | grep -E 'coredns|metrics|canal|kube-proxy'
   ```

   Ages should stop resetting every few seconds.

### B. Restore NFS CSI (if mounts still fail)

After CP is stable, confirm CSI driver registration:

```bash
kubectl get csidrivers
kubectl -n kube-system get pods | grep -iE 'csi-nfs|nfs'
```

If controller/node pods are not Ready, restart them:

```bash
kubectl -n kube-system rollout restart deploy/csi-nfs-controller
kubectl -n kube-system delete pod -l app=csi-nfs-node
```

(Adjust labels/names to match your chart.) Then re-check FailedMount events.

### C. Restore Rancher UI (if still 504 after CP is healthy)

Restart cattle-system agents so subscribe websockets rebuild against a healthy API:

```bash
kubectl -n cattle-system delete pod -l app=cattle-cluster-agent
# if Rancher server Deployment exists in this cluster:
kubectl -n cattle-system rollout restart deploy/rancher
kubectl -n cattle-system rollout status deploy/rancher --timeout=5m
```

In the observed incident, **restarting Rancher agent pods** cleared the UI 504 after the control plane had already recovered.

### D. What not to do during the storm

1. Do not treat Canal/CoreDNS as the primary fix while `:9345` is refused on a CP node.
2. Do not repeatedly restart all CP nodes in parallel (risks etcd quorum issues). Prefer one unhealthy node at a time.
3. Do not uncordon a memory-saturated CP node until `rke2-server` memory and node memory are back to a normal range.

## Verification <a href="#verification" id="verification"></a>

Cluster is considered recovered when all of the following hold for 15–30 minutes:

1. All needed nodes `Ready`; no new NotReady flaps.
2. `kubectl -n kube-system get pods` shows CoreDNS / Canal / kube-proxy Running without second-by-second AGE resets.
3. `kubectl get csidrivers` includes `nfs.csi.k8s.io` (if NFS CSI is used) and NFS PVC pods mount successfully.
4. Rancher UI loads without fail-whale / 504.
5. Peer `rke2-server` journals are quiet (only routine snapshot reconcile messages, not continuous reconnect errors).

## Prevention / hardening <a href="#prevention" id="prevention"></a>

1. Keep control-plane nodes sized for etcd + apiserver; alert on node memory > ~80% and disk > ~75% on CP roots and etcd data paths.
2. Avoid scheduling heavy workloads onto etcd control-plane nodes when possible; keep overloaded CP nodes cordoned until relieved.
3. Monitor RKE2 supervisor port reachability between CP nodes (`9345`) and `rke2-server` systemd restarts.
4. Retain short `journalctl -u rke2-server` / `dmesg` snippets when an incident starts so OOM vs disk vs crash can be proven.

## Related issues seen in the same window (separate from CP flap)

These may appear during or after the incident but have different fixes:

| Issue | Example signal | Fix direction |
| --- | --- | --- |
| GitLab image pull denied | `403 Forbidden` pulling `registry.gitlab.com/...` | Fix imagePullSecret / registry access |
| Missing secret keys | keycloak-init `client_secret` missing | Repair Secret / Helm values |
| App schema drift | missing DB tables such as `login_providers` | Run / repair app migrations for that env |

Do not confuse these with the control-plane flap root cause.

## Incident summary (reference)

| Item | Detail |
| --- | --- |
| Cluster | RKE2 `v1.33.6+rke2r1` |
| Primary failure | `rke2-server` instability on control-plane node (`node1`), with continued tunnel thrash involving `node7` |
| Blast radius | kube-proxy / Canal / CoreDNS / metrics, NFS CSI registration, cattle-cluster-agent websockets, Rancher UI 504, app probe failures |
| Fix | Stabilize `rke2-server` on affected CP nodes; allow kube-system/CSI to recover; restart `cattle-cluster-agent` (and Rancher server if needed) for UI |

<br>
