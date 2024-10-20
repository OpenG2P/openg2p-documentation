---
description: Guide to create public load balancer
---

# Make Environment Publicly Accessible using AWS LB Configuration

This document provides step-by-step instructions to make environment publicly accessible without wire guard configuration. Generally, all environments are privately accessible using wire guard configuration.

Notes:

The naming conventions may vary depending on the environment and this documentation will be applicable when using an AWS load balancer.

### Create Target Group for external-**http** <a href="#creating-target-group-for-openg2p-external-http" id="creating-target-group-for-openg2p-external-http"></a>

1. In the EC2 dashboard, under the _**Load Balancing**_ section, select _**Target Groups**_ from the menu.
2. Click the _**Create Target Group**_ button to create a new Target Group.
3. Configure Target Group
   * Choose target type - `IP addresses`
   * Target Group name - `openg2p-<envname>-external-http`
   * Protocol : Port - `TCP : 30080`
   * VPC - Select the VPC in which the instances are located
   * Health check protocol : Path : Port (**Traffic Port**) - `HTTP : /healthz/ready : 30521`
4. Register Targets
   * After configuring the Target Group, click the _**Next**_ button.
   * Select the targets (instances) to register with the Target Group.
   * Click the _**Add to registered**_ button to add the selected targets to the Target Group.
5. Review the configuration settings for the Target Group. After verification, click the _**Create Target Group**_ button to create the Target Group.
6. Once the Target Group is created, make a note of the Amazon Resource Name (ARN) of the newly created Target Group. This ARN is required when you configure Load Balancers or other services that use the Target Group.

### Create Target Group for external-**httpsredirect** <a href="#creating-target-group-for-openg2p-external-httpsredirect" id="creating-target-group-for-openg2p-external-httpsredirect"></a>

1. To create a Target Group for "external-httpsredirect," follow the same steps mentioned above. Only for the **Configure Target Group** section, use the following configurations.
   * Choose target type - `IP addresses`
   * Target Group name - `openg2p-<envname>-ext-httpsredirect`
   * Protocol : Port - `TCP : 30081`
   * VPC - Select the VPC in which the instances are located.
   * Health check protocol : Path : Port (**Overide**) - `HTTP : /healthz/ready : 30521`

### Create a Target Group for PostgreSQL <a href="#creating-a-target-group-for-postgresql" id="creating-a-target-group-for-postgresql"></a>

1. For PostgreSQL, there is no need to create a Target Group (TG). Instead, create a record with the name **internal.sandbox-name** and map the Internal NLB DNS name of the environment to it in AWS Route53.

### Create external n**etwork Load Balancer** <a href="#creating-external-network-load-balancer" id="creating-external-network-load-balancer"></a>

1. In the EC2 dashboard, click the _**Load Balancers**_ tab and then click _**Create Load Balancer.**_
2. Choose Load Balancer Type as **Network Load Balancer.**
3.  Configure Load Balancer Settings

    * Create NLB with name - `openg2p-<envname>-external`
    * Select VPC - Select the VPC and region in which the instances are located
    *   Select Security Group - Select the Security Group in which the instances are located

        &#x20;Notes:

    &#x20;      Click [here](create-security-group-on-aws.md) to create Security Group, if required

    *   Configure Routing - Define Target Groups to route traffic to specific instances

        *   Listeners and routing **Protocol : Port : Default action**

            Notes:   &#x20;

        &#x20;      Below the default action, select the Target Groups already created from the above steps.

        * `TLS : 443 : openg2p-<envname>-external-http`
        * `TCP : 80 : openg2p-<envname>-ext-httpsredirect`
        *   Select `ACM certificate` as per environment domain name.

            Notes:&#x20;

        &#x20;      Click [here](create-acm-certificate-on-aws.md) to create ACM certificate, if required.
    * Review the configuration settings and create the Load Balancer.
    * Do mapping on AWS Route53.

