---
description: This document explains how to import dashboards in superset
---

# Importing Dashboards on the Superset UI for OpenG2P Applications

## Steps to import dashboards on superset ui

Superset provides a simple and intuitive interface to import dashboards, allowing users to migrate or restore dashboards from one instance to another. Follow the steps below to successfully import dashboards using the Superset UI.

1. **Clone the repository from OpenG2P Github:** Clone the [repository](https://github.com/OpenG2P/openg2p-superset-reports/tree/develop) to obtain all the dashboard files, convert them into a ZIP file, and store it in your local directory.
2. **Login to Superset:** Login to the Superset UI using your credentials with the required permissions to import dashboards.
3.  **Add the Database:** Once logged in, add the database for the service associated with the dashboard you want to import. To add a database:

    1. Go to **Settings**.
    2. Click on **Database Connections**.
    3. Select **Add Database** and provide the necessary details, then save it.

    <figure><img src="../../.gitbook/assets/image (6) (1).png" alt=""><figcaption><p>Add database</p></figcaption></figure>


4. **Import the Dashboard:** From the main dashboard:
   1. Click on **Import Dashboards** in the top-right corner.
   2. Select the dashboard ZIP file from your local system.
   3. Provide the database password for authentication, and import.
5. **Verify the Import**: Once the import is complete:
   1. Navigate to the **Dashboards** tab to ensure the new dashboard appears.
   2. Open the dashboard to verify that all components are functioning as expected.
