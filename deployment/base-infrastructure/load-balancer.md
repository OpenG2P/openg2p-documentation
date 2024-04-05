---
layout:
  title:
    visible: true
  description:
    visible: false
  tableOfContents:
    visible: true
  outline:
    visible: true
  pagination:
    visible: true
---

# Load Balancer

Load balancing in Kubernetes (K8s) is essential to ensure high availability, scalability, and reliability of applications running within the cluster. It involves distributing incoming network traffic across multiple pods or nodes to optimise resource utilisation and prevent any single point of failure.

## Installation on AWS

Follow the steps below to create a load balancer on AWS.

Note: The naming conventions may vary depending on the environment.

* Creating Target Group for **http**
* Creating Target Group for **https-redirect**
* Creating Target Group for **PostgreSQL**
* Creating  **Network Load Balancer**

### Creating Target Group for **http** <a href="#creating-target-group-for-openg2p-external-http" id="creating-target-group-for-openg2p-external-http"></a>

1. In the EC2 dashboard, under the "Load Balancing" section, select "Target Groups" from the menu.
2. Click the "Create Target Group" button to create a new Target Group.
3. Configure Target Group
   * Choose target type - `Instance`
   * Target Group name - `openg2p-<envname>-http`
   * Protocol : Port - `TCP : 30080`
   * VPC - Select the VPC in which the instances are located
   * Health check protocol : Path : Port (**Traffic Port**) - `HTTP : /healthz/ready : 30521`
4. Register Targets
   * After configuring the Target Group, click the "Next" button
   * Select the targets (instances) to register with the Target Group
   * Click the "Add to registered" button to add the selected targets to the Target Group
5. Review the configuration settings for the Target Group. After verification, click the "Create Target Group" button to create the Target Group.
6. Once the Target Group is created, make a note of the Amazon Resource Name (ARN) of the newly created Target Group. This ARN is required when you configure Load Balancers or other services that use the Target Group.

### Creating Target Group for **https-redirect** <a href="#creating-target-group-for-openg2p-external-httpsredirect" id="creating-target-group-for-openg2p-external-httpsredirect"></a>

1. To create a Target Group for "https-redirect," follow the same steps mentioned above. Only for the "**Configure Target Group**" section, use the following configurations.
   * Choose target type - `Instance`
   * Target Group name - `openg2p-<envname>-httpsredirect`
   * Protocol : Port - `TCP : 30081`
   * VPC - Select the VPC in which the instances are located
   * Health check protocol : Path : Port (**Overide**) - `HTTP : /healthz/ready : 30521`

### Creating a Target Group for PostgreSQL <a href="#creating-a-target-group-for-postgresql" id="creating-a-target-group-for-postgresql"></a>

1. To create a Target Group for "PostgreSQL," follow the same steps mentioned above. Only for the "**Configure Target Group**" section, use the following configurations.
   * Choose target type - `Instance`
   * Target Group name - `openg2p-<envname>-postgres`
   * Protocol : Port - `TCP : 32432`
   * VPC - Select the VPC in which the instances are located
   * Health check protocol : Path : Port (**Overide**) - `HTTP : /healthz/ready : 30521`

### Creating **Network Load Balancer** <a href="#creating-external-network-load-balancer" id="creating-external-network-load-balancer"></a>

1. In the EC2 dashboard, click the "Load Balancers" tab and then click "Create Load Balancer" and Choose Load Balancer Type as **Network Load Balancer.**
2. Configure Load Balancer Settings
   * Create NLB with name - `openg2p-<envname>`
   * Select VPC - Select the VPC and region in which the instances are located
   *   Select Security Group - Select the Security Group in which the instances are located

       &#x20;Note:  Click here to create Security Group, if required
   * Configure Routing - Define Target Groups to route traffic to specific instances
     *   Listeners and routing **Protocol : Port : Default action**

         Note: Below default action, select the Target Groups already created from the above steps.
     * `TLS : 443 : openg2p-<envname>-http`
     * `TCP : 80 : openg2p-<envname>-httpsredirect`
     *   Select `ACM certificate` as per environment domain name.

         Note: Click here to create ACM certificate, if required
   * Review the configuration settings and create the Load Balancer
   * Do mapping on AWS Route53

## Installation on on-prem

In an on-premises environment, we have two methods for load balancing:

* &#x20;Use Istio as a Load Balancer
* Use NGINX External Load Balancer

### &#x20;Istio as a Load Balancer

1. When opting to use Istio as the load balancer, it will handle all load balancing tasks for the cluster. To install and set up Istio, please refer to the documentation provided [here](https://docs.openg2p.org/v/latest/deployment/infrastructure-setup/cluster-setup#istio-setup).
2. For the creation of a Wildcard TLS certificate, please refer to the documentation provided [here](https://docs.openg2p.org/v/latest/deployment/deployment-guide/ssl-certificates-using-letsencrypt).
3. Do mapping on AWS Route53

### NGINX external Load Balancer

1. When opting  to setup nginx as external Load Balancer/Reverse Proxy into OpenG2P Cluster.\
   To install and set up NGINX, please refer to the documentation provided [here](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/nginx).
2. For the creation of a Wildcard TLS certificate, please refer to the documentation provided [here](https://docs.openg2p.org/v/latest/deployment/deployment-guide/ssl-certificates-using-letsencrypt).
3. Do mapping on AWS Route53





