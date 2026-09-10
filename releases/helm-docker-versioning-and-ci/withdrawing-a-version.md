---
description: Delete a published develop build (chart + images) and record it in the catalogue.
---

# Withdrawing a version

Sometimes a published **develop build** has to go — it piles up in Rancher, or it is
simply bad and nobody should install it. There is a button for that on both forges.

{% hint style="danger" %}
**Only `0.0.0-develop.N` can be withdrawn, and it cannot be undone.**
Releases (`N.N.N`) are permanent. Release candidates (`N.N.N-rc.M`) are en route to a
release and are kept too. The pipeline **refuses** anything else, and also refuses the
**newest** develop build — the moving `develop` tag points at it — and any build that has
been [marked known-good](marking-a-known-good-build.md). A range or keep-N sweep skips
marked builds and says so, rather than failing; unmark one first if you really mean to
withdraw it.
{% endhint %}

## What it deletes

| | |
| --- | --- |
| Chart | `<chart>-<version>.tgz` and its entry in the Helm index **and the Rancher index** |
| Images | every image tag equal to that version (read from the chart itself) |
| Catalogue | **nothing is erased** — the version is listed under **Withdrawn**, with your reason |

The changelog **page is kept on purpose**. Each develop page says *"changes since
&lt;previous build&gt;"*, so deleting pages would break that chain; and for a bad build the
record of what it contained is exactly what you want to keep. Withdrawing removes the
**artifact**, not the history — the same idea as a "yank" on npm or PyPI.

## Run it — GitHub

**`openg2p-packaging` → Actions → "Withdraw versions" → Run workflow.**

| Field | Meaning |
| --- | --- |
| **repo** | the service repo, e.g. `pbms` |
| **chart** | chart name as published, e.g. `openg2p-pbms` |
| **mode** | `single` · `range` · `keep` |
| **version** / **from**+**to** / **keep_last** | for `single` / `range` / `keep` |
| **reason** | shown verbatim in the catalogue — required |
| **delete_images** | also delete the image tags (default on) |
| **dry_run** | **on by default** — shows what would go, changes nothing |
| **confirm** | to actually delete: retype the version (`single`) or `DELETE` |

## Run it — GitLab

**`openg2p/packaging` → Build → Pipelines → Run pipeline**, set `WITHDRAW_PROJECT`
(e.g. `openg2p/consent-manager`), `CHART`, `MODE`, `REASON`, then start the manual
**withdraw** job. Same fields, same rules, same scripts.

The job only appears when `WITHDRAW_PROJECT` is set, so an ordinary pipeline run on
that project can never delete anything.

## The two-step flow

1. Run with **dry run on** (the default). The log lists every chart, index entry and
   image tag that would be removed.
2. Read that list, then re-run with **dry run off** and **confirm** filled in.

## The three modes

* **single** — one bad build: `version = 0.0.0-develop.297`.
* **range** — clear a block: `from = 100`, `to = 200` (inclusive, by build number).
* **keep** — trim the pile: `keep_last = 10` withdraws every develop build except the
  newest 10. This is the one to use for Rancher clutter.

{% hint style="info" %}
**Why Rancher keeps showing old versions.** The Rancher index is built with
`helm repo index --merge`, which only ever *appends* — re-indexing never removes an
entry. The withdraw job edits that file directly, which is the only way those versions
disappear from the Rancher catalogue.
{% endhint %}

## A withdrawn version never comes back

The withdrawal writes a tombstone (`<repo>/.withdrawn` in the catalogue), and **the
build pipeline refuses to publish a version listed there**.

That guard matters because `0.0.0-develop.N` is derived from the **commit count**:
after a force-push a different commit can land on a withdrawn `N`. The normal
immutability guard only trips when the version still *exists* from another commit —
and the artifact has just been deleted, so nothing else would notice. Without the
tombstone, anyone still pinning that version would silently get different bytes.

If a build stops with *"… was WITHDRAWN and must not be republished"*, push an empty
commit so the build gets a fresh version:

```bash
git commit --allow-empty -m "G2P-XXXX Rebuild after withdrawal"
```

## Credentials

Both buttons live in the packaging projects on purpose: they need tokens that can
**delete** artifacts, and those belong in one place rather than in every service repo.

* **GitHub** — `OPENG2P_BOT_GITHUB_PAT` (helm repo + catalogue) and a Docker Hub token
  with delete rights (`DOCKERHUB_DELETE_TOKEN`, falling back to `docker_hub_token`).
* **GitLab** — `WITHDRAW_TOKEN`, a group access token with `api` scope (registry
  delete, package delete, and write on the catalogue).

## Related

* [Cutting a release (how to tag)](cutting-a-release.md)
* [Changelogs](changelogs.md) — what each page shows, and retention.
