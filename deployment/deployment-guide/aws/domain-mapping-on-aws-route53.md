---
description: Guide on mapping domain names on AWS Route53 (WORK IN PROGRESS)
---

# Domain mapping on AWS Route53

AWS Route 53 is a highly scalable and reliable Domain Name System (DNS) web service designed to route end users to internet applications by translating human-readable domain names like [www.example.com](http://www.example.com) into IP addresses like 192.0.2.1. It integrates seamlessly with other AWS services, providing developers with a robust toolset for managing DNS records, domain registration, and health checking to ensure high availability and performance of web applications.

## Procedure

The steps to perform domain mapping on AWS Route53 are given below.

1. Login to AWS. Navigate to the Route53 console on AWS dashboard and select _**hostedzone**_.&#x20;

Notes:

If the _**hostedzone**_ is not created, you have to create a new _**hostedzone**_.

2. Click the _**Create Record**_ button and do mapping according to your environment domain.
