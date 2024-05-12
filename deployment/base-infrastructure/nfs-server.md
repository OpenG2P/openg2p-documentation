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

* Use this [Storage size estimator](../hardware-requirements.md#storage-requirements-for-pilot-environments) to decide storage requirements
* One Virtual machine running on the same network as the rest of the nodes, and is accessible by them. For recommended configuration of the VM refer to [Hardware Requirements](../hardware-requirements.md)

#### Install

* Download/copy this install script from [https://github.com/OpenG2P/openg2p-deployment/blob/main/nfs-server/install-nfs-server.sh](https://github.com/OpenG2P/openg2p-deployment/blob/main/nfs-server/install-nfs-server.sh) into the NFS server machine.
* (Optional) Edit the script to change the local path for NFS storage, under the variable `nfsStorage.`Make a note of this path as it will be required during the installation of the [NFS client provisioner.](cluster-setup/#nfs-client-provisioner)
*   Run the script with root privileges.&#x20;

    ```
    ./install-nfs-server.sh
    ```
* Give any name for the "environment" when asked. If NFS is specific to an environment you may specify that name.
* Make sure to edit the firewall rules of this VM to enable incoming traffic to the NFS server port `tcp 2049` and disable incoming traffic on all other ports (excluding SSH)

## Backups

If your NFS holds critical data, there should be some mechanism to backup the same.  On AWS you may use the 'snapshot' feature to schedule periodic (daily/weekly) backups of the VM running NFS. &#x20;
