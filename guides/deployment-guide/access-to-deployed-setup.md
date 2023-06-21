# Access to Deployed Setup

## Introduction

The table below enumerates various admin/user access to the entire deployment. This includes access to machines, Rancher, Kubernetes cluster as well as OpenG2P application.

## Access matrix

| Resource            | Role                | Password/key | Access method                                                                     | Providing further access                                                                                                        |
| ------------------- | ------------------- | ------------ | --------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| Compute nodes       | DevOps Super Admin  | SSH Key      | SSH into the node via private IP (via Wireguard) with the root user using SSH key | Users generate their own SSH Keys whose public keys are added to the nodes.                                                     |
| Wireguard node      | DevOps Super Admin  | SSH Key      | SSH into the node via **public** IP with the root user using SSH key              | To provide Wireguard access to users/clients refer to the [guide](access-to-deployed-setup.md#wireguard-access-to-users) below. |
| Rancher (global)    | Rancher Super Admin | Password     | Open Rancher URL on browser and login via password                                | Individual cluster administrators can be created from Rancher UI.                                                               |
| Rancher (cluster)   | Cluster Admin       | Password     | Open Rancher URL on browser and login via password                                | Users can be added and provided RBAC by Cluster Administrator using Rancher UI.                                                 |
| OpenG2P Application | Odoo Super Admin    | Password     | Open OpenG2P URL on browser and login via password                                | Users can be created and assigned fine-grained roles.                                                                           |

## Wireguard access to users

The guide below provides steps to provide Wireguard access to users. Note that the access must provided for each unique device (like a desktop, laptop, mobile phone etc). Multiple logins with same conf file is not possible.&#x20;

{% hint style="warning" %}
Sharing of Wireguard conf file with other users must not be done for security reasons.
{% endhint %}

### Steps&#x20;

1.  Login to the Wireguard node via SSH.

    ```
    > ssh -i <SSH key pem file> <user>@<ip>
    ```
2.  Change to Wireguard conf folder

    ```
    > cd /etc/wireguard/conf
    ```
3. You will see several pre-created peer config files. You may assign any one of the file (not assigned before) to a new peer/user.
4.  Edit`assigned.txt` file to assign a new the peer (client/user). Make sure a file is assigned to a unique user and an already assigned file is never re-assigned to another user.

    ```
    > vim assigned.txt
    ```
5.  Add the peers with name as mentioned below. Example:

    ```
    > peer1 : <peer name>
    ```
6.  Edit the peer config file. Example:

    ```
    > vim peer1.conf 
    ```

* Delete the DNS IP.
* Update the allowed IP's(subnet IP of AWS).

7. Share the conf file with the peer/user.

