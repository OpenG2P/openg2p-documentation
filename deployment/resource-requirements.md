# Resource Requirements

For a full deployment you need the following

1. Hardware requirements mentioned below.&#x20;
2. Public IP assigned to machine if public access is enabled (for public facing portals and apps)
3. [Domain names](resource-requirements.md#domain-names)&#x20;
4. [Domain mapping](resource-requirements.md#domain-mapping)
5. [Certificates](resource-requirements.md#certificates)

### Hardware requirements

### Domain names&#x20;

To access resources on cluster,  domain names and mappings are required.  The suggested domain name convention is as follows:

\<module>.\<environment>.\<organisation>.\<tld>

Example:&#x20;

* spar.dev.openg2p.org
* socialregistry.uat.openg2p.org

### Domain mapping

| Requirement Description      | Domain Name (examples)                                                                      | Mapped to                                                                                                                                             |
| ---------------------------- | ------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| Domain mapping to sandbox    | <ul><li>dev.openg2p.net</li><li>uat.openg2p.net</li><li>staging.openg2p.org</li></ul>       | "A" Record mapped to Load Balancer IP (For sandbox, where LB is not used, this can be mapped directly to nodes of the K8s cluster, at least 3 nodes). |
| Wild card mapping to modules | <ul><li>*.dev.openg2p.net</li><li>*.uat.openg2p.net</li><li>*.staging.openg2p.org</li></ul> | "CNAME" Record mapped to the domain of the above "A" record. (This is a wildcard DNS mapping)                                                         |

The domain name mapping needs to be done on your domain service provider.  For example, on AWS this is configured on Route 53.

### Certificates <a href="#certificates" id="certificates"></a>

At least one wildcard certificate is required depending on the above domain names used. This can also be generated using Letsencrypt. See guide [here](https://docs.openg2p.org/deployment/deployment-guide/ssl-certificates-using-letsencrypt).

##
