"""Thin wrappers around sentence-transformers models used by the retriever."""

from __future__ import annotations

import numpy as np

# e5 models were trained with these prefixes; other models get none.
PREFIXES = {"intfloat/multilingual-e5-small": ("query: ", "passage: ")}


class SentenceEncoder:
    def __init__(self, name: str):
        from sentence_transformers import SentenceTransformer

        self.name = name
        self.model = SentenceTransformer(name, device="cpu")
        self.query_prefix, self.passage_prefix = PREFIXES.get(name, ("", ""))

    def _encode(self, texts: list[str]) -> np.ndarray:
        return self.model.encode(texts, normalize_embeddings=True, convert_to_numpy=True, batch_size=16)

    def encode_queries(self, texts: list[str]) -> np.ndarray:
        return self._encode([self.query_prefix + t for t in texts])

    def encode_passages(self, texts: list[str]) -> np.ndarray:
        return self._encode([self.passage_prefix + t for t in texts])


class CrossEncoderReranker:
    def __init__(self, name: str):
        from sentence_transformers import CrossEncoder

        self.name = name
        self.model = CrossEncoder(name, device="cpu", max_length=512)

    def score(self, query: str, texts: list[str]) -> list[float]:
        return [float(s) for s in self.model.predict([(query, t) for t in texts])]


def load_encoder(name: str) -> SentenceEncoder:
    return SentenceEncoder(name)


def load_reranker(name: str) -> CrossEncoderReranker:
    return CrossEncoderReranker(name)
