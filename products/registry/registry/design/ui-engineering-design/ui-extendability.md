---
description: Extend Staff Portal in Farmer Registry by pinning a registry-platform version and applying file-level overrides.
---

# UI Extendability

`farmer-registry` extends `registry-platform` to provide a farmer-specific experience while reusing the existing Staff Portal UI. Instead of maintaining a separate copy of the application, Farmer Registry pins a specific version of Staff Portal (`registry-platform/ui/staff-ui`) and replaces only the files that require domain-specific behavior.

The extension wrapper is located at `farmer-registry/ui/staff-ui`.

> **Note:** This approach is not limited to Farmer Registry. Any domain registry built on `registry-platform`, such as a social registry or vehicle registry, can extend Staff Portal using the same mechanism.

**Key concepts:**
- **Override:** A file under `overrides/` that replaces the corresponding Staff Portal file at the same path.
- **Generated application (`.app/`):** The materialized Staff Portal application with overrides applied. This directory is generated automatically and must not be edited directly.

## 1. When to Use Overrides

Overrides should be a last resort. Before replacing a platform file, consider whether an existing extension point can meet your requirements.

| Requirement | Recommended approach |
| --- | --- |
| Configure section fields or layouts | `section_ui_schema` / Section Builder |
| Customize colors | Registry themes |
| Customize labels and translations | Language packs |
| Add a new field type | `widgetRegistry.register` |
| Change behavior not supported by existing extension points | File overrides |

Use an override only when the existing configuration options and extension points cannot satisfy the requirement.

## 2. Quick Start

Clone the Farmer Registry repository and start the Staff Portal application:

```bash
git clone https://github.com/OpenG2P/farmer-registry.git
cd farmer-registry
git checkout 1.2
cd ui/staff-ui

npm install
npm run dev
```

The commands automatically prepare the application by fetching the pinned Staff Portal version, applying overrides, and installing dependencies when required.

## 3. Overriding a File

Follow these steps to customize an existing Staff Portal component or page.

1. **Locate the platform file.** After running `npm install`, find the file under `.app/src/` that needs customization.

2. **Copy the file to `overrides/`**, preserving its relative path.

   ```text
   .app/<path>  →  overrides/<path>
   ```

   For example, `.app/src/components/example.tsx` becomes `overrides/src/components/example.tsx`.

3. **Edit the override.** Make your changes in `overrides/`, not in `.app/`. The generated application may be recreated or updated by the wrapper scripts.

4. **Run the application.**

   ```bash
   npm run dev
   ```

   The wrapper applies your overrides before starting Next.js.

Overrides replace entire files rather than individual lines. If you want to restore the original platform implementation, delete the corresponding file from `overrides/` and run:

```bash
npm run reset
```

### Override Guidelines

- Preserve the platform component's exports, props, and expected behavior wherever possible.
- Reuse existing platform hooks and utilities, such as `useFetch`, `useRegisterRecords`, and `useRbac`.
- Use the `@/` import alias for platform source files. The alias maps to `.app/src/` through `tsconfig.json`.
- Keep overrides minimal to reduce maintenance when upgrading Staff Portal.
- Whenever you update the pinned `ref`, run `npm run reset` and review each override against the updated platform implementation.

## 4. Directory Structure and Configuration

The wrapper separates dependency configuration, customizations, and generated application files.

| Path | Purpose |
| --- | --- |
| `deps.json` | Defines the pinned Staff Portal repository, branch or tag, and source path |
| `overrides/` | Contains replacement files using the same relative paths as Staff Portal |
| `scripts/` | Contains scripts for materializing, installing, and resetting the application |
| `.app/` | Generated Staff Portal application with overrides applied; gitignored |
| `.env` | Optional environment file copied into `.app/.env`; gitignored |

### Example `deps.json`

Farmer Registry uses the following configuration to pin Staff Portal to the `1.2` branch:

```json
{
  "repo": "https://github.com/OpenG2P/registry-platform.git",
  "ref": "1.2",
  "path": "ui/staff-ui"
}
```

- `repo`: Git repository containing Staff Portal.
- `ref`: Branch or tag identifying the platform version to use.
- `path`: Path to the Staff Portal application within the repository.

Pinning a specific `ref` makes the platform dependency explicit and helps keep domain-specific customizations reproducible.

## 5. How It Works

The wrapper prepares the generated application before running development, build, or production commands.

The process works as follows:

1. **Materialize Staff Portal:** Clone the configured repository and reference into `.app/` when `.app/package.json` does not exist.
2. **Apply overrides:** Copy files from `overrides/` to their corresponding locations in `.app/`, replacing the original files.
3. **Install dependencies:** Run `npm ci` when the platform's `package-lock.json` differs from the stored dependency stamp.
4. **Run the application:** Execute the requested Next.js development, build, or production command from `.app/`.

On subsequent runs, the wrapper reapplies overrides without unnecessarily recreating the application. Existing `node_modules`, `.next`, and `.env` directories or files are left untouched by the overlay process.

### Available Commands

Run these commands from `farmer-registry/ui/staff-ui`:

| Command | Description |
| --- | --- |
| `npm install` | Materializes Staff Portal, applies overrides, and installs dependencies when needed |
| `npm run dev` | Applies overrides and starts the Next.js development server |
| `npm run build` | Applies overrides and builds the Next.js application |
| `npm start` | Applies overrides and starts the production server |
| `npm run reset` | Deletes `.app/`, then recreates it and reapplies overrides |

**Important:** Run `npm run reset` after changing the pinned `ref` or removing an override file. This ensures that the generated application reflects the intended platform version and no longer contains a deleted customization.

### Wrapper Scripts

| Script | Responsibility |
| --- | --- |
| `scripts/materialize-staff-ui.sh` | Sparse-clones the configured repository and reference into `.app/` when needed, applies overrides, and copies `ui/staff-ui/.env` to `.app/.env` when present |
| `scripts/ensure-app-deps.sh` | Runs `npm ci` in `.app/` only when `package-lock.json` differs from `.deps-stamp` |
| `scripts/reset-app.sh` | Deletes `.app/` and invokes the materialization and dependency setup scripts |

The `npm run reset` command delegates to `scripts/reset-app.sh`.

## 6. Docker Build

The Docker image is built from the Farmer Registry repository root. The image starts without a pre-existing `.app/` directory, so the installation step materializes the pinned Staff Portal application and the build process applies overrides before producing the standalone Next.js build.

```bash
docker build \
  -f docker/staff-ui/Dockerfile \
  -t openg2p/openg2p-farmer-registry-staff-ui:local .
```

## Reference Implementation

See the [OpenG2P Farmer Registry repository, branch `1.2`](https://github.com/OpenG2P/farmer-registry/tree/1.2), under `ui/staff-ui/`, for the working implementation of `deps.json`, `overrides/`, and the wrapper scripts.

This approach allows domain registries to reuse Staff Portal while maintaining their own custom behavior, minimizing duplicated code and keeping platform upgrades manageable.