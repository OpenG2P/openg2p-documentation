---
description: >-
  OpenG2P REST APIs allows you to create, update and retrieve individual/group
  information.
---

# ↔ Getting Started with OpenG2P REST APIs

OpenG2P REST APIs consist of the following end points.



## User authentication

{% swagger src=".gitbook/assets/auth.json" path="/login" method="post" %}
[auth.json](.gitbook/assets/auth.json)
{% endswagger %}

{% swagger src=".gitbook/assets/auth.json" path="/logout" method="post" %}
[auth.json](.gitbook/assets/auth.json)
{% endswagger %}

## Individual Registration

{% swagger src=".gitbook/assets/individual.json" path="/" method="get" %}
[individual.json](.gitbook/assets/individual.json)
{% endswagger %}

{% swagger src=".gitbook/assets/individual.json" path="/" method="post" %}
[individual.json](.gitbook/assets/individual.json)
{% endswagger %}

{% swagger src=".gitbook/assets/individual.json" path="/{id}" method="get" %}
[individual.json](.gitbook/assets/individual.json)
{% endswagger %}

{% swagger src=".gitbook/assets/individual.json" path="/search" method="get" %}
[individual.json](.gitbook/assets/individual.json)
{% endswagger %}

{% swagger src=".gitbook/assets/individual.json" path="/updateIdentification" method="patch" %}
[individual.json](.gitbook/assets/individual.json)
{% endswagger %}

## Group Registration

{% swagger src=".gitbook/assets/group.json" path="/" method="get" %}
[group.json](.gitbook/assets/group.json)
{% endswagger %}

{% swagger src=".gitbook/assets/group.json" path="/" method="post" %}
[group.json](.gitbook/assets/group.json)
{% endswagger %}

{% swagger src=".gitbook/assets/group.json" path="/{id}" method="get" %}
[group.json](.gitbook/assets/group.json)
{% endswagger %}

{% swagger src=".gitbook/assets/group.json" path="/search" method="get" %}
[group.json](.gitbook/assets/group.json)
{% endswagger %}
