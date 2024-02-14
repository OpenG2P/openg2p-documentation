# OpenG2P Registry MTS Connector

### Module name

g2p\_mts

### Module title

OpenG2P Registry MTS Connector

### Technology base

odoo

### Functionality

* Generates MOSIP token against the OpenG2P registry by calling [MTS](broken-reference).
* Uses `callback` delivery type of MTS
* Completely asynchronous execution
* OpenG2P can schedule a daily job to fetch the delta for the day
* A manual import feature will also be provided
* Removes VID if MOSIP Auth Token is generated

### Design notes

## NA

### Dependencies

module dependencies:

* mts\_connector
* g2p\_registry\_individual
* g2p\_registry\_rest\_api

### User interface

<figure><img src="../../../.gitbook/assets/spaces_4EyCrLbFom7vj7UcMIUZ_uploads_git-blob-db52d2d1e7849707e6275cfaaf7548016a971514_openg2p-registry-mts-connector.webp" alt=""><figcaption></figcaption></figure>

### Configuration

## Input

In OpenG2P, the user can configure for following fields to setup an interface with MTS through OMC.

**Name**: A string to identify the connector

**URL to reach MTS**: URL for MTS API

**MTS Input type**: OMC option could be proceeded by selecting "_OpenG2P Registry_".

**Mapping**: MTS Field mapping as required by the API. Please refer MTS Documentation. Format of Mapping would be JSON.

**Output Type**: MTS-C only supports JSON output type of MTS.

**Output Format**: Output format is a [JQ ](https://stedolan.github.io/jq/)string which will be used by MTS to format its output to suite the caller's requirement.

**Delivery Type**: Currently supporting only "Callback". Callback feature can be used to make MTS do a submission of results onto an API within Odoo. The output formatting will help in making the desired input for the api.

**Job Type**: MTS-C provide both recurring and one time execution. Recurring can be configured to do continuous pull from the ODK over MTS.

**MOSIP Language**: Mosip language setup. Default is "_eng_".

**Interval in minutes**: Interval at which the MTS-C job runs.

**Filters to apply to Registry**: A [domain filter](https://odootricks.tips/about/building-blocks/domain-in-odoo/) can be used to identify the records for tokenization. For. eg. Only records which have VID associated with it and is not tokenized need to be picked for tokenization.

**List of fields to be used**: List of fields which will be supplied as auth data. This field list may be a superset of fields required for auth as it may contain data required by the callback API. This list should be a valid JSON string array.

**Callback URL**: A URL end point which would be called upon successful processing at MTS

**Callback HTTP Method**: HTTP Method (POST/PUT/GET/PATCH) used while MTS makes the callback

**Callback Timeout**: Timeout awaited by the callback until acknowledged with a response.

**Callback Auth Type**: Type of authentication expected by callback URL. MTS-C currently support Odoo type which uses the session-based authentication implemented by Odoo.

**Callback Auth Database**: DB instance used by Odoo.

**Callback auth username**: Username to access callback api

**Callback auth password**: Password to access callback api

### Source Code

[https://github.com/OpenG2P/openg2p-mts/tree/15.0-develop/g2p\_mts](https://github.com/OpenG2P/openg2p-mts/tree/15.0-develop/g2p\_mts)
