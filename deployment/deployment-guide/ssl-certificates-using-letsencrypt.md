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

# Generate SSL Certificates using Letsencrypt

This document explains how to generate and renew SSL certificates using Let's Encrypt and how to automate the certificate issuance and renewal process with the AWS Route53 plugin.

## Procedure for creating a certificate manually

The steps to generate SSL certificates are given below.

* Install letsencrypt and certbot.

```bash
sudo apt install certbot
```

* Generate Certificate.

```bash
sudo certbot certonly --agree-tos --manual --preferred-challenges=dns -d *.openg2p.sandbox.net -d openg2p.sandbox.net
```



* Since the preferred challenge is DNS type, the above command asks for `_acme-challenge.` Create the `_acme-challenge` TXT DNS record accordingly, and continue with the above prompt to generate certs.
* The generated certs must be present in `/etc/letsencrypt` directory.

## Renew certificates

* Run the same generate certs command to renew certs.

```bash
sudo certbot certonly --agree-tos --manual --preferred-challenges=dns -d *.openg2p.sandbox.net -d openg2p.sandbox.net
```

* The above command generates a new pair of certificates. The DNS challenge needs to be performed again, as prompted.
* Restart Nginx&#x20;

```bash
sudo systemctl restart nginx
```

## Procedure for automatically creating and renewing a certificate using the AWS Route 53 Plugin

This will help you obtain and renew SSL certificates from Let’s Encrypt using Certbot and the AWS Route 53 plugin. The Route 53 plugin automates DNS validation by creating and deleting the necessary DNS records.

Steps for Using Let’s Encrypt with the AWS Route 53 Plugin

* You need an AWS account with Route 53 hosted zones configured.
*   Create an IAM user with the following permissions and have Route53FullAccess role:\


    ```json
    {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Effect": "Allow",
          "Action": [
            "route53:ListHostedZones",
            "route53:GetChange",
            "route53:ChangeResourceRecordSets"
          ],
          "Resource": "*"
        }
      ]
    ```


* Save the access key and secret key for this user.
*   Ensure Certbot is installed on your server. If not, install it\


    ```bash
    sudo apt update
    sudo apt install certbot python3
    sudo apt-get install python3-certbot-dns-route53
    certbot plugins
    ```


* You must own a domain name and have it configured in Route 53.
* Download and Configure AWS CLI on nginx node as **root user.**
  *   [ ] Download AWS CLI using below commands.\


      ```bash
      curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
      unzip awscliv2.zip
      sudo ./aws/install
      aws --version
      ```


  *   [ ] Certbot requires access to your AWS credentials to interact with Route 53. Run the command `aws configure`as **root user** to set up your AWS credentials, which will prompt you for your AWS IAM user's access key, secret key, and default region. Then verify your AWS CLI configuration by running\


      ```bash
      cat .aws/credentails or config
      aws sts get-caller-identity
      aws route53 list-hosted-zones    
      ```


*   Use Certbot with the Route 53 plugin to request a certificate—replace example.com with your domain. Once the certificate is generated, it will inform you that it will automatically renew when nearing expiry and that a systemd timer (certbot.timer) and service (certbot.service) are created in the /lib/systemd/system directory for automatic renewals.\


    ```bash
    certbot certonly --dns-route53 -d openg2p.sandbox.org -d '*.openg2p.sandbox.org'
    ```

    \
    Note

    If you're running an Nginx server on the same node, you can add a post-hook to restart it after a certificate renewal. Simply create the file `/etc/letsencrypt/renewal-hook/post/nginx-restart.sh` with the command to restart Nginx. And for more info on certbot auto-renewal refer [here](https://eff-certbot.readthedocs.io/en/stable/using.html#automated-renewals)



\
