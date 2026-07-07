# Registry Connector

This guide provides details on implementing the [Registry Connectors Interface](https://github.com/OpenG2P/pbms/tree/develop/extensions/openg2p-bg-task-registry-adapters) for integration with PBMS Background Tasks.

## Overview

The `RegistryInterface` defines a standardized contract for interacting with various **G2P Registries** within the PBMS. It ensures consistent behavior across different registry integrations, including eligibility checks, summary computation, entitlement processing, and beneficiary search functionalities.

Custom implementations of this interface allow developers to integrate new registry types (for example, `farmer`, `student`, or `worker` registries) without modifying the PBMS core logic.

**Interface Code:** [Registry Interface](https://app.gitbook.com/u/21UJpMbIpqP7PKcbN5AOu80ESpo1) in OpenG2P PBMS Background Tasks Extensions\
**Example Implementation:** [`farmer` Implementation](https://github.com/OpenG2P/pbms/blob/develop/extensions/openg2p-bg-task-registry-adapters/src/openg2p_bg_task_registry_adapters/computations/registry_farmer.py), [`households` Implementation](https://github.com/OpenG2P/pbms/blob/develop/extensions/openg2p-bg-task-registry-adapters/src/openg2p_bg_task_registry_adapters/computations/register_household.py)

{% content-ref url="key-components.md" %}
[key-components.md](key-components.md)
{% endcontent-ref %}

{% content-ref url="example-implementation-workflow.md" %}
[example-implementation-workflow.md](example-implementation-workflow.md)
{% endcontent-ref %}
