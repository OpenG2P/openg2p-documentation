---
layout:
  title:
    visible: true
  description:
    visible: false
  tableOfContents:
    visible: true
  outline:
    visible: true
  pagination:
    visible: true
---

# Install WireGuard Client on Desktop

## Description <a href="#prerequisites" id="prerequisites"></a>

The guide here provides steps to install WireGuard app on machine and to activate the tunnel. This app allows users to create an encrypted VPN for secure communication.

## Prerequisites <a href="#prerequisites" id="prerequisites"></a>

The prerequisites to install WireGuard on Machine:

1. Download WireGaurd Client [here](https://www.wireguard.com/install/).
2. Before proceeding with the installation, obtain the WireGuard conf file from a System Administrator.

## Procedure

The steps to set up a WireGuard client on an **windows machine** are:

1. After the successful installation, launch the WireGuard Application.
2. Click **Add Tunnel** and select the **wg.conf** file shared with you.
3. Click **Activate** to activate the WireGuard.

The steps to set up a WireGuard client on an **Ubuntu machine** are:

1. After successfully installing WireGuard, navigate to the directory `/etc/wireguard` using the terminal.
2. Next, create a file named `<name>.conf`, add the WireGuard configuration file to it, and save the file.\

3.  **Activate** WireGuard using the commands below.

    ```
    sudo systemctl enable wg-quick@<name> 
    sudo systemctl start wg-quick@<name>
    sudo systemctl status wg-quick@<name>
    ```

> Ensure that the listening port is unique for each WireGuard configuration file when using multiple instances.
