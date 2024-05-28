---
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

# NFS Server

NFS-based storage is recommended for providing persistent storage volumes to Kubernetes Clusters and backing up data of sandbox/pilot environments.

## Installation

#### Prerequisites

* One Virtual machine running on the same network as the rest of the nodes, and is accessible by them. For recommended configuration of the VM refer to [Hardware Requirements](../hardware-requirements.md)

#### Install

* Download/copy this install script from [https://github.com/OpenG2P/openg2p-deployment/blob/main/nfs-server/install-nfs-server.sh](https://github.com/OpenG2P/openg2p-deployment/blob/main/nfs-server/install-nfs-server.sh) into the NFS server machine.
*   Run the script with root privileges.&#x20;

    ```
    ./install-nfs-server.sh
    ```
* Make sure to edit the firewall rules of this VM to enable incoming traffic to the NFS server port `tcp 2049` and disable incoming traffic on all other ports (excluding SSH)
*   For every sandbox/namespace, create a new folder in `/srv/nfs` folder on the NFS node. Example:

    ```
    sudo mkdir /srv/nfs/rancher
    sudo mkdir /srv/nfs/prod
    sudo mkdir /srv/nfs/staging
    sudo chmod -R 777 /srv/nfs
    ```

## Backups

If your NFS holds critical data, there should be some mechanism to backup the same.  On AWS you may use the 'snapshot' feature to schedule periodic (daily/weekly) backups of the VM running NFS. &#x20;

{% hint style="info" %}
The Persistent Volumes (PV) of Kubernetes create folders of corresponding names in the NFS storage. The folders are not deleted even if you delete the PV from the cluster. Hence, it is recommended that a cleanup exercise is carried out to free up space. To identify folders with their respective applications see the notes [here](openg2p-cluster/cluster-setup/#backups).
{% endhint %}
