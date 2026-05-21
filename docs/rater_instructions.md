# Rater Instructions — Conversational Clustering Study
**Version:** v1.0  
**Status:** Locked — do not modify after the first rater completes the form.  
**Consent form:** See `docs/rater_consent_form.md`

---

## What you are being asked to do

You will see **20 pairs of cluster descriptions**. Each pair shows two alternative ways of grouping the same set of conflict events from the Russia-Ukraine war (2022–2024). For each pair, you will choose which grouping makes more sense to you as a meaningful way of categorising conflict events.

The task takes approximately **15–20 minutes**.

---

## What the data is

The events come from the UCDP Georeferenced Event Dataset — a publicly available academic dataset of organised violent events. Each event record includes:

- **Date** — when the event occurred
- **Location** — the oblast (region) and approximate coordinates
- **Actor** — the opposing military actor (e.g. Armed Forces of Ukraine, Wagner Group)
- **Fatalities** — estimated number of deaths

**Content warning:** The descriptions reference real military conflict events, including casualties. If you find this content distressing at any point, you are free to stop. Your participation is entirely voluntary.

---

## What you will see for each pair

Each cluster description shows:

1. A short **cluster label** (auto-generated from the most common event types and actors in that cluster)
2. The **size** of the cluster (number of events)
3. **3 representative events** from the cluster, each showing: date, region, opposing actor, and fatality estimate

You will see two such descriptions side by side, labelled **Option A** and **Option B**.

---

## The question you answer for each pair

> **"Which grouping makes more sense as a meaningful category of conflict event?"**

Choose **Option A** or **Option B**. You must choose one — ties are not allowed.

**What "makes more sense" means:** The better grouping is the one where the events within each cluster feel like they genuinely belong together — they share something real (geography, actor, intensity, or some combination) that makes the cluster interpretable as a category. The worse grouping is the one where clusters feel arbitrary or mixed in a way that is hard to explain.

You do not need expert knowledge of the conflict. Your judgement as an informed observer is what we are measuring.

---

## What to ignore

- Do not choose based on which option has more or fewer clusters — both options always have the same number of clusters (K=8).
- Do not choose based on cluster label quality — the labels are auto-generated and may be imperfect. Focus on the representative events.
- Do not try to match events to real news you remember. Judge the groupings on internal coherence only.

---

## How your data will be used

- Your choices are aggregated across all raters using majority vote.
- No individual rater's choices are published — only the aggregate.
- Your responses are stored anonymously (a random rater ID, not your name).
- The aggregated ratings are used to validate whether an LLM oracle agrees with human judgement (Research Question 2 of the study).

---

## Practical notes

- Rate all 20 pairs in one sitting if possible. Partial responses are recorded but excluded from the inter-rater reliability calculation if fewer than 15 pairs are completed.
- The order of pairs and the left/right position of Options A and B are randomised per rater.
- If a pair is genuinely impossible to judge (e.g. both descriptions appear identical), select either option and add a note in the free-text comment box.
