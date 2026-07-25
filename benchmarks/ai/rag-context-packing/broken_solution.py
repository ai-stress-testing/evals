"""Deliberately-broken variant for the RAG context-packing benchmark.

Bug: packs chunks greedily by relevance score alone (highest score
first, take it if it still fits in the remaining budget), never
reconsidering the choice. This ignores token-efficiency (score-per-token)
and can strand budget that a different, non-greedy combination of chunks
would have used to reach a strictly higher total score -- i.e. it does
not solve the 0/1 knapsack optimally. It still respects the budget
constraint and the "select each chunk at most once" constraint, so a
checker that only validates budget-safety (and not optimality) would
wrongly pass this.
"""
from __future__ import annotations


def pack_context(query: str, chunks: list, token_budget: int) -> list:
    if not chunks or token_budget <= 0:
        return []

    ordered = sorted(chunks, key=lambda c: c["score"], reverse=True)

    selected = []
    remaining = token_budget
    for chunk in ordered:
        if chunk["tokens"] <= remaining:
            selected.append(chunk["id"])
            remaining -= chunk["tokens"]

    return selected
