---
description: >-
  How to record that a develop build is known good, and have that note appear in
  the version catalogue — without tagging a release.
---

# Marking a known-good build

Not every good build is a release. A build passes QA, gets deployed to a pilot, or is confirmed working against a particular integration — and none of that means you want to ship it. Tagging `N.N.N` would say "this is a supported, stable release", which is a different and much stronger claim.

**Marking** records the weaker, more common statement: *this build is known good; you can rely on it.* No tag, no release, no rebuild.

## What it looks like

The note appears in bold in the **Notes** column of that module's catalogue page:

| Version | Date | Type | Notes |
| --- | --- | --- | --- |
| `0.0.0-develop.207` | 2026-08-24 | develop | |
| `0.0.0-develop.205` | 2026-08-21 | develop | **Intermediate Stable Version — verified on staging** |

Releases keep their own section in the catalogue because they are tagged. A mark is only an annotation, so it stays in the table rather than creating a category of its own.

## How to mark a build

Marks live in the **versions** repo ([`openg2p/versions`](https://gitlab.com/openg2p/versions)), in a file named `.marked` inside that module's folder. There is no pipeline and no form — it is a plain text file you edit directly.

1. Open the module's folder in the versions repo. The folder name is the project path with the group stripped and slashes flattened:
   * `openg2p/g2p-insights` → `g2p-insights`
   * `openg2p/registry/registry-platform` → `registry-registry-platform`
   * `openg2p/keycloak/keycloak-themes` → `keycloak-keycloak-themes`
2. Create or open `.marked` (**+ → New file** if it does not exist yet).
3. Add one line per marked version:

```
0.0.0-develop.205|Intermediate Stable Version — verified on staging
1.3.0-rc.151|Passed the full QA cycle; safe for pilot deployments
```

4. Commit to the versions repo's default branch.

The format is `version|note`. The version must match the page exactly — `versions/0.0.0-develop.205.md` means you write `0.0.0-develop.205`. Everything after the first `|` is free text.

The catalogue re-renders on every push to the versions repo, so the note appears on the site within a minute or so. You do **not** need to wait for the module's next build.

{% hint style="info" %}
**Editing and unmarking.** The note is meant to be revised — if you learn more later, edit the line. To unmark a build, delete its line. Both are ordinary commits to the versions repo.
{% endhint %}

## What marking guarantees

Two things happen automatically once a version is marked, and both exist so the mark cannot outlive the thing it points at:

* **Retention no longer applies to it.** Develop pages are normally pruned after the newest 20 builds (see [Changelogs](changelogs.md)). A marked page is exempt and stays until you unmark it. Without this, marking build 205 and doing nothing else would silently lose the note twenty builds later — exactly when you most want to look it up.
* **Withdrawal refuses it.** [Withdrawing a version](withdrawing-a-version.md) deletes a develop build's chart and images. It skips marked versions and says so. Deleting the artifact you told people was good is the mistake worth making impossible. Unmark it first if you really mean to withdraw it.

## What marking does *not* do

* It does not tag anything, and does not create a Git tag, a GitLab Release, or a new version.
* It does not rebuild, republish, or move any artifact. The image and chart are untouched.
* It does not change what `develop` (the moving alias) points at.
* It is not a substitute for a release. When you are ready to ship, cut a real tag — see [Cutting a release](cutting-a-release.md).

## Choosing what to write

The note is free text, so it can carry whatever is useful. Some patterns that work well:

* `Intermediate Stable Version — verified on staging`
* `Passed the full QA cycle; safe for pilot deployments`
* `Known good with registry-platform 0.0.0-develop.383`
* `Use this one — 0.0.0-develop.206 has a broken migration`

Keep it short enough to read in a table cell. If it needs more explanation than that, the explanation probably belongs in a ticket, and the note should link to it.
