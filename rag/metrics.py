"""Retrieval metrics over Pasal numbers; several chunks of one Pasal count as one result."""

from __future__ import annotations


def _dedupe(ranked: list[int]) -> list[int]:
    return list(dict.fromkeys(ranked))


def hit_at_k(ranked_pasal: list[int], gold: set[int], k: int) -> bool:
    return any(p in gold for p in _dedupe(ranked_pasal)[:k])


def reciprocal_rank(ranked_pasal: list[int], gold: set[int]) -> float:
    for rank, p in enumerate(_dedupe(ranked_pasal), start=1):
        if p in gold:
            return 1 / rank
    return 0.0


def summarize(rows: list[dict]) -> dict:
    """rows: {"ranked": [pasal, ...], "gold": [pasal, ...]} per question."""
    n = len(rows)
    out = {"n": n}
    for k in (1, 3, 5):
        out[f"hit@{k}"] = round(sum(hit_at_k(r["ranked"], set(r["gold"]), k) for r in rows) / n, 4)
    out["mrr"] = round(sum(reciprocal_rank(r["ranked"], set(r["gold"])) for r in rows) / n, 4)
    return out
