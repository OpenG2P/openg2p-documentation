---
description: (WIP)
---

# Create ACM Certificate on AWS

## Introduction

Amazon Certificate Manager (ACM) is a service provided by AWS that makes it easy to provision, manage, and deploy SSL/TLS certificates for use with AWS services and your internal resources.

**Here are the general steps to create an ACM certificate on AWS:**

1. Go to the ACM console by searching for "ACM" in the AWS Management Console search bar or by selecting "Certificate Manager" from the list of services.
2. Click on the "Request a certificate" button to start the certificate issuance process.
3. Enter the domain names for which you want to request a wildcard certificate by adding an asterisk () before the domain name (e.g., `*.openg2p.org`).
4. Choose a validation method to prove ownership of the domain. You can choose between email validation, DNS validation, or using an AWS-managed validation option if your domain is hosted on AWS Route 53.
5. Recommended `AWS Route53 validation`.  And this needs to be mapped in the Route53 in AWS. Make sure the name and values should be taken from the certificate only for routing.
6. Review the information you entered and confirm the certificate request.
7. Complete the validation process based on the chosen validation method. For example, if you selected email validation, you will receive an email with instructions to validate ownership of the domain.
8. Once the validation process is complete, the ACM certificate will be issued and available for use with Elastic Load Balancing (ELB).
9. Deploy the certificate to your AWS resources to enable secure communication over HTTPS.
10. You can manage your ACM certificates from the ACM console, including renewing, updating, or deleting certificates as needed.
