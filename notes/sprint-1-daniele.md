# Sprint 1 Notes — Daniele Notarangelo
**Period:** 2026-05-12 – 2026-05-20

---

## What I did this sprint

- Wrote `docs/study_design.md` v0.1: operationalised the study plan into a pre-registered experimental blueprint — factor structure, three conditions (A/B/C), two feature sets (F1/F2), outcome measures, decision rules, sample-size justification, randomisation plan, and amendment procedure.
- Wrote `docs/quality_spec.md`: defined the measurement rules for Silhouette, Davies-Bouldin, and H3 inter-rater statistics.
- Wrote `docs/data_provenance.md`: documented the UCDP GED 25.1 source, filter criteria, and EDA summary statistics.
- Wrote `docs/ethics_note.md`: ethical classification of dataset and human rater protocol.
- Committed the initial `related_work.md` anchor set (six thematic clusters, 17 references with one-line takes).
- Added the initial project structure and dependency file (`requirements.txt`).

## What I was blocked by

- The study design required K to be confirmed by elbow method before being locked, but the pre-run was not completed this sprint. K=8 was declared as the intended value pending confirmation.
- Prompt files (`prompts/interpreter.md`, `prompts/oracle_user.md`) could not be written until the interpreter's JSON schema was agreed — deferred to Sprint 2.

## What I am doing next

- Build the minimum viable build: `src/features.py`, `src/cluster.py`, `src/loop.py`, `src/logger.py`, `src/llm.py`.
- Run Condition A (F1 and F2, seeds 0–29) to produce the first 60 log entries.
- Pin the LLM model string in `config/model.yaml` and commit prompt files.
