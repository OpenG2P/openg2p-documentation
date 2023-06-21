# Access to Deployed Setup

## Introduction

The table below enumerates various admin/user access to the entire deployment. This includes access to machines, Rancher, Kubernetes cluster as well as OpenG2P application.

## Access matrix

| Resource            | Role               | Password/key | Access method                                                                     | Providing further access                                                                                                        |
| ------------------- | ------------------ | ------------ | --------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| Compute nodes       | DevOps Super Admin | SSH Key      | SSH into the node via private IP (via Wireguard) with the root user using SSH key | Users generate their own SSH Keys whose public keys are added to the nodes.                                                     |
| Wireguard node      | DevOps Super Admin | SSH Key      | SSH into the node via **public** IP with the root user using SSH key              | To provide Wireguard access to users/clients refer to the [guide](access-to-deployed-setup.md#wireguard-access-to-users) below. |
| Rancher (global)    | DevOps Super Admin | Password     | Open Rancher URL on browser and login via password                                | Individual cluster administrators can be created from Rancher UI.                                                               |
| Rancher (cluster)   | Cluster Admin      | Password     | Open Rancher URL on browser and login via password                                | Users can be added and provided RBAC by Cluster Administrator using Rancher UI.                                                 |
| OpenG2P Application | Odoo Super Admin   | Password     | Open OpenG2P URL on browser and login via password                                | Users can be created and assigned fine-grained roles.                                                                           |

## Wireguard access to users
