# Pulling Docker from Private Repository on Docker Hub

If your docker is hosted as private repository on Docker Hub, following the below steps to install the same using Helm

1. Create a Docker Hub secret in your namespace.  On Rancher select your namespace, and navigate to Secrets -> Create -> Registry -> DockerHub.  Provide&#x20;
   * Name: Name of the secret
   * Username:  Docker Hub user id
   * Password:  [User access token](https://docs.docker.com/security/for-developers/access-tokens/) (Make sure original password is NOT given here)
2. While deploying via Helm add the following into the Helm YAML

```yaml
image:
    pullPolicy: Always
    repository: openg2p/<your docker repository name>
    tag: <docker tag>
    pullSecrets: <name of the secret>
```
