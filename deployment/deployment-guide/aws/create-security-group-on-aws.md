---
description: Guide to create Security Group on AWS
---

# Create Security Group on AWS

## Introduction

A security group acts as a virtual firewall for your EC2 instances to control incoming and outgoing traffic. When you launch an instance, you can specify one or more security groups. Each security group contains rules that allow traffic to or from its associated instances. Security groups are stateful, meaning if you allow an incoming request from an IP address, the response to that request is automatically allowed, regardless of inbound rules. This makes managing access and security for your instances both flexible and powerful.

### Steps&#x20;

1. Go to EC2 dashboard and under Networks & Security click on Security Group and click on create Security Group.
2. To configure Security Group add name, description and VPC.
3. Add inbound and outbound rules as per the Firewall rules mentioned [here](https://docs.openg2p.org/\~/changes/xKUM0sBXFkyR8F24yAMq/deployment/base-infrastructure/openg2p-cluster/cluster-setup/firewall).
4. After configuring the inbound and outbound rules, review the settings. Create the security group.



