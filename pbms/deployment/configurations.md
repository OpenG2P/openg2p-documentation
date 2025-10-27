---
description: >-
  The instructions here are related to configuration of base settings for PBMS
  using the Odoo UI
---

# Configurations

Once all the pods are in **Running** state we can start interacting with the Odoo UI and configure some base settings.

## Prerequisites

* [ ] An installed and running instance of keycloak
* [ ] An installed and running instance of minio object store
* [ ] The user must have access to PBMS in OpenG2P systems
* [ ] The user must be an Administrator on the system

## Configure Minio Object Store

1. Navigate to the minio hostname specified during installation. You can find this in your Rancher namespace by navigating to **Istio -> Virtual Services**, and searching for `minio`
2. Login using credentials from Rancher **Storage -> Secrets**, search for `minio`
3. Navigate to the Buckets section in the Minio UI and click **Create Bucket**
4. Choose an appropriate bucket name (example: `documents`) and click on **Create Bucket**

## Configure PBMS Document Settings

1. Navigate to the pbms hostname specified during installation. You can find this in your Rancher namespace by navigating to **Istio -> Virtual Services**, and searching for `pbms`. Login using credentials from Rancher.
2. From the top-left Apps icon, go to **Settings -> Technical -> Storage Backend**
3. Create a new storage backend or update existing ones.
   * Give the record a name (example: Default S3 Document Store)
   * Select Backend type as **Amazon S3**
   * Check the `Is Public` boolean field.
   * Fill the Amazon S3 section using credentials from Rancher and the bucket name created while [configuring minio](configurations.md#configure-minio-object-store) (it is recomended to use internal url on port 9000, example: `http://minio-pbms:9000`).
   * Save the record using the top-left odoo save icon.

## Configure Keycloak

1. _To be added_

## Configure PBMS Base Settings

1. Navigate to the pbms hostname specified during installation. You can find this in your Rancher namespace by navigating to **Istio -> Virtual Services**, and searching for `pbms`. Login using credentials from Rancher.
2. From the top-left Apps icon, go to **Settings** and click on **G2P PBMS Settings** tab from the left sidebar.
3. Update the URLs for Background Task API and Bridge API from **Rancher -> Istio -> Virtual Services**.
4. Select the pre-configured Document Store from the dropdown.
5. Configure Keymanager if required (by default Keymanager is toggled off).
