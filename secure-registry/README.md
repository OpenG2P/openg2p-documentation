# 📋 Registration

## Introduction

According to the World Bank, registration is a series of three processes - intake, recording, and verification. Intake is the process of gathering information from registrants while recording is adding this information to the [Registry](registry.md). Verification is the process of authenticating those registrants whose information has been recorded.

In the OpenG2P platform, intake is carried out via offline/online forms, and recording via form submission. Verification (authentication) of registrants can be done prior to intake or after recording depending on the mode of registration (online/offline).

Registration aims to collect detailed records in the [Registry](registry.md) for [Eligibility Assessment](../beneficiary-management/eligibility.md). It must be noted that at this stage, the people are referred to as applicants or registrants. Once the applicants/registrants pass the eligibility criterion, they become eligible to enrol in the program and are referred to as beneficiaries.

A high-level view of the administrator-driven registration in offline mode is given below:

<figure><img src="https://github.com/OpenG2P/openg2p-documentation/raw/00d70c2522faff12a735f69918503f2aa1485c78/.gitbook/assets/registration-flow.png" alt=""><figcaption></figcaption></figure>

{% hint style="info" %}
### Registration approaches

Registration can be carried out via multiple channels such as digital service windows/kiosks, social workers, local registration offices, door-to-door visits, referrals from other programs, etc. The registration approach can be either on-demand or administrative-driven. Three key features distinguish between these two approaches:

**Applicant-initiated vs. program-initiated**

Whether the registration process was initiated by the applicant (on-demand) or by the program administrator (administrator-driven)

**Individual vs. group registration**

Whether applicants registered themselves individually (on-demand) or registered as a group/family/household (administrator-driven)

**Continuous vs. time-bound**

Whether applicants could register at the time of their choosing (on-demand) or had to apply in a specific time window (administrator-driven)
{% endhint %}

## Registration interfaces

While on-demand and administrative-driven approaches are distinct models described by the World Bank, the registration process operates in a spectrum between these two models. For example, a program may allow the applicants to register individually (on-demand) but only in a specific time window (administrative-driven). OpenG2P platform has a flexible implementation and caters to varied approaches across different registration modalities and programs through its various [Registration Interfaces](registration-methods/).

## Registration features

OpenG2P registration interfaces are key client-facing interfaces. The clients here could be the applicants, social workers, program administrators, program managers, etc. These are the main features offered by these interfaces:

#### **Authentication**

During online registrations, the registrants log into the system using their MOSIP ID/national ID and verify themselves. For registrations in offline mode, the registrants are authenticated using their identity number and demographic information by an ID authentication system.

#### **Offline mode**

OpenG2P's [ODK Collect App](registration-methods/offline-registration.md) allows social workers and field registration officers to record the applicant's information without internet connectivity.

#### **Secure**

The registrant's information is encrypted at rest and during transit to secure the demographic information against malicious attacks.

#### **Privacy-preserving**

The platform allows consent forms to be filled out and recorded before starting the intake. The recorded information is not used for purposes other than the explicitly stated purpose in the consent form.

#### Customizable intake

The applicant information is filled in using application forms (intake sheets). These application forms can be customized per the assessment information required by the program.

## Assistance unit - group/individual

OpenG2P defines an assistance unit as an **individual** or a **group**. A group may be a household, family, or any other group to which the program is targeted.

## FAQs

<details>

<summary></summary>



</details>
