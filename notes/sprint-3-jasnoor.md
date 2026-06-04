# Sprint 3 Notes — Jasnoor Singh
**Period:** 2026-05-29 – 2026-06-04

---

## What I did this sprint

- Implemented the four additional exploratory analyses (study_plan §11) in `notebooks/analysis.ipynb`: instruction taxonomy (§11.1), feature weight trajectory (§11.2), instruction-weight alignment check (§11.3), and per-turn Silhouette delta (§11.4). All labeled exploratory, documented with amendment A-002 in `study_design.md`.
- Performed the manual alignment review for §11.3: read all 48 flagged B/F2 instructions, classified each as TRUE_MISALIGNED / CLASSIFIER_ERROR / PARTIAL / AMBIGUOUS. Saved results to `runs/alignment_manual_review.json`. Key finding: true interpreter misalignment rate ~13%, not 32% as the automated classifier suggested.
- Built `scripts/reproduce_clusters.py`: standalone script to reproduce cluster assignments from any logged run and generate the 20 H3 pair descriptions.
- Generated the 20 H3 rating pairs (`runs/h3_pairs/`): pair selection, randomisation of A/B position, anonymised companion document, and 20 pair visualisation images (geographic scatter map + cluster profile table) for the Google Form.
- Committed the Google Form link to `docs/rating_instrument_link.txt` and cleaned the companion document of group-label leakage before sharing with raters.
- Updated `docs/study_plan.md` to v0.5 (§11 exploratory analyses) and committed sprint documentation.

## What I was blocked by

- The manual alignment review required reading 48 instructions individually — time-intensive but not technically blocked.
- The Google Form image upload (20 PNG files at ~2.25 MB total) caused an HTTP 400 error on push; resolved by increasing `http.postBuffer`.

## What I am doing next

- Final presentation: prepare and present the H2 section.
- Support the final report write-up with the H2 narrative (feature trap, Davies-Bouldin nuance, instruction taxonomy finding).
