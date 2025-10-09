---
description: Production Deployment Guide
---

# Production Deployment

The guide here provides some useful hints for production and pilot deployments. This guide is NOT intended to be a comprehensive production deployment handbook. Since production environments can vary widely, OpenG2P implementers—such as system integrators—have flexibility in choosing production configurations, orchestration platforms, and components. We also encourage our partners to contribute updates to this guide based on their real-world experiences and insights.

## Backups

Backups are <mark style="color:$danger;">**crtitical**</mark>  for any production deployment.  Ensure that the following backups are taken frequently, and supervised regularly:

* Periodic snapshotting and backup for Postgres DB, MinIO buckets and objects, all volumes in NFS. (TBD Guide)
* The Persistent Volume information of the Kubernetes cluster must be backed up after the installation. This is required in case the cluster goes down, or NFS has issues, the pods can be recreated with original data.
  * Download the YAMLs of PV in Rancher -> OpenG2P Cluster -> Storage -> Persistent Volumes and keep it securely accessible to system administrators.
  * Furthermore, this guide can be used to [restore a PV from an NFS folder](deployment-guide/restore-a-pvc-from-an-nfs-folder-and-attach-it-to-a-pod.md).
* ETCD needs to be backed up periodically. Refer to the guide [here](deployment-guide/etcd-backup-and-restore.md).

## Air-gapped deployment

Air-gapped deployment means that the nodes and cluster resources are placed in closed and tightly controlled network where the nodes cannot access the Internet, but users can access the nodes from the outside over Internet (or VPN).

### Private Docker registry

> _This section is not the same as a private image repository on Docker Hub, which still requires internet, albeit the docker image is not listed publicly._

This involves setting up a Docker registry to which all the Docker images required by the OpenG2P modules will be uploaded, and the Kubernetes Cluster will be pointed to this private registry instead of Public Docker hub. _(TBD Guide)_

Production Docker images will need to be pushed manually into this registry since there won't be any internet connection to pull automatically from Docker Hub.

### Private Git repositories

This setup requires configuring a Git server that is accessible within your network. The Git server will host repositories needed by OpenG2P modules at runtime, such as configuration files, scripts, and more. Additionally, storing Helm charts in this private Git server allows you to selectively deploy OpenG2P module upgrades by managing Helm chart versions. (Detailed guide TBD)

{% hint style="info" %}
You can [install Gitlab on a standalone instance](deployment-guide/air-gapped-deployment-setup-using-gitlab.md) on the same network. This acts as both a Git server and a private docker registry. Do read about the Gitlab products and their licenses before installing.
{% endhint %}

## Standalone PostgreSQL installation&#x20;

In the [OpenG2P deployment model ](openg2p-deployment-model.md) Postgres is installed on the same machine as the other services. However, if you wish to run Postgres on a separate machine for better maintaince, access control, and backups you may do so.  Please note the following:

* Master/Slave configuration is typically required for very high availability  applications.  If you are running portals that require 100% up-time then you may go for a Master/Slave configuration. In this case,  you will have to provision for sufficient hardware.
*   Production Configuration&#x20;

    **Note:** It is highly recommended that experienced Database Administrators determine the production configuration.

If you are moving your PostgreSQL DB from Docker to standalone machine refer to [Guide for migrating existing PostgreSQL docker to Standalone Instance](deployment-guide/transitioning-postgresql-from-docker-on-k8s-to-standalone-postgresql.md).

## Standalone MinIO installation

In the [OpenG2P deployment model ](openg2p-deployment-model.md) MinIO is installed as a Pod running on the Kubernetes cluster with undering storage on NFS. However, if you wish to run MinIO on a separate machine for better maintaince, access control, and backups you may follow the guide: [Standalone MinIO Installation Guide](deployment-guide/minio-standalone-installation-guide-on-ubuntu-vm.md).

## Backups

* Set up periodic snapshotting and backup for Postgres DB, MinIO buckets and objects, all volumes in NFS. (TBD Guide)
* The PV information must be backed up after the installation. In case the cluster goes down, or NFS has issues, the pods can be recreated with original data.
  * Download the YAMLs of PV in Rancher -> OpenG2P Cluster -> Storage -> Persistent Volumes and keep it securely accessible to system administrators.
  * Furthermore, this guide can be used to [restore a PV from an NFS folder](deployment-guide/restore-a-pvc-from-an-nfs-folder-and-attach-it-to-a-pod.md).
* ETCD needs to be backed up periodically. Refer to the guide [here](deployment-guide/etcd-backup-and-restore.md).

## Security

* Creation of [private access channels](deployment-guide/private-access-channel.md).

## Nginx & Load balancer

You may need to set Nginx load balancers in HA mode by having a Nginx cluster (available with Nginx Plus, but it comes with commercial terms). HA for Nginx is critical if user-facing portal traffic lands on the same Nginx. For back-office administration tasks, HA in Nginx may not be critical.

You must adjust the max request body size according to the number of files/data being uploaded. The general limit is set at 50MiB per request. This can be updated by modifying the `client_max_body_size` parameter in nginx.conf.

For cloud native deployment, you may consider moving to highly available cloud native load balancer depending on the use case and the available options.

## Docker Images

### Image Pull Policy

Ensure that image pull policy for all the docker images of the OpenG2P modules are set to `IfNotPresent`. This will prevent the system from pulling the docker images every time if the images already exist on the nodes.

This can be checked during installation of a module in Rancher -> Installed Apps -> (chose the OpenG2P module) -> Edit values.yaml -> Find all occurrences of `pullPolicy` across the yaml and ensure that the values are set to `IfNotPresent`.&#x20;

## Kubernetes configurations

### RBAC

Carefully assign roles to Rancher users. Pre-defined role templates are available on Rancher. Follow [this guide](https://ranchermanager.docs.rancher.com/how-to-guides/new-user-guides/authentication-permissions-and-global-configuration/manage-role-based-access-control-rbac/cluster-and-project-roles).  Specifically, protect the following action on resources:

* Deletion of Deployments/StatefulSets
* Viewing of Secrets - at all levels - Cluster, Namespace
* Deletion of Configmaps, Secrets
* Access to DB via port forwarding
* Logging into DB pods

### High availability of services

#### Pod replication

* Replication of pods for high-availability.

#### Node replication

* Provisioning of VMs across different underlying hardware and subnets for resilience.&#x20;
* Minimum 3 nodes for Rancher and OpenG2P cluster (3 control planes).

### Cluster Kubeconfig

Download the kubeconfig file of the OpenG2P RKE2 cluster and store it securely. This kubeconfig file allows users to perform any operation on the OpenG2P K8s cluster directly using `kubectl` (bypassing all RBAC set up on Rancher), like downloading K8s secrets, accessing pod logs, executing commands inside the pods, etc, even in case Rancher is not accessible. Hence it is very important to store this securely, so that only super admins of the project are allowed to access it.

## Data cleanup

Make sure any test or stray data in Postgres, OpenSearch or any other persistence is cleaned up completely before rollout.  In case of fresh installation of OpenG2P modules, make sure PVCs, and PVs from previous versions are deleted.

## OpenSearch

In development deployment mode, OpenSearch is installed as a single pod (that runs multiple roles). In production, switch to OpenSearch cluster deployment. OpenSearch cluster involves multiple pods each with different roles (like master, data, coordinating, ingest, etc).

Switching to OpenSearch Cluster deployment can be done directly during deployment of the OpenG2P Module _(TBD Guide)._
