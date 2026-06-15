---
description: Additional guides related to deployment on AWS
---

# AWS

{% hint style="info" %}
**For a standard production deployment on AWS, start with [Stage 2 — Provisioning](../../../operations/deployment/infrastructure-setup/provisioning.md).** The bundled `openg2p-aws-provision.sh` creates the production VMs (Reverse Proxy, Compute, Storage, and — with `backup_node.enabled: true` — the Backup node), networking, and the stable Elastic IP for the Reverse-Proxy node. The pages in this section are **manual / reference material** for the older AWS-LB exposure pattern and individual AWS tasks (ACM certificates, security groups, Route 53 mappings); they are not part of the supported automated flow.
{% endhint %}

These guides cover individual AWS console tasks that some deployments still perform by hand:

* [Create ACM Certificate on AWS](create-acm-certificate-on-aws.md)
* [Create Security Group on AWS](create-security-group-on-aws.md)
* [Domain mapping on AWS Route53](domain-mapping-on-aws-route53.md)
* [Make Environment Publicly Accessible using AWS LB Configuration](make-environment-publicly-accessible-using-aws-lb-configuration.md)
