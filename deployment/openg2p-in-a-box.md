---
description: Getting started with OpenG2P
---

# OpenG2P In a Box

This document describes a deployment model wherein the infrastructure and components required by OpenG2P modules can be set up on a single node/VM/machine.  This will help you to get started with OpenG2P and experience the functionality without having to meet all <mark style="color:blue;">r</mark>[esource requirements](hardware-requirements.md) for a production-grade setup. This is based on [V4 architecture](./#deployment-architecture), but a compact version of the same.  The essence of the V4 is preserved so that upgrading the infra is easier when more hardware resources are available.

## Deployment architecture

<figure><img src="../.gitbook/assets/openg2p-in-a-box.jpg" alt=""><figcaption><p>OpenG2P In a Box</p></figcaption></figure>

{% hint style="danger" %}
Do NOT use this deployment model for production/pilots.
{% endhint %}

## Installation

### Prerequisites

*   Take Machine with the following configuration.

    <table><thead><tr><th width="186">Purpose</th><th width="209">Compute/Memory/Storage</th><th>Note</th></tr></thead><tbody><tr><td>Wireguard Bastion / NFS Server / Rancher Cluster / OpenG2P Cluster / Nginx Server</td><td><p>16vCPU / 64 GB RAM /</p><p>256 GB storage / OS:Ubuntu 22.04</p></td><td>All the components mentioned will be installed on a single node.</td></tr></tbody></table>
* Before proceeding with the deployment, review the following topics to better understand each infrastructure component required for a successful setup:
  1. 🔒 **Firewall Rules**: Review basic firewall concepts and how to configure rules to allow traffic to and from required services.\
     [Read about Firewall Rules](https://docs.openg2p.org/deployment/base-infrastructure/openg2p-cluster/cluster-setup/firewall)
  2. 📦 **Kubernetes Cluster (RKE2 Server):** Understand how to set up and configure a lightweight, secure RKE2 Kubernetes cluster.\
     [Read about RKE2 Setup](https://docs.openg2p.org/deployment/base-infrastructure/openg2p-cluster/cluster-setup#cluster-installation)
  3. 🔐 **WireGuard Bastion:** Learn how to configure WireGuard as a secure VPN tunnel to access internal resources in your cluster.\
     [Read about WireGuard Bastion](https://docs.openg2p.org/deployment/base-infrastructure/wireguard-bastion#installation)
  4. 📁 **NFS Server:** Set up a Network File System to provide shared persistent storage across your Kubernetes workloads.\
     [Read about NFS Server](https://docs.openg2p.org/deployment/base-infrastructure/nfs-server#installation)
  5. 🔗 **Kubernetes NFS CSI Driver:** Deploy the CSI driver to enable dynamic NFS volume provisioning in Kubernetes.\
     [Read about NFS CSI Driver](https://docs.openg2p.org/deployment/base-infrastructure/openg2p-cluster/cluster-setup#nfs-client-provisioner)
  6. 🧩 **Istio Service Mesh:** Use Istio to manage traffic flow, security, and observability between microservices.\
     [Read about Istio](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/istio)
  7. 🔐 **SSL Certificates (Let's Encrypt):** Configure Let's Encrypt to automate SSL certificate issuance and renewal for secure access.\
     [Read about Let's Encrypt Setup](https://docs.openg2p.org/deployment/deployment-guide/ssl-certificates-using-letsencrypt)
  8. 🧑‍💻 **Rancher:** Use Rancher to manage and monitor your Kubernetes clusters through an intuitive web interface.\
     [Read about Rancher](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/rancher)
  9. 🧾 **Keycloak:** Implement Keycloak for identity, authentication, and authorization management using SSO and OIDC.\
     [Read about Keycloak](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/keycloak)
  10. 📊 **Prometheus Monitoring:** Set up Prometheus to collect metrics from your Kubernetes services and visualize them via Grafana.\
      [Read about Prometheus and Monitoring](https://docs.openg2p.org/deployment/base-infrastructure/openg2p-cluster/prometheus-and-grafana)
  11. 📝 **Logging and Fluentd:** Collect and centralize application logs using Fluentd for easier debugging and analysis.\
      Read about [Logging](https://docs.openg2p.org/pbms/functionality/monitoring-and-reporting/logging) and [Fluentd](https://docs.openg2p.org/deployment/base-infrastructure/openg2p-cluster/fluentd-and-opensearch)

### Base infrastructure setup

To set up the **base infrastructure**, log in to the machine and install the following. Make sure to follow each **verification step** to ensure that everything is installed correctly and the setup is progressing smoothly.\
**Note:** Perform all necessary installations on a **single node** as this configuration is designed to operate completely.

1.  Ensure that all the listed tools are installed on the node. After installation, verify the version of each tool to confirm that they have been installed correctly.\
    Tools: `wget` , `curl` , `kubectl` , `istioctl` , `helm` , `jq` \
    🔍 <mark style="color:red;">Verification Checkpoint:</mark>\
    <mark style="color:green;">Run the following commands and verify that each returns the version information:</mark>

    ```
    wget --version
    curl --version
    kubectl version --client
    istioctl version
    helm version
    jq --version
    ```

    ✅ <mark style="color:green;">You should see version details for each tool without any errors.</mark>
2. Follow the document linked below to set up the **firewall rules** required for the deployment.\
   🔒[Set up Firewall rules](https://docs.openg2p.org/deployment/base-infrastructure/openg2p-cluster/cluster-setup/firewall)\
   **Note:** Make sure to include K8s Firewall, NFS Firewall, Wireguard Firewall, and LB Firewall.\
   🔍 <mark style="color:red;">Verification Checkpoint:</mark>\
   <mark style="color:green;">Run</mark> <mark style="color:green;"></mark><mark style="color:green;">`iptables -L`</mark> <mark style="color:green;"></mark><mark style="color:green;">or</mark> <mark style="color:green;"></mark><mark style="color:green;">`ufw status`</mark> <mark style="color:green;"></mark><mark style="color:green;">to ensure the rules are active in case you're using on-premises or self-managed native server nodes. If you're deploying on AWS cloud infrastructure, verify or configure the necessary firewall rules within the</mark> <mark style="color:green;"></mark><mark style="color:green;">**Security Groups**</mark> <mark style="color:green;"></mark><mark style="color:green;">associated with your instances.</mark>
3. Follow the below steps to Setup **Kubernetes Cluster** (RKE2 Server) as a **root user**.
   1. Create the rke2 config directory - `mkdir -p /etc/rancher/rke2`
   2. &#x20;Create a `config.yaml` file in the above directory, using the following config file template.\
      Use [rke2-server.conf.primary.template](https://github.com/OpenG2P/openg2p-deployment/blob/main/kubernetes/rke2/rke2-server.conf.primary.template). The token can be any arbitrary string.
   3. Edit the above `config.yaml` file with the appropriate names, IPs, and tokens.
   4.  Run the following commands to set the **RKE2 version** and **download** and **start RKE2** **server:**

       ```
       export INSTALL_RKE2_VERSION="v1.28.9+rke2r1"
       curl -sfL https://get.rke2.io | sh - 
       systemctl enable rke2-server
       systemctl start rke2-server
       ```
   5.  To export KUBECONFIG, run:

       ```
       echo -e 'export PATH="$PATH:/var/lib/rancher/rke2/bin"\nexport KUBECONFIG="/etc/rancher/rke2/rke2.yaml"' >> ~/.bashrc
       source ~/.bashrc
       kubectl get nodes 
       ```

       **Note**:Download the Kubeconfig file `rke2.yaml` and keep it securely.\
       🔍 <mark style="color:red;">Verification Checkpoint:</mark>\ <mark style="color:green;">Run the below command to check the status of rke2 server shown in the screenshot below.</mark>&#x20;

       <figure><img src="../.gitbook/assets/image (34).png" alt=""><figcaption></figcaption></figure>
4. Install **Wireguard** Bastion servers for secure VPN access:
   1. Clone the [openg2p-deployment](https://github.com/OpenG2P/openg2p-deployment) repo and navigate to the [kubernetes/wireguard](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/wireguard) directory
   2.  Run this command to install wireguard server/channel with root user:

       ```bash
       WG_MODE=k8s ./wg.sh <name for this wireguard server> <client ips subnet mask> <port> <no of peers> <subnet mask of the cluster nodes & lbs>
       ```

       For example:

       ```
       WG_MODE=k8s ./wg.sh wireguard_app_users 10.15.0.0/16 51820 254 172.16.0.0/24
       ```
   3.  Check logs of the servers and wait for all servers to finish startup. Example:

       ```bash
       kubectl -n wireguard-system logs -f wireguard-app-users
       ```
   4. Once it finishes, navigate to `/etc/wireguard-app-users`. You will find multiple peer configuration files and cd in to `peer1` folder and copy `peer1.conf`  to your notepad.
   5.  Follow the link provided below to setup a WireGuard on your local system.\
       [Install WireGuard Client on Desktop](base-infrastructure/wireguard-bastion/install-wireguard-client-on-machine.md)\
       🔍 <mark style="color:red;">Verification Checkpoint:</mark>\ <mark style="color:green;">Make sure the WireGuard server is running and the setup is completed on your local machine. You can refer to the screenshots below for guidance.</mark>\ <mark style="color:green;">On server node:</mark>

       <figure><img src="../.gitbook/assets/image (18).png" alt=""><figcaption></figcaption></figure>

       <mark style="color:green;">On you local machine:</mark>

       <figure><img src="../.gitbook/assets/image (24).png" alt=""><figcaption></figcaption></figure>
   6. Once WireGuard is running and setup on your local machine, you can easily set up kubectl locally and access the cluster from your machine. (Optional)
5. Install NFS Server to provide **persistent storage volumes** to Kubernetes Cluster:
   1.  Download/copy the install script from the link provided below into the server machine.\
       [NFS Installation script ](https://docs.openg2p.org/deployment/base-infrastructure/nfs-server#installat)

       To install an NFS server, run the following command as root user:

       ```bash
       ./install-nfs-server.sh
       ```
   2.  For every sandbox/namespace, create a new folder in `/srv/nfs` folder on the server node. Suggested folder structure: `/srv/nfs/<cluster name>`. \
       **Example:**

       ```
       sudo mkdir /srv/nfs/rancher
       sudo mkdir /srv/nfs/openg2p
       ```

       Run this command to provide full accces for nfs folder `sudo chmod -R 777 /srv/nfs` \
       🔍 <mark style="color:red;">Verification Checkpoint:</mark>\
       <mark style="color:green;">Make sure the NFS server is running and the setup is completed on your local machine. You can refer to the screenshots below for guidance.</mark>

       <figure><img src="../.gitbook/assets/image (35).png" alt=""><figcaption></figcaption></figure>
6. Install the Kubernetes **NFS CSI driver** and the **NFS client provisioner** on the cluster as follows:
   1. Clone [https://github.com/OpenG2P/openg2p-deployment](https://github.com/OpenG2P/openg2p-deployment).
   2.  From [kubernetes/nfs-client](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/nfs-client) directory, **run**: (Make sure to replace the `<Node Internal IP>` and `<cluster name>` parameters appropriately below)

       ```
       NFS_SERVER=<Node Internal IP> \
       NFS_PATH=/srv/nfs/<cluster_name> \
           ./install-nfs-csi-driver.sh
       ```

       🔍 <mark style="color:red;">Verification Checkpoint:</mark>\
       <mark style="color:green;">Make sure the NFS CSI driver and client provisioner is running and the setup is completed on your local machine. You can refer to the screenshots below for guidance.</mark>

       <figure><img src="../.gitbook/assets/image (36).png" alt=""><figcaption></figcaption></figure>
7.  To set up **Istio** in the cluster, navigate to the directory linked below from the **openg2p-deployment** repository and run the provided commands to install the **Istio Operator**, **Istio Service Mesh**, and **Istio Ingress Gateway** components.\
    Install Istio from [kubernetes/istio](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/istio) directory:

    ```bash
    istioctl install -f istio-operator-no-external-lb.yaml
    kubectl apply -f istio-ef-spdy-upgrade.yaml
    ```

    Wait for `istiod` and `ingressgateway` pods to start on **istio-system** namespace.\
    🔍 <mark style="color:red;">Verification Checkpoint:</mark>\
    <mark style="color:green;">Check whether all the Istio pods have come up; refer to the screenshot below.</mark>

    <figure><img src="../.gitbook/assets/image (37).png" alt=""><figcaption></figcaption></figure>
8. Set up Transport Layer Security (TLS) for secure communication by following the steps outlined below. This will ensure that data transmitted between services is encrypted and protected from unauthorized access:
   1.  Install **letsencrypt** and **certbot** using below command:

       ```
       sudo apt install certbot
       ```
   2.  Since the preferred challenge is DNS type, the below command asks for `_acme-challenge.` Create the `_acme-challenge` **TXT** DNS record accordingly using a Public DNS Provider **(e.g., AWS Route 53, Cloudflare, GoDaddy)**, and continue with the prompt to generate certs.

       <figure><img src="../.gitbook/assets/image (44).png" alt=""><figcaption></figcaption></figure>
   3.  Create SSL Certificate using Letsencrypt for **Rancher** by editing **hostname** below:

       ```bash
       certbot certonly --agree-tos --manual \
           --preferred-challenges=dns \
           -d rancher.your.org
       ```

       Create **Rancher TLS Secret** using below command (Edit **certificate paths** below):

       ```bash
       kubectl -n istio-system create secret tls tls-rancher-ingress \
           --cert /etc/letsencrypt/live/rancher.your.org/fullchain.pem \
           --key /etc/letsencrypt/live/rancher.your.org/privkey.pem
       ```
   4.  Create SSL Certificate using Letsencrypt for **Keycloak** by editing **hostname** below:

       ```bash
       certbot certonly --agree-tos --manual \
           --preferred-challenges=dns \
           -d keycloak.your.org
       ```

       Create **Keycloak TLS** **Secret**, using (Edit **certificate paths** below):

       ```bash
       kubectl -n istio-system create secret tls tls-keycloak-ingress \
           --cert /etc/letsencrypt/live/keycloak.your.org/fullchain.pem \
           --key /etc/letsencrypt/live/keycloak.your.org/privkey.pem
       ```

       🔍 <mark style="color:red;">Verification Checkpoint:</mark>\
       <mark style="color:green;">After creating the certificates, verify that they are present in the /etc/letsencrypt/live/ directory and have been uploaded to the istio-system namespace as a Kubernetes secret. Refer the screenshot below. and use this command to check the secrets.</mark>

       ```
       kubectl get secrets -n istio-system
       ```

       <figure><img src="../.gitbook/assets/image (40).png" alt=""><figcaption></figcaption></figure>
9.  Set up **DNS** **records** for the Rancher and Keycloak hostnames so that they resolve to the public (or private, depending on your setup) IP address of the node where the services are exposed. This can be achieved in the following way:

    Using a Public DNS Provider **(e.g., AWS Route 53, Cloudflare, GoDaddy)**:

    Create A records (or CNAMEs, if appropriate) for the fully qualified domain names (FQDNs) you plan to use for Rancher and Keycloak (e.g., rancher.example.com and keycloak.example.com).

    Point these records to the Internal IP address of node.\
    🔍 <mark style="color:red;">Verification Checkpoint:</mark>\
    <mark style="color:green;">The screenshot below is an example of DNS mapping using AWS Route 53. You can use any DNS provider as per your requirements, and the domain mapping should be similar to what is shown in the screenshot.</mark>

    <figure><img src="../.gitbook/assets/image (42).png" alt=""><figcaption></figcaption></figure>
10. To Install **rancher** in the cluster, navigate to the directory linked below from the **openg2p-deployment** repository and run the provided command to install the rancher (Edit **hostname** below):\
    Install rancher from [kubernetes/rancher](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/rancher) directory:

    ```bash
    RANCHER_HOSTNAME=rancher.your.org \
    TLS=true \
    ./install.sh --set replicas=1 --version 2.9.3
    ```

    Login to Rancher using the above hostname and bootstrap the `admin` user according to the instructions. After successfully logging in to Rancher as admin, save the new admin user password in `local` cluster, in `cattle-system` namespace, under `rancher-secret`, with key `adminPassword`.\
    🔍 <mark style="color:red;">Verification Checkpoint:</mark>\
    <mark style="color:green;">Use the command below to verify that all Rancher pods are running properly in the cattle-system namespace, and ensure that Rancher is accessible from your browser. Refer the screenshot.</mark>

    <figure><img src="../.gitbook/assets/image (46).png" alt=""><figcaption></figcaption></figure>

    <figure><img src="../.gitbook/assets/image (47).png" alt=""><figcaption></figcaption></figure>
11. To Install **keycloak** in the cluster, navigate to the directory linked below from the **openg2p-deployment** repository and run the provided command to install the rancher (Edit **hostname** below):\
    Install rancher from [kubernetes/keycloak](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/keycloak) directory:

    ```bash
    KEYCLOAK_HOSTNAME=keycloak.your.org \
    TLS=true \
    ./install.sh --set replicaCount=1
    ```

    Log in to Keycloak using the configured hostname, and retrieve the admin user credentials from the Rancher UI by checking the Kubernetes secrets in the keycloak namespace.\
    🔍 <mark style="color:red;">Verification Checkpoint:</mark>\
    <mark style="color:green;">Use the command below to verify that all keycloak pods are running properly in the keycloak-system namespace, and ensure that keycloak is accessible from your browser. Refer the screenshot.</mark>

    <figure><img src="../.gitbook/assets/image (48).png" alt=""><figcaption></figcaption></figure>

    <figure><img src="../.gitbook/assets/image (49).png" alt=""><figcaption></figcaption></figure>
12. Integrate **Rancher** with **Keycloak** for Centralized Authentication.\
    Integrating Rancher with Keycloak allows you to use Keycloak as an identity provider (IdP) for Rancher, enabling centralized authentication and user management. This is especially useful in environments where single sign-on (SSO) and role-based access control (RBAC) are required across multiple services. Refer the link provide below to do the same.\
    [Steps to Integrate Rancher with Keycloak](https://docs.openg2p.org/deployment/base-infrastructure/rancher)\
    🔍 <mark style="color:red;">Verification Checkpoint:</mark>\
    <mark style="color:green;">Once you attempt to log in using rancher.hostname.org, you will be redirected to authenticate via Keycloak. Log in using your Keycloak credentials. In Rancher, your user status should appear as "Active," as shown in the screenshot.</mark>

    <figure><img src="../.gitbook/assets/image (50).png" alt=""><figcaption></figcaption></figure>

    **Note:** So, this completes the base infrastructure setup for OpenG2P, and you can now begin installing the **OpenG2P applications** by following the steps below.
13. Now, continue to use the same cluster (`local` cluster) for **OpenG2P** Modules installation also.
    1. In Rancher, create a Project and Namespace, on which the OpenG2P modules will be installed. **The rest of this guide will assume the namespace to be `dev`**.
    2.  In Rancher -> Namespaces menu, enable **Istio Auto Injection** for `dev` namespace.\
        🔍 <mark style="color:red;">Verification Checkpoint:</mark>\
        <mark style="color:green;">Refer to the screenshot below for the dev namespace under the dev project, and ensure that Istio injection is enabled.</mark>

        <figure><img src="../.gitbook/assets/image (51).png" alt=""><figcaption></figcaption></figure>
14. Set up an Istio gateway on **dev** namespace for a domain.
    1.  Provide your **hostname** and run this to define the variables:

        ```
        export NS=dev
        export WILDCARD_HOSTNAME='*.dev.your.org'
        ```
    2.  Go to [kubernetes/istio](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/istio) directory from **openg2p-deployment** repository and run this to apply gateway.

        ```bash
        kubectl create ns $NS
        envsubst < istio-gateway-tls.yaml | kubectl apply -f -
        ```
    3.  Create **SSL Certificate** using **Letsencrypt** for the wildcard hostname used above. Example usage(provide your hostname):

        ```bash
        certbot certonly --agree-tos --manual \
            --preferred-challenges=dns \
            -d dev.your.org \
            -d *.dev.your.org
        ```

        Create OpenG2P TLS Secret, using (Edit certificate paths below):

        ```
        kubectl -n istio-system create secret tls tls-openg2p-$NS-ingress \
            --cert=<certificate path> \
            --key=<certificate key path>
        ```
    4.  You can follow **step 9** for DNS record setup.\
        🔍 <mark style="color:red;">Verification Checkpoint:</mark>\
        <mark style="color:green;">Once you create the gateway, you should be able to see it under the Rancher UI in the Istio > Gateway section for the dev namespace. The SSL certificates will be stored in the /etc/letsencrypt/live directory. Refer to the screenshot below.</mark>

        <figure><img src="../.gitbook/assets/image (53).png" alt=""><figcaption></figcaption></figure>
15. Install Prometheus and enable cluster monitoring directly from the Rancher UI. Follow the link provided below to complete the deployment.\
    Install [Prometheus and Monitoring](base-infrastructure/openg2p-cluster/prometheus-and-grafana.md) on OpenG2P Cluster.\
    🔍 <mark style="color:red;">Verification Checkpoint:</mark>\
    <mark style="color:green;">Once monitoring is installed in Rancher, navigate to the Monitoring section where you'll see options for Alertmanager and Grafana. You can click on these to access their respective dashboards.</mark>

    <figure><img src="../.gitbook/assets/image (55).png" alt=""><figcaption></figcaption></figure>
16. Install **Logging** and **Fluentd** Installation.

    Fluentd is used to collect and parse logs generated by applications within the Kubernetes cluster.

    Only one Fluentd installation is required per Kubernetes cluster.

    To install **Fluentd** using **Rancher UI**:

    1. Navigate to **Apps** (or **Apps & Marketplace**) → **Charts**.
    2. Search for and select the **Logging** chart.
    3. Install it using the default values.
    4. When prompted, select **Project: System** to ensure Fluentd runs in the appropriate system namespace.\
       🔍 <mark style="color:red;">Verification Checkpoint:</mark>\
       <mark style="color:green;">Once logging is installed, verify that all pods in the cattle-logging-system namespace are up and running, and ensure that logs are being collected for each service.</mark>

### OpenG2P module's installation

You can follow the below links to install **OpenG2P** modules via **Rancher UI**.

1. Install [SocialRegistry](https://docs.openg2p.org/social-registry/deployment) Module.
2. Install [PBMS](https://docs.openg2p.org/pbms/deployment) Module.
3. Install [SPAR](https://docs.openg2p.org/spar/deployment) Module.
4.  Install [OpenG2P Landing Page](https://docs.openg2p.org/deployment/base-infrastructure/openg2p-cluster/landing-page-for-openg2p). \
    🔍 <mark style="color:red;">Verification Checkpoint:</mark>\
    <mark style="color:green;">Once you deploy any of the modules mentioned above, you can also deploy the OpenG2P Landing Page. All services should then be accessible from your web browser. Refer to the screenshot for reference.</mark>

    <figure><img src="../.gitbook/assets/image (56).png" alt=""><figcaption></figcaption></figure>

{% hint style="info" %}
**How is "In a Box" different from** [**V4**](./#deployment-architecture-v4)**? Why should this not be used for production?**

* In-a-box does not use the Nginx Load Balancer. The HTTPS traffic directly terminates on the Istio gateway via Wireguard. However, Nginx is required in production as described [here](base-infrastructure/load-balancer/nginx.md).
* The SSL certificates are loaded on the Istio gateway while in V4 the certificates are loaded on the Nginx server.
* The Wireguard bastion runs inside the Kubernetes cluster itself as a pod. This is not recommended in production where Wireguard must run on a separate node.
* A single private[ access channel](deployment-guide/private-access-channel.md) is enabled (via Wireguard).  In production, you will typically need several channels for access control.
* In-a-box **does not offer high availability** as the node is a single point of failure.&#x20;
* NFS runs inside the box. In production, NFS must run on a separate node with its access control, allocated resources and backups.
{% endhint %}
