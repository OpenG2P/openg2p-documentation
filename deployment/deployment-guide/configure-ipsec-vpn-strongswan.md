# Configure IPSec VPN Gateway to Connect to External Systems using Strongswan

1. Create a new virtual machine on the same network as the other cluster nodes. This machine will serve as a gateway to access external IPs and must have a public IP. The recommended OS is Ubuntu Server 20.04 or higher. Additionally, ensure that all required ports are open on this machine to run IPsec using StrongSwan.\
   **Note (AWS only):** If your creating virtual machine on AWS, disable **Source/Destination Check** on the EC2 instance. This can be ignored for non-AWS environments.
2. The rest of this guide will assume the following:
   1. `10.10.0.0/24` - the local network subnet.
   2. `192.168.0.0/24` - the external network subnet which we are trying to reach over VPN.
   3. `10.10.0.15` - the internal IP of the VPN gateway machine from Step 1.
   4. `3.10.x.x` - Public IP of the VPN gateway machine from Step 1.
   5. `4.10.y.y` - Public IP of VPN tunnel of the external Network.
3. VPN Gateway Setup:
   1. Enable IP Forwarding on the node.
      1.  Create a file `/etc/sysctl.d/60-ip-forward.conf` with the following contents:

          ```bash
          net.ipv4.ip_forward = 1
          net.ipv6.conf.all.forwarding = 1
          ```
      2.  Run this to apply the above config:

          ```bash
          sudo sysctl --system
          ```
   2. Install and configure Strongswan.
      1.  Install Strongswan, run:

          ```bash
          sudo apt install strongswan libcharon-extra-plugins libcharon-extauth-plugins libstrongswan-extra-plugins
          ```
      2.  Take backup of ipsec.conf, run:

          ```bash
          sudo cp /etc/ipsec.conf /etc/ipsec.conf.orig
          ```
      3.  Edit the /etc/ipsec.conf with the following contents:

          ```bash
          config setup
                  charondebug="all"
                  uniqueids=yes
          conn openg2p-to-external-vpn
                  type=tunnel
                  auto=start
                  keyexchange=ikev2
                  authby=psk
                  # Phase 1
                  ike=aes256-sha256-ecp521
                  ikelifetime=28800s
                  # Phase 2
                  esp=aes256-sha256-ecp256
                  lifetime=3600s
                  aggressive=no
                  keyingtries=%forever
                  rekeymargin=3m
                  left=10.10.0.15
                  leftsubnet=10.10.0.15/32
                  leftid=3.10.x.x
                  right=4.10.y.y
                  rightsubnet=192.168.0.0/24
                  rightid=4.10.y.y
                  dpddelay=30s
                  dpdtimeout=120s
                  dpdaction=restart
          ```
      4.  Create `/etc/ipsec.secrets` with the following content:

          ```bash
          10.10.0.15 4.10.y.y : PSK "<PSK Value>"
          ```
      5.  Start strongswan tunnel, run:

          ```bash
          sudo systemctl enable ipsec
          sudo systemctl start ipsec
          ```
      6.  Check status by running:

          ```bash
          sudo ipsec statusall
          ```
   3. Configure iptables (firewall).
      1.  Install `iptables-persistent` , run:

          ```bash
          sudo apt install iptables-persistent
          ```
      2.  Set default forward policy as DROP, run:

          ```bash
          sudo iptables -P FORWARD DROP
          ```
      3.  For each node that is allowed to access the external network, run the following: (The following is only an example, change it according to your system. To get the network interface names run: `ip link` )

          ```bash
          sudo iptables -A FORWARD -o <primary_network_interface_name> -s <10.10.node1.internalip> -j ACCEPT
          sudo iptables -A FORWARD -i <primary_network_interface_name> -d <10.10.node1.internalip> -j ACCEPT

          sudo iptables -A FORWARD -o <primary_network_interface_name> -s <10.10.node2.internalip> -j ACCEPT
          sudo iptables -A FORWARD -i <primary_network_interface_name> -d <10.10.node2.internalip> -j ACCEPT
          ```
      4.  Enable NAT forwarding; run

          ```bash
          sudo iptables -A POSTROUTING -t nat -o <primary_network_interface_name> -j MASQUERADE
          ```
      5.  Save the iptables changes for the next boot, run: (Make sure to run this whenever you change something on iptables)

          ```bash
          sudo bash -c 'iptables-save > /etc/iptables/rules.v4'
          ```
4.  Add an IP Route on all the other nodes that need to access the VPN, to hop over the VPN Gateway node. \
    **Note:** If a global **routing table** exists on the network, this rule can be added there instead.

    ```bash
    sudo ip route add 192.168.0.0/24 via 10.10.0.15
    ```

