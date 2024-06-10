---
description: Guide to create Security Group on AWS
---

# Create Security Group on AWS

A security group acts as a virtual firewall for your EC2 instances to control incoming and outgoing traffic. When you launch an instance, you can specify one or more security groups. Each security group contains rules that allow traffic to or from its associated instances. Security groups are stateful, meaning if you allow an incoming request from an IP address, the response to that request is automatically allowed, regardless of inbound rules. This makes managing access and security for your instances both flexible and powerful.

## Procedure

The steps to create _**Security Group**_ on AWS are given below.

1. Login to AWS. Navigate to the EC2 dashboard.
2. In _**Networks & Security**_ section, click the _**Security Group**_ and then click the _**Create Security Group**_.
3. Enter the _**Name**_, _**Description**_, and the _**VPC**_ in the associated fields to configure Security Group.
4. Set the inbound and outbound rules as per the firewall rules mentioned [here](https://docs.openg2p.org/\~/changes/xKUM0sBXFkyR8F24yAMq/deployment/base-infrastructure/openg2p-cluster/cluster-setup/firewall).
5. After configuring the inbound and outbound rules, recheck the settings. Create the security group.
