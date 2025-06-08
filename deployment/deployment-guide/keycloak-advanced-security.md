# Keycloak Advanced Security

Keycloak can manage user authentication for web and mobile apps. Users can self-register, and admins can add them. It also supports custom attributes beyond the default ones, like name and email.

This guide covers enabling advanced security features on Keycloak and configuring self-registration.

Please note that all of the following operations are made on the selected realm. Be mindful of which realm is being modified.

## Password strength policy

* Navigate to Keycloak Admin Console -> Authentication Menu -> Policies Section.
*   Add the following policies.

    <figure><img src="../../.gitbook/assets/image (27).png" alt=""><figcaption></figcaption></figure>

## Password expiry & history policy

TODO

## Account lockout

* Navigate to Keycloak Admin Console -> Realm Settings -> Security defenses.
*   Under "Brute force detection", configure Account lock out option after 3 wrong password attempts.

    <figure><img src="../../.gitbook/assets/image (30).png" alt=""><figcaption></figcaption></figure>

## MFA setup

* Navigate to Keycloak Admin Console -> Authentication Menu -> Flows Section.
*   Click on **Browser** flow, make a copy of the Browser as **Browser with 2Fa** and bind it to Browser flow.

    <figure><img src="../../.gitbook/assets/image (25).png" alt=""><figcaption></figcaption></figure>

    1. Look for the Browser - Conditional OTP option which by default is set to `Alternative`. Change this to `Required`.
    2. That's it. KeyCloak is now configured for 2FA.

## Self-Registration

Refer to [Keycloak User self-registration](enabling-keycloak-user-self-registration.md) guide.
