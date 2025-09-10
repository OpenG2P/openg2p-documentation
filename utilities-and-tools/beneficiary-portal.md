# Beneficiary Portal

The Beneficiary Portal is a user-friendly website designed specifically for beneficiaries, showcasing the full range of OpenG2P features on a desktop web browser. Its primary purpose is to illustrate OpenG2P’s capabilities from the beneficiary’s perspective, presented through a branded, attractive,  and intuitive interface.

This portal integrates all major modules—Registry, PBMS, SPAR, and G2P Bridge—by connecting to each one to provide beneficiaries with the necessary information and processes. Consequently, the portal is intended to be deployed as a single installation per environment or sandbox, rather than one per module. The underlying concepts and design of the portal can also be leveraged for developing a mobile application for beneficiaries.

## Functionality

1. Landing page (without login): OpenG2P branded landing page, highlighting that this is a beneficiary portal (detailed contents TBD)
2. User (beneficiary) login via eSignet&#x20;
3. Home page like a dashboard post login showing the following:
   1. All the programs that the beneficiary is part of along with their status including the ones she/he has applied but not yet confirmed
   2. All the registries that she/he is part of&#x20;
   3. User’s current linked bank account (from SPAR)
   4. Total amount of benefit - cash or in-kind -  received till date under each scheme
   5. Potential applicable schemes for the user (that she/he has not applied for yet)
   6. Any notifications/broadcast from the system&#x20;
   7. Any issues with money or in-kind transfer (from G2P Bridge)
4. List of all programs offered by the department and ability to apply for them
5. Application via a form (we can follow our existing self service flow)
6. Ability to update bank account via SPAR
7. View of all the transactions related to money or benefit transfer - history of all benefits received under each scheme she/he is enrolled for.&#x20;
8. Detailed registry view with ability to update fields (for now let’s have a simple flow as this can get very complex). &#x20;
9. A separate space for grievance redressal - file a complaint.  This would show the list of past complaints and form to file a new one.&#x20;

## Wireframes

{% embed url="https://www.figma.com/proto/3hYyBVpNpqSl4PbaXy8rgw/Beneficiary-Portal?node-id=1-2&page-id=0:1&starting-point-node-id=1:2&t[%E2%80%A6]ntent-scaling=fixed" %}

## Architecture



{% embed url="https://miro.com/app/board/uXjVJKFLcas=/?share_link_id=553998889894" %}

## Backend APIs

