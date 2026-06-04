# Sprint 2 Notes — Giacomo Vettore
**Period:** 2026-05-20 – 2026-05-29

---

## What I did this sprint

- Executed Condition A (F1 + F2, seeds 0–29): 60 runs confirmed reproducible from a clean clone.
- Executed Condition C (F1 + F2, seeds 0–29): 60 oracle runs complete.
- Executed Condition B sessions for assigned seeds: F2 seeds 7, 9, 10, 23–25; F1 seeds to follow in Sprint 3.
- Added the second progress-report presentation (`docs/presentations/progress_report_21_05.pdf`).
- Reviewed and fixed EDA notebook sections 6–13 for consistency with the locked sample.

## What I was blocked by

- Condition B sessions are time-intensive (5 turns × ~2 minutes each per session). With 10 assigned seeds × 2 feature sets = 20 sessions, completing all in one sprint was not feasible alongside other work.
- The branch-based workflow for Condition B runs added overhead (pull before each session, push after each seed).

## What I am doing next

- Complete the remaining Condition B sessions (seeds 23–29, F1 and F2).
- Once B is complete, run `scripts/check_integrity.py` to confirm all 180 runs are logged.
- Begin H3 oracle evaluation and human rating pipeline.
