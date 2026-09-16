---
description: How the G2P Bridge core stays standard while connectors are pluggable per deployment
---

# Connectors & Extensibility

The G2P Bridge integrates with the outside world through **connectors** — bank
connectors, the ID→FA mapper, notifiers, and the geo/agency/warehouse allocators for
in-kind flows. These are the one part of the Bridge that legitimately varies per
deployment (every programme has its own sponsor bank, its own notifier, sometimes its
own registry). Everything *else* — the disbursement engine, the APIs, the Celery
pipeline, the data model — is the same for everyone.

This page describes how the codebase is organised so that **adopters can supply their
own connectors without ever forking or modifying the Bridge platform.**

## 1. Repository structure

| Repo | Contents | Who changes it |
| --- | --- | --- |
| [**`g2p-bridge`**](https://github.com/OpenG2P/g2p-bridge) | The **platform** — `core/` (models, partner-api, bene-portal-api, celery beat + workers), the Docker builds, the Helm chart, and CI. It also bundles the demo **Example Bank**. | OpenG2P only — standard, versioned, **never forked** by adopters |
| [**`g2p-bridge-connectors`**](https://github.com/OpenG2P/g2p-bridge-connectors) | The six **connector** packages: interfaces + DTOs + config-driven factories + the **reference** implementations (SPAR mapper, Example Bank connector, Novu notifier, …). | OpenG2P for the reference set; **adopters fork/copy freely** |
| _your connector repo_ | One small package implementing a connector interface, plus a ~4-line Dockerfile. | the adopter |

`g2p-bridge` **builds everything and deploys nothing you have to touch.** The
connectors repo holds only Python source; the Bridge's Celery image pulls the
reference connectors from it at build time (by git ref) and bakes them in.

## 2. Why the split

Previously the connectors lived inside `g2p-bridge` (in an `extensions/` folder). To
run a different bank or notifier, an adopter had to **fork the whole Bridge repo,
edit a factory, and rebuild** — which meant they were now carrying a modified copy of
the entire platform, could not cleanly take upstream fixes, and were effectively
unsupportable ("what did you change?").

The goals of the split:

- **Keep core standard and tightly versioned.** Adopters consume it as an immutable,
  version-pinned dependency — they cannot tamper with it just because they need a
  different connector.
- **Make connectors the only variable part**, isolated in their own repo, safe to
  fork or copy.
- **Let adopters build their own image** (core + their connector) as a thin overlay,
  not a fork — so support has a crisp boundary.

## 3. How the split works

Two mechanisms make this possible with **no change to core** when a connector changes.

### a) Core consumes connectors by git ref

The Bridge's Celery image installs `core/*` from local source, then pulls the
reference connectors from `g2p-bridge-connectors` by git ref — the same way it already
pulls `openg2p-fastapi-common`:

```
# docker/g2p-bridge-celery/Dockerfile (excerpt)
ARG G2P_BRIDGE_CONNECTORS_REF=develop
RUN pip install --no-cache-dir \
    "git+https://github.com/openg2p/g2p-bridge-connectors@${G2P_BRIDGE_CONNECTORS_REF}#subdirectory=bank-connectors" \
    ...
```

The reference connectors are thus **baked into the published Celery image**, which
doubles as the **base image** adopters extend.

### b) Connectors are selected by config, not code

Each connector package exposes a **factory** and an **Initializer**. The Initializer
registers the implementation named in config; the factory returns whatever was
registered (via the framework's interface-based component lookup). Nothing references
a concrete implementation by name, so **adding one needs no code edit** — not in core,
not even in the connectors repo.

- **Single-implementation** connectors (mapper, notification, agency, warehouse) read
  one dotted path, `…_IMPL`.
- **Keyed** connectors (bank → sponsor bank code; geo → target registry) read a
  `{key: dotted-path}` map, `…_IMPLS`, and the factory dispatches by key.

| Connector | Config env var | Default (reference impl) |
| --- | --- | --- |
| bank | `G2P_BRIDGE_BANK_CONNECTORS_IMPLS` | `{"EXAMPLE-BANK": "…ExampleBankConnector"}` |
| mapper | `G2P_BRIDGE_MAPPER_CONNECTORS_IMPL` | `…SPARMapper` |
| notification | `G2P_BRIDGE_NOTIFICATION_CONNECTORS_IMPL` | `…NovuNotifier` |
| geo | `G2P_BRIDGE_GEO_RESOLVER_IMPLS` | `{"farmer": "…FarmerGeoResolverImpl"}` |
| agency | `G2P_BRIDGE_AGENCY_ALLOCATOR_IMPL` | `…AgencyAllocatorRefImpl` |
| warehouse | `G2P_BRIDGE_WAREHOUSE_ALLOCATOR_IMPL` | `…WarehouseAllocatorRefImpl` |

### The extend-the-base-image pattern

```
                 g2p-bridge (platform)                g2p-bridge-connectors
                 ┌───────────────────┐                ┌──────────────────┐
   builds ─────► │  Celery image     │ ◄── git ref ── │ reference conns  │
                 │  = core + ref      │                │ (interfaces +    │
                 │    connectors      │                │  factories +     │
                 └─────────┬─────────┘                │  impls)          │
                           │  published, immutable     └──────────────────┘
                           │
       adopter's Dockerfile│  FROM <celery image>
                           ▼  + pip install their-connector
                 ┌───────────────────┐
                 │ adopter image     │   selected via config
                 │ = base + their     │   (…_IMPL / …_IMPLS)
                 │   connector        │
                 └───────────────────┘
```

The adopter's image inherits the entrypoint, the core install, and all the build
logic from the base image — they can only *add* a layer, never modify the platform.

### Which connectors version is in an image

Because the connectors are pulled by git ref, every published Celery image records the
**exact connectors commit** it was built from — the CI resolves the pinned ref (e.g.
`develop`) to a commit SHA at build time, passes that SHA as the build arg (so the
build is reproducible), and stamps it as an OCI image label. You can therefore read the
connectors commit straight off the image, without running it:

```bash
# from the registry, without pulling the image
docker buildx imagetools inspect \
  openg2p/openg2p-bridge-celery:<version> \
  --format '{{ json .Image.Config.Labels }}'
```

The relevant labels:

| Label | Meaning |
| --- | --- |
| `org.openg2p.pin.g2p-bridge-connectors-ref` | connectors commit SHA baked into this image |
| `org.openg2p.pin.fastapi-common-ref` / `org.openg2p.pin.spar-ref` | the other pinned dependency SHAs |
| `org.opencontainers.image.revision` | the `g2p-bridge` (platform) commit the image was built from |
| `org.opencontainers.image.version` | the published version (e.g. `0.0.0-develop.41`) |

The SHA is frozen at build time, so a given image tag always resolves to the same
connectors commit even after `develop` moves on. As a second, always-exact source, each
connector package inside the image also carries pip's PEP 610 record —
`…/openg2p_g2p_bridge_bank_connectors-*.dist-info/direct_url.json` — whose `commit_id`
is the same SHA.

## 4. Writing and integrating a new connector

An adopter never forks core. The end-to-end steps:

1. **Implement the interface** in your own small package, depending on the relevant
   connector package (in `g2p-bridge-connectors`) for the interface + DTOs. E.g. a
   bank connector subclasses `BankConnectorInterface` and implements
   `check_funds` / `block_funds` / `disburse_funds` / etc.
2. **Build a derived image** from the published Celery image:
   ```dockerfile
   FROM openg2p/openg2p-bridge-celery:<version>
   COPY acme-bank-connector /conn
   RUN pip install /conn
   ```
3. **Select it via config** (env vars / Helm values). Keyed connectors register under
   their dispatch key:
   ```
   G2P_BRIDGE_BANK_CONNECTORS_IMPLS={"ACME-BANK":"acme_bank_connector.AcmeBankConnector"}
   ```
   Single-impl connectors point `…_IMPL` at your class.
4. **Deploy** with the standard Bridge Helm chart, overriding only the Celery
   `image.tag` to your derived image. The APIs, the chart, and every other image stay
   the Bridge's standard, unmodified builds.

That's the whole contract: **implement the interface, install your package onto the
base image, name it in config.** No fork, no core change, a thin and supportable
overlay.

See the connector interface guides under
[Tech Guides](../tech-guides/README.md) (e.g. the
[Bank Connector Interface Guide](../tech-guides/bank-connector-interface-guide.md)) for
the method-by-method contract of each interface, and the
[`g2p-bridge-connectors` README](https://github.com/OpenG2P/g2p-bridge-connectors)
for a copy-paste quickstart.
