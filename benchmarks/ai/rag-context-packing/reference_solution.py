"""Reference solution for the RAG context-packing benchmark.

Correct 0/1 knapsack (dynamic programming) over the token budget:
selects the subset of chunks maximizing total relevance score without
exceeding the token budget, since a chunk is an atomic, non-splittable
unit of retrieved context.

Stdlib only.
"""
from __future__ import annotations


def pack_context(query: str, chunks: list, token_budget: int) -> list:
    n = len(chunks)
    if n == 0 or token_budget <= 0:
        return []

    # dp[i][b] = best total score achievable using the first i chunks
    # within a budget of b tokens.
    dp = [[0.0] * (token_budget + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        w = chunks[i - 1]["tokens"]
        v = chunks[i - 1]["score"]
        row_prev = dp[i - 1]
        row_cur = dp[i]
        for b in range(token_budget + 1):
            best = row_prev[b]
            if w <= b:
                candidate = row_prev[b - w] + v
                if candidate > best:
                    best = candidate
            row_cur[b] = best

    # Backtrack to recover which chunks were selected.
    selected = []
    b = token_budget
    for i in range(n, 0, -1):
        if dp[i][b] != dp[i - 1][b]:
            selected.append(chunks[i - 1]["id"])
            b -= chunks[i - 1]["tokens"]

    return selected
