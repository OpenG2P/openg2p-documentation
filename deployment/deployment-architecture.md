# Deployment Architecture

## Introduction

OpenG2P provides Dockers for all its components. The proposed deployment architecture is based on Kubernetes.&#x20;

## Deployment architecture

<figure><img src="../.gitbook/assets/deployment-architecture (1).jpg" alt=""><figcaption><p>Deployment architecture</p></figcaption></figure>

Rancher is used to manage multiple OpenG2P clusters. Rancher itself is installed on a Kubernetes cluster with redundancy as it is a critical gateway to manage the clusters.  The clusters may be directly managed by the command line utility `kubectl` as well.

