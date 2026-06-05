# Sprint 3 Notes — Giacomo Vettore
**Period:** 2026-05-29 – 2026-06-04

---

## What I did this sprint

- Completed the remaining Condition B / F1 sessions for assigned seeds (7, 9, 10, 23–29): 10 sessions, bringing the total to 180/180 runs across all conditions and feature sets.
- Fixed three mislabelled B/F1 runs (seeds 6, 8, 11) that had been logged with incorrect metadata.
- Ran the full H3 oracle evaluation pipeline (`scripts/run_h3_oracle_eval.py`): submitted all 20 cluster pairs to the oracle in both original and swapped A/B configurations to detect position bias. Saved results to `runs/h3/oracle/`.
- Processed the Google Form human ratings export using `scripts/prepare_h3_human_ratings.py` and saved the standardised output to `runs/h3/human/ratings_wide.csv`.
- Ran `scripts/analyze_h3.py`: computed Krippendorff's α (0.13), oracle–human agreement (65%), Cohen's κ (0.22), Spearman's ρ (0.24), and the swap diagnostic (19/20 pairs showed position bias). H3 not supported.
- Refined `notebooks/analysis.ipynb` with the complete 180-run log: updated all figures and tables to final values.
- Built the results dashboard (`project/`): React/TypeScript/Vite app with six views (overview, dataset funnel, H1 results, per-turn trajectory, H3 oracle analysis, team contributions). Data hardcoded from committed logs.
- Aligned all documentation with executed findings: updated `docs/study_design.md` to v0.2, `docs/study_plan.md` to v0.8, `docs/data_provenance.md`, `docs/quality_spec.md`.
- Wrote the LaTeX skeleton for `report/final_report.tex` covering all required sections.

## What I was blocked by

- H3 oracle evaluation revealed strong position/display-label bias — the oracle chose the same displayed label in 19/20 pairs regardless of content. This made H3 uninterpretable under the original design and required adding the swap diagnostic post-hoc (amendment A-003 to study_design.md).
- Human inter-rater reliability was very low (α = 0.13), weakening the human reference signal independently of the oracle bias.

## What I am doing next

- Complete the technical report body (results and discussion sections).
- Prepare contribution slides for the final presentation.
