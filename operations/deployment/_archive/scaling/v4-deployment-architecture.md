# V4 Deployment Architecture

<figure><img src="../../../../.gitbook/assets/deployment-architecture-v4.jpg" alt=""><figcaption><p>Deployment Architecture</p></figcaption></figure>

The V4 architecture consists of a [Rancher](base-infrastructure/rancher.md) (it requires its own dedicated Kubernetes cluster. [Learn more >>](https://ranchermanager.docs.rancher.com/getting-started/installation-and-upgrade#high-availability-kubernetes-install-with-the-helm-cli)) and one (or more clusters) for all application modules and supporting components. Rancher is capable of managing several clusters if required. However, in our case it suffices to have one "OpenG2P cluster" which hosts all environments (sandboxes) under separate namespaces. The RBAC of Kubernetes is used to provide users access to namespaces. Further, the secure access to applications can be controlled by the following means:

1. Multiple Wireguard servers enable separate [access channels](../../../../deployment/deployment-guide/private-access-channel.md).
2. Access control at the application level, where login to dashboards and portals is controlled via authentication and authorisation defined in Keycloak.

The Keycloak inside the Rancher cluster provides **organisation-wide authorisation** and offers single sign-on for all resources.

{% hint style="info" %}
This deployment architecture is referred to as "V4" by the OpenG2P team due to the way it has evolved over the past few years. The V4 deployment architecture is an evolution of MOSIP's [V3 architecture](https://github.com/mosip/k8s-infra). Unlike V3, where separate clusters are created for environments, in V4, all sandboxes and environments reside in the same cluster with finer access controls
{% endhint %}
