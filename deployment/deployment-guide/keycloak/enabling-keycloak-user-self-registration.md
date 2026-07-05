---
description: >-
  This document provides a guide to enabling Keycloak user self-registration for
  public environments.
---

# Enabling Keycloak User Self-Registration

## Overview

This guide covers enabling self-registration for users on Keycloak. Also refer to [Keycloak Advanced Security](keycloak-advanced-security.md) guide for other security policies.

## Prerequisites

* The following requires an SMTP server to be set up within the same Kubernetes cluster for email notifications. Check [openg2p/mail](https://github.com/OpenG2P/openg2p-deployment/tree/main/charts/mail) helm chart.
* This also requires the Keycloak server to be publicly accessible.

## Procedure

1. **Log in to Keycloak**
   1. Open the Keycloak Admin Console.
   2. Log in using admin credentials.
   3. You can configure self-registration in your existing realm or create a separate realm for public environments and configure it there.<br>
2. **Enable User Registration**
   1. Navigate to **Realm Settings**.
   2.  Click on the **General Settings** tab and provide the necessary details.<br>

       <figure><img src="../../../.gitbook/assets/image (33) (1).png" alt=""><figcaption></figcaption></figure>
   3. Click on the **Login** tab, enable the following options:
      * **User registration**: Allows users to register themselves.
      * **Verify email**: Ensures users confirm their email addresses after registration.
      * **Forgot password**: Allows users to reset their passwords via email.
      * **Login with email**: Enables users to log in using their email addresses instead of usernames.<br>
3. **Configure Email Settings**
   1. In the **Realm Settings**, locate the **Email** section.
   2.  Configure the **Template** and **Connection & Authentication** sections with SMTP settings.

       <figure><img src="../../../.gitbook/assets/image (31) (1).png" alt=""><figcaption></figcaption></figure>
   3. Ensure the SMTP server is installed within the Kubernetes cluster.
   4.  Provide SMTP server details (host, port, authentication credentials, etc.).

       <figure><img src="../../../.gitbook/assets/image (32) (1).png" alt=""><figcaption></figcaption></figure>
   5. Save the configuration to enable email notifications for user registrations.
4. **Configure Authentication and reCAPTCHA**
   1.  Navigate to the **Authentication** tab and make a copy of the **registration** as **registration2** and bind it to Resgistration flow.

       <figure><img src="../../../.gitbook/assets/image (13) (1) (1).png" alt=""><figcaption></figcaption></figure>

       1. Edit the newly created registration flow, ensuring all step requirements remain the same.
       2. Add reCAPTCHA in the **reCAPTCHA settings**.
       3. Generate the reCAPTCHA site key and secret key from Google reCAPTCHA and configure them in Keycloak.
5. **Assign Client Roles**
   1. Add the required **client roles** under each client to grant access to applications. For more refer [here](https://docs.openg2p.org/social-registry/deployment).
   2. To provide complete access to **SR** or **PBMS** for self-registered users, create the necessary roles for the respective clients.
   3.  Assign all the created client roles to **Realm Settings → User Registration** to set default roles for self-registered users.

       <figure><img src="../../../.gitbook/assets/image (4) (1) (1).png" alt=""><figcaption><p><br></p></figcaption></figure>
6. **Integrate Keycloak Credentials with Applications**
   1. Make sure your application is already integrated with Keycloak login for authentication. If not, configure it for [Keycloak authentication](../../../products/pbms/_archive/previous-generation/functionality/administration/role-based-access-control/user-guides/configure-keycloak-authentication-provider-for-user-log-in.md).<br>
7. **Verify Self-Registration**
   1. Open **Socialregistry** or **PBMS** service in an incognito/private browser window.
   2. Try to **login with keycloak** and it will redirect you to keycloak login page.
   3.  The **Register** link should now be visible.

       <figure><img src="../../../.gitbook/assets/image (8) (1) (1).png" alt=""><figcaption></figcaption></figure>
   4. Click the **Register** link to access the registration page.
   5. Users can enter their details (name, email, and password) and proceed with 2 factor authentication to create an account.
   6. Upon registration, users will receive a confirmation email (if email verification is enabled).
   7. After confirming their email, users can log in to odoo application.<br>
8. Once users are registered in Keycloak, they can use the same credentials wherever the app integrates with Keycloak authentication.
