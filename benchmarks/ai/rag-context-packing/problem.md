# RAG Context Packing Under a Fixed Token Budget

## Niche

This is the **context-assembly step of a Retrieval-Augmented Generation
(RAG) pipeline**: retrieval has already run and produced a ranked list of
candidate chunks with per-chunk relevance scores (e.g. cosine similarity
of a chunk embedding to the query embedding) and per-chunk token counts.
Before the chunks can be dropped into the model's context window, they
must be **packed** into a fixed token budget (the space left in the
prompt after the system prompt, the user query, and reserved output
tokens) so that the *total relevance* of what actually reaches the model
is maximized. This is the classic **0/1 (bounded) knapsack** shape, but
it is a real, load-bearing building block of a RAG feature, not a
generic textbook puzzle: a chunk is an indivisible unit (you cannot
truncate mid-chunk and keep it coherent), so fractional/greedy packing is
the wrong tool — the correct behavior requires exact 0/1 selection.

## Required signature

Implement, in a module with no import-time side effects:

```python
def pack_context(query: str, chunks: list[dict], token_budget: int) -> list[str]:
    """
    query: the user query string. Present for signature realism (this is
        the context-*packing* step, which runs after retrieval/scoring);
        implementations are not required to use it for scoring.

    chunks: a list of candidate chunk dicts, each with the keys:
        - "id":     str   — unique identifier for the chunk
        - "tokens": int   — token count of this chunk's text (>= 1)
        - "score":  float or int — relevance score of this chunk
                    against `query` (already computed upstream, e.g. via
                    cosine similarity between query and chunk embeddings;
                    higher is more relevant)

    token_budget: int — the maximum total tokens summed across the
        "tokens" values of every selected chunk. token_budget may be 0.

    Returns:
        list[str] — the "id"s of the selected chunks such that:
          1. each chunk is selected at most once (0/1 selection — a
             chunk is an atomic unit, it is never split/fractional),
          2. sum of "tokens" over selected ids does not exceed
             token_budget,
          3. sum of "score" over selected ids is the maximum achievable
             under constraints (1) and (2).

        Order of ids within the returned list does not matter. If
        multiple subsets achieve the same maximum total score, any one
        of them is an acceptable return value (the checker verifies the
        achieved total score and constraint validity, not which specific
        optimal subset was chosen).
    """
```

## Inputs / outputs

- Input `chunks` may be empty.
- `token_budget` may be `0` or smaller than every chunk's token count.
- A single chunk's `tokens` may exceed `token_budget` on its own — such a
  chunk can never be selected and must be excluded from the result.
- Relevance scores (`score`) may tie across multiple chunks.
- All `tokens` values are non-negative integers; all `score` values are
  non-negative numbers. `id` values are unique strings within one call.

## Edge cases a correct solution must handle

1. **Empty candidate list** — `chunks == []` must return `[]` regardless
   of `token_budget`.
2. **Zero budget** — `token_budget == 0` must return `[]` (no chunk of
   `tokens >= 1` can fit).
3. **A single chunk larger than the whole budget** — that chunk must be
   excluded from the optimal selection (must not appear in the output),
   even if it has the highest relevance score of all candidates.
4. **Ties in relevance score** — when several chunks share the same
   score and only one can fit, selecting any one of them is acceptable,
   as long as the total achieved score is optimal.
5. **Exact-fit boundary** — a chunk whose `tokens` exactly equals the
   remaining/full budget must be selectable (the budget check is
   `<=`, not `<`).
6. **Greedy-by-relevance-alone is wrong** — always preferring the
   highest-scoring chunks first, without considering whether a
   different combination of lower-individually-scored-but-more-
   token-efficient chunks yields a higher total score within budget, is
   an incorrect strategy and will be rejected by the checker.

## Judge

Run: `python3 check.py <path-to-solution.py>`

The checker dynamically imports the given module, calls `pack_context`
against a fixed set of deterministic cases baked into `check.py`, and for
each case independently computes the true optimal achievable score via
brute-force subset enumeration (a separate code path from any knapsack/DP
approach, so the ground truth does not share a bug class with a
straightforward-but-wrong reference implementation). It checks, per case:

- the returned ids are a subset of the input chunk ids with no duplicates,
- the total token count of selected chunks does not exceed the budget,
- the total score of selected chunks equals the independently-computed
  optimal score.

Exits `0` if every case passes, non-zero (with a summary of which
case(s) failed and why) otherwise.
