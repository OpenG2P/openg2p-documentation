# Air-gapped deployment setup using Gitlab

The guide describes steps to setup OpenG2P infra on air-gapped networks (where components run without accessing the internet) using Gitlab.

To achieve this, we will setup Gitlab on a machine running on the same network as the rest of the K8s machines. This Gitlab instance will host code repositories, helm charts, docker images, etc. (And anything else that is required to run OpenG2P modules in air-gapped).

This guide will assume that during installation and initial setup internet connection is available. Internet connection is not required after the installation and setup is finished.

## Prerequisites

* One machine (machine configuration TBD) running the same network as rest of the OpenG2P machines.
  * OS: Ubuntu Server.
  * TCP ports; 22, 80, 443, 5000 are open on the firewall of this machine.

## Gitlab Installation

* Use this to [install Gitlab](https://docs.gitlab.com/omnibus/). (Use `gitlab-ce` instead of `gitlab-ee` in all the commands, if you want community edition. Check [gitlab licensing](https://about.gitlab.com/install/ce-or-ee/)).
* [Configure Gitlab](https://docs.gitlab.com/omnibus/settings/) (TODO: elaborate each of the following):
  * Configure gitlab hostname, configure Docker registry hostname.
  * Enable HTTPS. And configure SSL. Prefer manual certificates options (so that certificates can be copied from Nginx machine).
  * Disable SMTP. Disable Postfix.
  * Disabled Prometheus and related monitoring exporters.
  * Disable the following configurations. TODO: WIP

## Gitlab Keycloak Integration

* Use [Keycloak client creation](keycloak/keycloak-client-creation.md) guide to create new client for Gitlab.
* Use this to configure the Keycloak client as [auth provider for gitlab](https://docs.gitlab.com/administration/auth/oidc/). TODO: elaborate.
* Create users on Gitlab, link the user of gitlab with the user from Keycloak. TODO: elaborate.
* All logins to Gitlab can be through Keycloak only after applying these changes.

## Gitlab Repositories and Docker Repo setup.

TODO

## Setup Backup for Gitlab

TODO
