---
description: Production Deployment Guide
---

# Production Deployment

The guide here provides some useful hints for production deployment. It is assumed that you are familiar with the [V4 deployment architecture](./#v4-deployment-architecture) and have already deployed the same for your development. This guide is NOT intended to be a comprehensive production deployment handbook. Since production environments can vary widely, OpenG2P implementers—such as system integrators—have flexibility in choosing production configurations, orchestration platforms, and components. We also encourage our partners to contribute updates to this guide based on their real-world experiences and insights.

## Air-gapped deployment

Air-gapped deployment means that the nodes and cluster resources are placed in closed and tightly controlled network where the nodes cannot access the Internet, but users can access the nodes from the outside over Internet (or VPN).

### Private Docker registry

_\[This section is not the same as a private image repository on Docker Hub, which still requires internet, albeit the docker image is not listed publicly.]_

This involves in setting up a docker registry to which all the docker images required by the OpenG2P modules will be uploaded, and the Kubernetes Cluster will be pointed to this private registry instead of Public Docker hub. _(TBD Guide)_

Newer tags of docker images will need to be pushed manually into this registry since there won't be any internet connection to pull automatically.

### Private Git repositories

This involves in setting up a Git Server that is accessible within the network. This new Git server will store some repos required by OpenG2P modules during runtime. These repos include config repos, script repos, etc. This also gives the advantage of selectively pushing OpenG2P module upgrades in the form of Helm chart versions, since helm charts will also be stored in one of the repos in the private Git server. _(TBD Guide)_

{% hint style="info" %}
You can [install Gitlab on a standalone instance](deployment-guide/air-gapped-deployment-setup-using-gitlab.md) on the same network. This acts as both git server and private docker registry. Do read about the Gitlab products and their licenses before installing.
{% endhint %}

## Standalone PostgreSQL installation&#x20;

* Postgres on a separate machine with high capacity.&#x20;
* Number of instances of PostgreSQL nodes
  * Master / Slave configuration
* Cloud native if available
* Production configuration
* [Guide for migrating existing PostgreSQL docker to Standalone Instance](deployment-guide/transitioning-postgresql-from-docker-on-k8s-to-standalone-postgresql.md).

## Standalone MinIO installation

* MinIO on separate machine with high capacity.
* MinIO data directory pointed to a separate disk (or partition) that uses a filesystem ([XFS](https://wiki.ubuntu.com/XFS) for example) which can handle large number of files.
* [Standalone MinIO Installation Guide](deployment-guide/minio-standalone-installation-guide-on-ubuntu-vm.md).

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
