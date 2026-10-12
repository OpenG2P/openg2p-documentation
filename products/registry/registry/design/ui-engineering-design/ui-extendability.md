---
description: How a domain registry extends Staff Portal by pinning ui/staff-ui and overlaying replacement files. Farmer Registry is the reference.
---

# UI extendability

A domain registry customizes Staff Portal (`registry-platform/ui/staff-ui`) by pinning it and overlaying its own files. It does not fork it. Farmer Registry (`farmer-registry/ui`) is the reference.

## Need

Staff Portal is generic. Farmer Registry, Social Registry, and other domain registries all run the same screens.

Each domain still needs its own look and feel on some screens and components. 

So a domain needs a way to replace specific screens while still getting every Staff Portal feature and fix.

## Layout

| Path | Role |
| --- | --- |
| `deps.json` | Staff Portal pin (`repo`, `ref`, `path`) |
| `overrides/` | Replacement files, same paths as `ui/staff-ui` |
| `scripts/` | Materialize and install `.app` dependencies |
| `.app/` | Generated app. Gitignored. Do not edit |

```json
{
  "repo": "https://github.com/OpenG2P/registry-platform.git",
  "ref": "1.2",
  "path": "ui/staff-ui"
}
```

## How it works

`npm install`, `npm run dev`, and `npm run build` run `scripts/materialize-staff-ui.mjs`:

1. Sparse-clone `repo` at `ref` and sync `path` into `.app/`. `node_modules`, `.next`, and `.env` are kept.
2. Copy `overrides/` onto `.app/` at the same paths. Override files win.
3. Seed `.app/.env` from `.env.example` if it is missing.

`scripts/ensure-app-deps.mjs` then runs `npm ci` in `.app` when its lockfile changes. Next builds from `.app/`.

The overlay replaces whole files. Removing a file from `overrides/` brings back the platform version.

## Writing an override

Copy the Staff Portal file to the same path under `overrides/` and edit it:

```text
staff-ui/src/components/ui/StatsCard.tsx  →  overrides/src/components/ui/StatsCard.tsx
```

* Keep the same default export and props. Other Staff Portal files still import this module.
* Reuse platform hooks (`useFetch`, `useRegisterRecords`, `useRbac`). Change presentation, not behaviour.
* Import with `@/…`. The wrapper `tsconfig.json` maps `@/*` to `.app/src/*`.
* After bumping `ref`, re-check every overridden file.

## Farmer Registry overrides

| File | Change |
| --- | --- |
| `src/components/ui/StatsCard.tsx` | New card design. Same props, endpoints, and links |
| `src/app/[locale]/register/[type]/page.tsx` | New register list cards and table. Same hooks, filters, export, and intake actions |

## Build and run

```bash
cd farmer-registry/ui
npm install
npm run dev     # or: npm run build && npm start
```

Docker, from `farmer-registry`:

```bash
docker build -f docker/staff-ui/Dockerfile \
  -t openg2p/openg2p-farmer-registry-staff-ui:local .
```

The image runs the same materialize step, then a standalone Next.js build. Runtime env is the same as for the platform Staff Portal.

## When not to override

| Need | Use |
| --- | --- |
| Fields or layout in a section | `section_ui_schema` / Section Builder |
| Colours | Registry themes |
| Labels | Language packs |
| New field type | `widgetRegistry.register` |
