# Sprint 1 Notes — Jasnoor Singh
**Period:** 2026-05-12 – 2026-05-20

---

## What I did this sprint

- Initialised the repository structure and committed the first scaffolding (directories, `.gitignore`, README skeleton).
- Wrote `docs/study_plan.md` v0.1: defined the two research questions (RQ1 conversational refinement, RQ2 oracle validity), the three hypotheses (H1/H2/H3), and the scope boundary. This became the authoritative statement of what the project is testing.
- Iterated on the study plan after the first team discussion, producing v0.2: incorporated EDA findings into feature-set decisions (excluding `side_a`, `type_of_violence`; clarifying F2 scope), added the Sprint 2 roadmap, and resolved four of the six open questions.

## What blocked me

- The feature-set decisions (what goes into F1 vs F2) depended on the EDA results, which Giacomo was completing in parallel. I had to wait for the cardinality table before finalising the F2 description in the study plan.
- The model string for the LLM (`config/model.yaml`) was not confirmed until Daniele pinned it late in the sprint, so the study-design document still had a placeholder at sprint end.

## What I am doing next

- Confirm K=8 is correctly justified once the elbow pre-run is executed (Sprint 2 blocker).
- Finalise `prompts/interpreter.md` and `prompts/oracle_user.md` — required before any Condition B or C run begins.
- Begin updating `docs/related_work.md` from the anchor-set draft toward v1 with positioning paragraphs.
