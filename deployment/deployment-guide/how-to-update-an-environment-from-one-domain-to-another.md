---
description: >-
  This document describes how to Update an Environment from One Domain to
  Another
---

# How to Update an Environment from One Domain to Another

### Steps to Follow

1. Create an SSL certificate for the new domain and update it in the Nginx server. Also, ensure DNS mapping is completed for the new domain.
2. Create a new Gateway for the new domain in the existing environment, and delete the old one.
3. Go to **Apps**, then **Edit** and **Upgrade** the application where you need to update the new domain.
4. Update the new domain name wherever required by removing all references to the old domain name.
5. Update the client names according to the new domain.
6. Ensure the correct **Client ID** and **Client Secret** are configured while upgrading.
7. Click **Next** and proceed to upgrade the application.
8. After the upgrade, verify all **Virtual Services** to ensure the new domain name is updated correctly.
9. Manually update the domain configuration in **Odoo UI** wherever old URLs were configured.

The below screenshot is for reference, showing how the domain name was changed from **nissa**  env to **zanzibar** en&#x76;**.**

<figure><img src="../../.gitbook/assets/image (79).png" alt=""><figcaption></figcaption></figure>

#### &#x20;
