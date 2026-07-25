#!/usr/bin/env python3
"""Automated, deterministic judge for the RAG context-packing benchmark.

Usage:
    python3 check.py <path-to-solution.py>

Dynamically imports the given module, calls its `pack_context` against a
fixed set of deterministic test cases (baked in below, no randomness, no
network/clock dependence), and for each case independently computes the
true optimal achievable score via brute-force subset enumeration -- a
code path deliberately separate from any knapsack/DP implementation, so
the ground truth here does not share a bug class with a plausible-but-
wrong solution under test.

Exits 0 if every case passes, exits 1 (non-zero) if any case fails.
"""
from __future__ import annotations

import copy
import importlib.util
import itertools
import sys


def load_solution(path: str):
    spec = importlib.util.spec_from_file_location("solution_under_test", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"could not load module spec from {path!r}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "pack_context"):
        raise AttributeError(
            f"{path!r} does not define a `pack_context` function"
        )
    return module.pack_context


def brute_force_optimal_score(chunks: list, token_budget: int) -> float:
    """Ground truth: exhaustively try every subset (independent of any
    knapsack/DP strategy). Only used with small fixed n (<= 6) here, so
    2**n enumeration is cheap and exact."""
    if token_budget <= 0 or not chunks:
        return 0.0
    best = 0.0
    n = len(chunks)
    for r in range(n + 1):
        for combo in itertools.combinations(chunks, r):
            total_tokens = sum(c["tokens"] for c in combo)
            if total_tokens <= token_budget:
                total_score = sum(c["score"] for c in combo)
                if total_score > best:
                    best = total_score
    return best


# ---------------------------------------------------------------------
# Fixed, deterministic test cases.
# ---------------------------------------------------------------------
CASES = [
    {
        "name": "non-greedy-optimal (two efficient chunks beat one big one)",
        "query": "how does the retry policy work?",
        "chunks": [
            {"id": "A", "tokens": 6, "score": 6},
            {"id": "B", "tokens": 5, "score": 5},
            {"id": "C", "tokens": 5, "score": 5},
        ],
        "budget": 10,
        # Greedy-by-score-alone takes A (score 6) then nothing else fits.
        # True optimum is B + C = 10 tokens, score 10.
    },
    {
        "name": "tie in relevance score, only one fits",
        "query": "what is the refund window?",
        "chunks": [
            {"id": "D", "tokens": 3, "score": 5},
            {"id": "E", "tokens": 3, "score": 5},
            {"id": "F", "tokens": 3, "score": 5},
        ],
        "budget": 3,
        # Any single one of D/E/F is an acceptable optimal answer.
    },
    {
        "name": "single chunk larger than the whole budget must be excluded",
        "query": "summarize the incident timeline",
        "chunks": [
            {"id": "G", "tokens": 50, "score": 100},
            {"id": "H", "tokens": 1, "score": 1},
        ],
        "budget": 10,
        # G can never fit; optimum is H alone, score 1.
    },
    {
        "name": "empty candidate list",
        "query": "anything",
        "chunks": [],
        "budget": 100,
    },
    {
        "name": "zero token budget",
        "query": "anything",
        "chunks": [
            {"id": "I", "tokens": 1, "score": 10},
            {"id": "J", "tokens": 2, "score": 20},
        ],
        "budget": 0,
    },
    {
        "name": "exact-fit boundary (<=, not <)",
        "query": "what changed in v2?",
        "chunks": [
            {"id": "K", "tokens": 10, "score": 10},
            {"id": "L", "tokens": 1, "score": 1},
        ],
        "budget": 10,
        # K exactly fills the budget and must be selectable; optimum is
        # K alone (score 10) over L alone (score 1).
    },
    {
        "name": "mixed: some large low-value chunks must be skipped",
        "query": "explain the pricing tiers",
        "chunks": [
            {"id": "M", "tokens": 4, "score": 3},
            {"id": "N", "tokens": 4, "score": 3},
            {"id": "O", "tokens": 4, "score": 3},
            {"id": "P", "tokens": 9, "score": 8},
        ],
        "budget": 9,
        # M+N+O = 12 tokens (too many); best pair M+N = 8 tokens, score 6,
        # beats P alone (score 8)? No: P alone = score 8 > 6, and fits
        # budget 9. True optimum is P alone, score 8. Greedy-by-score
        # (P has highest single score) happens to get this one right,
        # exercising the "greedy is sometimes right" trap so a checker
        # that only used this case would be too weak on its own.
    },
]


def run_case(pack_context, case: dict) -> tuple:
    budget = case["budget"]

    # Compute the ground truth (valid ids, per-id lookup, brute-force
    # optimum) from a snapshot taken BEFORE the solution runs, over a
    # copy the solution never sees. A solution that mutates its `chunks`
    # argument (or the dicts inside it) as a side effect must not be able
    # to corrupt the oracle it's graded against.
    baseline_chunks = copy.deepcopy(case["chunks"])
    valid_ids = {c["id"] for c in baseline_chunks}
    by_id = {c["id"]: c for c in baseline_chunks}
    optimal_score = brute_force_optimal_score(baseline_chunks, budget)

    solution_chunks = copy.deepcopy(case["chunks"])
    try:
        result = pack_context(case["query"], solution_chunks, budget)
    except Exception as exc:  # noqa: BLE001 - want to report any failure
        return False, f"raised {type(exc).__name__}: {exc}"

    if not isinstance(result, list):
        return False, f"expected a list, got {type(result).__name__}"

    if len(set(result)) != len(result):
        return False, f"returned duplicate ids: {result}"

    unknown = [rid for rid in result if rid not in valid_ids]
    if unknown:
        return False, f"returned ids not present in input chunks: {unknown}"

    total_tokens = sum(by_id[rid]["tokens"] for rid in result)
    if total_tokens > budget:
        return False, (
            f"selected chunks use {total_tokens} tokens, exceeding "
            f"budget {budget}: {result}"
        )

    total_score = sum(by_id[rid]["score"] for rid in result)

    if abs(total_score - optimal_score) > 1e-9:
        return False, (
            f"selected {result} with total score {total_score}, but the "
            f"achievable optimum is {optimal_score}"
        )

    return True, f"ok (score={total_score}, tokens={total_tokens}/{budget})"


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: python3 {sys.argv[0]} <path-to-solution.py>")
        return 1

    solution_path = sys.argv[1]

    try:
        pack_context = load_solution(solution_path)
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: could not load solution: {exc}")
        return 1

    failures = 0
    for case in CASES:
        ok, detail = run_case(pack_context, case)
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {case['name']}: {detail}")
        if not ok:
            failures += 1

    total = len(CASES)
    print(f"\n{total - failures}/{total} cases passed")

    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
