# MOSIP Integration

## Introduction

OpenG2P integrates with MOSIP to verify the UIN/VIDs provided by individuals as part of the registration process. As a result of the verification, OpenG2P receives a unique token against an individual's UIN/VID along with KYC data. This data is stored in the registry.

There are two ways to obtain the MOSIP tokens:

1. For new registrations that are conducted via ODK form, The MTS Connector is configured to pull data directly from ODK Central and return MOSIP tokens. See [ODK MTS Connector](broken-reference).
2. For already existing records in the registry, the [Registry MTS Connector](broken-reference) is used to trigger a connection with MTS and in turn, receive MOSIP tokens for all the records requested.
