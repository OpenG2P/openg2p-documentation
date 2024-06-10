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

This document guides you to generate and renew SSL certificates using letsencrypt. &#x20;

## Procedure

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
* Run the following to upload new certs back to Kubernetes Cluster. Adjust the certs path in the below command.

```bash
kubectl delete secret tls-openg2p-ingress -n istio-system
kubectl create secret tls tls-openg2p-ingress -n istio-system \
  --cert=/etc/letsencrypt/live/openg2p.sandbox.net-renewed/fullchain.pem \
  --key=/etc/letsencrypt/live/openg2p.sandbox.net-renewed/privkey.pem
```
