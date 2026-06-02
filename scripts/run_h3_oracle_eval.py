#!/usr/bin/env python
"""
Run H3 oracle evaluation with Anthropic Claude.

Inputs:
  - prompts/oracle_eval.md
  - runs/h3_pair_metadata.csv
  - runs/h3_pairs/pair_XX_left.txt
  - runs/h3_pairs/pair_XX_right.txt

Outputs:
  - runs/h3/oracle/ratings_long.csv
  - runs/h3/oracle/ratings_raw.jsonl
  - runs/h3/oracle/position_bias_summary.csv
  - optional prompt audit files in runs/h3/oracle/prompt_audits/

PowerShell:
  python scripts/run_h3_oracle_eval.py --orders original swapped --overwrite
"""

from __future__ import annotations

import argparse
import json
import os
import re
import time
from pathlib import Path

import pandas as pd

from h3_utils import EXPECTED_PAIR_COUNT, ensure_can_write, validate_pair_text_files


HEADER_PREFIXES_TO_REMOVE = ("Run:", "Condition:", "Features:", "Seed:", "Silhouette:")
JSON_CHOICE_RE = re.compile(r'"choice"\s*:\s*"([AB])"', re.IGNORECASE)
FALLBACK_CHOICE_RE = re.compile(r"\b(?:OPTION\s+)?([AB])\b", re.IGNORECASE)


def load_prompt_template(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Oracle prompt not found: {path}")

    text = path.read_text(encoding="utf-8")
    for placeholder in ("{option_a}", "{option_b}"):
        if placeholder not in text:
            raise ValueError(f"Prompt must contain {placeholder}: {path}")
    return text


def sanitize_option_text(text: str) -> str:
    kept_lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(HEADER_PREFIXES_TO_REMOVE):
            continue
        kept_lines.append(line)
    sanitized = "\n".join(kept_lines).strip()
    if not sanitized:
        raise ValueError("Sanitized option text became empty.")
    return sanitized


def load_pair_text(pair_dir: Path, pair_id: str, side: str) -> str:
    path = pair_dir / f"{pair_id}_{side}.txt"
    if not path.exists():
        raise FileNotFoundError(f"Missing pair description: {path}")
    return sanitize_option_text(path.read_text(encoding="utf-8"))


def map_display_order(row: pd.Series, order: str) -> dict[str, str]:
    if order == "original":
        displayed_a_side = row["option_A_side"]
        displayed_b_side = row["option_B_side"]
        displayed_a_run_id = row["option_A_run_id"]
        displayed_b_run_id = row["option_B_run_id"]
        displayed_a_condition = row["option_A_condition"]
        displayed_b_condition = row["option_B_condition"]
        displayed_a_feature_set = row["option_A_feature_set"]
        displayed_b_feature_set = row["option_B_feature_set"]
    elif order == "swapped":
        displayed_a_side = row["option_B_side"]
        displayed_b_side = row["option_A_side"]
        displayed_a_run_id = row["option_B_run_id"]
        displayed_b_run_id = row["option_A_run_id"]
        displayed_a_condition = row["option_B_condition"]
        displayed_b_condition = row["option_A_condition"]
        displayed_a_feature_set = row["option_B_feature_set"]
        displayed_b_feature_set = row["option_A_feature_set"]
    else:
        raise ValueError(f"Unsupported order: {order}")

    return {
        "displayed_A_side": displayed_a_side,
        "displayed_B_side": displayed_b_side,
        "displayed_A_run_id": displayed_a_run_id,
        "displayed_B_run_id": displayed_b_run_id,
        "displayed_A_condition": displayed_a_condition,
        "displayed_B_condition": displayed_b_condition,
        "displayed_A_feature_set": displayed_a_feature_set,
        "displayed_B_feature_set": displayed_b_feature_set,
    }


def parse_oracle_response(text: str) -> dict[str, object]:
    cleaned = text.strip()

    try:
        payload = json.loads(cleaned)
        if not isinstance(payload, dict):
            raise ValueError("JSON response was not an object.")
        choice = str(payload.get("choice", "")).strip().upper()
        if choice not in {"A", "B"}:
            raise ValueError(f"Invalid JSON choice: {choice!r}")

        confidence = payload.get("confidence")
        if confidence is None:
            confidence_value = None
        else:
            confidence_value = float(confidence)
            if not 0.0 <= confidence_value <= 1.0:
                raise ValueError(f"Confidence out of range: {confidence_value}")

        reason = str(payload.get("reason", "")).strip()
        return {
            "choice": choice,
            "confidence": confidence_value,
            "reason": reason,
            "parsed_via": "json",
        }
    except (json.JSONDecodeError, TypeError, ValueError):
        match = JSON_CHOICE_RE.search(cleaned) or FALLBACK_CHOICE_RE.search(cleaned)
        if not match:
            raise ValueError(f"Could not parse oracle response into A/B: {text!r}")
        return {
            "choice": match.group(1).upper(),
            "confidence": None,
            "reason": "",
            "parsed_via": "regex_fallback",
        }


def call_claude(client, anthropic_module, model: str, prompt: str, temperature: float, max_retries: int = 3) -> tuple[str, int]:
    for attempt in range(max_retries):
        try:
            message = client.messages.create(
                model=model,
                max_tokens=200,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
            )
            text = "".join(
                block.text for block in message.content if getattr(block, "type", None) == "text"
            )
            tokens = 0
            if getattr(message, "usage", None) is not None:
                tokens = int(
                    getattr(message.usage, "input_tokens", 0)
                    + getattr(message.usage, "output_tokens", 0)
                )
            return text, tokens
        except (
            anthropic_module.RateLimitError,
            anthropic_module.APITimeoutError,
            anthropic_module.APIConnectionError,
        ):
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** (attempt + 1))

    raise RuntimeError("Unexpected Claude retry loop exit.")


def order_consensus(values: list[str]) -> str:
    if not values:
        return ""
    counts = pd.Series(values).value_counts()
    if len(counts) > 1 and counts.iloc[0] == counts.iloc[1]:
        return ""
    return str(counts.index[0])


def build_position_bias_summary(long_df: pd.DataFrame, out_path: Path) -> None:
    pair_rows: list[dict[str, object]] = []

    for pair_id, pair_df in long_df.groupby("pair_id"):
        original_df = pair_df.loc[pair_df["order"] == "original"]
        swapped_df = pair_df.loc[pair_df["order"] == "swapped"]

        original_display_choice = order_consensus(original_df["choice_displayed"].tolist())
        swapped_display_choice = order_consensus(swapped_df["choice_displayed"].tolist())
        original_side = order_consensus(original_df["chosen_side"].tolist())
        swapped_side = order_consensus(swapped_df["chosen_side"].tolist())

        same_underlying = bool(original_side and swapped_side and original_side == swapped_side)
        same_display = bool(
            original_display_choice
            and swapped_display_choice
            and original_display_choice == swapped_display_choice
        )
        position_bias_flag = bool(same_display and not same_underlying)

        pair_rows.append(
            {
                "pair_id": pair_id,
                "original_display_choice": original_display_choice,
                "swapped_display_choice": swapped_display_choice,
                "original_chosen_side": original_side,
                "swapped_chosen_side": swapped_side,
                "same_underlying_choice_after_swap": same_underlying,
                "same_display_label_after_swap": same_display,
                "position_bias_flag": position_bias_flag,
            }
        )

    summary_df = pd.DataFrame(pair_rows).sort_values("pair_id")
    aggregate_row = {
        "pair_id": "__aggregate__",
        "original_display_choice": f"A:{int((long_df['choice_displayed'] == 'A').sum())};B:{int((long_df['choice_displayed'] == 'B').sum())}",
        "swapped_display_choice": "",
        "original_chosen_side": f"consistent_underlying_after_swap:{int(summary_df['same_underlying_choice_after_swap'].sum())}",
        "swapped_chosen_side": f"same_display_after_swap:{int(summary_df['same_display_label_after_swap'].sum())}",
        "same_underlying_choice_after_swap": int(summary_df["same_underlying_choice_after_swap"].sum()),
        "same_display_label_after_swap": int(summary_df["same_display_label_after_swap"].sum()),
        "position_bias_flag": int(summary_df["position_bias_flag"].sum()),
    }
    summary_df = pd.concat([summary_df, pd.DataFrame([aggregate_row])], ignore_index=True)
    summary_df.to_csv(out_path, index=False)


def maybe_write_prompt_audits(
    prompt_jobs: list[dict[str, object]],
    prompt_dir: Path,
    overwrite: bool,
) -> int:
    if not prompt_jobs:
        return 0

    prompt_paths = [prompt_dir / f"{job['pair_id']}_{job['order']}_{job['trial_id']}_prompt.md" for job in prompt_jobs]
    ensure_can_write(prompt_paths, overwrite=overwrite)

    written = 0
    for job, prompt_path in zip(prompt_jobs, prompt_paths):
        prompt_path.write_text(str(job["prompt"]), encoding="utf-8")
        job["prompt_path"] = str(prompt_path)
        written += 1
    return written


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", default="prompts/oracle_eval.md")
    parser.add_argument("--pair-dir", default="runs/h3_pairs")
    parser.add_argument("--metadata", default="runs/h3/metadata.csv")
    parser.add_argument("--prompt-out-dir", default="runs/h3/oracle/prompt_audits")
    parser.add_argument("--out-long", default="runs/h3/oracle/ratings_long.csv")
    parser.add_argument("--raw-out", default="runs/h3/oracle/ratings_raw.jsonl")
    parser.add_argument("--position-bias-out", default="runs/h3/oracle/position_bias_summary.csv")
    parser.add_argument("--orders", nargs="+", choices=["original", "swapped"], default=["original"])
    parser.add_argument("--model", default="claude-sonnet-4-5")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--repetitions", type=int, default=1)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--write-prompt-audits",
        action="store_true",
        help="Write per-trial prompt audit files. Dry-run enables this automatically.",
    )
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    if args.repetitions < 1:
        raise ValueError("--repetitions must be at least 1.")

    prompt_path = Path(args.prompt)
    pair_dir = Path(args.pair_dir)
    metadata_path = Path(args.metadata)
    prompt_out_dir = Path(args.prompt_out_dir)
    out_long = Path(args.out_long)
    raw_out = Path(args.raw_out)
    position_bias_out = Path(args.position_bias_out)

    if not metadata_path.exists():
        raise FileNotFoundError(f"Missing H3 metadata CSV: {metadata_path}")

    prompt_template = load_prompt_template(prompt_path)
    validate_pair_text_files(pair_dir)
    metadata_df = pd.read_csv(metadata_path)
    if len(metadata_df) != EXPECTED_PAIR_COUNT:
        raise ValueError(
            f"Expected {EXPECTED_PAIR_COUNT} rows in H3 metadata, found {len(metadata_df)}."
        )
    if not metadata_df["pair_id"].is_unique:
        raise ValueError("Duplicate pair_id detected in H3 metadata.")

    requested_outputs = [out_long, raw_out]
    if "swapped" in args.orders:
        requested_outputs.append(position_bias_out)

    ensure_can_write(requested_outputs, overwrite=args.overwrite)
    write_prompt_audits = args.dry_run or args.write_prompt_audits
    if write_prompt_audits:
        prompt_out_dir.mkdir(parents=True, exist_ok=True)

    prompt_jobs: list[dict[str, object]] = []
    for _, row in metadata_df.sort_values("pair_id").iterrows():
        for order in args.orders:
            display_map = map_display_order(row, order)
            option_a = load_pair_text(pair_dir, row["pair_id"], display_map["displayed_A_side"])
            option_b = load_pair_text(pair_dir, row["pair_id"], display_map["displayed_B_side"])

            for repetition in range(1, args.repetitions + 1):
                prompt = prompt_template.format(option_a=option_a, option_b=option_b)
                job = {
                    "pair_id": row["pair_id"],
                    "trial_id": f"{order}_trial_{repetition:02d}",
                    "order": order,
                    "prompt": prompt,
                    "prompt_path": "",
                    **display_map,
                }
                prompt_jobs.append(job)

    prompt_count = 0
    if write_prompt_audits:
        prompt_count = maybe_write_prompt_audits(prompt_jobs, prompt_out_dir, overwrite=args.overwrite)

    if args.dry_run:
        print(f"Dry run complete. Wrote {prompt_count} prompt audit files to {prompt_out_dir}")
        print("No oracle ratings were written because no API call was made.")
        return

    try:
        import anthropic
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "The 'anthropic' package is not installed. Install project dependencies first:\n"
            "  pip install -r requirements.txt"
        ) from exc

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "ANTHROPIC_API_KEY is not set.\n"
            "PowerShell example:\n"
            '  $env:ANTHROPIC_API_KEY="your_key_here"'
        )

    client = anthropic.Anthropic(api_key=api_key)
    raw_out.parent.mkdir(parents=True, exist_ok=True)

    results: list[dict[str, object]] = []
    with raw_out.open("w", encoding="utf-8") as raw_file:
        for job in prompt_jobs:
            response_text, tokens = call_claude(
                client=client,
                anthropic_module=anthropic,
                model=args.model,
                prompt=str(job["prompt"]),
                temperature=args.temperature,
            )
            parsed = parse_oracle_response(response_text)
            if parsed["choice"] not in {"A", "B"}:
                raise ValueError(f"Claude returned a non A/B choice: {parsed['choice']!r}")

            chosen_side = job["displayed_A_side"] if parsed["choice"] == "A" else job["displayed_B_side"]
            chosen_run_id = (
                job["displayed_A_run_id"] if parsed["choice"] == "A" else job["displayed_B_run_id"]
            )
            chosen_condition = (
                job["displayed_A_condition"] if parsed["choice"] == "A" else job["displayed_B_condition"]
            )
            chosen_feature_set = (
                job["displayed_A_feature_set"]
                if parsed["choice"] == "A"
                else job["displayed_B_feature_set"]
            )

            result = {
                "pair_id": job["pair_id"],
                "trial_id": job["trial_id"],
                "order": job["order"],
                "displayed_A_side": job["displayed_A_side"],
                "displayed_B_side": job["displayed_B_side"],
                "displayed_A_run_id": job["displayed_A_run_id"],
                "displayed_B_run_id": job["displayed_B_run_id"],
                "choice_displayed": parsed["choice"],
                "chosen_side": chosen_side,
                "chosen_run_id": chosen_run_id,
                "chosen_condition": chosen_condition,
                "chosen_feature_set": chosen_feature_set,
                "model": args.model,
                "llm_tokens_used": tokens,
                "confidence": parsed["confidence"],
                "reason": parsed["reason"],
                "raw_response": response_text.strip(),
                "parsed_via": parsed["parsed_via"],
                "prompt_path": job["prompt_path"],
            }
            results.append(result)
            raw_file.write(json.dumps(result, ensure_ascii=False) + "\n")
            print(
                f"{job['pair_id']} {job['order']} {job['trial_id']}: "
                f"{parsed['choice']} -> {chosen_side} ({tokens} tokens)"
            )

    long_df = pd.DataFrame(results).sort_values(["pair_id", "order", "trial_id"])
    if long_df.empty:
        raise RuntimeError("No oracle results were collected.")

    long_df.to_csv(out_long, index=False)
    if "swapped" in args.orders:
        build_position_bias_summary(long_df, position_bias_out)

    print(f"Wrote {out_long}")
    print(f"Wrote {raw_out}")
    if "swapped" in args.orders:
        print(f"Wrote {position_bias_out}")
    if write_prompt_audits:
        print(f"Wrote {prompt_count} prompt audit files to {prompt_out_dir}")


if __name__ == "__main__":
    main()
