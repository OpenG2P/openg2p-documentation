---
description: >-
  Review of the Activity Registry concept notes (crop sown, livestock, work
  log) against the activity register as built, with suggested priorities.
---

# Concept Notes Review

{% hint style="info" %}
Review date: 30 September 2026. A report for future reference; nothing here was built at the time of the review unless stated. Since then, phase 1 of the [register model design](register-model-design.md#phase-1-built), which grew out of this review, has built typed participants, the Cluster register (difference 9), the crop-change link (difference 11) and verification status in DCI.
{% endhint %}

This compares three concept notes with the [activity register](activity-register.md) as built in the registry platform and the [Crop Sown Registry](crop-sown-registry.md). The notes apply the Activity Registry concept to three registries:

* **Crop sown:** an evaluation of the ATI crop sown implementation ([cropsown-regsitry](https://github.com/Centre-for-Open-Societal-Systems/cropsown-regsitry), `develop`);
* **Livestock:** born, vaccinated, sold;
* **Work log:** attendance, work performed, training attended.

Each note classifies every fact as entity registry, catalogue (Master Data), activity, trust or correction.

**Verdict:** the notes fit our formulation. They use the same split between entity registry, catalogues (MDS) and activity, the same append-only corrections, and derive state from history the same way. Nothing contradicts the core. They go further than we have in **trust** (verification and approval as separate, per-type steps), **certificates**, **participants**, and **activities that trigger entity changes**. There are also a few smaller differences, listed below.

## Where they match what we built

| Their concept | Ours |
| --- | --- |
| **Entity vs occurrence.** Farmer, plot, animal and person live in entity registries; codes and geography in the catalogues (MDS) | Same. Activities refer to farmers and plots. Code lists and geography are read live from Master Data |
| **The "season case"** groups a farmer's occurrences; its lifecycle stage is _read_ from the activities | The **context** (crop season). The stage is **derived** in the projection |
| Occurrence time vs record time; source; recorded by; status; schema version; location on every line | `occurred_at` / `recorded_at`, `channel` (+ partner), `recorded_by`, status, `schema_version`, `geo_dimensions` |
| **Corrections are new records.** The original stays; a cancellation keeps the record | Supersede (`supersedes_activity_id`; the old one becomes `SUPERSEDED`) and void (`VOIDED`, kept) |
| **Entity errors are fixed in the entity registry,** not by editing activities | Same. Activities never hold a farmer's identity, only references |
| **Derived readings:** stage, yield, current crop, days present, animal status | Projections (stage, yield), aggregates (the farmer's season summary), indicators |
| Land facts snapshotted onto an activity when this system doesn't own the land | The location is snapshotted on each activity; land facts such as soil fertility are recorded in the payload |
| Verification only on the types that warrant it | `requires_verification` on Sown and Harvested only; not on Planned, Observed or Infestation |
| The farmer is identified, not owned; production is not an activity | Same: the farmer is referenced by ID, and there is no production type |

## Where they differ from us

1. **Approval as a separate trust step. This is the biggest gap.** The notes separate two questions, each switched on per activity type, with approval off by default:
   * **verification:** did it happen as reported?
   * **approval:** will the programme stand behind it? Needed only for certificates, payments, procurement or official figures.

   We have **one step**: verification (submitted → verified / rejected). A type can't require approval, and nothing distinguishes a verified sowing from an approved one.
2. **Trust as its own records.** In the notes, verification, disputes and a supervisor's decision are records _attached to_ the activity. Evidence (a geo-tagged photo, a vaccine batch record, a device capture, a vet's credentials) is kept separate from the source. We store only the **latest** verification state on the activity row itself. Evidence is just payload fields such as `photo_document_id`, and there is no log of disputes or verifications.
3. **A trusted source can itself verify.** An authenticated veterinarian's record, or a biometric device, counts as verification. Our verification always needs a person with `activity:verify`. Nothing is verified automatically because of the channel or partner it came from.
4. **Certificates from verified activities.** A crop, vaccination or training certificate is issued as a verifiable credential once the activity is verified, and approved where that type requires it:
   * the certificate names the farmer, the plot, the activity and the verified facts, and points to the activity;
   * one activity gets one certificate;
   * a correction revokes it and reissues it after the correction is verified;
   * a cancellation revokes it.

   The crop certificate is distinct from the land certificate, which stays on the land registry. We have **nothing** for activities; the platform's VC issuance covers register records only.
5. **Correcting and disputing.**
   * The notes distinguish `CORRECTS` from `SUPERSEDES`.
   * A type can require **approval of a correction**; an authorised system may correct directly where the type allows it.
   * A disputed line whose original a supervisor confirms stands; the dispute is recorded against it.

   We have only supersede and void, gated by the `activity:correct` permission and a required reason. There is no correction approval and no disputes.
6. **Participants with roles.** An occurrence has several named participants:
   * farmer and plot (crop sown);
   * farmer, animal and veterinarian (livestock);
   * person, event and worksite (work log).

   We had **one subject** plus typed references in the payload (`plot_id`, `da_id`). The roles worked in practice but weren't first-class, so "all vaccinations by vet V789" was a payload search rather than a participant query. _(Built since: typed participants, phase 1.)_
7. **Activities that change entities.**
   * **Birth:** the animal is created in the animal registry.
   * **Sale:** an ownership change is made on the animal registry through _that registry's_ own process.

   In both cases the activity stays the history of what happened. We don't have this pattern. The hook exists (`on_activity_event`, run by the outbox worker), but nothing raises a change request on another registry. _(Decided since: entities first, see the [register model design](register-model-design.md#participants-and-entities-first).)_
8. **A strict integrity check.** Before anything is stored, the notes check that the farmer and plot **exist**, that dates fall **in the season window**, and that the area is coherent with the plot. The check passes or fails; there is no reviewer and no trust status. We compare as follows:
   * **stricter:** code lists and geography are always checked (strict mode);
   * **format-only:** farmer and plot IDs, a deliberate decision, since the Crop Sown Registry may run on its own instance and doesn't look IDs up yet;
   * **warnings, not failures:** plausibility checks (area vs plan, yield bounds);
   * **no season-window date check.**

   This is a deliberate difference, and it is recorded here.
9. **Cluster is an entity.** The notes put the cluster in its own entity registry, and treat the repository's CultivationCluster register as a duplicate of it. Our `CLUSTER_ENROLLED` activity carried the cluster's attributes (name, agro-ecological zone, area, smallholders, water source). That contradicted their classification, and also our own original design ("a cluster register in the same instance, referenced by activities"). The better model:
   * a cluster entity;
   * the activity records only the plot or farmer joining the cluster;
   * cluster totals are derived from the plot activities.

   _(Built since: the Cluster register, phase 1.)_
10. **Grain of the season case.** Theirs is per **farmer × crop year × season**. Ours is per **plot × crop year × season × crop**; the farmer level comes from the aggregate (`FARMER_SEASON_SUMMARY`). The two are compatible but not the same object. Theirs also carries the registration address and GPS; ours takes the location from the activities.
11. **Changing the crop.** Their `is_crop_changed` marks a cultivation that revised the plan. For us a different crop is a different crop season, because the crop is part of the context key, so the link between the old and new season was lost. _(Built since: the crop-change link, `replaces_crop_season_id`, phase 1.)_
12. **Naming.** Theirs are `CROP_PLANNED`, `CROP_CULTIVATED`, `CROP_SOWN`, `CROP_HARVESTED` and `CROP_INFESTATION`; ours are `PLANNED`, `LAND_PREPARED`, `SOWN`, `HARVESTED` and `INFESTATION_REPORTED`. They say "Cancelled" where we say `VOIDED`. It's cosmetic, but worth aligning if their vocabulary becomes the reference.

## What the livestock and work-log notes add

* **Livestock:**
  * three participants on a vaccination (farmer, animal, veterinarian);
  * the vet's authenticated submission as verification;
  * birth and sale driving changes on the animal registry;
  * current animal status (e.g. Sold) derived from its history.
* **Work log:**
  * attendance whose trust usually ends at _recorded_, with verification optional and approval only when a wage, benefit or certificate depends on it;
  * a biometric template as identity data on the person registry, while one day's capture is evidence on that day's attendance;
  * summaries (days present or absent) derived from the log;
  * disputes and correction approval as the main supervisor involvement.

Our platform can already hold both. Attendance maps to contexts (a person-day or a session), with check-in and check-out in the payload and summaries as aggregates. The gaps are the same ones listed above, especially 1, 2, 3, 5, 6 and 7.

## Suggested priorities

| # | Item | Why | Differences addressed |
| --- | --- | --- | --- |
| 1 | **Approval as a separate, per-type step**, plus **automatic verification from trusted sources** | Subsidies, loans and payments need "the programme stands behind it", not just "it happened". Authenticated sources (a vet system, a device) shouldn't need a person to verify every line. | 1, 3 |
| 2 | **A trust and evidence log per activity**, and **correction approval** (with disputes) | Auditable trust: several verifications, disputes and supervisor decisions, with evidence kept separate from the source | 2, 5 |
| 3 | **Certificates from verified (and approved) activities**, reusing the platform's VC issuance | Crop, vaccination and training certificates that other systems can check | 4 |
| 4 | **Cluster as an entity**, and the **crop-change link** | Removes cluster attributes from activities; keeps the history when a crop is revised | 9, 11 |
| 5 | **Participants with roles**, and **activity-triggered entity changes** | Needed for livestock (animal, vet; birth and sale) and the work log (person, event, worksite) more than for crop sown | 6, 7 |
| 6 | **Record the integrity-check difference** (farmer and plot format-only until IDs are looked up); add a season-window date check | Makes the deliberate difference explicit; closes an easy gap | 8 |

Items 10 (grain of the season case) and 12 (naming) need a decision rather than a build.

The [register model design](register-model-design.md) turns these priorities into a design. It decides differently on two of them: programme approval and certificates stay outside the registry (PBMS decides whether a programme acts on verified records), and activities don't change entities (entities first).

## Related

* [Register model design](register-model-design.md): turns these priorities into a design, making trust and corrections common to both register kinds
* [Register vs activity register](../architecture/register-vs-activity-register.md)
* [Activity register](activity-register.md), including its comparison with the Observations design
* [Crop Sown Registry](crop-sown-registry.md)
* [Open items](../open-items/README.md)
