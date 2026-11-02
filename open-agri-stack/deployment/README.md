---
description: >-
  Installing Agri Stack: the reference topology, the prerequisites and the
  install steps (registries and Exchange in either order, each department's
  release of data, the test).
---

# Deployment

Agri Stack is installed from the OpenG2P Helm charts, through Rancher. These pages are the install steps. How the parts work together, and what the install sets up by itself: [Architecture & Concepts](../architecture/README.md). Managing partners and keys once it runs: [Administration](../administration/README.md).

## Topology

The reference install runs three namespaces in one Kubernetes cluster. Each namespace is installed as a separate organisation, with its own commons, and calls the others only through their public hostnames.

<figure><img src="../../.gitbook/assets/open-agri-stack-deployment-topology.svg" alt="Reference topology: one Kubernetes cluster with three namespaces, each installed as a separate organisation with its own commons. trial: the Farmer Registry; dept1: the Crop Sown Registry; agrix: the Exchange, with the Composite. Partners call the Composite; the Composite calls each registry by its public hostname, through the ingress."><figcaption><p>The reference topology</p></figcaption></figure>

| Namespace | Install | Charts |
| --- | --- | --- |
| `trial` | The **Farmer Registry** (Agriculture Department) | Commons Base, Commons Services, Farmer Registry |
| `dept1` | The **Crop Sown Registry** (Crops Department) | Commons Base, Commons Services, Crop Sown Registry |
| `agrix` | The **Exchange** | Commons Base, Commons Services, Composite |

Each namespace has its own domain on the `internal` gateway (`*.trial.openg2p.org`, `*.dept1.openg2p.org`, `*.agrix.openg2p.org`), with DNS and TLS. The names are examples: any work. Departments on their own clusters: [Separate Clusters](separate-clusters.md).

## Prerequisites

| What | Where |
| --- | --- |
| A Kubernetes cluster with Rancher, Istio and the `internal` gateway | [Infrastructure setup](../../operations/deployment/infrastructure-setup/README.md) |
| One namespace per install, with its domain, DNS and TLS | [Environment setup](../../operations/deployment/environment-setup-multi-node.md) |
| The OpenG2P chart repository in Rancher (**Apps → Repositories**) | [Commons Helm chart](../../deployment/openg2p-commons-helm-chart.md) |
| For the test: `kubectl` and Python 3 on the operator's machine | [Testing](testing.md) |

## Install steps

<figure><img src="../../.gitbook/assets/open-agri-stack-install-order.svg" alt="Install steps: the registries, each in its own namespace with its commons, and the Exchange with its commons and the Composite, in either order; then each department releases its registry's data to the Exchange in its Partner Management; then the test script."><figcaption><p>Install steps</p></figcaption></figure>

| # | Step | Page |
| --- | --- | --- |
| 1 | Install the registries: Farmer Registry in `trial`, Crop Sown Registry in `dept1` | [Farmer Registry](farmer-registry.md), [Crop Sown Registry](crop-sown-registry.md) |
| 2 | Install the Exchange in `agrix`: Commons Base, Commons Services, the Composite | [Exchange](exchange.md) |
| 3 | In each department's Partner Management, add the Composite's scope policy for its registry. Until then the registry releases nothing to the Exchange | [Releasing Data to the Exchange](../administration/releasing-data-to-the-exchange.md) |
| 4 | Run the test | [Testing](testing.md) |

* Steps 1 and 2 can come in either order. Registries usually exist already; upgrading their Commons Services with **Exchange Role** `department` is then step 1.
* Start each install once the one before it in the same namespace is ready: releases `deployed`, all pods running (`helm -n <ns> list`, `kubectl -n <ns> get pods`).
* Every install loads the same country pack (Commons Services default `ETH`; it carries a [licence obligation](../../platform/platform-services/master-data-service/country-packs.md#sources-and-licence)).
* For a test install, step 4 adds the step 3 policies itself, for the use case it tests.
* Before going live: [Production](production.md).
