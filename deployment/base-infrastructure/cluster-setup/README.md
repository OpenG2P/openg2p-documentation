---
description: Kubernetes cluster setup guide
layout:
  title:
    visible: true
  description:
    visible: false
  tableOfContents:
    visible: true
  outline:
    visible: true
  pagination:
    visible: true
---

# Kubernetes Cluster

OpenG2P modules and components are recommended to be run on [Kubernetes](https://kubernetes.io/) (K8s), because of ease-of-use, management, and security features that K8s provides.

K8s cluster may be installed on the following infrastructures:

* **Cloud-native** (like EKS on AWS, or AKS on Azure)
* Non-cloud native, or **on-prem** (resources provisioned on a cloud or local data centre).

Here we provide instructions to set up K8s cluster **on-prem**.

Broadly, the steps to install are as follows:

1. [Provision virtual machines ](./#provision-virtual-machines)
2. [Set firewall rules](./#firewall-setup)
3. [Set up the K8s cluster](./#cluster-installation) using Rancher's tool [RKE2](https://docs.rke2.io/).
4. [Install NFS client on the cluster](./#nfs-client-provisioner)
5. [Install Istio on cluster](./#istio)
6. [Import cluster into Rancher](./#cluster-import-to-rancher)
7. Provide access to users

## Virtual machines provisioning

Provision for virtual machines (VMs) as per configuration mentioned in [Hardware Requirements](../../hardware-requirements.md). Make sure you have root privileges to the machines and have secure access to them.

Install the following tools on all machines including the one you are using to connect to the VMs.

* `wget` , `curl` , `kubectl` , `istioctl` , `helm` , `jq`

{% hint style="danger" %}
If you have SSH access to the VMs, and root privileges, you are the Super Admin. Make sure very limited access is given to the machines.&#x20;
{% endhint %}

## Firewall setup

Refer guide [here](firewall.md).

## Cluster installation

The following section uses [RKE2](https://docs.rke2.io) to set up the K8s cluster.

* Decide on the number of **control-planes** (RKE2 server).  For high availability the minimum of nodes running control-plane should 3. If your cluster is < 3 nodes,  run only 1 control-plane (odd number). Refer [RKE2 docs](https://docs.rke2.io/install/ha). The rest of the nodes are Kubernetes **workers** (RKE2 agent).
* The following setup has to be done on each node on the cluster.
  * SSH into the node.  Execute all the below commands as root user.
  *   Create the rke2 config directory

      ```
      mkdir -p /etc/rancher/rke2
      ```
  * Create a `config.yaml` file in the above directory, using one of the following config file templates:
    * For the first control-plane node, use [rke2-server.conf.primary.template](https://github.com/OpenG2P/openg2p-deployment/blob/main/kubernetes/rke2/rke2-server.conf.primary.template). The token can be any arbitrary string.
    * For subsequent control-plane nodes, use [rke2-server.conf.subsequent.template](https://github.com/OpenG2P/openg2p-deployment/blob/main/kubernetes/rke2/rke2-server.conf.subsequent.template). (Make sure the token defined in the first node's control plane is used here too.)
    * For worker nodes, use [rke2-agent.conf.template](https://github.com/OpenG2P/openg2p-deployment/blob/main/kubernetes/rke2/rke2-agent.conf.template).  (Make sure the token defined in the first node's control plane is used here too.)
  * Edit the above `config.yaml` file with the appropriate names, IPs, and tokens
  *   Run the following to set the RKE2 version after referring to [RKE2 Releases](https://github.com/rancher/rke2/releases).

      ```bash
      export INSTALL_RKE2_VERSION="v1.30.0+rke2r1"
      ```
  *   Run this to download rke2.

      ```bash
      curl -sfL https://get.rke2.io | sh -
      ```
  * Run this to start rke2:
    *   On the control-plane node, run:

        ```bash
        systemctl enable rke2-server
        systemctl start rke2-server
        ```
    *   On the worker node, run:

        ```bash
        systemctl enable rke2-agent
        systemctl start rke2-agent
        ```
* To export KUBECONFIG, run (only on control-plane nodes):
* ```bash
  echo -e 'export PATH="$PATH:/var/lib/rancher/rke2/bin"\nexport KUBECONFIG="/etc/rancher/rke2/rke2.yaml"' >> ~/.bashrc
  source ~/.bashrc
  kubectl get nodes    
  ```
* Download the Kubeconfig file `rke2.yaml` and keep it <mark style="color:red;">securely</mark> <mark style="color:red;"></mark><mark style="color:red;">**shared with only**</mark> <mark style="color:red;"></mark><mark style="color:red;">Super Admins</mark>. Rename it so that it can be identified with the cluster. This file will be used if cluster control via Rancher is unavailable.
* Additional Reference: [RKE2 High Availability Installation](https://docs.rke2.io/install/ha)

## NFS client provisioner&#x20;

This section assumes an[ NFS server](../nfs-server.md) has already been set up.  Install NFS client provisioner on the cluster as follows:

* Clone [https://github.com/OpenG2P/openg2p-deployment](https://github.com/OpenG2P/openg2p-deployment).
*   From [kubernetes/nfs-client](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/nfs-client) directory, run: (Make sure to replace the `<NFS Node Internal IP>` and `<cluster name>` parameters appropriately below)

    ```bash
    NFS_SERVER=<NFS Node Internal IP> \
    NFS_PATH=/srv/nfs/<cluster_name> \
        ./install-nfs-csi-driver.sh
    ```

{% hint style="info" %}
In StorageClass, when the `reclaimPolicy` is set to `Retain` it implies that, when a PVC is deleted the PV will not get deleted. And when a PV is deleted the relevant directory in NFS is also not deleted.

When `reclaimPolicy` is set to `Delete`, and if a PVC is deleted, both the PV and the relevant directory in the NFS get deleted.
{% endhint %}

### Longhorn&#x20;

This installation only applies if Longhorn is used as storage. This may be skipped if you are using NFS.

[Longhorn Install as a Rancher App](https://longhorn.io/docs/1.3.2/deploy/install/install-with-rancher/)

## Istio

Refer guide [here](istio.md).

## Cluster import to Rancher

This step assumes that a [Rancher server ](../rancher.md)has already been set up and operational.

* Navigate to the _Cluster Management_ section in Rancher
* Click on _Import Existing Cluster_. Follow the steps to import the new OpenG2P cluster
* After importing, download `kubeconfig` file for the new cluster from rancher (top right on the main page), to access the cluster through kubectl from the user's machine (client), without SSH

## Cluster access to users

Users may be given access to the cluster using [Rancher's RBAC](https://ranchermanager.docs.rancher.com/how-to-guides/new-user-guides/authentication-permissions-and-global-configuration/manage-role-based-access-control-rbac).&#x20;

{% hint style="info" %}
Rancher provides "Project" feature. This feature is not a standard Kubernetes feature and hence it is recommended to not use it for OpenG2P deployments.
{% endhint %}

## Backups

Your cluster may hold critical data that needs to be backed up.  The following minimal backups are highly recommended:

<table><thead><tr><th width="221">Backup item</th><th>Recommendations</th></tr></thead><tbody><tr><td>NFS data</td><td>Refer <a href="../nfs-server.md#backups">here</a>.</td></tr><tr><td>Persistent Volumes (PVs)</td><td>The PVs on NFS are stored as folders that are hard to associate with original application/pod. Download the YAML of critical PVs - like Postgres, Minio etc and keep it safely. This will be required in case a cluster has to be recreated, in which case, the corresponding PVs may be mounted back from the storage provided the name of the PV is known. On Rancher the PV YAMLs are available under <em>Storage -> PersistentVolumes</em> of a cluster.  Alternatively, you may  download PVs using command line utility <code>kubectl</code>.</td></tr></tbody></table>
