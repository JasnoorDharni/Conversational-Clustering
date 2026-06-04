# Sprint 2 Notes — Jasnoor Singh
**Period:** 2026-05-20 – 2026-05-29

---

## What I did this sprint

- Updated `docs/study_plan.md` to v0.3 and v0.4: documented the model-string inconsistency between Condition A and C runs as protocol amendment A-001; updated execution status (120 runs complete for A and C); added preliminary H1 result for Condition C (not supported, p=0.9992); added dashboard plan (§10).
- Updated `docs/related_work.md` to v1: wrote positioning paragraphs for all six literature threads, closed resolved open questions (safety filters, context window limits, prior GED clustering uses), and replaced the notes-for-v1 section with a synthesis statement ready for the final report.
- Added the elbow-method analysis (§14) to `notebooks/eda_ucdp_ukraine.ipynb`: computed inertia and Silhouette for K=2–15 on both F1 and F2, generated `data/eda_outputs/08_elbow_plot.png`, and documented the monotonically-increasing Silhouette artifact due to geographic concentration.
- Executed Condition B / F2 sessions for seeds 17–22 (6 sessions), and Condition B / F1 sessions for seeds 6, 8, 11, 12, 17–22 (10 sessions), using a dedicated branch (`condition-b-jasnoor`) merged back via PR.
- Filled `config/experimenter_order.txt` with the seed-to-experimenter assignment.

## What I was blocked by

- Condition B required the API key, which was initially held by one team member. Resolved by sharing the key and each member using their own branch.
- The `experimenter_order.txt` was still `PENDING` at the start of sprint — could not begin Condition B sessions until it was filled.

## What I am doing next

- Complete the remaining Condition B sessions once all team members have pushed their runs.
- Implement the four additional exploratory analyses (§11: instruction taxonomy, weight trajectory, alignment check, per-turn delta) in `notebooks/analysis.ipynb`.
- Generate H3 cluster pairs and rating form materials once all B runs are complete.
