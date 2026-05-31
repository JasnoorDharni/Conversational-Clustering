#!/usr/bin/env python3
"""
scripts/reproduce_clusters.py
------------------------------
Reproduce cluster assignments from run_log.jsonl and generate
the 20 cluster-pair descriptions needed for the H3 human rating task.

Usage
-----
# List all reproducible runs
python scripts/reproduce_clusters.py --list

# Reproduce one run and print its cluster description
python scripts/reproduce_clusters.py --run-id A_F2_seed005

# Select the 20 H3 pairs and save descriptions to runs/h3_pairs/
python scripts/reproduce_clusters.py --generate-pairs

How reproduction works
----------------------
- Condition A: k-means with default weights (all 1.0).
- Condition B/C: k-means with the parsed_params from the *last completed turn*
  in the log. This reconstructs the exact feature matrix the final cluster
  assignment was produced from, since k-means is deterministic given
  (weights, seed, K).

Output format (--generate-pairs)
----------------------------------
runs/h3_pairs/
    pairs.json          — list of 20 pair dicts (metadata)
    pair_01_left.txt    — cluster description for the left side
    pair_01_right.txt   — cluster description for the right side
    ...
    pair_20_left.txt
    pair_20_right.txt
    summary.txt         — one-line description of each pair for review

H3 sampling plan (study_design.md §5.3)
-----------------------------------------
5 pairs: A/F2 vs B/F2  (same seed)  — human refinement perceptible?
5 pairs: A/F2 vs C/F2  (same seed)  — oracle refinement perceptible?
5 pairs: B/F2 vs C/F2  (same seed)  — human vs oracle differ?
5 pairs: A/F1 vs A/F2  (same seed)  — feature richness perceptible?
Seeds drawn by stratified random sampling; no seed appears more than once.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

# Allow running from repo root
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.cluster import run_kmeans, summarise_clusters
from src.features import build_feature_matrix, default_weights


# ── Constants ─────────────────────────────────────────────────────────────

LOG_PATH    = Path("runs/run_log.jsonl")
SAMPLE_PATH = Path("data/sample_seed42.csv")
PAIRS_DIR   = Path("runs/h3_pairs")

H3_GROUPS = [
    ("A", "F2", "B", "F2", "A vs B / F2 — human refinement perceptible?"),
    ("A", "F2", "C", "F2", "A vs C / F2 — oracle refinement perceptible?"),
    ("B", "F2", "C", "F2", "B vs C / F2 — human vs oracle differ?"),
    ("A", "F1", "A", "F2", "A/F1 vs A/F2 — feature richness perceptible?"),
]
N_PER_GROUP  = 5
SAMPLING_SEED = 42


# ── Log loading ───────────────────────────────────────────────────────────

def load_log(log_path: Path = LOG_PATH) -> list[dict]:
    if not log_path.exists():
        print(f"[error] Log file not found: {log_path}", file=sys.stderr)
        sys.exit(1)
    return [json.loads(line) for line in log_path.read_text().splitlines() if line.strip()]


def find_run(records: list[dict], condition: str, feature_set: str, seed: int) -> dict | None:
    """Return the first complete run matching (condition, feature_set, seed)."""
    for r in records:
        if (r.get("condition") == condition
                and r.get("feature_set") == feature_set
                and r.get("seed") == seed
                and r.get("status") == "complete"):
            return r
    return None


# ── Cluster reproduction ──────────────────────────────────────────────────

def get_final_weights(run: dict) -> dict[str, float]:
    """
    Extract the feature weights used for the final cluster assignment.
    - Condition A: default weights (all 1.0).
    - Condition B/C: parsed_params from the last completed turn.
    """
    condition = run["condition"]
    fs = run["feature_set"]

    if condition == "A":
        return default_weights(fs)

    turns = run.get("turns", [])
    if not turns:
        print(f"  [warn] No turns found for {run['run_id']} — using default weights.")
        return default_weights(fs)

    # Last turn's parsed_params
    last_params = turns[-1].get("parsed_params", {})
    w = default_weights(fs)
    w.update({k: float(v) for k, v in last_params.items()})
    return w


def reproduce_run(run: dict, df_sample: pd.DataFrame) -> tuple[np.ndarray, str]:
    """
    Reproduce the cluster assignment for a run record.

    Returns
    -------
    labels      : np.ndarray, shape (n_events,)
    description : str — human-readable cluster summary
    """
    fs     = run["feature_set"]
    K      = run["K"]
    seed   = run["seed"]
    weights = get_final_weights(run)

    X, _ = build_feature_matrix(df_sample, fs, weights=weights)
    result = run_kmeans(X, K, seed)
    description = summarise_clusters(df_sample, result.labels, K)
    return result.labels, description


# ── Pair description formatting ───────────────────────────────────────────

def format_pair_description(run: dict, description: str) -> str:
    """Format a cluster description for display to a human rater."""
    header = (
        f"Run:        {run['run_id']}\n"
        f"Condition:  {run['condition']}  "
        f"({'Baseline' if run['condition']=='A' else 'Human conversational' if run['condition']=='B' else 'LLM oracle'})\n"
        f"Features:   {run['feature_set']}  "
        f"({'Location only' if run['feature_set']=='F1' else 'Full features'})\n"
        f"Seed:       {run['seed']}\n"
        f"Silhouette: {run['silhouette_final']:.4f}\n"
        f"{'─' * 60}\n"
    )
    return header + description


# ── Pair selection ────────────────────────────────────────────────────────

def select_h3_pairs(
    records: list[dict],
    n_per_group: int = N_PER_GROUP,
    sampling_seed: int = SAMPLING_SEED,
) -> list[dict[str, Any]]:
    """
    Select 20 cluster pairs for H3 following study_design.md §5.3.
    Returns a list of pair dicts with metadata.
    Raises ValueError if not enough complete runs are available.
    """
    rng = random.Random(sampling_seed)
    pairs = []
    used_seeds: set[int] = set()

    for cond_l, fs_l, cond_r, fs_r, description in H3_GROUPS:
        # Find seeds that have BOTH runs complete
        seeds_l = {r["seed"] for r in records
                   if r["condition"] == cond_l and r["feature_set"] == fs_l
                   and r["status"] == "complete"}
        seeds_r = {r["seed"] for r in records
                   if r["condition"] == cond_r and r["feature_set"] == fs_r
                   and r["status"] == "complete"}

        eligible = sorted((seeds_l & seeds_r) - used_seeds)
        if len(eligible) < n_per_group:
            raise ValueError(
                f"Not enough paired seeds for group '{description}'.\n"
                f"  Need {n_per_group}, found {len(eligible)} eligible.\n"
                f"  Complete the missing runs before generating pairs."
            )

        chosen = rng.sample(eligible, n_per_group)
        used_seeds.update(chosen)

        for seed in chosen:
            pairs.append({
                "group":       description,
                "seed":        seed,
                "left":        {"condition": cond_l, "feature_set": fs_l},
                "right":       {"condition": cond_r, "feature_set": fs_r},
            })

    return pairs


# ── Main actions ──────────────────────────────────────────────────────────

def action_list(records: list[dict]) -> None:
    """Print a summary of all complete runs grouped by condition."""
    print(f"{'Condition':<12} {'Feature':<8} {'Seeds complete'}")
    print("─" * 50)
    for cond in ("A", "B", "C"):
        for fs in ("F1", "F2"):
            done = sorted(
                r["seed"] for r in records
                if r["condition"] == cond and r["feature_set"] == fs
                and r["status"] == "complete"
            )
            missing = sorted(set(range(30)) - set(done))
            status = "✅" if len(done) == 30 else "⏳"
            print(f"{status} {cond:<11} {fs:<8} {len(done)}/30", end="")
            if missing:
                print(f"  — missing: {missing}", end="")
            print()


def action_reproduce_run(run_id: str, records: list[dict],
                         df_sample: pd.DataFrame) -> None:
    """Reproduce and print the cluster description for one run."""
    run = next((r for r in records if r.get("run_id") == run_id), None)
    if run is None:
        print(f"[error] run_id '{run_id}' not found in log.", file=sys.stderr)
        sys.exit(1)
    if run["status"] != "complete":
        print(f"[error] Run '{run_id}' has status '{run['status']}', not 'complete'.",
              file=sys.stderr)
        sys.exit(1)

    print(f"Reproducing: {run_id}")
    labels, description = reproduce_run(run, df_sample)
    print(format_pair_description(run, description))


def action_generate_pairs(records: list[dict], df_sample: pd.DataFrame) -> None:
    """Select 20 H3 pairs, reproduce their clusters, and save to runs/h3_pairs/."""
    print("Selecting 20 H3 pairs (study_design.md §5.3)...")
    try:
        pairs = select_h3_pairs(records)
    except ValueError as e:
        print(f"[error] {e}", file=sys.stderr)
        sys.exit(1)

    PAIRS_DIR.mkdir(parents=True, exist_ok=True)
    summary_lines = []

    for i, pair in enumerate(pairs, start=1):
        seed = pair["seed"]
        run_l = find_run(records, pair["left"]["condition"],
                         pair["left"]["feature_set"], seed)
        run_r = find_run(records, pair["right"]["condition"],
                         pair["right"]["feature_set"], seed)

        if run_l is None or run_r is None:
            print(f"[warn] Could not find runs for pair {i} (seed={seed}) — skipping.")
            continue

        print(f"  Pair {i:02d}: {run_l['run_id']} vs {run_r['run_id']}")

        _, desc_l = reproduce_run(run_l, df_sample)
        _, desc_r = reproduce_run(run_r, df_sample)

        left_txt  = format_pair_description(run_l, desc_l)
        right_txt = format_pair_description(run_r, desc_r)

        (PAIRS_DIR / f"pair_{i:02d}_left.txt").write_text(left_txt,  encoding="utf-8")
        (PAIRS_DIR / f"pair_{i:02d}_right.txt").write_text(right_txt, encoding="utf-8")

        summary_lines.append(
            f"Pair {i:02d}  [{pair['group']}]\n"
            f"  LEFT : {run_l['run_id']}  sil={run_l['silhouette_final']:.4f}\n"
            f"  RIGHT: {run_r['run_id']}  sil={run_r['silhouette_final']:.4f}\n"
        )

    # Save pair metadata as JSON (used by analysis notebook for H3)
    pairs_json_path = PAIRS_DIR / "pairs.json"
    pairs_json_path.write_text(json.dumps(pairs, indent=2), encoding="utf-8")

    # Save human-readable summary
    summary_path = PAIRS_DIR / "summary.txt"
    summary_path.write_text(
        "H3 Cluster Pairs — Summary\n"
        "=" * 60 + "\n\n"
        + "\n".join(summary_lines),
        encoding="utf-8",
    )

    print(f"\n✅ {len(pairs)} pairs generated in {PAIRS_DIR}/")
    print(f"   pairs.json        — metadata (used by analysis notebook)")
    print(f"   pair_NN_left.txt  — left cluster description for each pair")
    print(f"   pair_NN_right.txt — right cluster description for each pair")
    print(f"   summary.txt       — one-line overview for review")
    print(
        "\nNext steps:\n"
        "  1. Review summary.txt to confirm pair selection is sensible.\n"
        "  2. Create Google Form with these 20 pairs (forced choice).\n"
        "  3. Commit the Form link to docs/rating_instrument_link.txt.\n"
        "  4. Share with 5–8 raters.\n"
        "  5. Save responses to runs/human_ratings.csv and runs/oracle_ratings.csv."
    )


# ── CLI ───────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Reproduce cluster assignments and generate H3 rating pairs."
    )
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--list", action="store_true",
                       help="List all complete runs in the log.")
    group.add_argument("--run-id", metavar="RUN_ID",
                       help="Reproduce one run and print its cluster description.")
    group.add_argument("--generate-pairs", action="store_true",
                       help="Select 20 H3 pairs and save descriptions to runs/h3_pairs/.")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    records = load_log()

    if args.list:
        action_list(records)
        return

    # Load sample data (needed for reproduction and pair generation)
    if not SAMPLE_PATH.exists():
        print(f"[error] Sample file not found: {SAMPLE_PATH}", file=sys.stderr)
        sys.exit(1)
    df_sample = pd.read_csv(SAMPLE_PATH, low_memory=False)
    print(f"Sample loaded: {len(df_sample):,} events from {SAMPLE_PATH}")

    if args.run_id:
        action_reproduce_run(args.run_id, records, df_sample)
    elif args.generate_pairs:
        action_generate_pairs(records, df_sample)


if __name__ == "__main__":
    main()
