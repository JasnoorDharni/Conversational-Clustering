# Conversational Clustering on UCDP GEDEvent 25.1

**Study:** Does conversational LLM refinement improve k-means clustering of conflict events?  
**Pre-registration:** `docs/study_design.md` (locked at first run log entry)  
**Stack:** Python 3.11+, scikit-learn, Anthropic API, pandas, jsonlines

---

## Repo Structure

```
conv-clustering/
├── README.md
├── requirements.txt
├── config/                        # One YAML per experimental condition
│   ├── condition_A_F1.yaml        # Baseline, location-only features
│   ├── condition_A_F2.yaml        # Baseline, full features
│   ├── condition_B_F1.yaml        # Human conversational, location-only
│   ├── condition_B_F2.yaml        # Human conversational, full features
│   ├── condition_C_F1.yaml        # LLM oracle, location-only
│   ├── condition_C_F2.yaml        # LLM oracle, full features
│   ├── model.yaml                 # Pinned LLM version (single source of truth)
│   ├── toy.yaml                   # Smoke-test config (no data file, no API key needed)
│   └── experimenter_order.txt     # Pre-drawn seed-to-experimenter assignment (Condition B)
├── data/
│   ├── sample_seed42.csv          # Locked 2,000-event sample (committed once, never redrawn)
│   └── clean.py                   # Filter + sample script (Person 3)
├── prompts/                       # Versioned prompt files — NOT embedded in code
│   ├── interpreter.md             # LLM interpreter prompt (Person 1 to finalise)
│   └── oracle_user.md             # LLM oracle-as-user prompt (Person 1 to finalise)
├── src/                           # Library modules
│   ├── __init__.py
│   ├── features.py                # F1 / F2 feature encoding
│   ├── cluster.py                 # k-means wrapper, silhouette, Davies-Bouldin
│   ├── llm.py                     # Anthropic API calls with retry/backoff
│   ├── loop.py                    # Conversational turn loop (Conditions B & C)
│   └── logger.py                  # Structured JSONL logging
├── scripts/
│   ├── run_experiment.py          # Main entry point
│   └── check_integrity.py         # Post-run completeness check
├── notebooks/
│   └── analysis.ipynb             # Pre-specified analysis (reads from run_log.jsonl)
├── runs/
│   └── run_log.jsonl              # Append-only experiment log (pre-registration lock point)
└── docs/
    ├── study_plan.md
    ├── study_design.md
    ├── related_work.md
    ├── data_provenance.md
    └── rating_instrument_link.txt
```

---

## Setup

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

---

## Reproduce the Headline Result (Toy Example)

Run this to verify the pipeline works end-to-end with no data file and no API key:

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

Silhouette values will vary slightly by platform but should be in the range 0.35–0.45.

---

## Run a Full Experimental Condition

```bash
# Condition A, F2 features, seeds 0–29 (no API key needed)
python scripts/run_experiment.py --config config/condition_A_F2.yaml --seeds 0 29

# Condition C, F2 features, seeds 0–29 (requires ANTHROPIC_API_KEY)
python scripts/run_experiment.py --config config/condition_C_F2.yaml --seeds 0 29
```

Each run appends one JSONL record to `runs/run_log.jsonl`.

---

## Check Run Completeness Before Analysis

Always run this before opening `notebooks/analysis.ipynb`:

```bash
python scripts/check_integrity.py --log runs/run_log.jsonl
```

**Example output:**
```
Condition A / F1 : 30 intended, 30 complete,  0 errors. ✓
Condition A / F2 : 30 intended, 30 complete,  0 errors. ✓
Condition B / F1 : 30 intended, 28 complete,  2 refused. ⚠ Missing seeds: [14, 22]
Condition B / F2 : 30 intended, 30 complete,  0 errors. ✓
Condition C / F1 : 30 intended, 30 complete,  0 errors. ✓
Condition C / F2 : 30 intended, 30 complete,  0 errors. ✓
```

Refused runs (Claude safety filter on conflict data) are logged with `status: "refused"` and reported as data loss in the final analysis — they are never silently dropped.

---

## Log Format

Each record in `runs/run_log.jsonl` has the following schema:

```json
{
  "run_id": "B_F2_seed007",
  "condition": "B",
  "feature_set": "F2",
  "K": 8,
  "seed": 7,
  "config_hash": "a3f9c2d",
  "prompt_hashes": {
    "interpreter": "b7e1a44",
    "oracle_user": null
  },
  "model_version": "claude-sonnet-4-20250514",
  "timestamp_start": "2026-05-20T14:32:11Z",
  "timestamp_end": "2026-05-20T14:34:03Z",
  "silhouette_final": 0.312,
  "davies_bouldin_final": 1.84,
  "n_turns_completed": 2,
  "turns": [
    {
      "turn": 1,
      "instruction": "separate by actor",
      "parsed_params": {"weight_actor": 2.0},
      "silhouette": 0.287,
      "db_index": 1.91,
      "timestamp": "2026-05-20T14:32:45Z",
      "llm_tokens_used": 412
    }
  ],
  "errors": [],
  "status": "complete"
}
```

`status` values: `"complete"` | `"refused"` | `"error"` | `"partial"`

---

## Pre-Registration Note

`runs/run_log.jsonl` is empty until the first experimental run. The moment the first record is appended, `docs/study_design.md` is considered locked. Any subsequent change to the analysis plan must be recorded as a numbered amendment in `docs/study_design.md §12`.

**Do not run any condition before:**
1. `prompts/interpreter.md` contains the real prompt (not the placeholder)
2. `prompts/oracle_user.md` contains the real prompt (Conditions B/C only)
3. `data/sample_seed42.csv` is committed and its MD5 recorded in `docs/data_provenance.md`
4. `docs/study_design.md` v0.2 is committed (K confirmed by elbow method)
