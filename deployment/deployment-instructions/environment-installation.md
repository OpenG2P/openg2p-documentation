# Environment Installation

## Common resources

Install common components as below:

* Create namespace for your environment using Rancher UI or command line&#x20;
* For **production environment** install PostgreSQL server separately on the same virtual machine using command line
* Install openg2p-commons Helm Chart.  For **production environment** do not install Docker based Postgres (see step above)
* The **latest `openg2p-commons` Helm chart** is available directly in the **Rancher UI**.
* To deploy it:
  1. Open the **Rancher UI** and go to the **Apps & Marketplace** section.
  2. In the search bar, type **`openg2p-commons`**.
  3. Select the chart, **configure the required values** (e.g., domains, Keycloak Clients).
  4. Click **Install** to deploy the Commons Helmchart.

Once deployed, the OpenG2P Commons services such as PostgreSQL, MinIO, Keymanager, OpenSearch, and others will be automatically set up and available for dependent applications.

## Modules

Install the modules and other utility apps individually using their respective instructions:

1. [Registry](../../social-registry/deployment/registry-installation-instructions.md)
2. [PBMS](https://docs.openg2p.org/pbms/deployment)&#x20;
3. [SPAR](https://docs.openg2p.org/spar/deployment)&#x20;
4. [G2P Bridge](https://docs.openg2p.org/g2p-bridge/deployment#installation-using-rancher-ui)&#x20;
5. Beneficiary Portal

