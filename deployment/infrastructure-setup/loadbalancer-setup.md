# Loadbalancer Setup

## Introduction

Load balancing in Kubernetes (K8s) is a crucial aspect of ensuring high availability, scalability, and reliability of applications running within the cluster. It involves distributing incoming network traffic across multiple pods or nodes to optimise resource utilisation and prevent any single point of failure.

## Installation on AWS

Note: The naming conventions may vary depending on the environment.

Follow the steps below to create a load balancer on AWS.

* Creating Target Group for **http**
* Creating Target Group for **https-redirect**
* Creating Target Group for **PostgreSQL**
* Creating  **Network Load Balancer**

### Creating Target Group for **http** <a href="#creating-target-group-for-openg2p-external-http" id="creating-target-group-for-openg2p-external-http"></a>

1. In the EC2 dashboard, under the "Load Balancing" section, select "Target Groups" from the left-hand navigation menu.
2. Click on the "Create target group" button to start the process of creating a new target group.
3. Configure Target Group
   * Choose target type - `Instance`
   * Target Group name - `openg2p-<envname>-http`
   * Protocol : Port - `TCP : 30080`
   * VPC - Select the VPC in which the instaces are located.
   * Health check protocol : Path : Port (**Traffic Port**)- `HTTP : /healthz/ready : 30521`
4. Register Targets
   * After configuring the target group, click on the "Next" button to proceed to the next step.
   * Select the targets (instances) to register with the target group.
   * Click on the "Add to registered" button to add the selected targets to the target group.
5. Review the configuration settings for the target group. Verify that all the settings are correct.Click on the "Create target group" button to create the target group.
6. Once the target group is created, make a note of the Amazon Resource Name (ARN) of the newly created target group. You will need this ARN when configuring load balancers or other services that use the target group.

### Creating Target Group for **https-redirect** <a href="#creating-target-group-for-openg2p-external-httpsredirect" id="creating-target-group-for-openg2p-external-httpsredirect"></a>

1. Choose target type - `Instance`
2. Target Group name - `openg2p-<envname>-httpsredirect`
3. Protocol : Port - `TCP : 30081`
4. VPC - `Choose vpc`
5. Health check protocol : Path : Port (**Overide**) - `HTTP : /healthz/ready : 30521`
6. Next, navigate to "Register Targets", verify the network settings, add cluster instances, and create the target group.

### Creating a Target Group for PostgreSQL <a href="#creating-a-target-group-for-postgresql" id="creating-a-target-group-for-postgresql"></a>

* Choose target type - `Instance`
* Target Group name - `openg2p-<envname>-postgres`
* Protocol : Port - `TCP : 32432`
* VPC - `choose vpc`
* Health check protocol : Path : Port (**Overide**) - `HTTP : /healthz/ready : 30521`
* Next, navigate to "Register Targets", verify the network settings, add cluster instances, and create the target group.

### Creating  **Network Load Balancer** <a href="#creating-external-network-load-balancer" id="creating-external-network-load-balancer"></a>

1. Create NLB with name - `openg2p-<envname>`
2. Select VPC -`general-vpc` do map for `ap-south-1a, 1b, 1c`
3. Select Security Group - `default-nginx-node`
4. Listeners and routing **Protocol : Port : Default action**
   * `TLS : 443 : openg2p-<envname>-http`
   * `TCP : 80 : openg2p-<envname>-httpsredirect`
5. Select `ACM certificate` as per environment domain name and create NLB.
6. Map LB according to the Environment on Route53.

## Installation on-prem

