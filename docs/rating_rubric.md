# Rating Rubric — Pairwise Cluster Quality Judgement
**Version:** v1.0  
**Status:** Locked — do not modify after the first rater completes the form.  
**Used in:** H3 (oracle–human agreement), inter-rater reliability (Krippendorff's α)

---

## The forced-choice question

Displayed verbatim above every pair in the rating form:

> **"Which grouping makes more sense as a meaningful category of conflict event? Choose one."**

No ties are allowed. Raters must select Option A or Option B.

---

## Display format for each cluster description

Each option (A or B) is displayed as a card with the following structure:

```
┌─────────────────────────────────────────────────────┐
│  OPTION [A / B]                                     │
│                                                     │
│  Cluster 1 — [auto-generated label]   (n = [size]) │
│    • [date]  [oblast]  vs [actor]  fatalities=[n]   │
│    • [date]  [oblast]  vs [actor]  fatalities=[n]   │
│    • [date]  [oblast]  vs [actor]  fatalities=[n]   │
│                                                     │
│  Cluster 2 — [auto-generated label]   (n = [size]) │
│    • ...                                            │
│                                                     │
│  [... up to K=8 clusters]                          │
└─────────────────────────────────────────────────────┘
```

Both options always show the same K=8 clusters, the same number of representative events per cluster (3), and are drawn from the same seed (same 2,000 events). The only difference is the cluster assignment.

---

## Auto-generated label format

Labels are produced by `src/cluster.py: summarise_clusters()`. They are generated from the 3 most frequent event types and the dominant actor in the cluster. They are shown to help raters navigate the clusters but should not be the basis for the forced choice — raters are instructed to focus on the representative events.

---

## Randomisation applied to the display

- **Pair order:** the 20 pairs are presented in a randomised order, independently per rater (per-rater seed).
- **Left/right position:** for each pair, which option appears on the left (A) and which on the right (B) is randomised independently per rater.

This prevents position bias and order effects from inflating inter-rater agreement.

---

## What the oracle sees

The LLM oracle (H3) receives the same cluster descriptions in the same text format, presented in a prompt that mirrors the forced-choice question above. The oracle prompt does not reveal which condition (A, B, or C) generated each cluster assignment. The oracle must return either "A" or "B" and nothing else.

The oracle evaluation prompt is committed separately at `prompts/oracle_eval.md` before any oracle ratings are collected.

---

## Scoring and aggregation

- Each pair produces one binary outcome per rater: 0 (chose Option A) or 1 (chose Option B).
- Aggregation: majority vote across 5–8 raters. Ties (equal votes for A and B) are recorded as ties and excluded from the Spearman ρ calculation; their count is reported in the paper.
- Inter-rater reliability: Krippendorff's α computed over the full rater × pair matrix (nominal scale) before any oracle-correlation analysis.

---

## Deviations from this rubric

Any change to the question wording, display format, or scoring procedure after the first rater completes the form must be recorded as a protocol amendment in `docs/study_design.md §12` with a timestamp and rationale.
