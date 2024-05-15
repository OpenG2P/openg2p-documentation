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

* Decide the number of K8s control-plane nodes (server nodes) and worker nodes (agent nodes).
  * Choose an odd number of control-plane nodes. For example, for a 3-node k8s cluster, choose 1 control-plane node and 2 worker nodes. For a 7-node k8s cluster, choose 3 control-plane nodes and 4 worker nodes.
* The following setup has to be done on each node on the cluster.
  * SSH into the node
  *   Create the rke2 config directory

      ```
      mkdir -p /etc/rancher/rke2
      ```
  * Create a `config.yaml` file in the above directory, using one of the following config file templates:
    * For the first control-plane node, use [rke2-server.conf.primary.template](https://github.com/OpenG2P/openg2p-deployment/blob/main/kubernetes/rke2/rke2-server.conf.primary.template)
    * For subsequent control-plane nodes, use [rke2-server.conf.subsequent.template](https://github.com/OpenG2P/openg2p-deployment/blob/main/kubernetes/rke2/rke2-server.conf.subsequent.template). (Make sure the token defined in the first node's control plane is used here too.)
    * For worker nodes, use [rke2-agent.conf.template](https://github.com/OpenG2P/openg2p-deployment/blob/main/kubernetes/rke2/rke2-agent.conf.template).  (Make sure the token defined in the first node's control plane is used here too.)
  * Edit the above `config.yaml` file with the appropriate names, IPs, and tokens
  *   Run this to download rke2.

      ```
      curl -sfL https://get.rke2.io | sh -
      ```
  * Run this to start rke2:
    *   On the control-plane node, run:

        ```
        systemctl enable rke2-server
        systemctl start rke2-server
        ```
    *   On the worker node, run:

        ```
        systemctl enable rke2-agent
        systemctl start rke2-agent
        ```
* To export KUBECONFIG, run (only on control-plane nodes):
* ```
  > echo -e 'export PATH="$PATH:/var/lib/rancher/rke2/bin"\nexport KUBECONFIG="/etc/rancher/rke2/rke2.yaml"' >> ~/.bashrc
  > source ~/.bashrc
  > kubectl get nodes    
  ```
* Download the Kubeconfig file `rke2.yaml` and keep it <mark style="color:red;">securely</mark> <mark style="color:red;"></mark><mark style="color:red;">**shared with only**</mark> <mark style="color:red;"></mark><mark style="color:red;">Super Admins</mark>. Rename it so that it can be identified with the cluster. This file will be used if cluster control via Rancher is unavailable.
* Additional Reference: [RKE2 High Availability Installation](https://docs.rke2.io/install/ha)

## NFS client provisioner&#x20;

This section assumes an[ NFS server](../nfs-server.md) has already been set up.  The NFS client provisioner runs on the cluster and connects seamlessly to the NFS server.  Install NFS client provisioner on the cluster as follows:

* Log in to each node and run `apt install nfs-common`.
* On your machine run [https://github.com/OpenG2P/openg2p-deployment/blob/main/kubernetes/nfs-client/install-nfs-client-provisioner.sh](https://github.com/OpenG2P/openg2p-deployment/blob/main/kubernetes/nfs-client/install-nfs-client-provisioner.sh)
* Provide the internal IP address of the NFS server (the IP must be accessible from Kubernetes nodes).
* Provide the path on which NFS was mounted on the NFS server (noted during NFS Server installation)

### Longhorn&#x20;

This installation only applies if Longhorn is used as storage. This may be skipped if you are using NFS.

[Longhorn Install as a Rancher App](https://longhorn.io/docs/1.3.2/deploy/install/install-with-rancher/)

## Istio&#x20;

* The following setup can be done from the client machine. This installs Istio Operator, Istio Service Mesh, Istio Ingressgateway components.
*   From [kubernetes/istio](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/istio) directory, configure the istio-operator.yaml, and run;

    ```
    istioctl operator init
    kubectl apply -f istio-operator.yaml
    ```

    *   If an external Loadbalancer is being used, then use the `istio-operator-external-lb.yaml` file.

        ```
        kubectl apply -f istio-operator-external-lb.yaml
        ```
    * Configure the operator.yaml with any further configuration
*   Gather Wildcard TLS certificate and key and run;\
    Note: To create TLS certificates refer [here](https://docs.openg2p.org/v/latest/deployment/deployment-guide/ssl-certificates-using-letsencrypt)

    ```
    kubectl create secret tls tls-openg2p-ingress -n istio-system \
        --cert=<CERTIFICATE PATH> \
        --key=<KEY PATH>
    ```
*   Create istio gateway for all hosts using this command:

    ```
    kubectl apply -f istio-gateway.yaml
    ```

    *   If using external loadbalancer/external TLS termination, use the `istio-gateway-no-tls.yaml` file

        ```
        kubectl apply -f istio-gateway-no-tls.yaml
        ```

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

<table><thead><tr><th width="221">Backup item</th><th>Recommended method</th></tr></thead><tbody><tr><td>NFS data</td><td>Backup the NFS server along with its storage. On AWS, this may be achieved using Snapshots. </td></tr><tr><td>Persistent Volumes (PVs)</td><td>The PVs on NFS are stored as folders that are hard to associate with original application/pod. Download the YAML of critical PVs - like Postgres, Minio etc and keep it safely. This will be required in case a cluster has to be recreated, in which case, the corresponding PVs may be mounted back from the storage provided the name of the PV is known. On Rancher the PV YAMLs are available under <em>Storage -> PersistentVolumes</em> of a cluster.  Alternatively, you may  download PVs using command line utility <code>kubectl</code>.</td></tr></tbody></table>
