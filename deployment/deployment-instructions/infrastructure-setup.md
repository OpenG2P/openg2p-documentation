# Infrastructure Setup

{% hint style="info" %}
**CONCETPS**: Before proceeding with deployment, read up on the following topics (using material available on the Internet) to better understand each infrastructure component required for a successful setup:

1. 🔒 **Firewall Rules**
2. 📦 **Kubernetes**&#x20;
3. 🔐 **WireGuard**&#x20;
4. 📁 **NFS**&#x20;
5. 🔗 [**Kubernetes NFS CSI Driver**](https://docs.openg2p.org/deployment/base-infrastructure/openg2p-cluster/cluster-setup#nfs-client-provisioner)
6. 🧩 **Istio**&#x20;
7. 🔐 **SSL Certificates**
8. 🧑‍💻 **Rancher**
9. 🧾 **Keycloak**
10. 📊 **Prometheus & Grafana**
11. 📝 **Fluentd**
{% endhint %}

## Base infrastructure setup

To set up the **base infrastructure**, log in to the machine and install the following. Make sure to follow each **verification step** to ensure that everything is installed correctly and the setup is progressing smoothly.

#### **1. Tools setup**

Install the following tools. After installation, verify the version of each tool to confirm that they have been installed correctly.\
Tools: `wget` , `curl` , `kubectl` , `istioctl` , `helm` , `jq`&#x20;

🔍 <mark style="color:red;">Verification Checkpoint:</mark>\
<mark style="color:green;">Run the following commands and verify that each returns version information without errors.</mark>

```bash
wget --version
curl --version
kubectl version --client
istioctl version
helm version
jq --version
```

#### **2. Firewall setup**

Follow the link below to set up the firewall rules required for the deployment.\
🔒[Set up Firewall rules](https://docs.openg2p.org/deployment/base-infrastructure/openg2p-cluster/cluster-setup/firewall)

🔍 <mark style="color:red;">Verification Checkpoint:</mark>\
<mark style="color:green;">Run</mark> <mark style="color:green;"></mark><mark style="color:green;">`iptables -L`</mark> <mark style="color:green;"></mark><mark style="color:green;">or</mark> <mark style="color:green;"></mark><mark style="color:green;">`ufw status`</mark> <mark style="color:green;"></mark><mark style="color:green;">to ensure the rules are active in case you're using on-premises or self-managed native server nodes. If you're deploying on AWS cloud infrastructure, verify or configure the necessary firewall rules within the</mark> <mark style="color:green;"></mark><mark style="color:green;">**Security Groups**</mark> <mark style="color:green;"></mark><mark style="color:green;">associated with your instances.</mark>

#### **3. Kubernetes cluster installation**

Follow the below steps to set up Kubernetes Cluster (RKE2 Server) as a `root` user.

1. Create the rke2 config directory - `mkdir -p /etc/rancher/rke2`
2. &#x20;Create a `config.yaml` file in the above directory, using the following config file template.\
   Use [rke2-server.conf.primary.template](https://github.com/OpenG2P/openg2p-deployment/blob/main/kubernetes/rke2/rke2-server.conf.primary.template). The token can be any arbitrary string.
3. Edit the above `config.yaml` file with the appropriate names, IPs, and tokens.
4.  Run the following commands to set the `RKE2` version, download  the same and start RKE2 server:

    ```bash
    export INSTALL_RKE2_VERSION="v1.28.9+rke2r1"
    curl -sfL https://get.rke2.io | sh - 
    systemctl enable rke2-server
    systemctl start rke2-server
    ```
5.  Export KUBECONFIG:

    ```bash
    echo -e 'export PATH="$PATH:/var/lib/rancher/rke2/bin"\nexport KUBECONFIG="/etc/rancher/rke2/rke2.yaml"' >> ~/.bashrc
    source ~/.bashrc
    kubectl get nodes 
    ```

{% hint style="warning" %}
Download the Kubeconfig file `rke2.yaml` and keep it securely. (This is important!)
{% endhint %}

🔍 <mark style="color:red;">Verification Checkpoint:</mark>\ <mark style="color:green;">Check the status of rke2 server as shown in the screenshot below.</mark>&#x20;

<figure><img src="../../.gitbook/assets/image (34) (1).png" alt=""><figcaption></figcaption></figure>

#### **4. Wireguard installation**

Install Wireguard Bastion server for secure VPN access:

1. Clone the [openg2p-deployment](https://github.com/OpenG2P/openg2p-deployment) repo and navigate to the [kubernetes/wireguard](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/wireguard) directory
2.  Run this command to install wireguard server/channel with root user:

    ```bash
    WG_MODE=k8s ./wg.sh <name for this wireguard server> <client ips subnet mask> <port> <no of peers> <subnet mask of the cluster nodes & lbs>
    ```

    For example:

    ```bash
    WG_MODE=k8s ./wg.sh wireguard_app_users 10.15.0.0/16 51820 254 172.16.0.0/24
    ```
3.  Check logs of the servers and wait for all servers to finish startup. Example:

    ```bash
    kubectl -n wireguard-system logs -f wireguard-app-users
    ```
4. Once it finishes, navigate to `/etc/wireguard-app-users`. You will find multiple peer configuration files and CD in to `peer1` folder and copy `peer1.conf`  to your notepad.
5. Follow the link provided below to setup a WireGuard on your system.\
   [Install WireGuard Client on Desktop](../scaling/base-infrastructure/wireguard-bastion/install-wireguard-client-on-machine.md)

🔍 <mark style="color:red;">Verification Checkpoint:</mark>\ <mark style="color:green;">Make sure the WireGuard service is running on k8s cluster and the Wireguard setup is completed on your machine.</mark>\ <mark style="color:green;">On k8s cluster:</mark>

<div align="left"><figure><img src="../../.gitbook/assets/image (25).png" alt=""><figcaption></figcaption></figure></div>

<mark style="color:green;">On your machine:</mark>

<div align="left"><figure><img src="../../.gitbook/assets/image (23).png" alt=""><figcaption></figcaption></figure></div>

{% hint style="success" %}
After installing WireGuard on the cluster and configuring it on your local machine, you can install and configure `kubectl` using the RKE2 kubeconfig file generated during the Kubernetes cluster setup on the server. This allows you to access the cluster from your local command line.
{% endhint %}

#### **5. NFS Server installation**

&#x20;Install NFS Server to provide persistent storage volumes to kubernetes cluster:

1.  Follow the openg2p-deployment repository under the [openg2p-deployment/nfs-server](https://github.com/OpenG2P/openg2p-deployment/blob/main/nfs-server/install-nfs-server.sh) directory to install the NFS server. Run the following command as the root user.

    ```bash
    ./install-nfs-server.sh
    ```
2.  For every sandbox/namespace, create a new folder in `/srv/nfs` folder on the server node. Suggested folder structure: `/srv/nfs/<cluster name>`. \
    Example:

    ```bash
    sudo mkdir /srv/nfs/rancher
    sudo mkdir /srv/nfs/openg2p
    ```

    Run this command to provide full accces for `nfs` folder `sudo chmod -R 777 /srv/nfs`&#x20;

🔍 <mark style="color:red;">Verification Checkpoint:</mark>\
&#x20;<mark style="color:green;">Make sure the NFS server is running and the setup is completed on server node.</mark>

<div align="left" data-full-width="false"><figure><img src="../../.gitbook/assets/image (24).png" alt=""><figcaption></figcaption></figure></div>

3. Install the Kubernetes NFS CSI driver and the NFS client provisioner on the cluster.
4.  From openg2p-deployment repo [kubernetes/nfs-client](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/nfs-client) directory, **run**: (Make sure to replace the `<Node Internal IP>` and `<cluster name>` parameters appropriately below)

    ```bash
    NFS_SERVER=<Node Internal IP> \
    NFS_PATH=/srv/nfs/<cluster_name> \
        ./install-nfs-csi-driver.sh
    ```

🔍 <mark style="color:red;">Verification Checkpoint:</mark>\
<mark style="color:green;">Make sure the NFS CSI driver and client provisioner is running and the setup is completed on server node.</mark>

<div align="left"><figure><img src="../../.gitbook/assets/image (36).png" alt=""><figcaption></figcaption></figure></div>

#### **6. Istio installation**

To set up Istio from [kubernetes/istio](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/istio) directory, run the commands below to install the Istio Operator, Istio Service Mesh, and Istio Ingress Gateway components. Wait for `istiod` and `ingressgateway` pods to start on istio-system namespace.

```bash
istioctl install -f istio-operator-no-external-lb.yaml
kubectl apply -f istio-ef-spdy-upgrade.yaml
```

🔍 <mark style="color:red;">Verification Checkpoint:</mark>\
<mark style="color:green;">Check whether all the Istio pods have come up.</mark>

<div align="left"><figure><img src="../../.gitbook/assets/image (21) (1).png" alt=""><figcaption></figcaption></figure></div>

#### **7.** Setting up TLS certificates for domain

Set up TLS/SSL certificates for your domain (e.g., sandbox.\<your-domain>) to enable secure, encrypted communication between services.\
Ensure certificates are created for the following four domains to enable HTTPS in the environment:

<table data-header-hidden><thead><tr><th width="206"></th><th width="219"></th><th></th></tr></thead><tbody><tr><td><strong>Purpose</strong></td><td><strong>Domain Example</strong></td><td><strong>Description</strong></td></tr><tr><td>Rancher UI</td><td><code>rancher.example.com</code></td><td>Used to access the Rancher web interface</td></tr><tr><td>Keycloak Authentication</td><td><code>keycloak.example.com</code></td><td>Used for authentication via Keycloak</td></tr><tr><td>Sandbox Environment</td><td><code>sandbox.example.com</code></td><td>Main entry point for the sandbox environment</td></tr><tr><td>Wildcard for Sandbox</td><td><code>*.sandbox.example.com</code></td><td>Covers subdomains like <code>app.sandbox.example.com</code>, etc.</td></tr></tbody></table>

Follow the below steps to generate SSL certifiactes for each domain.

1.  Install letsencrypt and certbot using below command:

    ```bash
    sudo apt install certbot
    ```
2. Since the preferred challenge is DNS type, the below commands asks for `_acme-challenge.` Create the `_acme-challenge` TXT DNS record accordingly using a Public DNS Provider (e.g., AWS Route 53, Cloudflare, GoDaddy), and continue with the prompt to generate certs and map the value in DNS Provider.
3.  Create SSL Certificate using letsencrypt for **`rancher`** by editing hostname below:

    ```bash
    certbot certonly --agree-tos --manual \
        --preferred-challenges=dns \
        -d rancher.example.com
    ```

    Create Rancher TLS Secret using below command (edit certificate paths below):

    ```bash
    kubectl -n istio-system create secret tls tls-rancher-ingress \
        --cert /etc/letsencrypt/live/rancher.example.com/fullchain.pem \
        --key /etc/letsencrypt/live/rancher.example.com/privkey.pem
    ```

    Screenshot for TXT record mapping:

    <figure><img src="../../.gitbook/assets/image (17).png" alt=""><figcaption></figcaption></figure>
4.  Create SSL Certificate using letsencrypt for **`keycloak`** by editing hostname below:

    ```bash
    certbot certonly --agree-tos --manual \
        --preferred-challenges=dns \
        -d keycloak.example.com
    ```

    Create Keycloak TLS Secret, using (edit certificate paths below):

    ```bash
    kubectl -n istio-system create secret tls tls-keycloak-ingress \
        --cert /etc/letsencrypt/live/keycloak.example.com/fullchain.pem \
        --key /etc/letsencrypt/live/keycloak.example.com/privkey.pem
    ```

    Screenshot for TXT record mapping:

    <figure><img src="../../.gitbook/assets/image (18).png" alt=""><figcaption></figcaption></figure>
5.  Create SSL Certificate using letsencrypt for **`Sandbox Environment`** and **`Wildcard for Sandbox`** at the same time by editing hostname below and keep it ready for future use:

    ```bash
    certbot certonly --agree-tos --manual \
        --preferred-challenges=dns \
        -d dev.example.com \  
        -d *.dev.example.com
    ```

    Create OpenG2P-Sandbox envrionment TLS Secret, using (Edit certificate paths below):

    <pre class="language-bash"><code class="lang-bash">export NS=&#x3C;sandbox-name>
    <strong>kubectl -n istio-system create secret tls tls-openg2p-$NS-ingress \
    </strong>    --cert /etc/letsencrypt/live/dev.example.com/fullchain.pem \
        --key /etc/letsencrypt/live/dev.example.com/privkey.pem
    </code></pre>

    **Note:** `You can name your sandbox anything, e.g., dev, qa, or test`. Make sure to note it down for future use, as you’ll use the same name for the **project and namespace** when creating them in Rancher.\
    Screenshot for TXT record mapping:

    <figure><img src="../../.gitbook/assets/image (21).png" alt=""><figcaption></figcaption></figure>

🔍 <mark style="color:red;">Verification Checkpoint:</mark>\ <mark style="color:green;">After creating the certificates, verify that they are present in the /etc/letsencrypt/live/ directory and have been uploaded to the istio-system namespace as a Kubernetes secret.</mark>

<div align="left"><figure><img src="../../.gitbook/assets/image (4) (1).png" alt=""><figcaption></figcaption></figure></div>

#### **8.** Mapping domains to cluster IP

Set up DNS records for the Rancher and Keycloak, OpenG2P-Sandbox hostnames so that they resolve to the private IP address of the node where the services are exposed. Using a public DNS provider (e.g., AWS Route 53, Cloudflare, GoDaddy) or a provider of your choice.

Create **A** records (or **CNAMEs**, if appropriate) for the fully qualified domain names (FQDNs) you plan to use for Rancher and Keycloak, OpenG2P-Sandbox (e.g., rancher.example.com and keycloak.example.com, dev.example.com, \*.dev.example.com).

{% hint style="success" %}
Point these records to the **Internal IP** address of node.
{% endhint %}

🔍 <mark style="color:red;">Verification Checkpoint:</mark>\
<mark style="color:green;">The screenshot below is an example of DNS mapping using AWS Route 53. You can use any DNS provider as per your requirements, and the domain mapping should be similar to what is shown in the</mark> \ <mark style="color:green;">screenshot.</mark>

<div align="left"><figure><img src="../../.gitbook/assets/image (2) (1).png" alt=""><figcaption></figcaption></figure></div>

#### **9. Rancher installation**

Install rancher from [kubernetes/rancher](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/rancher) directory (edit hostname):

```bash
RANCHER_HOSTNAME=rancher.example.com \
NS=cattle-system \
TLS=true \
./install.sh --set replicas=1 --version 2.9.3
```

Login to Rancher using the above hostname and bootstrap the `admin` user according to the instructions. After successfully logging in to Rancher as admin, save the new admin user password in `local` cluster, in `cattle-system` namespace, under `rancher-secret`, with key `adminPassword`.

🔍 <mark style="color:red;">Verification Checkpoint:</mark>\
<mark style="color:green;">Verify that all Rancher pods are running properly in the cattle-system namespace, and Rancher is accessible from your browser.</mark>&#x20;

<div align="left"><figure><img src="../../.gitbook/assets/image (61).png" alt=""><figcaption></figcaption></figure></div>

<div align="left"><figure><img src="../../.gitbook/assets/image (62).png" alt=""><figcaption></figcaption></figure></div>

#### **10. keycloak installation**

Install keycloak from [kubernetes/keycloak](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/keycloak) directory (edit hostname):

```bash
KEYCLOAK_HOSTNAME=keycloak.example.com \
NS=keycloak-system \
TLS=true \
./install.sh --set replicaCount=1
```

Log in to Keycloak using admin credentials from the Keycloak namespace secrets in Rancher UI.

🔍 <mark style="color:red;">Verification Checkpoint:</mark>\
<mark style="color:green;">Verify Keycloak pods in the</mark> <mark style="color:green;"></mark><mark style="color:green;">`keycloak-system`</mark> <mark style="color:green;"></mark><mark style="color:green;">namespace and ensure it's accessible in your browser.</mark>

<div align="left"><figure><img src="../../.gitbook/assets/image (9) (1).png" alt=""><figcaption></figcaption></figure></div>

<div align="left"><figure><img src="../../.gitbook/assets/image (49).png" alt=""><figcaption></figcaption></figure></div>

#### 11. Integrating Rancher with Keycloak&#x20;

[Integrating Rancher with Keycloak](https://docs.openg2p.org/deployment/base-infrastructure/rancher#rancher-keycloak-integration) enables centralized authentication and user management using Keycloak as the IdP.

🔍 <mark style="color:red;">Verification Checkpoint:</mark>\
<mark style="color:green;">Once you attempt to log in using rancher.hostname.org, you will be redirected to authenticate via Keycloak. Log in using your Keycloak credentials. In Rancher, your user status should appear as "Active," as shown in the screenshot.</mark>

<div align="left"><figure><img src="../../.gitbook/assets/image (50).png" alt=""><figcaption></figcaption></figure></div>

{% hint style="success" %}
So, this completes the base infrastructure setup for OpenG2P, and you can now begin installing the `OpenG2P modules` by following the steps below.
{% endhint %}

#### **12. Creating a project and namespace**

Continue to use the same cluster (`local` cluster) for OpenG2P modules  installation.

In Rancher, create a project and namespace, on which the OpenG2P modules will be installed.

{% hint style="info" %}
&#x20;The rest of this guide assumes the namespace to be `dev`, as the TLS certificates were created for the domain `dev.example.com` during the certificate setup.
{% endhint %}

{% hint style="warning" %}
In Rancher, make sure that `Istio auto-injection` for the dev namespace is disabled.
{% endhint %}

🔍 <mark style="color:red;">Verification Checkpoint:</mark>\
&#x20;<mark style="color:green;">Verify your project name and namespace appear under project/namespace section.</mark>

<figure><img src="../../.gitbook/assets/image (82).png" alt=""><figcaption></figcaption></figure>

#### **13. Istio** gateway setup

&#x20;Set up an Istio gateway on `dev` namespace.

1.  Provide your hostname and run this to define the variables:

    ```bash
    export NS=dev
    export WILDCARD_HOSTNAME='*.dev.example.com'
    ```
2.  Go to [kubernetes/istio](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/istio) directory and run this to apply gateway.

    ```bash
    envsubst < istio-gateway-tls.yaml | kubectl apply -f -
    ```

🔍 <mark style="color:red;">Verification Checkpoint:</mark>\
&#x20;<mark style="color:green;">Once created, the gateway will appear in Rancher UI under Istio > Gateway in the dev namespace.</mark>   &#x20;

<div align="left"><figure><img src="../../.gitbook/assets/image (11).png" alt=""><figcaption></figcaption></figure></div>

#### **14. Cluster Monitoring installation**

Install [Prometheus and Monitoring](../scaling/base-infrastructure/openg2p-cluster/prometheus-and-grafana.md)  enable cluster monitoring directly from the Rancher UI.

🔍 <mark style="color:red;">Verification Checkpoint:</mark>\
<mark style="color:green;">Once monitoring is installed in Rancher, navigate to the Monitoring section where you'll see options for Alertmanager and Grafana. You can click on these to access their respective dashboards.</mark>

<figure><img src="../../.gitbook/assets/image (55).png" alt=""><figcaption></figcaption></figure>

#### **15. Cluster Logging installation**

Install [Logging and Fluentd](https://docs.openg2p.org/deployment/base-infrastructure/openg2p-cluster/fluentd-and-opensearch#fluentd-installation) is used to collect and parse logs generated by applications within the Kubernetes cluster.

🔍 <mark style="color:red;">Verification Checkpoint:</mark>\
<mark style="color:green;">Once logging is installed, verify that all pods in the cattle-logging-system namespace are up and running, and ensure that logs are being collected for each service.</mark>

{% hint style="success" %}
This completes the OpenG2P cluster setup and you can now proceed with installing the OpenG2P modules.
{% endhint %}
