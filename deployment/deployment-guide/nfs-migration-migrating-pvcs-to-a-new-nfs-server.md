---
description: >-
  This document explains how to migrate all existing Persistent Volume Claim
  (PVC) data from an old NFS server to a new NFS server, and reconnect your
  Kubernetes cluster to the new NFS node.
---

# NFS Migration – Migrating PVC's to a New NFS Server

### Prerequisites

* You already have,an existing NFS server connected to your Kubernetes cluster and PVC data stored on the old NFS node.
* You have prepared a **new NFS server/node** where you want to migrate the data.

### Steps to perform NFS migration

1. Prepare the new nfs server
   1. Install NFS server packages on the **new NFS machine**.
   2.  Configure the same export path used in the old server, for example:

       ```bash
       /srv/nfs/openg2p/<env-name>
       ```
   3. Set up **passwordless SSH** between the new and old NFS servers for data copy.
2. Stop applications using the PVCs (important)
   1. Before copying data, ensure **no application is reading or writing** to the PVCs.
   2.  You should **scale down all deployments/statefulsets using PVCs or shut down the entire environment**.\
       Example to scale down all deployments in a namespace:

       ```bash
       kubectl scale deploy --all -n <namespace> --replicas=0
       kubectl scale statefulset --all -n <namespace> --replicas=0
       ```
3. Copy pvc data from old nfs to new nfs
   1.  Use `rsync` to securely copy existing environment PVC data.

       ```bash
       rsync -aADEHU root@172.51.12.117:/srv/nfs/openg2p/<folder-name> /srv/nfs/<folder-name>
       example:
       rsync -aADEHU root@172.51.12.117:/srv/nfs/openg2p/openg2p /srv/nfs/openg2p
       ```

       **Note**: Make sure the NFS path and folder name should be same as old NFS node and you should always perfrom this as root user.
4. Update pv's in kubernetes to point to new nfs ip
   1.  Run the provided script to patch all PersistentVolumes with the **new NFS server IP**. And make sure to provide the namespace in the script.

       <pre class="language-bash"><code class="lang-bash">#!/usr/bin/env bash
       <strong>if [ -z "$NEW_NFS_SERVER_IP" ]; then
       </strong>    echo "New server IP required!!"
           exit 1
       fi
       if [ -z "$TMP_PV_YAML_PATH" ]; then
           export TMP_PV_YAML_PATH=/tmp/move-pv.yaml
       fi
       # 👇 Add the namespaces you want to patch
       NAMESPACES="&#x3C;provide the namespace name>"
       sleep 10
       for ns in $NAMESPACES; do
           echo "===== Processing namespace: $ns ====="
           PV_LIST=$(kubectl get pv -o jsonpath="{range .items[?(@.spec.claimRef.namespace=='$ns')]}{.metadata.name}{'\n'}{end}")
           for pv in $PV_LIST; do
               echo "patching pv started --- $pv"
               [ -f $TMP_PV_YAML_PATH ] &#x26;&#x26; rm $TMP_PV_YAML_PATH
               kubectl get pv $pv -oyaml > $TMP_PV_YAML_PATH
               # Update NFS server
               sed -i "s/server:.*/server: $NEW_NFS_SERVER_IP/g" $TMP_PV_YAML_PATH
               # Update volumeHandle IP only
               sed -i "s/[0-9]\{1,3\}\(\.[0-9]\{1,3\}\)\{3\}#/${NEW_NFS_SERVER_IP}#/g" $TMP_PV_YAML_PATH
               kubectl delete pv/$pv &#x26;
               delete_pid=$!
               sleep 1
               kubectl patch pv/$pv --type json \
                 --patch='[{"op": "remove", "path": "/metadata/finalizers"}]'
               if [ $? -eq 0 ]; then
                   wait $delete_pid
                   kubectl apply -f $TMP_PV_YAML_PATH
               fi
               echo "patching pv done --- $pv"
           done
       done
       </code></pre>


   2.  Run the below commands

       ```bash
       export NEW_NFS_SERVER_IP=<NEW NFS IP>
       ./updatepv.sh
       ```
5. Update nfs provisioner with new server ip
   1. Download the NFS CSI YAML file from your NFS storage class, update it with the new NFS IP address, and reapply it.\
      **Note:** Make sure to delete the previous NFS storage class before you re-apply.
6. Start applications using the PVCs (Important)
   1. Now you can **scale up the replicas for each deployment and statefulset**, and the services will reconnect to their respective PVCs.
7. Validate migration
   1. Confirm PVs point to new NFS server.
   2. Ensure pods successfully mount PVCs.
   3. Restart affected workloads if required.
   4. Verify data integrity and application functionality.
