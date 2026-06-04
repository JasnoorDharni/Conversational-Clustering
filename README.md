# Conversational Clustering on UCDP GEDEvent 25.1

This repository contains the code, prompts, committed sample data, logs, and study documents for the capstone project on conversational clustering of UCDP GED conflict events.

This README is intentionally limited to setup, repository structure, and reproduction entry points. Study framing, methodology, ethics, and reporting live in `docs/` and `report/`.

Results dashboard: https://conversational-clust-g58t.bolt.host/

## Setup

Requirements:
- Python 3.11+
- `pip`
- Anthropic API key only for LLM-dependent steps

From the repository root:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

If you need the LLM-backed paths:

```powershell
$env:ANTHROPIC_API_KEY="..."
```

## Repository Structure

```text
Conversational-Clustering/
|-- config/                  # Condition configs and model pin
|-- data/
|   |-- sample_seed42.csv    # Locked 2,000-event sample
|   `-- eda_outputs/         # Saved EDA outputs
|-- docs/                    # Study and ethics documents
|-- notebooks/
|   |-- analysis.ipynb
|   `-- eda_ucdp_ukraine.ipynb
|-- prompts/                 # Versioned prompt files
|-- report/
|   `-- final_report.tex     # Final report draft
|-- project/                 # Results dashboard UI
|-- runs/
|   |-- run_log.jsonl        # Main experiment log
|   |-- h3/                  # H3-only outputs
|   `-- h3_pairs/            # Fixed H3 pair materials
|-- scripts/
|   |-- run_experiment.py
|   |-- check_integrity.py
|   |-- prepare_h3_human_ratings.py
|   |-- run_h3_oracle_eval.py
|   `-- analyze_h3.py
|-- src/                     # Core pipeline code
|-- requirements.txt
`-- README.md
```

## Main Reproduction Entry Points

### Run the main experiment pipeline

```bash
python scripts/run_experiment.py --config config/condition_A_F2.yaml --seeds 0 29
```

Examples:

```bash
python scripts/run_experiment.py --config config/condition_A_F2.yaml --seeds 0 29
python scripts/run_experiment.py --config config/condition_C_F2.yaml --seeds 0 29
python scripts/run_experiment.py --config config/condition_B_F2.yaml --seeds 7 7
```

### Check run completeness before analysis

```bash
python scripts/check_integrity.py --log runs/run_log.jsonl
```

### Open the committed notebooks

- Main analysis: `notebooks/analysis.ipynb`
- EDA: `notebooks/eda_ucdp_ukraine.ipynb`

## H3 Reproduction

H3 files are kept under `runs/h3/` and `runs/h3_pairs/`.

Prepare human ratings:

```bash
python scripts/prepare_h3_human_ratings.py --input "Conflict Event Clustering - Rating Task.csv" --overwrite
```

Dry-run oracle evaluation:

```bash
python scripts/run_h3_oracle_eval.py --orders original swapped --dry-run --overwrite
```

Run oracle evaluation:

```bash
python scripts/run_h3_oracle_eval.py --orders original swapped --overwrite
```

Analyze H3:

```bash
python scripts/analyze_h3.py --overwrite
```

Optional diagnostic figure:

```bash
python scripts/analyze_h3.py --overwrite --write-plot
```

Current minimal H3 output footprint:
- `runs/h3/metadata.csv`
- `runs/h3/human/ratings_wide.csv`
- `runs/h3/oracle/ratings_long.csv`
- `runs/h3/oracle/ratings_raw.jsonl`
- `runs/h3/oracle/position_bias_summary.csv`
- `runs/h3/analysis/results_summary.csv`
- optional `runs/h3/analysis/oracle_bias_diagnostic.svg`

## Key Documents

- `docs/study_plan.md`
- `docs/study_design.md`
- `docs/quality_spec.md`
- `docs/related_work.md`
- `docs/data_provenance.md`
- `docs/ethics_note.md`
- `docs/dashboard_design.md`
- `report/final_report.tex`

## Notes

- The raw UCDP GED file is not committed to the repository.
- The committed experimental sample is `data/sample_seed42.csv`.
- H3 was executed, but it failed as evidence for oracle validity because the oracle showed strong displayed-label bias and the human inter-rater reliability was low.
