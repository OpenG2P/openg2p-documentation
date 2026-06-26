---
description: Post-deployment guide
---

# Access a Database from Outside the Cluster

This guide covers connecting to a database (or any in-cluster service — MinIO, Redis, Kafka, …) from outside the cluster using `kubectl` port-forwarding.

{% hint style="warning" %}
**PostgreSQL is different in production.** It is the **host install on the Storage node** — *not* an in-cluster `*-postgresql-0` pod — so `kubectl port-forward` won't reach it. See **[Host PostgreSQL (production)](#host-postgresql-production)** just below for SSH-based access (required even on Wireguard). The `kubectl port-forward` method later in this guide applies to **in-cluster services** (MinIO, Redis, Kafka, …) and to PostgreSQL only on a sandbox / legacy in-cluster-PG install.
{% endhint %}

## Host PostgreSQL (production)

Production PostgreSQL is a **host install on the storage node**, locked down by two layers:

* **Host firewall (ufw):** port `5432` is open **only to the compute node's IP**.
* **`pg_hba.conf`:** the only remote rule is `host all all <compute_ip>/32`; PostgreSQL listens on `localhost` + the storage private IP.

So there is **no direct network path to `5432`** from a laptop — and that includes when you're on Wireguard. Connect via SSH instead.

{% hint style="warning" %}
**Wireguard does _not_ give you direct access to `5432`.** A WG laptop _can_ SSH to the nodes (port `22` is open to the whole private subnet), but a direct `psql` to `<storage_private_ip>:5432` still fails: WG NATs (`MASQUERADE`) your traffic to the **reverse-proxy's** private IP, and `5432` is allow-listed for the **compute** node only — so the packet is rejected at both the firewall and `pg_hba`. Use one of the SSH methods below (over WG they're trivial, since you can reach the storage/compute private IPs on port 22).
{% endhint %}

**Option 1 — quick admin, on the box** (simplest; peer auth, no password):

```bash
ssh -i <key> <user>@<storage-host>      # or the storage private IP, if on Wireguard
sudo -u postgres psql
```

**Option 2 — SSH tunnel, for `psql` / pgAdmin / DBeaver on your laptop:**

```bash
# Via the storage node (simplest). On Wireguard, use the storage PRIVATE IP as the host.
ssh -i <key> -L 5432:localhost:5432 <user>@<storage-host>

# Alternative — via the compute node (which is already allow-listed for 5432):
ssh -i <key> -L 5432:<storage_private_ip>:5432 <user>@<compute-host>
```

Leave that SSH session open, then point your client at **`localhost:5432`**:

```bash
psql -h 127.0.0.1 -p 5432 -U postgres        # superuser password: see below
```

For a GUI client (pgAdmin, DBeaver), configure the connection as host `127.0.0.1`, port `5432` — or use the client's built-in "SSH tunnel" option with the same hop, which avoids running `ssh` separately.

**Credentials.** The PostgreSQL superuser password is on the storage node at `/etc/openg2p/secrets/postgres-superuser.env` (root-owned, mode `0600`) and is also printed in the installer's final summary (`automation/production/setup-output/SETUP-SUMMARY.txt`). Per-service users (`esignetuser`, etc.) and their passwords live in the namespace secrets (`esignet-db-user`, …).

{% hint style="info" %}
Don't open `5432` to the wider private subnet (or to the Wireguard subnet) just to reach it from a laptop — that erodes the private-channel posture for the system's most sensitive component. The SSH tunnel needs no firewall changes. If a dedicated DBA/admin host genuinely needs direct access, allow **that one source** in both `ufw` and `pg_hba.conf` (over Wireguard, allow the reverse-proxy's private IP, since WG traffic is NAT'd to it — not the WG subnet) and reload PostgreSQL.
{% endhint %}

## Prerequisites

1. Installation and configuration.

The steps to install and configure kubectl to access the Kubernetes Cluster in your machine are given below.

*   Install kubectl.

    ```bash
    sudo snap install kubectl --classic
    ```
*   Check the kubectl version.

    ```bash
    kubectl version --client
    ```
*   Configure kubectl and create a .kube directory in your home folder.

    ```bash
     mkdir -p $HOME/.kube 
    ```
* Download the kube-config file from Rancher UI.
*   Place the kube-config file in the .kube folder.

    ```bash
    cp /path/to/your/kube-config $HOME/.kube/config
    ```
*   Set permissions for the kube-config file.

    ```bash
    chmod 400 $HOME/.kube/config
    ```
*   Export the KUBECONFIG environment variable.

    ```bash
    export KUBECONFIG="$HOME/.kube/config" 
    ```
*   Verify the configuration.

    ```bash
    kubectl config view
    ```

2. You must have access to the Kubernetes Cluster.
3. You must have the necessary permissions to perform port-forwarding to the database service in the Kubernetes Cluster.

## Procedure (in-cluster services)

Ensure the cluster kubeconfig is set on your machine, then port-forward the in-cluster service you want to reach.

*   List the relevant pods/services in the environment namespace:

    ```bash
    kubectl get pods,svc -n <namespace of env>
    # e.g. an in-cluster MinIO, Redis, or Kafka service
    ```
*   Port-forward the service (or pod) to a local port:

    ```bash
    kubectl -n <namespace> port-forward svc/<service> <local-port>:<service-port>
    # e.g. MinIO console:  kubectl -n prod port-forward svc/commons-minio 9001:9001
    ```
*   Connect with the appropriate client on `localhost:<local-port>` (e.g. a browser for MinIO, `redis-cli`, etc.).

For an **in-cluster PostgreSQL** (sandbox or a legacy in-cluster-PG install), the same pattern applies:

    ```bash
    kubectl -n <namespace> port-forward svc/<release>-postgresql 5432:5432
    psql -h localhost -p 5432 -U <dbuser> -d <database>
    ```

For the **host PostgreSQL** in production, use SSH instead — see [Host PostgreSQL (production)](#host-postgresql-production) above.

    <br>

Notes

* The `kubectl port-forward` must keep running in the foreground while you are accessing the database.
* Ensure that your local port (e.g., 5432) is not being used by another service on your local machine.&#x20;
