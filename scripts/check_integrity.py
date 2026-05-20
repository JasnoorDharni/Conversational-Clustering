#!/usr/bin/env python3
"""
scripts/check_integrity.py
---------------------------
Post-run completeness check. Run this BEFORE opening analysis.ipynb.

Usage
-----
python scripts/check_integrity.py --log runs/run_log.jsonl

Reads run_log.jsonl and reports, for each (condition × feature_set) cell:
  - How many runs were intended (based on what's in the log)
  - How many completed successfully
  - How many were refused (Claude safety filter — data loss, must be reported)
  - How many errored
  - Which seeds are missing

Exit code 0 if all cells are complete, 1 otherwise.
The analysis notebook should not be run if exit code is 1.
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

import jsonlines


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Check experiment log completeness.")
    p.add_argument(
        "--log", default="runs/run_log.jsonl",
        help="Path to JSONL run log (default: runs/run_log.jsonl).",
    )
    p.add_argument(
        "--expected-seeds", type=int, default=30,
        help="Expected number of seeds per cell (default: 30).",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    log_path = Path(args.log)

    if not log_path.exists():
        print(f"[error] Log file not found: {log_path}", file=sys.stderr)
        print("No runs have been executed yet.")
        sys.exit(1)

    # Collect records per cell
    cells: dict[tuple, dict[str, set]] = defaultdict(
        lambda: {"complete": set(), "refused": set(), "error": set(), "partial": set()}
    )

    with jsonlines.open(log_path) as reader:
        for rec in reader:
            cond = rec.get("condition", "?")
            fs   = rec.get("feature_set", "?")
            seed = rec.get("seed")
            status = rec.get("status", "unknown")
            key = (cond, fs)
            if status in cells[key]:
                cells[key][status].add(seed)
            else:
                cells[key]["error"].add(seed)

    if not cells:
        print("Log file is empty — no runs recorded.")
        sys.exit(1)

    print(f"\nIntegrity report — {log_path}\n{'─' * 60}")

    all_ok = True
    expected = set(range(args.expected_seeds))

    for (cond, fs), counts in sorted(cells.items()):
        complete = counts["complete"]
        refused  = counts["refused"]
        errors   = counts["error"] | counts["partial"]
        seen     = complete | refused | errors
        missing  = expected - seen if len(seen) > 0 else set()

        ok = len(refused) == 0 and len(errors) == 0 and len(missing) == 0
        tag = "✓" if ok else "⚠"

        print(
            f"Condition {cond} / {fs} : "
            f"{args.expected_seeds} intended, "
            f"{len(complete):2d} complete, "
            f"{len(refused):2d} refused, "
            f"{len(errors):2d} errors.  {tag}"
        )

        if refused:
            print(f"   ⚠  Refused seeds (report as data loss in paper): "
                  f"{sorted(refused)}")
        if errors:
            print(f"   ✗  Error seeds (investigate before analysis):     "
                  f"{sorted(errors)}")
        if missing:
            print(f"   ?  Missing seeds (never ran):                     "
                  f"{sorted(missing)}")

        if not ok:
            all_ok = False

    print()
    if all_ok:
        print("All cells complete. Safe to run notebooks/analysis.ipynb.")
    else:
        print("Some cells are incomplete. Resolve issues before running analysis.")
        print("Refused runs must be reported as data loss — do NOT re-run them.")

    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
