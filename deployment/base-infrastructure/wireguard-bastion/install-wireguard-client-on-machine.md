---
description: (WIP)
---

# Install WireGuard Client on Machine

## Description <a href="#pre-requisites" id="pre-requisites"></a>

The guide here provides steps to install WireGuard app on machine and to activate the tunnel. This app allows users to create an encrypted VPN for secure communication.

## Pre-requisites <a href="#pre-requisites" id="pre-requisites"></a>

The pre-requisites to install WireGuard on Machine:

1. Download WireGaurd Client [here](https://www.wireguard.com/install/).
2. Before proceeding with the installation, obtain the WireGuard conf file from a System Administrator.

## Procedure

The steps to set up a WireGuard client on an **windows machine** are:

1. After the successful installation, launch the WireGuard Application.
2. Click **Add Tunnel** and select the **wg.conf** file shared with you.
3. Click **Activate** to activate the WireGuard.

The steps to set up a WireGuard client on an **Ubuntu machine** are:

1. After successfully installing WireGuard, navigate to the directory `/etc/wireguard` using the terminal.
2. Next, create a file named `<anyname>.conf`, add the WireGuard configuration file to it, and save the file.\
   ![](../../../.gitbook/assets/image.png)
3.  &#x20;**Activate** WireGuard using the commands below.

    ```
    sudo systemctl enable wg-quick@wge2e 
    sudo systemctl start wg-quick@wge2e
    sudo systemctl status wg-quick@wge2e
    ```



> Ensure that the listening port is unique for each WireGuard configuration file when using multiple instances.

