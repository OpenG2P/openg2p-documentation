---
description: >-
  Document describes How to Set Up MinIO Object Storage Server in Standalone
  Mode on Ubuntu
---

# MinIO Standalone Installation Guide on Ubuntu VM

### Overview

This document guides you through installing **MinIO in standalone mode** on a single Ubuntu-based VM, either from AWS Cloud or a native datacenter/server. This setup is suitable for development, testing, or small production use cases, with flexibility to scale into a distributed cluster later.

### Prerequisites

* Operating System: Ubuntu 20.04+ VM (AWS EC2 or native server)
* 2vCPU / 4 GB RAM / 32 GB storage
* Root or sudo access to the VM
* Filesystem Recommendation: XFS over LVM (preferred for performance; ext4 can also be used initially)

### Minio standalone installation steps

1.  Run this to update and install dependencies

    ```bash
    sudo apt update && sudo apt upgrade -y
    sudo apt install -y curl wget
    ```
2.  Install MinIO

    Create user and data directory:

    ```bash
    # Create a system user 'minio-user' with no login shell
    sudo useradd -r minio-user -s /sbin/nologin

    # Create the directory for MinIO data
    sudo mkdir -p /data/minio

    # Set ownership of the directory to 'minio-user'
    sudo chown -R minio-user:minio-user /data/min
    ```

    Download MinIO binary:

    ```bash
    wget https://dl.min.io/server/minio/release/linux-amd64/minio
    chmod +x minio
    sudo mv minio /usr/local/bin/
    ```
3.  Create MinIO Systemd Service

    Create the service file:

    ```bash
    sudo nano /etc/systemd/system/minio.service
    ```

    Paste the following configuration:

    ```bash
    [Unit]
    Description=MinIO
    After=network.target

    [Service]
    User=minio-user
    Group=minio-user
    ExecStart=/usr/local/bin/minio server /data/minio --console-address ":9001"
    Restart=always
    LimitNOFILE=65536
    Environment="MINIO_ACCESS_KEY=minioadmin"
    Environment="MINIO_SECRET_KEY=minioadmin123"

    [Install]
    WantedBy=multi-user.target
    ```

    > **Note:** Change `MINIO_ACCESS_KEY` and `MINIO_SECRET_KEY` to secure values.
4.  Start and Enable MinIO

    ```bash
    sudo systemctl daemon-reexec
    sudo systemctl enable minio
    sudo systemctl start minio
    sudo systemctl status minio
    ```
5. Access MinIO Web Console
   1. Open your browser and go to:\
      `http://<your-server-ip>:9001`
   2. Login using the `MINIO_ACCESS_KEY` and `MINIO_SECRET_KEY`.

### Scaling later (Distributed MinIO)

* You can scale to a **multi-node distributed setup** by adding VMs and drives.
* MinIO supports **erasure coding**, **high availability**, and **horizontal scalability**.
* Ensure:
  * Consistent hardware across nodes (CPU, RAM, disk)
  * XFS file system across all volumes
