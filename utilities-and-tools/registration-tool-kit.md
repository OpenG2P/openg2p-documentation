---
layout:
  title:
    visible: true
  description:
    visible: false
  tableOfContents:
    visible: true
  outline:
    visible: true
  pagination:
    visible: true
---

# Registration Tool Kit

According to the World Bank, registration is a series of three processes - intake, recording, and verification. Intake is the process of gathering information from registrants while recording is adding this information to the [Registry](../pbms/functionality/beneficiary-management/beneficiary-registry/). Verification is the process of authenticating those registrants whose information has been recorded.

In the OpenG2P platform, intake is carried out via offline/online forms, and recording via form submission. Verification (authentication) of registrants can be done prior to intake or after recording depending on the mode of registration (online/offline).

## Mode of Registration Interfaces

OpenG2P platform offers registration of persons into programs via the following interfaces:

1. Agent-assisted registration using [ODK Collect app](odk-collection-app.md)
2. Self-registration by a potential beneficiary
3. API-based registration by other systems
4. Manual entry
5. Bulk import from CSV, XLSX

ODK Collect App also supports [offline registration](odk-collection-app/user-guides/register-offline.md) in remote areas without internet connectivity.

Registration can be done for individuals or groups like families, households, schools, etc.

### Registration Process

Registration aims to collect detailed records from the Registry for [Eligibility Assessment](../pbms/features/eligibility/). It must be noted that at this stage, the people are referred to as applicants or registrants. Once the applicants/registrants pass the eligibility criterion, they become eligible to enroll in the program and are referred to as beneficiaries.

While on-demand and administrative-driven approaches are distinct models described by the World Bank, the registration process operates in a spectrum between these two models. For example, a program may allow the applicants to register individually (on-demand) but only in a specific time window (administrative-driven). OpenG2P platform has a flexible implementation and caters to varied approaches across different registration modalities and programs through its various Registration Interfaces.

## Registration features

OpenG2P registration interfaces are key client-facing interfaces. The clients here could be the applicants, social workers, program administrators, program managers, etc. These are the main features offered by these interfaces:

#### **Authentication**

During online registrations, the registrants log into the system using their MOSIP ID/national ID and verify themselves. For registrations in offline mode, the registrants are authenticated using their identity number and demographic information by an ID authentication system.

#### **Offline mode**

OpenG2P's ODK Collect App allows social workers and field registration officers to record the applicant's information without internet connectivity.

#### **Secure**

The registrant's information is encrypted at rest and during transit to secure the demographic information against malicious attacks.

#### **Privacy-preserving**

The platform allows the applicants to fill the consent forms and record them before the intake process. The recorded information is used only for the specific purposes stated in the consent forms.

#### Customizable intake

The applicant information is filled in using application forms (intake sheets). These application forms can be customized per the assessment information required by the program.

## Assistance unit - group/individual

OpenG2P defines an assistance unit as an **individual** or a **group**. A group may be a household, family, or any other group to which the program is targeted.
