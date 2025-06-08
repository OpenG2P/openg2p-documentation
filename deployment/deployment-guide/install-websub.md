# Install WebSub

## Installation

* Go to Rancher -> Apps -> Repositories. Add a repository with this URL if it doesn't exist [https://openg2p.github.io/openg2p-helm](https://openg2p.github.io/openg2p-helm/rancher) (name can be given as `openg2p-extras`).
* Select the namespace which contains OpenG2P Social Registry/PBMS/other modules, in the Rancher namespace filter.
* Go to Rancher -> Apps -> Charts. Refresh all charts. Search and select WebSub. Choose name of installation like `websub`.
* Configure hostname to reach this WebSub, and Keycloak Base Url, and click "Edit Values.yaml":
  *   Disable Kafka Installation under `kafka` section:

      {% code fullWidth="false" %}
      ```yaml
      ...
      kafka:
        enabled: false
      ...
      ```
      {% endcode %}
  * Get the name of existing Kafka service running in the namespace depending on which OpenG2P module you want to use with this WebSub instance. Example: `social-registry-kafka` . The exact service names can be checked under Rancher -> Service Discovery -> Services.
  *   Replace Kafka Service name in values.yaml, against the following property. Example:

      {% code fullWidth="false" %}
      ```yaml
      ...
      # kafkaInstallationName: '{{ include "common.names.fullname" .Subcharts.kafka }}'
      # Above line is replaced with the following.
      kafkaInstallationName: social-registry-kafka
      ...
      ```
      {% endcode %}
* Click proceed and Finalize WebSub installation.

## Post-installation Keycloak Setup

* Assign the following realm roles to the Service Account of `openg2p-sr-<ns>` client, if this WebSub instance is required to be used with Social Registry. If required with PBMS assign to `openg2p-pbms-<ns>` client. Create the realm roles if they do not exist already.
  * `PUBLISH_WEBSUB_GROUP_CREATED_ALL_INDIVIDUAL`.
  * `PUBLISH_WEBSUB_GROUP_UPDATED_ALL_INDIVIDUAL`.
  * `PUBLISH_WEBSUB_INDIVIDUAL_CREATED_ALL_INDIVIDUAL`.
  * `PUBLISH_WEBSUB_INDIVIDUAL_UPDATED_ALL_INDIVIDUAL`.
* The role name needs to be in the form of `PUBLISH_<event_name>_ALL_INDIVIDUAL`.
  * For any additional events create and assign the roles accordingly.
