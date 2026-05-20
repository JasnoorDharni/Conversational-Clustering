#!/usr/bin/env python3
"""
scripts/run_experiment.py
--------------------------
Main entry point for the conversational clustering experiment.

Usage
-----
# Full run: all 30 seeds for one condition/feature-set cell
python scripts/run_experiment.py --config config/condition_A_F2.yaml --seeds 0 29

# Single seed (debugging)
python scripts/run_experiment.py --config config/condition_B_F2.yaml --seeds 7 7

# Toy smoke test (no data file, no API key needed)
python scripts/run_experiment.py --config config/toy.yaml --seeds 0 4

What this script does
---------------------
1. Load and validate the YAML config.
2. Check pre-registration gate: prompts must NOT be placeholders for B/C.
3. Load the dataset (or generate toy data).
4. For each seed in [seed_start, seed_end]:
   a. Override config['seed'] with current seed.
   b. Build feature matrix (F1 or F2).
   c. Run baseline k-means (Condition A terminates here).
   d. For B/C: run conversational loop.
   e. Log the result.
5. Print integrity summary after all seeds complete.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd
import yaml

# Allow running as `python scripts/run_experiment.py` from repo root
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.cluster import run_kmeans, summarise_clusters
from src.features import build_feature_matrix, toy_dataframe
from src.logger import RunLogger
from src.loop import run_loop


# ── CLI ───────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run one experimental condition.")
    p.add_argument("--config", required=True, help="Path to condition YAML config.")
    p.add_argument(
        "--seeds", nargs=2, type=int, metavar=("START", "END"),
        default=[0, 29],
        help="Inclusive seed range, e.g. --seeds 0 29 (default) or --seeds 7 7.",
    )
    return p.parse_args()


# ── Config loading ────────────────────────────────────────────────────────

def load_config(config_path: str) -> dict:
    p = Path(config_path)
    if not p.exists():
        print(f"[error] Config file not found: {p}", file=sys.stderr)
        sys.exit(1)
    with open(p) as f:
        cfg = yaml.safe_load(f)
    cfg["_config_path"] = str(p)   # stored for hash in logger
    required = ["condition", "feature_set", "K", "max_turns", "log_path", "model"]
    for key in required:
        if key not in cfg:
            print(f"[error] Config missing required key: {key!r}", file=sys.stderr)
            sys.exit(1)
    return cfg


# ── Pre-registration gate ─────────────────────────────────────────────────

def check_prompt_readiness(cfg: dict) -> None:
    """Fail loud if prompts are still placeholders for B/C conditions."""
    if cfg["condition"] not in ("B", "C"):
        return
    for key in ("interpreter_prompt", "oracle_prompt"):
        path = cfg.get(key)
        if not path:
            continue
        p = Path(path)
        if not p.exists():
            print(
                f"[error] Prompt file missing: {p}\n"
                "Person 1 must write and commit the real prompt before running "
                f"Condition {cfg['condition']}.",
                file=sys.stderr,
            )
            sys.exit(1)
        if "YOU ARE A PLACEHOLDER" in p.read_text(encoding="utf-8"):
            print(
                f"[error] Prompt file {p} is still a placeholder.\n"
                "Person 1 must replace it before any B/C run.",
                file=sys.stderr,
            )
            sys.exit(1)


# ── Dataset loading ───────────────────────────────────────────────────────

def load_data(cfg: dict) -> pd.DataFrame:
    data_path = cfg.get("data_path", "")
    if data_path == "TOY":
        n   = cfg.get("toy_n_events", 120)
        seed = cfg.get("toy_seed", 0)
        print(f"[toy] Generating synthetic dataset (n={n}, seed={seed})")
        return toy_dataframe(n=n, seed=seed)

    p = Path(data_path)
    if not p.exists():
        print(
            f"[error] Dataset not found: {p}\n"
            "Has Person 3 committed data/sample_seed42.csv?",
            file=sys.stderr,
        )
        sys.exit(1)
    df = pd.read_csv(p, low_memory=False)
    print(f"Loaded {len(df):,} events from {p}")
    return df


# ── Single run ────────────────────────────────────────────────────────────

def run_one(cfg: dict, df: pd.DataFrame, seed: int, client) -> str:
    """
    Execute one run (one seed). Returns the status string.
    Appends one record to run_log.jsonl regardless of outcome.
    """
    cfg = {**cfg, "seed": seed}   # override seed without mutating original

    condition   = cfg["condition"]
    feature_set = cfg["feature_set"]
    K           = cfg["K"]
    is_toy      = cfg.get("data_path") == "TOY"

    # Prompt paths (None for Condition A)
    prompt_paths = {}
    if "interpreter_prompt" in cfg:
        prompt_paths["interpreter"] = cfg["interpreter_prompt"]
    if "oracle_prompt" in cfg:
        prompt_paths["oracle_user"] = cfg["oracle_prompt"]

    label = f"{'[toy] ' if is_toy else ''}Condition {condition} | {feature_set} | K={K} | seed={seed}"

    with RunLogger(cfg["log_path"], cfg, prompt_paths) as run:
        try:
            # ── Build features & baseline cluster ────────────────────────
            X, col_names = build_feature_matrix(df, feature_set)
            baseline = run_kmeans(X, K, seed)

            print(
                f"  {label}  "
                f"baseline silhouette={baseline.silhouette:.4f}  "
                f"db={baseline.davies_bouldin:.4f}"
            )

            if condition != "A":
                # Print cluster summary for the experimenter (Condition B)
                # or for reference (Condition C); not shown to human in B
                print(summarise_clusters(df, baseline.labels, K))

            # ── Conversational loop (no-op for Condition A) ───────────────
            final = run_loop(df, cfg, client, run, baseline, col_names)

            run.finish(final)
            print(f"  ✓ seed={seed}  final silhouette={final.silhouette:.4f}")
            return "complete"

        except Exception as exc:
            # run.__exit__ will call run.fail() automatically
            print(f"  ✗ seed={seed}  ERROR: {exc}", file=sys.stderr)
            raise   # re-raise so __exit__ logs it


# ── Integrity summary ─────────────────────────────────────────────────────

def print_integrity(log_path: str, condition: str, feature_set: str,
                    seed_start: int, seed_end: int) -> None:
    import jsonlines

    intended = set(range(seed_start, seed_end + 1))
    complete = set()
    refused  = set()
    errors   = set()

    p = Path(log_path)
    if not p.exists():
        print("[integrity] No log file found — no runs completed.")
        return

    with jsonlines.open(p) as reader:
        for rec in reader:
            if rec.get("condition") == condition and rec.get("feature_set") == feature_set:
                seed = rec.get("seed")
                status = rec.get("status", "unknown")
                if status == "complete":
                    complete.add(seed)
                elif status == "refused":
                    refused.add(seed)
                else:
                    errors.add(seed)

    missing = intended - complete - refused - errors
    tag = "✓" if not missing and not refused and not errors else "⚠"

    print(
        f"\n[integrity] Condition {condition} / {feature_set}: "
        f"{len(intended)} intended, "
        f"{len(complete)} complete, "
        f"{len(refused)} refused, "
        f"{len(errors)} errors.  {tag}"
    )
    if refused:
        print(f"  Refused seeds (data loss — report in paper): {sorted(refused)}")
    if errors:
        print(f"  Error seeds (investigate before analysis): {sorted(errors)}")
    if missing:
        print(f"  Missing seeds (never ran): {sorted(missing)}")
    if not missing and not refused and not errors:
        print("  All runs complete. Safe to run analysis notebook.")


# ── Main ──────────────────────────────────────────────────────────────────

def main() -> None:
    args  = parse_args()
    cfg   = load_config(args.config)
    seed_start, seed_end = args.seeds[0], args.seeds[1]

    check_prompt_readiness(cfg)

    df = load_data(cfg)

    # Anthropic client — only needed for B/C
    client = None
    if cfg["condition"] in ("B", "C"):
        import anthropic
        client = anthropic.Anthropic()   # reads ANTHROPIC_API_KEY from env

    is_toy = cfg.get("data_path") == "TOY"
    n_seeds = seed_end - seed_start + 1
    print(
        f"\n{'[toy] ' if is_toy else ''}"
        f"Condition {cfg['condition']} | {cfg['feature_set']} | "
        f"K={cfg['K']} | {n_seeds} seeds ({seed_start}–{seed_end})\n"
    )

    for seed in range(seed_start, seed_end + 1):
        try:
            run_one(cfg, df, seed, client)
        except Exception:
            # Already logged by RunLogger; continue to next seed
            pass

    print_integrity(
        cfg["log_path"], cfg["condition"], cfg["feature_set"],
        seed_start, seed_end,
    )


if __name__ == "__main__":
    main()
