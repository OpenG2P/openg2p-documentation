# Registry MTS Connector

## Overview

Registry MTS Connector (RMC) is an Odoo addon that fetches [MOSIP Auth Token](https://docs.mosip.io/1.2.0/id-lifecycle-management/identifiers#token-id) against any record in the registry by calling [MOSIP Token Seeder](broken-reference) (MTS) and stores the same in the registry.&#x20;

## Features

* Generates MOSIP token against the OpenG2P registry by calling [MTS](broken-reference).
* Uses `callback` delivery type of MTS
* Completely asynchronous execution
* OpenG2P can schedule a daily job to fetch the delta for the day
* A manual import feature will also be provided
* Removes VID if MOSIP Auth Token is generated&#x20;

## Configuration
|Property|Configuration|
|---|---|
|`Name`| A string to identify the connector|
|`URL to reach MTS`| URL for MTS API|
|`MTS Input type`| OMC option could be proceeded by selecting _OpenG2P Registry_.|
|`Mapping`| MTS Field mapping as required by the API. Please refer to MTS Documentation. Format of Mapping would be JSON.|
|`Output Type`| MTS-C only supports JSON output type of MTS.|
|`Output Format`| Output format is a [JQ ](https://stedolan.github.io/jq/)string which will be used by MTS to format its output to suite the caller's requirement.|
|`Delivery Type`| Currently supporting only "Callback". Callback feature can be used to make MTS do a submission of results onto an API within Odoo. The output formatting will help in making the desired input for the api.|
|`Job Type`| MTS-C provide both recurring and one time execution. Recurring can be configured to do continuous pull from the ODK over MTS.|
|`MOSIP Language`| Mosip language setup. Default is _eng_.|
|`Interval in minutes`| Interval at which the MTS-C job runs.|
|`Filters to apply to Registry`| A [domain filter](https://odootricks.tips/about/building-blocks/domain-in-odoo/) can be used to identify the records for tokenisation. For. eg. Only records which have VID associated with it and are not tokenised need to be picked for tokenisation.|
|`List of fields to be used`| List of fields which will be supplied as auth data. This field list may be a superset of fields required for auth as it may contain data required by the callback API.  This list should be a valid JSON string array.|
|`Callback URL`| A URL endpoint which would be called upon successful processing at MTS|
|`Callback HTTP Method`| HTTP Method (POST/PUT/GET/PATCH) used while MTS makes the callback|
|`Callback Timeout`| Timeout awaited by the callback until acknowledged with a response.|
|`Callback Auth Type`| Type of authentication expected by callback URL. MTS-C currently support Odoo type which uses the session-based authentication implemented by Odoo.|
|`Callback Auth Database`| DB instance used by Odoo.|
|`Callback auth username`| Username to access callback API|
|`Callback auth password`| Password to access callback API|
