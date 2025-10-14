# Environment Installation

## Common resources

Install common components as below:

* Create namespace for your environment using Rancher UI or command line&#x20;
* For production environment install PostgreSQL server separately on the same virtual machine using command line
* Install openg2p-commons Helm Chart.  For production environment do not install Docker based Postgres (see step above)

## Modules

Install the modules and other utility apps individually using their respective instructions:

1. [Registry](../../social-registry/deployment/registry-installation-instructions.md)
2. [PBMS](https://docs.openg2p.org/pbms/deployment)&#x20;
3. [SPAR](https://docs.openg2p.org/spar/deployment)&#x20;
4. [G2P Bridge](https://docs.openg2p.org/g2p-bridge/deployment#installation-using-rancher-ui)&#x20;
5. Beneficiary Portal

