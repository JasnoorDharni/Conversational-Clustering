"""
src/loop.py
-----------
Conversational refinement loop for Conditions B and C.

Condition B — human experimenter issues instructions via stdin.
              Silhouette is NOT shown to the experimenter (study_design §3).
Condition C — LLM oracle issues instructions automatically.

Both conditions share the same loop structure:
    for turn in 1..max_turns:
        get instruction (human input OR oracle call)
        call interpreter -> new feature weights
        re-encode features with new weights
        re-run k-means
        log turn
        if done: break

Public API:
    run_loop(df, config, client, run_logger, initial_result, col_names)
        -> ClusterResult   (the final cluster result after all turns)
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from src.cluster import ClusterResult, run_kmeans, summarise_clusters
from src.features import build_feature_matrix, default_weights
from src.llm import call_interpreter, call_oracle
from src.logger import RunLogger


def run_loop(
    df: pd.DataFrame,
    config: dict[str, Any],
    client,                   # anthropic.Anthropic | None (None for Condition A)
    run_logger: RunLogger,
    initial_result: ClusterResult,
    col_names: list[str],
) -> ClusterResult:
    """
    Run the conversational refinement loop for one experimental session.

    For Condition A (max_turns=0) this is a no-op and returns initial_result.

    Parameters
    ----------
    df             : Original DataFrame (same rows as were clustered).
    config         : Loaded YAML config dict for this run.
    client         : Anthropic client (required for B and C).
    run_logger     : Active RunLogger context for this run.
    initial_result : ClusterResult from the baseline k-means run (turn 0).
    col_names      : Column names from the initial feature build (informational).

    Returns
    -------
    The ClusterResult from the final turn (or initial_result if max_turns=0).
    """
    condition  = config["condition"]
    feature_set = config["feature_set"]
    K          = config["K"]
    seed       = config["seed"]
    max_turns  = config.get("max_turns", 0)
    model      = config.get("model", "claude-sonnet-4-5")

    interpreter_prompt = config.get("interpreter_prompt", "prompts/interpreter.md")
    oracle_prompt      = config.get("oracle_prompt",      "prompts/oracle_user.md")

    if max_turns == 0:
        return initial_result   # Condition A — nothing to do

    current_result = initial_result
    current_weights = default_weights(feature_set)

    for turn_n in range(1, max_turns + 1):

        # ── 1. Get cluster summary for prompts ────────────────────────────
        summary = summarise_clusters(df, current_result.labels, K)

        # ── 2. Get instruction ────────────────────────────────────────────
        if condition == "B":
            instruction = _get_human_instruction(turn_n, max_turns)
            if instruction is None:
                print("  Session ended by experimenter.")
                break

        elif condition == "C":
            oracle_res = call_oracle(
                client, oracle_prompt, summary, turn_n, model
            )
            if oracle_res.refused:
                run_logger.log_error(
                    f"Oracle refused on turn {turn_n}: {oracle_res.instruction}"
                )
                run_logger.refuse(f"oracle turn {turn_n}")
                return current_result
            if oracle_res.error:
                run_logger.log_error(f"Oracle error on turn {turn_n}: {oracle_res.error}")
                raise RuntimeError(oracle_res.error)
            instruction = oracle_res.instruction
            if oracle_res.done:
                print(f"  Oracle says DONE at turn {turn_n}.")
                break
        else:
            raise ValueError(f"Unknown condition: {condition!r}")

        # ── 3. Interpret instruction -> new weights ───────────────────────
        interp_res = call_interpreter(
            client, interpreter_prompt, summary, instruction, model
        )
        if interp_res.refused:
            run_logger.log_error(
                f"Interpreter refused on turn {turn_n}: {interp_res.rationale}"
            )
            run_logger.refuse(f"interpreter turn {turn_n}")
            return current_result
        if interp_res.error:
            run_logger.log_error(
                f"Interpreter parse error on turn {turn_n}: {interp_res.error}"
            )
            # Non-fatal: keep previous weights, log the error, continue
            print(f"  [warn] Interpreter error on turn {turn_n} — keeping previous weights.")
        else:
            # Merge new weights (only keys returned by LLM are updated)
            current_weights.update(interp_res.weights)

        # ── 4. Re-encode and re-cluster ───────────────────────────────────
        X_new, _ = build_feature_matrix(df, feature_set, weights=current_weights)
        current_result = run_kmeans(X_new, K, seed)

        # ── 5. Log the turn ───────────────────────────────────────────────
        total_tokens = getattr(interp_res, "tokens_used", 0)
        if condition == "C":
            total_tokens += getattr(oracle_res, "tokens_used", 0)

        run_logger.log_turn(
            turn_n        = turn_n,
            instruction   = instruction,
            parsed_params = current_weights.copy(),
            silhouette    = current_result.silhouette,
            db_index      = current_result.davies_bouldin,
            llm_tokens_used = total_tokens,
        )

        print(
            f"  Turn {turn_n}/{max_turns}  "
            f"silhouette={current_result.silhouette:.4f}  "
            f"db={current_result.davies_bouldin:.4f}"
        )

    return current_result


# ── Human input helper ────────────────────────────────────────────────────

def _get_human_instruction(turn_n: int, max_turns: int) -> str | None:
    """
    Prompt the experimenter for a natural-language instruction.
    Returns None if the experimenter types 'done' or presses Ctrl+D.

    NOTE: The Silhouette score is intentionally NOT shown here
    (study_design §3: experimenter is blind to score during Condition B).
    """
    print(f"\n  [Turn {turn_n}/{max_turns}]")
    print("  Cluster summary printed above. Enter your refinement instruction.")
    print("  (Type 'done' and press Enter to end the session early.)")
    try:
        instruction = input("  > ").strip()
    except EOFError:
        return None
    if instruction.lower() == "done":
        return None
    return instruction if instruction else None
