# SSL Certificates using Letsencrypt

## Generate certificates

* Install letsencrypt and certbot.

```bash
sudo apt install letsencrypt certbot
```

* Generate Certificate.

```bash
sudo certbot certonly --agree-tos --manual --preferred-challenges=dns -d *openg2p.sandbox.net -d openg2p.sandbox.net
```

* The above command will ask for `_acme-challenge`, since the chosen challenge is of type DNS. Create the `_acme-challenge` TXT DNS record accordingly, and continue with the above prompt to certs generation.
* The generated certs should be present in `/etc/letsencrypt` directory.

## Renew certificates

* Run the same generate certs command to renew certs.

```bash
sudo certbot certonly --agree-tos --manual --preferred-challenges=dns -d *openg2p.sandbox.net -d openg2p.sandbox.net
```

* The above command will generate new pair of certificates. The DNS challenge needs to be performed again, as prompted.
* Run the following to upload new certs back to Kubernetes Cluster. Adjust the certs path in the below command.

```bash
kubectl delete secret tls-openg2p-ingress -n istio-system
kubectl create secret tls tls-openg2p-ingress -n istio-system \
  --cert=/etc/letsencrypt/live/openg2p.sandbox.net-renewed/fullchain.pem \
  --key=/etc/letsencrypt/live/openg2p.sandbox.net-renewed/privkey.pem
```

