# Sprint 1 Notes — Giacomo Vettore
**Period:** 2026-05-12 – 2026-05-20

---

## What I did this sprint

- Built `notebooks/eda_ucdp_ukraine.ipynb`: full exploratory data analysis on the UCDP GED 25.1 dataset filtered to the Russia-Ukraine conflict (27,942 events, 2022-02-24 onwards).
- Key EDA findings documented: `side_a` has cardinality 1 (always Government of Russia), `type_of_violence` is 99.2% state-based, Donetsk oblast accounts for 49.1% of events. These findings directly shaped the F2 feature-set decisions.
- Drew and committed the locked experimental sample: 2,000 events, seed 42, `data/sample_seed42.csv`. MD5 recorded in `docs/data_provenance.md`.
- Produced and committed six EDA output figures (`data/eda_outputs/01–06`).
- Committed the first progress report presentation (`docs/presentations/progress_report_14_05.pdf`).

## What I was blocked by

- EDA revealed that `adm_2` had 19.8% null rate and 128 categories — decision on whether to include it in F2 required team discussion. Resolved: excluded.
- The `where_description` embedding question (whether to use sentence-transformers) required a team decision. Resolved: excluded, marginal value over structured geographic features.

## What I am doing next

- Run Condition A (F1 + F2, 30 seeds each) once the MVB is stable — this is the primary Sprint 2 execution task.
- Begin Condition C oracle runs.
- Sanity-check all run logs for completeness before analysis begins.
