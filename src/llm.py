"""
src/llm.py
----------
Anthropic API wrapper for the conversational clustering study.

Handles:
  - Prompt template loading from .md files (reads file, substitutes {variables})
  - Interpreter calls: user instruction -> feature weight dict (JSON)
  - Oracle calls: cluster summary -> next instruction (plain text)
  - Exponential backoff on transient errors (rate limits, timeouts)
  - Explicit refusal detection (safety filter on conflict data)

The distinction between transient and permanent errors is critical
(see professor's requirement, section 8):
  - Transient  (retry): RateLimitError, APITimeoutError, APIConnectionError
  - Permanent  (fail loud): refusal in response content, AuthenticationError,
                             BadRequestError, unparseable JSON from interpreter

Public API:
    load_prompt(path, **variables) -> str
    call_interpreter(client, prompt_path, cluster_summary, instruction, model)
        -> InterpreterResult
    call_oracle(client, prompt_path, cluster_summary, turn_n, model)
        -> OracleResult
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import anthropic


# ── Constants ─────────────────────────────────────────────────────────────

MAX_RETRIES = 3
BACKOFF_BASE = 2.0       # seconds; doubles on each retry (2, 4, 8)
MAX_TOKENS   = 512       # enough for a JSON weight dict or one instruction

# Strings in a response that indicate a safety refusal
_REFUSAL_PHRASES = [
    "i'm not able to",
    "i cannot",
    "i can't assist",
    "i'm unable to",
    "as an ai",
    "i apologize",
    "i won't",
]


# ── Result dataclasses ────────────────────────────────────────────────────

@dataclass
class InterpreterResult:
    weights: dict[str, float]    # feature group -> weight multiplier
    rationale: str               # one-sentence explanation from LLM
    tokens_used: int
    refused: bool = False
    error: str | None = None


@dataclass
class OracleResult:
    instruction: str             # plain-text instruction for next turn
    done: bool                   # True if oracle says DONE
    tokens_used: int
    refused: bool = False
    error: str | None = None


# ── Prompt loading ────────────────────────────────────────────────────────

def load_prompt(path: str | Path, **variables: str) -> str:
    """
    Load a prompt template from a .md file and substitute {variables}.

    Raises
    ------
    FileNotFoundError if the file does not exist.
    ValueError        if the file still contains the PLACEHOLDER sentinel.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(
            f"Prompt file not found: {p}\n"
            "Has Person 1 committed the real prompt yet?"
        )
    text = p.read_text(encoding="utf-8")
    if "YOU ARE A PLACEHOLDER" in text:
        raise ValueError(
            f"Prompt file {p} still contains the placeholder text.\n"
            "Person 1 must write and commit the real prompt before running "
            "Conditions B or C."
        )
    # Substitute {variable} placeholders
    for key, value in variables.items():
        text = text.replace(f"{{{key}}}", value)
    return text


# ── Internal helpers ──────────────────────────────────────────────────────

def _is_refused(text: str) -> bool:
    lower = text.lower()
    return any(phrase in lower for phrase in _REFUSAL_PHRASES)


def _call_with_backoff(
    client: anthropic.Anthropic,
    model: str,
    prompt: str,
) -> tuple[str, int]:
    """
    Call the Anthropic API with exponential backoff on transient errors.

    Returns (response_text, tokens_used).
    Raises on permanent errors (auth, bad request, refusal).
    """
    transient = (
        anthropic.RateLimitError,
        anthropic.APITimeoutError,
        anthropic.APIConnectionError,
    )

    for attempt in range(MAX_RETRIES):
        try:
            msg = client.messages.create(
                model=model,
                max_tokens=MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}],
            )
            text = msg.content[0].text if msg.content else ""
            tokens = msg.usage.input_tokens + msg.usage.output_tokens
            return text, tokens

        except transient as exc:
            if attempt == MAX_RETRIES - 1:
                raise   # propagate on final attempt
            wait = BACKOFF_BASE ** (attempt + 1)
            print(f"  [backoff] {type(exc).__name__} — retrying in {wait:.0f}s "
                  f"(attempt {attempt + 1}/{MAX_RETRIES})")
            time.sleep(wait)

        except (anthropic.AuthenticationError, anthropic.BadRequestError):
            raise   # permanent — never retry


# ── Interpreter ───────────────────────────────────────────────────────────

def call_interpreter(
    client: anthropic.Anthropic,
    prompt_path: str | Path,
    cluster_summary: str,
    instruction: str,
    model: str,
) -> InterpreterResult:
    """
    Send user instruction + cluster summary to the interpreter LLM.
    Expects a JSON response: {"feature_weights": {...}, "rationale": "..."}

    Returns InterpreterResult. If the response is refused or unparseable,
    sets .refused=True or .error=<message> and returns default weights.
    """
    prompt = load_prompt(
        prompt_path,
        cluster_summary=cluster_summary,
        user_instruction=instruction,
    )

    try:
        text, tokens = _call_with_backoff(client, model, prompt)
    except Exception as exc:
        return InterpreterResult(
            weights={}, rationale="", tokens_used=0,
            error=f"{type(exc).__name__}: {exc}",
        )

    # Refusal check
    if _is_refused(text):
        return InterpreterResult(
            weights={}, rationale=text[:200], tokens_used=tokens,
            refused=True,
        )

    # Parse JSON — strip markdown code fences if present
    clean = re.sub(r"```(?:json)?|```", "", text).strip()
    try:
        parsed = json.loads(clean)
        weights = {str(k): float(v) for k, v in parsed.get("feature_weights", {}).items()}
        rationale = str(parsed.get("rationale", ""))
        return InterpreterResult(weights=weights, rationale=rationale, tokens_used=tokens)
    except (json.JSONDecodeError, ValueError) as exc:
        return InterpreterResult(
            weights={}, rationale="", tokens_used=tokens,
            error=f"JSON parse error: {exc} | raw: {text[:200]}",
        )


# ── Oracle ────────────────────────────────────────────────────────────────

def call_oracle(
    client: anthropic.Anthropic,
    prompt_path: str | Path,
    cluster_summary: str,
    turn_n: int,
    model: str,
) -> OracleResult:
    """
    Send cluster summary to the oracle LLM, which plays the role of user.
    Expects a plain-text instruction, or the word DONE on the last turn.

    Returns OracleResult.
    """
    prompt = load_prompt(
        prompt_path,
        cluster_summary=cluster_summary,
        turn_number=str(turn_n),
    )

    try:
        text, tokens = _call_with_backoff(client, model, prompt)
    except Exception as exc:
        return OracleResult(
            instruction="", done=False, tokens_used=0,
            error=f"{type(exc).__name__}: {exc}",
        )

    if _is_refused(text):
        return OracleResult(
            instruction=text[:200], done=False, tokens_used=tokens,
            refused=True,
        )

    done = text.strip().upper().startswith("DONE")
    return OracleResult(instruction=text.strip(), done=done, tokens_used=tokens)
