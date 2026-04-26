# Resource Requirements

For a full deployment you need the following

1. Compute requirements
2. [Domain names](resource-requirements.md#domain-names)
3. [Domain mapping](resource-requirements.md#domain-mapping)
4. [Certificates](resource-requirements.md#certificates)
5. Additional requirements

## Compute requirements

### Single-node

| Machine Purpose   | Specs                                                                                                                | Notes                                                                                                                                                                                                                                                      |
| ----------------- | -------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Compute node      | <ul><li>16 vCPU/64 GB RAM/128 GB SSD</li><li>2 network interface cards</li><li>OS: Ubuntu Server 24.04<br></li></ul> | This configuration will let you install 2 environments with all OpenG2P modules loaded. For more, expand the virtual machines. The network interface cards are required to setup the[ private access channel](deployment-guide/private-access-channel.md). |
| Backup (optional) | <ul><li>2 vCPU/8 GB RAM/256 GB HDD/SDD</li></ul>                                                                     | Backup machine need not have SSD.                                                                                                                                                                                                                          |

### Three-node

| Machine Purpose    | Specs                                                                                                         | Notes                                                                                                                                                                                                                     |
| ------------------ | ------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Compute node       | <ul><li>16 vCPU/64 GB RAM/128 GB SSD</li><li>OS: Ubuntu Server 24.04</li></ul>                                | This configuration will let you install 2 environments with all OpenG2P modules loaded. For more, expand the virtual machines.                                                                                            |
| Storage node       | <ul><li>8 vCPU/32 GB/256 GB SSD</li><li>OS: Ubuntu Server 24.04</li></ul>                                     | If PostgreSQL is getting overloaded, the CPU/RAM may have to expanded                                                                                                                                                     |
| Reverse proxy node | <ul><li>2 vCPU/8 GB/64 GB SSD</li><li>2 network interface cards</li><li>OS: Ubuntu Server 24.04<br></li></ul> | Its not expected that this machine will get overloaded unless very high traffic applications. The network interface cards are required to setup the[ private access channel](deployment-guide/private-access-channel.md). |
| Backup (optional)  | <ul><li>2 vCPU/8 GB RAM/512 GB HDD/SDD</li></ul>                                                              | Backup machine need not have SSD.                                                                                                                                                                                         |

### Full-scale

<table><thead><tr><th width="182.60546875">Machine Purpose</th><th width="117.859375" align="center">Number of machines</th><th>Specs</th><th>Notes</th></tr></thead><tbody><tr><td>OpenG2P cluster Kubernetes nodes</td><td align="center">3</td><td><ul><li>8 vCPU/32 GB RAM/128 GB SSD</li><li>OS: Ubuntu Server 24.04</li></ul></td><td>Minimum 3 nodes are required for fail safety of Kubernetes 'master' node. All these nodes also act as 'workers'.</td></tr><tr><td>Rancher cluster Kubernetes nodes</td><td align="center">1</td><td><ul><li>8 vCPU/32 GB RAM/128 GB SSD</li><li>OS: Ubuntu Server 24.04</li></ul></td><td>The number of machines may be increased to 3 if high availablity of Rancher cluster is critically.</td></tr><tr><td>Reverse proxy node</td><td align="center">1</td><td><ul><li>2 vCPU/8 GB/64 GB SSD</li><li>2 network inteface cards</li><li>OS: Ubuntu Server 24.04</li></ul></td><td>Its not expected that this machine will get overloaded unless very high traffic applications.</td></tr><tr><td>Storage node</td><td align="center">1</td><td><ul><li>16 vCPU/64 GB/512 GB SSD</li><li>OS: Ubuntu Server 24.04</li></ul></td><td>Both PostgreSQL and NFS</td></tr><tr><td>Backup (optional)</td><td align="center">1</td><td><ul><li>2 vCPU/8 GB RAM/512 GB HDD/SDD</li></ul></td><td>Backup machine need not have SSD.</td></tr></tbody></table>

## Domain names

To access resources on cluster, domain names and mappings are required. The suggested domain name convention is as follows:

\<module>.\<environment>.\<organisation>.\<tld>

Example:

* spar.dev.openg2p.org
* socialregistry.uat.openg2p.org

## Domain mapping

| Requirement Description      | Domain Name (examples)                                                                             | Mapped to                                                                                                                                             |
| ---------------------------- | -------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| Domain mapping to sandbox    | <ul><li>dev.openg2p.net</li><li>uat.openg2p.net</li><li>staging.openg2p.org</li></ul>              | "A" Record mapped to Load Balancer IP (For sandbox, where LB is not used, this can be mapped directly to nodes of the K8s cluster, at least 3 nodes). |
| Wild card mapping to modules | <ul><li><em>.dev.openg2p.net</em></li><li>.uat.openg2p.net</li><li>*.staging.openg2p.org</li></ul> | "CNAME" Record mapped to the domain of the above "A" record. (This is a wildcard DNS mapping)                                                         |

The domain name mapping needs to be done on your domain service provider. For example, on AWS this is configured on Route 53.

## Certificates <a href="#certificates" id="certificates"></a>

At least one wildcard certificate is required depending on the above domain names used. This can also be generated using Letsencrypt. See guide [here](https://docs.openg2p.org/deployment/deployment-guide/ssl-certificates-using-letsencrypt).

## Additional requirements

There may be additional resources that may need to be arranged based on your requirements and rollout plan. Some of these are assumed to be available:

* Tablets/phones for offline registrations
* Firewall for on-prem setups

{% hint style="info" %}
**General Recommendations**

If you would like to get started with OpenG2P with couple of sandboxes like dev/qa go with single-node architecture. For pilot and production, the three-node architecture is highly recommened. If you decide to use the single-node setup for pilots, make sure you have backups in place - this is very important. In this case you may need to migrate the data from PostgreSQL on Kubernetes to standaone PostgreSQL server. Follow the migration guide give [here](deployment-guide/transitioning-postgresql-from-docker-on-k8s-to-standalone-postgresql.md).
{% endhint %}
