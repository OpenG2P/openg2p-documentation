---
description: Guide
---

# Wireguard Access to Users

This is an administrator's guide to provide access to [Wireguard Bastion](./) via users' devices (called peers). Access must be provided to each unique device (like a desktop, laptop, mobile phone etc). Multiple connections to Wireguard bastion with the same conf file are not possible.

{% hint style="warning" %}
The Wireguard conf file MUST NOT be shared with any other users for security reasons.
{% endhint %}

### Steps

1.  Login to the Wireguard node via SSH.

    ```
    > ssh -i <SSH key pem file> <user>@<ip>
    ```
2.  Navigate to Wireguard conf folder

    ```
    > cd /etc/wireguard_general
    ```
3. You will see several pre-created peer config files. You may assign any one of the file (not assigned before) to a new peer/user.
4.  Edit`assigned.txt` file to assign a new the peer (client/user). Make sure a conf file is assigned to a unique user, already assigned file is never re-assigned to another user.

    ```
    > vim assigned.txt
    ```
5.  Add the peers with name as mentioned below. Example:

    ```
    > peer1 : <peer name>
    ```
6. Share the conf file with the peer/user securely. Example: `peer1/peer1.conf`
7. Create a local Git repo to maintain versions of `assigned.txt.`  Use `git init` command to initiate a local repo.  Check in any changes to this file.
