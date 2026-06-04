# Dashboard Design Document

## Goal

Turn the existing `project/` site into a static results dashboard for the study.
It should present only committed project evidence, not act like a chat product or slide deck.

Current deployed dashboard: https://conversational-clust-g58t.bolt.host/

## Content Rules

- Use only data backed by committed files in `runs/`, `data/eda_outputs/`, `docs/`, and `report/`.
- Organize the main story around the three hypotheses: H1, H2, H3.
- Keep text short and interpretive only when it helps read the charts.
- Remove old placeholder framing that centered Condition C as the main comparison.
- Do not show controls or widgets that imply live clustering, live prompting, or user interaction with the model.

## Information Architecture

### 1. Overview

Purpose: orient the viewer in one screen.

Show:
- filtered Ukraine events
- sampled events
- total completed runs
- H3 human raters
- one-line study scope: static dashboard of committed experiment results

### 2. Dataset + Experiment Context

Purpose: give just enough context to read the hypotheses.

Show:
- raw -> filtered -> sampled funnel
- top oblast distribution
- fatality skew summary
- feature-set definition cards for F1 and F2
- 3 x 2 run matrix summary (A/B/C by F1/F2)

Do not show:
- long methodology prose
- prompt details
- implementation notes that do not affect interpretation

### 3. H1 Section

Hypothesis:
Conversational refinement improves final Silhouette relative to the one-shot baseline under F2.

Show:
- paired seed-level `B - A` Silhouette delta chart for F2
- summary cards: median delta, 95% bootstrap CI, positive/negative/zero seeds
- condition summary comparison for A/F2, B/F2, C/F2
- compact turn trajectory for B and C under F2 to show how refinement evolved

Interpretation line:
- concise statement that H1 is not supported if the CI crosses zero and the median delta is non-positive

### 4. H2 Section

Hypothesis:
Refinement helps more under the richer feature set than under the location-only set.

Show:
- side-by-side seed-level delta distributions for `B - A` under F1 and F2
- cards for F1 median delta, F2 median delta, and the median difference `(F2 - F1)`
- small grouped comparison of cell medians across feature sets

Interpretation line:
- concise statement that the richer feature set does not clearly increase the benefit of refinement if the difference CI spans zero

### 5. H3 Section

Hypothesis:
The oracle is a valid proxy for human judgment in pairwise cluster comparisons.

Show:
- key summary cards: Krippendorff alpha, original-order agreement, Cohen kappa, position-bias pairs
- strong visual for swap diagnostic: same displayed label after swap vs same underlying clustering after swap
- grouped human-majority preference counts for the four H3 pair families

Interpretation line:
- concise statement that H3 is not supported because human reliability is low and displayed-label bias is strong

## Visual Direction

- Replace the generic white dashboard look with a more editorial, evidence-wall style.
- Use warm paper tones with deep ink, rust, teal, and gold accents.
- Keep charts crisp and high-contrast; make hypothesis status visible without needing paragraphs.
- Use expressive typography for headings and a calmer body face.
- Use subtle grid/gradient backgrounds and section separators, not flat blank panels.

## Components to Remove or Replace

- old "oracle vs baseline" framing as the main result section
- old incomplete-status messaging about hiding Condition B
- instruction-theme cards as a primary finding
- generic "implementation to evidence" presentation-style summary blocks
- long methodological note lists that do not help interpret the data

## Source Files to Ground the Dashboard

- `runs/run_log.jsonl`
- `runs/h3/analysis/results_summary.csv`
- `runs/h3/metadata.csv`
- `runs/h3/oracle/position_bias_summary.csv`
- `data/eda_outputs/eda_summary.txt`
- `report/final_report.tex`
