# Set up ClamAV virus scanning for incoming traffic

## Description

This guide is for setting up ClamAV antivirus and the steps to set up virus scanning for files being uploaded by users onto OpenG2P Modules.

Please note that this guide only applies to enabling virus scanning for HTTP traffic coming into a particular module from outside (ingress), and this doesn't apply to virus scanning for service-to-service traffic.

### Flow description

All the incoming traffic to the particular service will first be sent to Clammit. Clammit will then scan the requests for Virus with ClamAV. If no viruses are found, Clammit will forward the request to the backend service. If viruses are found, Clammit will deny the request.

<figure><img src="../../.gitbook/assets/Clammit Proxy.png" alt=""><figcaption></figcaption></figure>

## Installation

Only one ClamAV + Clammit installation is enough for the entire Kubernetes Cluster (for all namespaces/sandboxes). This installation can be individually scaled up depending on incoming traffic.

### ClamAV Installation

This section uses Wiremind Helm charts for ClamAV installation on Kubernetes.

*   Create `clamav-system` namespace.

    <pre class="language-sh" data-full-width="false"><code class="lang-sh">kubectl create ns clamav-system
    </code></pre>
* \[Optional] Move `clamav-system` namespace into `System` project in Rancher to manage access control.
*   Add wiremind helm repo

    <pre class="language-sh" data-full-width="false"><code class="lang-sh">helm repo add wiremind https://wiremind.github.io/wiremind-helm-charts
    helm repo update
    </code></pre>
*   &#x20;Install ClamAV in `clamav-system` namespace.

    <pre class="language-sh" data-full-width="false"><code class="lang-sh">helm -n clamav-system upgrade --install clamav wiremind/clamav
    </code></pre>

### Clammit Installation

* Requires ClamAV from above.
*   Add openg2p helm repo

    <pre class="language-sh" data-full-width="false"><code class="lang-sh">helm repo add openg2p https://openg2p.github.io/openg2p-helm
    helm repo update
    </code></pre>
*   &#x20;Install Clammit in `clamav-system` namespace.

    <pre class="language-sh" data-full-width="false"><code class="lang-sh">helm -n clamav-system upgrade --install clammit openg2p/clammit
    </code></pre>

## Virus-scan setup

This section describes the configuration process to pass all incoming traffic of a particular service for virus scanning, using the previously installed Clammit instance.

* Navigate to Rancher -> Istio -> Virtual Services, choose the virtual service for which you want to enable virus scanning, and edit as YAML.
*   Copy the route -> destination -> host and port number. Under headers -> request -> set, add a header like:

    <pre class="language-yaml" data-full-width="false"><code class="lang-yaml">x-clammit-backend: http://{destination_host}.{destination_namespace}:{destination_port}
    </code></pre>
*   Change the route -> destination -> host and port number to the following.

    <pre class="language-yaml" data-full-width="false"><code class="lang-yaml">route:
      - destination:
          host: clammit.clamav-system.svc.cluster.local
          port:
            number: 80
    </code></pre>

### Example

Say you want to virus-scan all incoming traffic of the Social Registry odoo module, the Istio Virtual Service `social-registry-odoo` would look like this.

*   Before

    <pre class="language-yaml" data-full-width="false"><code class="lang-yaml">spec:
      ...
      http:
        ...
        - headers:
            request:
              set:
                ...
          route:
            - destination:
                host: social-registry-odoo
                port:
                  number: 80
    </code></pre>
*   After

    <pre class="language-yaml" data-full-width="false"><code class="lang-yaml">spec:
      ...
      http:
        ...
        - headers:
            request:
              set:
                x-clammit-backend: http://social-registry-odoo.dev
                ...
          route:
            - destination:
                host: clammit.clamav-system.svc.cluster.local
                port:
                  number: 80
    </code></pre>

## Sources

* ClamAV [website](https://www.clamav.net/) and [docs](https://docs.clamav.net/).
* Clammit [site, source code and docs](https://github.com/ifad/clammit).
* Wiremind ClamAV [Helm chart source](https://github.com/wiremind/wiremind-helm-charts/tree/main/charts/clamav).
* OpenG2P Clammit [Helm chart & Docker source code](https://github.com/openg2p/clammit-k8s).
