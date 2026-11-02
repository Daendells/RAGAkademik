"""Keyword (BM25) and embedding search over chunks, fused with reciprocal rank fusion.

About 120 chunks fit in memory as a numpy matrix, so there is no vector database.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import numpy as np
from rank_bm25 import BM25Okapi

from rag.ingest import read_chunks
from rag.models import Chunk

MODES = ("bm25", "dense", "hybrid", "hybrid_rerank")
CANDIDATES = 20  # pool size for fusion and reranking


class Encoder(Protocol):
    def encode_queries(self, texts: list[str]) -> np.ndarray: ...
    def encode_passages(self, texts: list[str]) -> np.ndarray: ...


class Reranker(Protocol):
    def score(self, query: str, texts: list[str]) -> list[float]: ...


@dataclass
class Hit:
    chunk: Chunk
    score: float


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def rrf(rankings: list[list[int]], c: int = 60) -> dict[int, float]:
    scores: dict[int, float] = {}
    for ranking in rankings:
        for rank, idx in enumerate(ranking, start=1):
            scores[idx] = scores.get(idx, 0.0) + 1 / (c + rank)
    return scores


class Retriever:
    def __init__(self, chunks, embeddings, encoder, reranker=None, default_mode="hybrid"):
        self.chunks = list(chunks)
        self.embeddings = np.asarray(embeddings, dtype=np.float32)
        self.encoder = encoder
        self.reranker = reranker
        self.default_mode = default_mode
        self.bm25 = BM25Okapi([tokenize(c.text) for c in self.chunks])

    def _bm25(self, query: str) -> np.ndarray:
        return self.bm25.get_scores(tokenize(query))

    def _dense(self, query: str) -> np.ndarray:
        return self.embeddings @ self.encoder.encode_queries([query])[0]

    @staticmethod
    def _top(scores: np.ndarray, n: int) -> list[int]:
        return [int(i) for i in np.argsort(-scores, kind="stable")[:n]]

    def search(self, query: str, k: int = 5, mode: str | None = None) -> list[Hit]:
        mode = mode or self.default_mode
        if mode not in MODES:
            raise ValueError(f"unknown mode {mode!r}; expected one of {MODES}")
        if mode == "hybrid_rerank" and self.reranker is None:
            raise ValueError("hybrid_rerank needs a reranker")

        if mode in ("bm25", "dense"):
            scores = self._bm25(query) if mode == "bm25" else self._dense(query)
            ranked = [(i, float(scores[i])) for i in self._top(scores, k)]
        else:
            fused = rrf([self._top(self._bm25(query), CANDIDATES), self._top(self._dense(query), CANDIDATES)])
            ranked = sorted(fused.items(), key=lambda kv: -kv[1])[:CANDIDATES]
            if mode == "hybrid_rerank":
                ids = [i for i, _ in ranked]
                rescored = self.reranker.score(query, [self.chunks[i].text for i in ids])
                ranked = sorted(zip(ids, rescored), key=lambda kv: -kv[1])
            ranked = ranked[:k]
        return [Hit(self.chunks[i], s) for i, s in ranked]

    @classmethod
    def load(cls, data_dir: Path) -> "Retriever":
        """Load chunks, embeddings and the settings chosen by eval/run_retrieval.py."""
        from rag.encoders import load_encoder, load_reranker

        config = json.loads((data_dir / "index.json").read_text(encoding="utf-8"))
        reranker = load_reranker(config["reranker"]) if config.get("reranker") else None
        return cls(
            read_chunks(data_dir / "chunks.jsonl"),
            np.load(data_dir / "embeddings.npy"),
            load_encoder(config["encoder"]),
            reranker=reranker,
            default_mode=config["mode"],
        )
