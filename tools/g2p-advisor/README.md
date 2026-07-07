---
noIndex: true
---

# G2P Advisor

A hosted, login-based web app that walks an implementer through deploying OpenG2P. It collects requirements through guided conversation, generates a working baseline of customised code in a local sandbox, and hands the artefacts off to the implementer when they're satisfied.

The repository lives at [github.com/openg2p/g2p-advisor](https://github.com/openg2p/g2p-advisor).

## What it does

The Advisor serves system integrators and government departments adopting OpenG2P — typically Registry, with PBMS and other modules to follow.

* **Chat mode** — a conversational interface for general OpenG2P questions. Reads the wiki, drills into the relevant pages, and synthesises an answer with citations.
* **Project mode** — the primary value proposition. Walks the implementer through a phased implementation effort, with the wiki's **playbook** as the operating contract.

A user can have multiple projects open simultaneously, each with its own state, sandbox, working case, and chat thread.

## How it works at a glance

The Advisor reads from a curated knowledge base — [G2P WikiLLM](../g2p-wikillm/) — at runtime; it never queries GitBook or GitHub directly. The wiki carries a structured **playbook** (the [Registry use-case-implementation page](../../products/registry/registry/use-case-implementation.md)) that defines every phase, every Discovery item, and every Activity in a machine-consumable format. The Advisor reads the playbook at runtime; the orchestrator's behaviour is driven by the playbook, not by hardcoded prompts.

When an implementer starts a project, the Advisor walks them through the phases in order, captures their answers in a per-project working case, and (in Phase 2) generates a complete customised registry — extension code, Helm chart, Docker images — pushed to the implementer's GitLab namespace.

## Sub-pages

* [Concept](concept.md) — design philosophy: wiki-grounded, playbook-driven, kickstart-then-handover.
* [Design](design.md) — architecture, tech stack, repo relationships, prompt layering, LLM mode factory.
* [Modes](modes.md) — Chat vs. Project mode behaviour, off-topic handling, known limits.
* [Phases](phases.md) — Phase 1 (Requirements) and Phase 2 (Build) walkthroughs.
* [Running](running.md) — prerequisites, env vars, first-time setup.
* [Scripts](scripts.md) — utility scripts (migrate, seed, cleanup).
* [Roadmap](roadmap.md) — what's deferred, known issues, in-progress work.

## Related

* [G2P WikiLLM](../g2p-wikillm/) — the knowledge base the Advisor reads at runtime.
* [Registry implementation playbook](../../products/registry/registry/use-case-implementation.md) — the operating contract for Project mode.
