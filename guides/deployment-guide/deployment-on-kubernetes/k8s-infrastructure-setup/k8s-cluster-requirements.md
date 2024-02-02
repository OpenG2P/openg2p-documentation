# K8s Cluster Requirements

## Hardware requirements

### For sandbox&#x20;

<table><thead><tr><th width="150">Purpose</th><th width="100" align="center">vCPUs</th><th width="105" align="center">RAM</th><th align="center">Storage (SSD)</th><th width="104" align="right"># of VMs</th><th>OS</th></tr></thead><tbody><tr><td>Cluster nodes</td><td align="center">8</td><td align="center">32 GB</td><td align="center">128 GB</td><td align="right">3</td><td>Ubuntu Server 20.04</td></tr><tr><td>Wireguard</td><td align="center">4</td><td align="center">16 GB</td><td align="center">64 GB</td><td align="right">1</td><td>Ubuntu Server 20.04</td></tr></tbody></table>

### For pilot

<table><thead><tr><th width="166">Purpose</th><th width="95" align="center">vCPUs</th><th width="98" align="center">RAM</th><th width="140" align="center">Storage (SSD)</th><th width="101" align="right"># of VMs</th><th>OS</th></tr></thead><tbody><tr><td>Cluster nodes</td><td align="center">8</td><td align="center">32 GB</td><td align="center">128 GB</td><td align="right">3</td><td>Ubuntu Server 20.04</td></tr><tr><td>Wireguard*</td><td align="center">4</td><td align="center">16 GB</td><td align="center">64 GB</td><td align="right">1</td><td>Ubuntu Server 20.04</td></tr><tr><td>Rancher*</td><td align="center">8</td><td align="center">32 GB</td><td align="center">128 GB</td><td align="right">1</td><td>Ubuntu Server<br>20.04</td></tr><tr><td>Nginx LB*</td><td align="center">4</td><td align="center">16 GB</td><td align="center">64 GB</td><td align="right">1</td><td>Ubuntu Server 20.04</td></tr><tr><td>NFS for Storage</td><td align="center">4</td><td align="center">16 GB</td><td align="center">1 TB*</td><td align="right">1</td><td>Ubuntu Server 20.04</td></tr></tbody></table>

\* Wireguard: One VM for Wireguard is sufficient for all the environments/setups in your network. This is used to facilitate VPN access to the pilot environments.

\* Rancher: One VM for Rancher is sufficient to manage all the K8s environments/setups. This is used to facilitate K8s Access Control & Management of the pilot environments.

\* Nginx LB: Nginx VMs for load balancing. These VMs are not required if using a Cloud Provider. Instead, it is recommended to use Cloud-native Load balancers.

\* NFS Storage Size: This will facilitate persistent storage for components in the K8s Cluster. The actual size of storage required will vary from setup to setup. Can be computed using the [Storage requirements](k8s-cluster-requirements.md#storage-requirements-for-pilot-environments).

## Networking requirements

* All the machines in the same network.
* Public IP assigned to the Wireguard machine.

## DNS requirements

The following domain names and mappings will be required. Examples:

| Requirement Description                                                        | Domain Name (examples)                                                                                                                                       | Mapped to                                                                                                                                                      |
| ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Top level domain that points to the sandbox.                                   | <p></p><ul><li>openg2p.<em>&#x3C;your domain></em></li><li>uat.<em>&#x3C;your domain></em></li><li>pilot.openg2p.<em>&#x3C;your domain></em></li></ul>       | "A" Record mapped to Load Balancer IP (For sandox, where loadbalancer is not present, this can be mapped directly nodes of the K8s Cluster, at least 3 nodes). |
| Wildcard subdomain for accessing individual components within OpenG2P sandbox. | <p></p><ul><li>*.openg2p.<em>&#x3C;your domain></em></li><li>*.uat.<em>&#x3C;your domain></em></li><li>*.pilot.openg2p.<em>&#x3C;your domain></em></li></ul> | "CNAME" Record mapped to the domain of the above "A" record. (This is a wildcard DNS mapping)                                                                  |

## Certificate requirements

One wildcard certificate is required at least, depending on the above domain names used. This can also be generated using Letsencrypt.

## Storage requirements for pilot environments

The following are the components in each K8s cluster that require persistent storage.

| Component          | Purpose                                                          | Size Estimate |
| ------------------ | ---------------------------------------------------------------- | ------------- |
| PostgreSQL         | Database for all modules                                         | TBD           |
| MinIO Object Store | For storing documents                                            | TBD           |
| OpenSearch         | For indexing service logs (And generating reports & dashboards). | TBD           |
| Total              |                                                                  | TBD           |

