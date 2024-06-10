---
description: (WIP)
---

# Create ACM Certificate on AWS

Amazon Certificate Manager (ACM) is a service provided by AWS that makes it easy to furnish, manage, and deploy SSL/TLS certificates for use with AWS services and your internal resources.

## Procedure

The general steps to create an ACM certificate on AWS are given below.

1. Search for ACM in AWS Management Console or select _**Certificate Manager**_ from the list of the services.
2. Click the _**Request a certificate**_ button to start the certificate issuance process.
3. Enter the domain name that requires a wildcard certificate and add an asterisk \* before the domain name. For example, \*.openg2p.org.
4. If the domain is hosted on AWS Route53, then you can select or choose any one of the validation methods to prove the ownership of the domain. The available validation methods are: _**Email**_, _**DNS**_, and _**AWS-Managed**_.
5. The recommended validation is AWS Route53 and it needs to be mapped in the Route53 in AWS. For routing, it is mandatory that the name and the values must be taken from the certificate.
6. Recheck the data you have entered and confirm the certificate request.

This completes the validation process based on the chosen validation method. For example, if you have selected email validation, you will receive an email with instructions to validate ownership of the domain.&#x20;

After the successful validation, an ACM certificate will be issued and available for use with Elastic Load Balancing (ELB).&#x20;

Deploy the certificate to your AWS resources to enable secure communication over HTTPS.

You can manage your ACM certificates from the ACM console which renews, updates, and deletes certificates as needed.
