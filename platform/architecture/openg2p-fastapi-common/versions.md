---
description: Version history of the OpenG2P FastAPI Common framework packages.
---

# Versions

The framework lives in the single repository
[`openg2p-fastapi-common`](https://github.com/OpenG2P/openg2p-fastapi-common) and
publishes four packages (`openg2p-fastapi-common`, `openg2p-fastapi-auth`,
`openg2p-fastapi-auth-models`, `openg2p-fastapi-partner-auth`). Services install
them from a git ref — the `develop` branch by default, pinnable to a tag via each
service's `FASTAPI_COMMON_REF` build-arg.

<!-- MAINTAINER NOTE: When you add a NEW version row, its Comments cell must
     briefly summarise the differences/additions relative to the PREVIOUS row
     (not a full description). Keep it terse. -->

| Version | Packages | Last Modified | Comments |
| ------- | -------- | ------------- | -------- |
| [develop](https://github.com/OpenG2P/openg2p-fastapi-common/tree/develop) | openg2p-fastapi-common<br><br>openg2p-fastapi-auth<br><br>openg2p-fastapi-auth-models<br><br>openg2p-fastapi-partner-auth | 03-Jul-2026 | In progress. Active development branch (installed from the `develop` git ref). Includes the `partner-mgmt` crypto backend — verify partner signatures by fetching keys from Partner Management with in-process caching (soft/hard TTL, negative cache, unknown-kid refresh, single-flight). |

{% hint style="info" %}
The **Last Modified** date for the in-progress `develop` line is updated as work
continues. Tagged package releases will be listed here as they are cut.
{% endhint %}
