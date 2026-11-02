"""Embedding and reranking models.

The app runs the quantised ONNX export of multilingual-e5-small (118 MB, no PyTorch) so it fits a 512 MB
container. The sentence-transformers wrappers are only used by the evaluation scripts to compare models.
"""

from __future__ import annotations

import numpy as np

# e5 models were trained with these prefixes; other models get none.
PREFIXES = {"intfloat/multilingual-e5-small": ("query: ", "passage: ")}


ONNX_FILE = "onnx/model_qint8_avx512_vnni.onnx"


def mean_pool(hidden: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Average token vectors where mask == 1, then L2-normalise each row."""
    mask = mask[..., None].astype(hidden.dtype)
    pooled = (hidden * mask).sum(axis=1) / np.maximum(mask.sum(axis=1), 1e-9)
    return pooled / np.maximum(np.linalg.norm(pooled, axis=1, keepdims=True), 1e-9)


class XlmrTokenizer:
    """XLM-RoBERTa tokenisation from the 5 MB SentencePiece model.

    tokenizer.json gives the same ids but holds the 250k-entry vocabulary in about 245 MB of RAM, which does not
    fit a 512 MB host next to the model. XLM-R shifts SentencePiece ids by one and reserves 0-3 for specials.
    """

    BOS, PAD, EOS, UNK = 0, 1, 2, 3

    def __init__(self, model_path: str, max_length: int = 512):
        import sentencepiece as spm

        self.sp = spm.SentencePieceProcessor(model_file=model_path)
        self.max_length = max_length

    def ids(self, text: str) -> list[int]:
        pieces = [i + 1 if i else self.UNK for i in self.sp.encode(text)][: self.max_length - 2]
        return [self.BOS, *pieces, self.EOS]

    def batch(self, texts: list[str]) -> tuple[np.ndarray, np.ndarray]:
        rows = [self.ids(t) for t in texts]
        width = max(map(len, rows))
        ids = np.full((len(rows), width), self.PAD, dtype=np.int64)
        mask = np.zeros((len(rows), width), dtype=np.int64)
        for r, row in enumerate(rows):
            ids[r, : len(row)], mask[r, : len(row)] = row, 1
        return ids, mask


class OnnxEncoder:
    def __init__(self, name: str, max_length: int = 512):
        import onnxruntime as ort
        from huggingface_hub import hf_hub_download

        self.name = name
        self.session = ort.InferenceSession(hf_hub_download(name, ONNX_FILE), providers=["CPUExecutionProvider"])
        self.tokenizer = XlmrTokenizer(hf_hub_download(name, "onnx/sentencepiece.bpe.model"), max_length)
        self.inputs = {i.name for i in self.session.get_inputs()}
        self.query_prefix, self.passage_prefix = PREFIXES.get(name, ("", ""))

    def _encode(self, texts: list[str], batch_size: int = 16) -> np.ndarray:
        out = []
        for start in range(0, len(texts), batch_size):
            ids, mask = self.tokenizer.batch(texts[start : start + batch_size])
            feed = {"input_ids": ids, "attention_mask": mask}
            if "token_type_ids" in self.inputs:
                feed["token_type_ids"] = np.zeros_like(ids)
            out.append(mean_pool(self.session.run(None, feed)[0], mask))
        return np.vstack(out).astype(np.float32)

    def encode_queries(self, texts: list[str]) -> np.ndarray:
        return self._encode([self.query_prefix + t for t in texts])

    def encode_passages(self, texts: list[str]) -> np.ndarray:
        return self._encode([self.passage_prefix + t for t in texts])


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


def load_encoder(name: str, runtime: str = "onnx"):
    return OnnxEncoder(name) if runtime == "onnx" else SentenceEncoder(name)


def load_reranker(name: str) -> CrossEncoderReranker:
    return CrossEncoderReranker(name)
