# Dynamic languages

Allow admins to define new languages and upload translation files from the UI **entirely after deployment** — no rebuild, no new Docker image, no env-var change, no restart.

***

## Goals

1. Admin uploads a `.json` for `hi` in production → visible immediately.
2. Admin clicks "Add language: Hindi" → `/hi/...` URLs start working immediately.
3. The container image never needs to change to add or translate a language.

***

## Where the hardcoding lives today

* `src/i18n/routing.ts` — literal `['en', 'es', 'fr']` used by the middleware (`src/proxy.ts`).
* `src/i18n/request.ts` — dynamic `import('../../locales/${locale}.json')` from the bundled `locales/` folder.
* `src/components/layout/LanguageSwitcher.tsx` — hardcoded `LANGUAGE_CONFIG` with label + flag per locale.
* `/locales/en.json|es.json|fr.json` — filesystem-only translation files.

The project already has a near-identical pattern we can reuse: **`registry-config` / `registry-theme`** — fetched from the backend on each request, cached in `ClientSafeConfig` (`src/app/api/_lib/client-safe-config.ts`), and consumed in `app/[locale]/layout.tsx` + `RuntimeConfigContext`. Languages sit in the same system.

***

## Core principle: Backend is the source of truth, `/locales` is a safety net

There is a strict **primary + fallback** relationship — never a choice made per user or per request:

```
Request for locale "hi"
        │
        ▼
┌───────────────────────────┐       ┌─────────────────────────────┐
│  Backend (cached)         │  ──▶  │  /locales/hi.json (bundled) │
│  PRIMARY source           │  fail │  FALLBACK only              │
└───────────────────────────┘       └─────────────────────────────┘
```

`/locales/*.json` exists only to keep the app rendering when:

* Local dev runs without the backend.
* A pod has just started and the cache is cold **and** the backend is momentarily unreachable.
* An admin has not uploaded a translation for that locale yet.

Admins never touch `/locales/`. One-time migration: POST the existing `en.json`, `es.json`, `fr.json` to the new backend endpoint so they appear as editable records in the admin UI.

***

## Design

### 1. Backend endpoints (must be built)

Mirror how `configuration/registers`, `configuration/registry`, and `registry-theme` work today. Two resources:

*   **Language metadata** — `GET/POST/PUT/DELETE /configuration/languages`

    ```json
    {
      "code": "hi",
      "label": "हिन्दी",
      "flag_url": "...",
      "is_default": false,
      "enabled": true
    }
    ```
* **Translation bundle** — `GET/PUT /configuration/languages/{code}/messages` storing the JSON blob (same shape as today's `en.json`).

Without these endpoints there is no "upload after deployment" — the server has nowhere to put the uploaded data. This is the one piece that cannot be avoided.

### 2. Server-side language registry + cache

Create `src/i18n/language-registry.ts` (server-only):

```ts
// Pseudocode
export const getLanguages = unstable_cache(
  async () => fetchFromBackend('/configuration/languages'),
  ['languages'],
  { tags: ['languages'], revalidate: 300 }
);

export const getMessages = async (locale: string) => {
  try {
    return await fetchFromBackend(
      `/configuration/languages/${locale}/messages`
    );
  } catch {
    return (await import(`../../locales/${locale}.json`)).default; // fallback
  }
};
```

**Cache invalidation is what makes "upload → works immediately" work.** Every POST/PUT/DELETE to `/api/configuration/languages/...` calls `revalidateTag('languages')` on success.

### 3. Dynamic-locale middleware (replaces `src/proxy.ts`)

`next-intl`'s middleware needs the locale list synchronously at request time. Today it comes from a literal array. After the change, it comes from `getLanguages()` (cached), with a bootstrap fallback read from the bundled `/locales/*.json` filenames so the pod can still render on a cold cache + unreachable backend.

```ts
import createMiddleware from 'next-intl/middleware';
import { defineRouting } from 'next-intl/routing';
import { getLanguages } from '@/i18n/language-registry';

const BOOTSTRAP_LOCALES = ['en', 'es', 'fr']; // derived from /locales/*.json

export default async function proxy(req: NextRequest) {
  let locales = BOOTSTRAP_LOCALES;
  let defaultLocale = 'en';

  try {
    const langs = await getLanguages();
    if (langs.length) {
      locales = langs.filter(l => l.enabled).map(l => l.code);
      defaultLocale = langs.find(l => l.is_default)?.code ?? locales[0];
    }
  } catch {
    // backend unreachable → use bootstrap
  }

  const routing = defineRouting({ locales, defaultLocale });
  return createMiddleware(routing)(req);
}

export const config = {
  matcher: ['/((?!api|_next|.*\\..*).*)']
};
```

Notes:

* The cache TTL + tag invalidation are what keep latency acceptable and still make admin changes take effect immediately.
* After the first successful backend fetch, `BOOTSTRAP_LOCALES` is never used again until the next cold boot.

### 4. Translation loading — `src/i18n/request.ts`

Same primary-plus-fallback pattern:

```ts
export default getRequestConfig(async ({ requestLocale }) => {
  const locale = (await requestLocale) ?? 'en';
  let messages;
  try {
    messages = await getMessages(locale);
  } catch {
    messages = (await import(`../../locales/${locale}.json`)).default;
  }
  return { locale, messages };
});
```

### 5. Data-driven `LanguageSwitcher`

`LanguageSwitcher.tsx` stops hardcoding `LANGUAGE_CONFIG` and reads the list (code, label, flag URL) from `RuntimeConfigContext`. That context is already populated server-side in `app/[locale]/layout.tsx` via `clientSafeConfig.fetchRegistryConfig(origin)`. Extend that payload with `languages: [...]` — no new client-side fetch needed.

### 6. Admin UI (new page)

`src/app/[locale]/configuration/languages/` + a feature folder `src/features/configuration/languages/` (same layout as `registers/` or `data-models/`). Three flows:

* **Add language** — form: code (`hi`), label (`हिन्दी`), flag upload, default/enabled toggles. POSTs metadata.
* **Upload translations** — `.json` file picker that:
  * rejects malformed JSON,
  * validates the key tree against `en`'s keyset (warn on missing/extra keys, show a diff summary before save),
  * PUTs to `/configuration/languages/{code}/messages`.
* **Edit / set default / enable / disable / delete.**

Each mutation hits a Next API route under `src/app/api/configuration/languages/…` that proxies via `proxyToBackend` and calls `revalidateTag('languages')` on success.

***

## What actually changes in the repo

| File / Area                                         | Change                                                                               |
| --------------------------------------------------- | ------------------------------------------------------------------------------------ |
| `src/proxy.ts`                                      | Rewritten as custom middleware that builds routing from cached backend data          |
| `src/i18n/routing.ts`                               | Kept for type exports only (or removed if no longer needed)                          |
| `src/i18n/request.ts`                               | Replace static `import(...)` with `getMessages(locale)` + bundled fallback           |
| `src/i18n/language-registry.ts`                     | **New** — server cache + backend fetchers                                            |
| `src/app/api/configuration/languages/**`            | **New** — thin proxies via `proxyToBackend`, each calls `revalidateTag('languages')` |
| `src/features/configuration/languages/**`           | **New** — admin UI feature                                                           |
| `src/app/[locale]/configuration/languages/page.tsx` | **New** — admin route                                                                |
| `src/components/layout/LanguageSwitcher.tsx`        | Read languages from `RuntimeConfigContext` instead of hardcoded map                  |
| `src/app/api/_lib/client-safe-config.ts`            | Include `languages` in the runtime config payload (one extra fetch)                  |
| `locales/*.json`                                    | Stay in the repo as **bootstrap/fallback only**; seed backend once from these        |

No changes needed to `next.config.ts`, `package.json`, the `next-intl` version, or `tailwind.config.ts`.

***

## Rollout plan

### Phase 1 — Foundations

1. Backend: implement language-metadata + translation-bundle endpoints.
2. Seed backend from current `locales/*.json`.
3. Add Next API proxy routes under `src/app/api/configuration/languages/`, each calling `revalidateTag('languages')` on mutation.
4. Add `src/i18n/language-registry.ts` with backend fetch + bundled fallback.

### Phase 2 — Wire into rendering

5. Switch `src/i18n/request.ts` to `getMessages(locale)`.
6. Rewrite `src/proxy.ts` to build routing from `getLanguages()` with bootstrap fallback.
7. Extend `clientSafeConfig` payload with `languages`; make `LanguageSwitcher` consume it.

### Phase 3 — Admin UI

8. Build the `configuration/languages` admin feature: list, add, edit, upload, disable, delete. Enforce translation-file validation against the `en` keyset.

***

## Gotchas

* **Translation validation** — enforce the schema against `en`'s key tree on upload so a partial file can't break production pages. Missing keys → log and fall back to `en` for that key.
* **Caching** — `getLanguages()` and `getMessages()` must be cached (`unstable_cache` with a `languages` tag). Every mutation API route must call `revalidateTag('languages')` — this is the mechanism that turns "uploaded now" into "live now".
* **Cold-boot window** — after a pod restart, before the first backend fetch resolves, only bootstrap locales (`en/es/fr` bundled) will URL-match. This window is milliseconds in practice.
* **Flag assets** — store uploaded flags wherever branding assets already go; keep `/public/images/common/flags/` as defaults.
* **RTL languages** — pair each language record with `direction: 'ltr' | 'rtl'` and set `<html dir>` in `layout.tsx` from it. Cheap to add up front.
* **Permissions** — gate the new `configuration/languages` routes behind the same RBAC checks used for other configuration domains.
* **Fallback hygiene** — do not let the admin UI show the bundled `/locales/*.json` as "records". It always shows the backend list; the fallback is invisible to the admin.
