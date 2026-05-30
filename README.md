# Conversational Clustering on UCDP GEDEvent 25.1

> **Research question:** Does iterative conversational LLM refinement produce measurably better k-means clusters of conflict events than a one-shot automated baseline — and can an LLM oracle reliably substitute for human judgment when evaluating cluster quality?

**Pre-registration:** `docs/study_design.md` (locked at first `run_log.jsonl` entry)  
**Stack:** Python 3.11+, scikit-learn, Anthropic API (`claude-sonnet-4-5`), pandas, jsonlines

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Repo Structure](#2-repo-structure)
3. [Setup](#3-setup)
4. [Quickstart — Smoke Test](#4-quickstart--smoke-test)
5. [Running Experimental Conditions](#5-running-experimental-conditions)
6. [Checking Run Completeness](#6-checking-run-completeness)
7. [Analysis](#7-analysis)
8. [Results Dashboard](#8-results-dashboard)
9. [Experimental Design Summary](#9-experimental-design-summary)
10. [Current Status](#10-current-status)
11. [Key Findings (Preliminary)](#11-key-findings-preliminary)
12. [Data Provenance](#12-data-provenance)
13. [Ethics Note](#13-ethics-note)
14. [Team](#14-team)
15. [Documentation Index](#15-documentation-index)

---

## 1. Project Overview

This project investigates whether a conversational loop — where a user refines k-means clusters through free-form natural language instructions interpreted by an LLM — produces higher-quality cluster assignments than a standard one-shot automated run.

The dataset is a 2,000-event random sample drawn from the **UCDP Georeferenced Event Dataset (GED) v25.1**, filtered to the Russia-Ukraine conflict from 24 February 2022 onwards. Each event record encodes location (coordinates + oblast), actor identities, violence type, and estimated fatalities. There is no ground-truth partition, making it a suitable testbed for unsupervised clustering evaluation.

The study has two primary claims:

- **RQ1 (H1/H2):** Conversational refinement improves Silhouette score versus a one-shot k-means baseline, with improvement moderated by feature set richness.
- **RQ2 (H3):** An LLM oracle's cluster-quality rankings correlate with human rater rankings at Spearman's ρ > 0.7, making oracle evaluation a viable low-cost proxy.

The study follows a **pre-registered design** (`docs/study_design.md`). All hypotheses, outcome measures, and analysis steps were committed before any experimental run was executed. Protocol amendments are timestamped in `docs/study_design.md §12`.

---

## 2. Repo Structure

```
conv-clustering/
├── README.md
├── requirements.txt
├── config/                         # One YAML per experimental condition
│   ├── condition_A_F1.yaml         # Baseline, location-only features
│   ├── condition_A_F2.yaml         # Baseline, full features
│   ├── condition_B_F1.yaml         # Human conversational, location-only
│   ├── condition_B_F2.yaml         # Human conversational, full features
│   ├── condition_C_F1.yaml         # LLM oracle, location-only
│   ├── condition_C_F2.yaml         # LLM oracle, full features
│   ├── model.yaml                  # Pinned LLM version (single source of truth)
│   ├── toy.yaml                    # Smoke-test config (no data file, no API key needed)
│   └── experimenter_order.txt      # Pre-drawn seed-to-experimenter assignment (Condition B)
├── data/
│   ├── sample_seed42.csv           # Locked 2,000-event sample (committed once, never redrawn)
│   └── clean.py                    # Filter + sample script
├── prompts/                        # Versioned prompt files — NOT embedded in code
│   ├── interpreter.md              # LLM interpreter prompt
│   └── oracle_user.md              # LLM oracle-as-user prompt
├── src/                            # Library modules
│   ├── __init__.py
│   ├── features.py                 # F1 / F2 feature encoding
│   ├── cluster.py                  # k-means wrapper, Silhouette, Davies-Bouldin
│   ├── llm.py                      # Anthropic API calls with retry/backoff
│   ├── loop.py                     # Conversational turn loop (Conditions B & C)
│   └── logger.py                   # Structured JSONL logging
├── scripts/
│   ├── run_experiment.py           # Main entry point
│   └── check_integrity.py          # Post-run completeness check
├── notebooks/
│   ├── eda_ucdp_ukraine.ipynb      # Exploratory data analysis & sample generation
│   └── analysis.ipynb              # Pre-specified confirmatory analysis
├── runs/
│   └── run_log.jsonl               # Append-only experiment log (pre-registration lock point)
└── docs/
    ├── study_plan.md               # Research questions, hypotheses, roadmap (v0.5)
    ├── study_design.md             # Pre-registered experimental blueprint (v0.1)
    ├── quality_spec.md             # Metric definitions and reporting rules (v0.1)
    ├── related_work.md             # Literature survey across 6 threads (v1)
    ├── data_provenance.md          # Dataset provenance, hashes, ethics
    └── rating_instrument_link.txt  # Link to human rater Google Form
```

---

## 3. Setup

**Requirements:** Python 3.11+, git

```bash
# 1. Clone and enter the repo
git clone <repo-url>
cd conv-clustering

# 2. Create a virtual environment and install dependencies
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. Set your Anthropic API key (only needed for Conditions B and C)
export ANTHROPIC_API_KEY="sk-ant-..."
```

> **Note:** Condition A (baseline k-means) requires no API key. Conditions B and C require a valid `ANTHROPIC_API_KEY` environment variable.

---

## 4. Quickstart — Smoke Test

Run this to verify the full pipeline end-to-end with no data file and no API key:

```bash
python scripts/run_experiment.py --config config/toy.yaml --seeds 0 4
```

**Expected output:**
```
[toy] Condition A | F1 | K=3 | 5 seeds
Seed 0 → silhouette=0.412  ✓
Seed 1 → silhouette=0.389  ✓
Seed 2 → silhouette=0.401  ✓
Seed 3 → silhouette=0.397  ✓
Seed 4 → silhouette=0.415  ✓

Integrity check: 5 intended, 5 complete, 0 errors.
Log written to: runs/toy_run_log.jsonl
```

Silhouette values will vary slightly by platform but should fall in the range 0.35–0.45.

---

## 5. Running Experimental Conditions

```bash
# Condition A — automated baseline, F2 features, seeds 0–29 (no API key needed)
python scripts/run_experiment.py --config config/condition_A_F2.yaml --seeds 0 29

# Condition C — LLM oracle, F2 features, seeds 0–29 (requires ANTHROPIC_API_KEY)
python scripts/run_experiment.py --config config/condition_C_F2.yaml --seeds 0 29

# Condition B — human conversational, single seed for debugging
python scripts/run_experiment.py --config config/condition_B_F2.yaml --seeds 7 7
```

Each run appends one JSONL record to `runs/run_log.jsonl`.

**Condition B session rules** (human experimenter must follow these):
1. Do **not** view Silhouette or Davies-Bouldin scores during the session.
2. Interact only via the CLI — no manual parameter edits.
3. Complete all 5 turns before logging the session as finished.
4. Record a brief post-session qualitative note (2–3 sentences) on cluster interpretability.

---

## 6. Checking Run Completeness

Always run this before opening `notebooks/analysis.ipynb`:

```bash
python scripts/check_integrity.py --log runs/run_log.jsonl
```

**Example output:**
```
Condition A / F1 : 30 intended, 30 complete,  0 refused,  0 errors. ✓
Condition A / F2 : 30 intended, 30 complete,  0 refused,  0 errors. ✓
Condition B / F1 : 30 intended, 28 complete,  2 refused,  0 errors. ⚠ Missing seeds: [14, 22]
Condition B / F2 : 30 intended, 30 complete,  0 refused,  0 errors. ✓
Condition C / F1 : 30 intended, 30 complete,  0 refused,  0 errors. ✓
Condition C / F2 : 30 intended, 30 complete,  0 refused,  0 errors. ✓
```

**Refused runs** (Claude safety filter on conflict data) are logged with `status: "refused"` and reported as data loss in the final analysis — they are **never silently dropped**.

---

## 7. Analysis

All confirmatory analyses are pre-specified in `docs/study_design.md §8`. Open `notebooks/analysis.ipynb` only after `check_integrity.py` exits with code 0.

The notebook tests:

| Hypothesis | Type | Test |
|---|---|---|
| **H1** — Conversational refinement improves Silhouette vs baseline | Confirmatory | One-sided Wilcoxon signed-rank (Condition B/F2 vs A/F2, paired by seed); bootstrap 95% CI on median improvement |
| **H2** — Improvement is larger under F2 than F1 | Exploratory | Mann-Whitney U on per-seed B−A improvement scores |
| **H3** — Oracle–human Spearman ρ > 0.7 | Confirmatory | Spearman's ρ on 20 held-out pairs; bootstrap 95% CI |

Any analysis **not** listed in `study_design.md §8` must be labelled exploratory and post-hoc. See `study_plan.md §11` for the four post-hoc exploratory analyses registered under amendment A-002.

---

## 8. Results Dashboard

A lightweight Streamlit dashboard accompanies the final analysis (read-only — no recomputation of clustering):

```bash
pip install streamlit plotly
streamlit run dashboard/app.py
```

**Views:**

| View | Description |
|---|---|
| Overview | Summary table: mean Silhouette and Davies-Bouldin per (condition × feature set) |
| H1 comparison | Box plot of final Silhouette scores for A vs B vs C, split by feature set |
| Per-turn trajectory | Median Silhouette by turn number for Conditions B and C |
| Geographic cluster map | Scatter map of 2,000 events coloured by cluster assignment for a selected run |
| Run explorer | Filterable table of all records in `run_log.jsonl` |

Data source: `runs/run_log.jsonl` and `data/sample_seed42.csv`.

---

## 9. Experimental Design Summary

### Conditions

| Condition | Description | API needed |
|---|---|---|
| **A** | One-shot k-means on the fixed feature matrix (automated baseline) | No |
| **B** | Human experimenter issues 5 free-form refinement instructions via CLI | No (runtime); Yes (API for interpreter) |
| **C** | LLM oracle issues 5 instructions autonomously, simulating a user | Yes |

### Feature Sets

| Level | Features |
|---|---|
| **F1** | Latitude, longitude, adm1 (one-hot) |
| **F2** | F1 + event type (one-hot) + actor identity (one-hot, top-N) + best fatality estimate |

### Key Parameters

- **K = 8** (fixed across all conditions; confirmed via elbow method)
- **30 seeds** per (condition × feature set) cell → 180 total runs planned
- **Model:** `claude-sonnet-4-5` (pinned in `config/model.yaml`)
- **Max turns per session:** 5

### Primary Metrics

- **Silhouette score** (primary; higher = better separated, more cohesive clusters)
- **Davies-Bouldin index** (secondary; lower = better; robustness check)

---

## 10. Data Provenance

- **Source:** UCDP GEDEvent v25.1 — [https://ucdp.uu.se/downloads/](https://ucdp.uu.se/downloads/)
- **Raw file MD5:** `56d33581a615c8e3772b7500c8a2c1c6` (385,918 rows × 49 columns)
- **Filter:** `country_id == 369` (Ukraine) AND `date_start >= 2022-02-24`
- **Sample:** N = 2,000, drawn with `random_state=42`; committed to `data/sample_seed42.csv`
- **Sample MD5:** `97a7b1673e78d26834d6237d1c6cbe39`

The raw data file (`data/raw/GEDEvent_v25_1.csv`) is **not committed** to this repo due to size. Download it from the UCDP website and place it at `data/raw/GEDEvent_v25_1.csv` before running `notebooks/eda_ucdp_ukraine.ipynb`. Full provenance is documented in `docs/data_provenance.md`.