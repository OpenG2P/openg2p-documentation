---
description: >-
  This document provides a guide to enabling Keycloak user self-registration for
  public environments.
---

# Enabling Keycloak User Self-Registration

### Overview

Keycloak can manage user authentication for web and mobile apps. Users can self-register, and admins can add them. It also supports custom attributes beyond default ones like name and email. This guide covers enabling self-registration and adding custom fields.

### Prerequisites

1. The Keycloak server is installed on the Kubernetes cluster and should be publicly accessible.
2. And Keycloak should be integrated as part of your application.
3. An SMTP server is set up within the same Kubernetes cluster for email notifications.

### Steps to Enable Keycloak Self-Registration

1. **Log in to Keycloak**
   1. Open the Keycloak Admin Console.
   2. Log in using admin credentials.
   3. You can configure self-registration in your existing realm or create a separate realm for public environments and configure it there.
2. **Enable User Registration**
   1. Navigate to **Realm Settings**.
   2. Click on the **General Settings** tab and provide the necessary details.
   3. Click on the **Login** tab, enable the following options:
      * **User registration**: Allows users to register themselves.
      * **Verify email**: Ensures users confirm their email addresses after registration.
      * **Forgot password**: Allows users to reset their passwords via email.
      * **Login with email**: Enables users to log in using their email addresses instead of usernames.
3. **Configure Email Settings**
   1. In the **Realm Settings**, locate the **Email** section.
   2. Configure the **Template** and **Connection & Authentication** sections with SMTP settings.
   3. Ensure the SMTP server is installed within the Kubernetes cluster.
   4. Provide SMTP server details (host, port, authentication credentials, etc.).
   5. Save the configuration to enable email notifications for user registrations.
4. **Configure Authentication and reCAPTCHA**
   1. Navigate to the **Authentication** tab.
   2.  Make a copy of the **registration** as **registration2** and bind it to Resgistration flow.\
       \


       <figure><img src="../../.gitbook/assets/image (13).png" alt=""><figcaption></figcaption></figure>


   3. Edit the newly created registration flow, ensuring all step requirements remain the same.
   4. Add reCAPTCHA in the **reCAPTCHA settings**.
   5. Generate the reCAPTCHA site key and secret key from Google reCAPTCHA and configure them in Keycloak.
5. **Assign Client Roles**
   1. Add the required **client roles** under each client to grant access to applications. For more refer [here](https://docs.openg2p.org/social-registry/deployment).
   2. To provide complete access to **SR** or **PBMS** for self-registered users, create the necessary roles for the respective clients.
   3.  Assign all the created client roles to **Realm Settings → User Registration** to set default roles for self-registered users.\
       \


       <figure><img src="../../.gitbook/assets/image (4).png" alt=""><figcaption></figcaption></figure>


6. **Integrate Keycloak Credentials with Applications**
   1. Make sure your application is already integrated with Keycloak login for authentication. If not, configure it for [Keycloak authentication](../../pbms/functionality/administration/role-based-access-control/user-guides/configure-keycloak-authentication-provider-for-user-log-in.md).
7. **Verify Self-Registration**
   1. Open **Socialregistry** or **PBMS** service in an incognito/private browser window.
   2. Try to **login with keycloak** and it will redirect you to keycloak login page.
   3.  The **Register** link should now be visible.\
       \


       <figure><img src="../../.gitbook/assets/image (8).png" alt=""><figcaption></figcaption></figure>


   4. Click the **Register** link to access the registration page.
   5. Users can enter their details (name, email, and password) to create an account.
   6. Upon registration, users will receive a confirmation email (if email verification is enabled).
   7. After confirming their email, users can log in with basic permissions.
8. Once users are registered in Keycloak, they can use the same credentials wherever the app integrates with Keycloak authentication.

