"""
RAG Pipeline — Knowledge Base Teks + FAISS + Sentence Transformers
Sumber data: knowledge_base.py (bukan PDF)
"""

import os
import pickle
import hashlib
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Tuple

from knowledge_base import get_all_chunks

# ─── Config ───────────────────────────────────────────────────────────────────
CACHE_DIR = os.path.join(os.path.dirname(__file__), ".cache")

# Multilingual — support Bahasa Indonesia
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

TOP_K = 3


# ─── Cache ────────────────────────────────────────────────────────────────────

def _cache_key() -> str:
    """Hash berdasarkan isi chunks + nama model agar cache otomatis invalid saat data berubah."""
    chunks = get_all_chunks()
    content = "\n---\n".join(chunks) + EMBEDDING_MODEL
    return hashlib.md5(content.encode("utf-8")).hexdigest()


def _cache_paths(key: str) -> dict:
    os.makedirs(CACHE_DIR, exist_ok=True)
    return {
        "index":  os.path.join(CACHE_DIR, f"{key}.faiss"),
        "chunks": os.path.join(CACHE_DIR, f"{key}.pkl"),
    }


# ─── Encoding ─────────────────────────────────────────────────────────────────

def _encode(chunks: List[str], model: SentenceTransformer) -> np.ndarray:
    return model.encode(
        chunks,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
        batch_size=32,
    ).astype(np.float32)


# ─── Load or Build ────────────────────────────────────────────────────────────

def load_or_build_rag(status_callback=None):
    key   = _cache_key()
    paths = _cache_paths(key)

    if os.path.exists(paths["index"]) and os.path.exists(paths["chunks"]):
        if status_callback: status_callback("📦 Memuat index dari cache…")
        index = faiss.read_index(paths["index"])
        with open(paths["chunks"], "rb") as f:
            chunks = pickle.load(f)
        if status_callback: status_callback("🤖 Memuat model embedding…")
        model = SentenceTransformer(EMBEDDING_MODEL)
        return index, chunks, model

    if status_callback: status_callback("📚 Membaca knowledge base akademik…")
    chunks = get_all_chunks()

    if status_callback: status_callback(f"🤖 Memuat model embedding (pertama kali, ~1 menit)…")
    model  = SentenceTransformer(EMBEDDING_MODEL)

    if status_callback: status_callback(f"🔢 Encoding {len(chunks)} dokumen…")
    embs   = _encode(chunks, model)

    index  = faiss.IndexFlatIP(embs.shape[1])
    index.add(embs)

    faiss.write_index(index, paths["index"])
    with open(paths["chunks"], "wb") as f:
        pickle.dump(chunks, f)

    return index, chunks, model


# ─── Retrieval ────────────────────────────────────────────────────────────────

def retrieve(query: str, index, chunks, model, top_k: int = TOP_K) -> List[Tuple[str, float]]:
    q = model.encode([query], convert_to_numpy=True, normalize_embeddings=True).astype(np.float32)
    scores, idxs = index.search(q, top_k)
    return [(chunks[i], float(s)) for s, i in zip(scores[0], idxs[0]) if i != -1]
