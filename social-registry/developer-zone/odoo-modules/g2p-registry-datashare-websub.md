# G2P Registry Datashare: WebSub

### Module name

g2p\_registry\_datashare\_websub

### Module title

G2P Registry Datashare: WebSub

### Technology base

[Odoo](https://www.odoo.com/)

### Functionality

This module adds functionality that enables sharing of Registry data to external partners via WebSub.

Refer to [Data Sharing with WebSub](../../features/data-share/data-sharing-websub/) feature documentation.

* Automatically publishes the configuration to WebSub when a config record is created.
  * There is also an Odoo action to manually sync the current selected config data to WebSub.
* Automatically publishes event data to WebSub whenever the particular event is raised.
  * There is also a button which can be used to manually publish selected records

### Configuration

<table><thead><tr><th width="106.142822265625">Field Name</th><th width="126.7142333984375">Field name (db)</th><th width="375.28570556640625">Description</th><th>Default Value</th></tr></thead><tbody><tr><td>Name</td><td><pre><code>name
</code></pre></td><td>Can be a combination of Partner name and event type.  (Each Datashare config should considered unique for the combination of partner_id + event_type.)</td><td></td></tr><tr><td>Partner ID</td><td><pre><code>partner_id
</code></pre></td><td>This should exactly match the Keycloak client ID of the partner.</td><td></td></tr><tr><td>Event Type</td><td><pre><code>event_type
</code></pre></td><td>This decides which event type this partner is interested in. If the partner is interested in more than one event duplicate this entire config for the other event_type(s).</td><td></td></tr><tr><td>Data Transform JQ Expression</td><td><pre><code>transform_data_jq
</code></pre></td><td><ul><li><p>This JQ filter will be used to convert original data into final data that is supposed to be sent to partner. The following fields are available in the original JSON data.</p><ul><li><code>web_base_url</code>: Root URL to access Social Registry.</li><li><code>publisher</code>: This configuration record data itself - available as JSON.</li><li><code>curr_datetime</code>: Current Datetime</li><li><code>data</code>: Only the part of the data that is changed. For advanced usage only. (TODO: elaborate)</li><li><code>record_data</code>: Entire Record data - as JSON.</li><li><code>extra_fields</code>: Any extra fields configured - available as JSON with the key being the extra field's name.</li></ul></li></ul></td><td></td></tr><tr><td>Condition JQ Expression</td><td><pre><code>condition_jq
</code></pre></td><td>For advanced usage only. (TODO: elaborate)</td><td>true</td></tr><tr><td>Extra Fields</td><td><pre><code>extra_fields
</code></pre></td><td>Table of set of additional fields to be computed before sending data to partner. Can contain signed JWT, etc.</td><td></td></tr><tr><td>Topic Joiner</td><td><pre><code>topic_joiner
</code></pre></td><td>For advanced usage only. Final WebSub topic name will be constructed as <code>{partner_id}{topic_joiner}{event_type}</code>.</td><td>/</td></tr><tr><td>Encryption Provider ID</td><td><pre><code>encryption_provider_id
</code></pre></td><td>Encryption Provider to be used for signing the JWT, etc. Leave blank to take the default encryption provider. This will decide whether to use keymanager (if so which keys in keymaanger) or any custom encryption provider.</td><td></td></tr><tr><td>WebSub Base URL</td><td><pre><code>websub_base_url
</code></pre></td><td>WebSub Hub Url. This should be K8s internal service url.</td><td>http://websub/hub</td></tr><tr><td>WebSub Auth URL (Token Endpoint)</td><td><pre><code>websub_auth_url
</code></pre></td><td>Keycloak OAuth2 Token endpoint</td><td></td></tr><tr><td>WebSub Auth Client ID</td><td><pre><code>websub_auth_client_id
</code></pre></td><td>Keycloak Client ID of Publisher (Social Registry).  (Not the partner)</td><td>openg2p-sr-&#x3C;ns></td></tr><tr><td>WebSub Auth Client Secret</td><td><pre><code>websub_auth_client_secret
</code></pre></td><td>Keycloak Client Secret of Publisher (Social Registry).  (Not the partner)</td><td></td></tr><tr><td>WebSub Auth Grant Type</td><td><pre><code>websub_auth_grant_type
</code></pre></td><td></td><td>client_credentials</td></tr><tr><td>WebSub API Timeout</td><td><pre><code>websub_api_timeout
</code></pre></td><td>Timeout to be used while publishing data to WebSub. Given in seconds.</td><td>10</td></tr><tr><td>Active</td><td><pre><code>active
</code></pre></td><td>If this is off, this config will not be considered for automatic publishing of data when the event occurs. Manual Publish can still be used.</td><td>true</td></tr></tbody></table>

### Source code

[https://github.com/OpenG2P/openg2p-registry/tree/17.0-develop/g2p\_registry\_datashare\_websub](https://github.com/OpenG2P/openg2p-registry/tree/17.0-develop/g2p_registry_datashare_websub)
