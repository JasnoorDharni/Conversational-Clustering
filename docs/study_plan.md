# Study Plan - Conversational Clustering on the UCDP GEDEvent 25.1 Dataset

**Dataset:** UCDP Georeferenced Event Dataset (GED) v25.1, filtered to the Russia-Ukraine conflict  
**Version:** v0.8

---

## Changelog

| Version | Date | Summary of changes |
|---|---|---|
| v0.1 | 2026-05-13 | Initial draft. Research questions, hypotheses, scope, and preliminary measurement plan committed at Sprint 1 start. |
| v0.2 | 2026-05-20 | EDA-informed update. Feature-set assumptions revised after the first data audit. |
| v0.3 | 2026-05-22 | Study-plan update after early execution work. Model pin, prompt files, and operational K value clarified. |
| v0.4 | 2026-05-28 | Execution status and remaining run planning updated during Condition B work. |
| v0.5 | 2026-05-29 | Post-hoc exploratory analyses documented and explicitly marked exploratory. |
| v0.6 | 2026-06-02 | Feature-set description aligned with the executed implementation. |
| v0.7 | 2026-06-02 | H3 execution recorded. The oracle-human evaluation was completed and interpreted as not supported because of strong displayed-label bias and low human inter-rater reliability. |
| v0.8 | 2026-06-02 | Study-plan cleanup. Result-heavy interpretation and report-style prose removed so this document remains a versioned record of questions, hypotheses, scope, and open issues. |

---

## 1. Context and Motivation

The UCDP GEDEvent 25.1 dataset provides structured, georeferenced records of organized violence in the Russia-Ukraine conflict. The project asks whether a conversational clustering workflow can improve on a simple automated baseline when there is no ground-truth clustering label set.

The study also asks a methodological question: whether an LLM oracle can stand in for humans when judging cluster quality. That question matters because the main experiment is cheap to scale computationally, while human judgment is not.

---

## 2. Research Questions

### Primary - RQ1

> Does iterative conversational refinement produce better clusters than a one-shot baseline on the UCDP GED sample, and does that depend on the feature representation?

### Secondary - RQ2

> Can an LLM oracle serve as a valid proxy for human judgment when rating pairwise cluster-quality comparisons in this setting?

---

## 3. Hypotheses

| ID | Type | Statement |
|---|---|---|
| H1 | Confirmatory | Conversational refinement improves final Silhouette score relative to the one-shot baseline under the full feature set. |
| H2 | Exploratory | Conversational refinement helps more under the richer feature set than under the location-only feature set. |
| H3 | Confirmatory | Oracle judgments correlate strongly enough with human judgments to support oracle-based evaluation in this setting. |

H1 is the primary confirmatory claim. H2 is exploratory. H3 is confirmatory but depends on the human reference signal being reliable enough to support interpretation.

---

## 4. Study Design Summary

Full operational detail is in `docs/study_design.md`. The core structure is:

- Condition A: one-shot k-means baseline.
- Condition B: conversational refinement with a human experimenter.
- Condition C: conversational refinement with an LLM oracle acting as user.
- Feature set F1: location-heavy baseline representation.
- Feature set F2: F1 plus `type_of_violence`, `side_b`, and raw min-max normalized `best` fatalities.
- Analysis paired by seed over 30 replications per condition-feature cell.

---

## 5. Primary Outcome and Measurement

Full measurement definitions are in `docs/quality_spec.md`. The core plan is:

- Primary outcome for H1: final Silhouette score.
- Secondary quantitative checks: Davies-Bouldin index and turn-level trajectory summaries.
- H3 evaluation: oracle-versus-human pairwise forced-choice agreement, reported together with human inter-rater reliability and swap-based bias diagnostics.

---

## 6. Scope Boundary

The repository build exists to run the study reproducibly. The project scope is:

- Config-driven experimental conditions.
- Logged runs reproducible from committed scripts and inputs.
- Versioned prompts, configs, and rating materials.
- Analysis generated from committed logs.

The project does not currently promise any separate product layer beyond what is needed to run and report the study.

---

## 7. Open Questions

### Resolved

- The experimental sample was locked as `data/sample_seed42.csv`.
- The executed F2 implementation was clarified and documented.
- The prompt files and model pin were committed.
- H3 was executed on the available 20-pair set with five human raters.

### Still open or to be handled in reporting

- Final report synthesis across H1, H2, and H3.
- Clear separation of confirmatory versus exploratory findings in the final write-up.
- Explicit documentation of remaining design limitations that the experiment does not rule out.

---

## 8. Study Evolution Note

This study plan is a living document rather than a frozen pre-registration. The detailed design, amendment trail, and measurement rules are carried by `docs/study_design.md` and `docs/quality_spec.md`. The purpose of this file is to keep the research trajectory and its version history legible.

---

## 9. H3 Status

H3 was executed, but it failed as evidence for oracle validity. The decisive reasons are:

- strong displayed-label bias in the oracle judgments under the original/swapped A/B diagnostic
- low human inter-rater reliability, which weakens the human reference signal itself

Detailed reporting belongs in `report/final_report.tex`, not in this study-plan file.

---

## 10. Engineering Scope Note

The repository scope is limited to the study pipeline, versioned materials, and reproducible analysis/reporting artifacts.
The project also includes a lightweight results dashboard UI in `project/`, deployed at <https://conversational-clust-g58t.bolt.host/>, for presenting EDA and H1-H3 outputs.

---

## 11. Additional Exploratory Analyses

These analyses remain explicitly exploratory and separate from H1-H3:

- instruction taxonomy comparing human and oracle refinement behavior
- feature-weight trajectories over conversational turns
- instruction-to-weight alignment checks for the interpreter
- per-turn Silhouette delta analysis

If reported, they should be labeled exploratory in the final report.
