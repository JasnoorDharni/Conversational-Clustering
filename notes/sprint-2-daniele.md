# Sprint 2 Notes — Daniele Notarangelo
**Period:** 2026-05-20 – 2026-05-29

---

## What I did this sprint

- Built the minimum viable build: `src/features.py` (F1/F2 feature encoding with configurable weights), `src/cluster.py` (k-means wrapper, Silhouette, Davies-Bouldin, cluster summary), `src/loop.py` (conversational turn loop for Conditions B and C), `src/logger.py` (structured JSONL logging), `src/llm.py` (Anthropic API wrapper with retry/backoff, refusal detection).
- Pinned the LLM model string in `config/model.yaml` (`claude-sonnet-4-5`) and committed versioned prompt files (`prompts/interpreter.md`, `prompts/oracle_user.md`).
- Executed Condition A (F1 + F2, seeds 0–29): 60 runs, all complete, logged to `runs/run_log.jsonl`.
- Executed Condition C (F1 + F2, seeds 0–29): 60 runs, all complete.
- Executed Condition B sessions for assigned seeds (F1 and F2).
- Updated analysis figures: improved Silhouette boxplot, H1 improvement chart, turn trajectory plot.
- Refined code structure for readability; added print-cluster display in the Condition B loop so experimenters could see the cluster summary before issuing instructions.

## What I was blocked by

- A `_sha7` function for config hashing failed on empty paths — fixed mid-sprint.
- Condition B required careful branch management to avoid `run_log.jsonl` merge conflicts; resolved with per-person branches and sequential merges.

## What I am doing next

- Contribute to the technical report: method section, results tables, figures.
- Review and update the README to reflect the completed build.
