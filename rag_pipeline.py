"""
RAG Pipeline - Static Embeddings + OpenRouter API untuk query embedding
=======================================================================
Tidak memerlukan model lokal (sentence-transformers) saat runtime!
- Embedding dokumen: dibaca dari file statis di embeddings/ (pre-computed)
- Embedding query:   via OpenRouter API (sama seperti LLM)
- Pencarian:         cosine similarity dengan numpy (dot product)
"""

import os
import pickle
import numpy as np
import requests
import json
from typing import List, Tuple
from dotenv import load_dotenv

load_dotenv()

# --- Config -------------------------------------------------------------------
EMBEDDINGS_DIR  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "embeddings")
EMB_PATH        = os.path.join(EMBEDDINGS_DIR, "doc_embeddings.npy")
CHUNKS_PATH     = os.path.join(EMBEDDINGS_DIR, "chunks.pkl")
TOP_K           = 3

# OpenRouter config (sama dengan llm.py)
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_API_KEY  = os.getenv("OPENROUTER_API_KEY", "")

# Model embedding gratis via OpenRouter
# Gunakan text-embedding-ada-002 (OpenAI) atau model gratis lainnya
EMBEDDING_API_MODEL = "openai/text-embedding-3-small"

# --- Load static embeddings ---------------------------------------------------

_doc_embeddings: np.ndarray = None
_chunks: List[str] = None


def _load_static_embeddings():
    """Load pre-computed embeddings dari file. Cached di memory."""
    global _doc_embeddings, _chunks
    if _doc_embeddings is not None:
        return  # sudah di-load sebelumnya

    if not os.path.exists(EMB_PATH) or not os.path.exists(CHUNKS_PATH):
        raise FileNotFoundError(
            f"File embedding tidak ditemukan di '{EMBEDDINGS_DIR}'.\n"
            "Jalankan dulu: python precompute_embeddings.py"
        )

    _doc_embeddings = np.load(EMB_PATH)           # shape: (N, 384)
    with open(CHUNKS_PATH, "rb") as f:
        _chunks = pickle.load(f)


# --- Query embedding via API --------------------------------------------------

def _embed_query_api(query: str) -> np.ndarray:
    """Embed satu query menggunakan OpenRouter Embeddings API."""
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY tidak ditemukan di .env")

    response = requests.post(
        f"{OPENROUTER_BASE_URL}/embeddings",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/Daendells/RAGAkademik",
            "X-Title": "RAG Akademik",
        },
        json={
            "model": EMBEDDING_API_MODEL,
            "input": query,
        },
        timeout=15,
    )
    response.raise_for_status()
    data = response.json()

    vec = np.array(data["data"][0]["embedding"], dtype=np.float32)

    # Normalize agar cosine similarity = dot product
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm

    # Sesuaikan dimensi jika berbeda dengan doc embeddings
    # (doc: 384-dim, text-embedding-3-small: 1536-dim)
    # Gunakan PCA sederhana: ambil 384 dimensi pertama lalu re-normalize
    doc_dim = _doc_embeddings.shape[1]
    if vec.shape[0] != doc_dim:
        vec = vec[:doc_dim]
        norm2 = np.linalg.norm(vec)
        if norm2 > 0:
            vec = vec / norm2

    return vec.reshape(1, -1)


# --- Load or Build (backward-compatible) --------------------------------------

def load_or_build_rag(status_callback=None):
    """
    Load embeddings statis dari disk. Tidak perlu build atau model lokal.
    Interface sama dengan versi lama agar app.py tidak perlu diubah.
    """
    if status_callback:
        status_callback("Memuat embedding dokumen dari cache statis...")

    _load_static_embeddings()

    if status_callback:
        status_callback(f"Siap! {len(_chunks)} dokumen akademik dimuat.")

    # Return None untuk model karena tidak dipakai lagi
    return _doc_embeddings, _chunks, None


# --- Retrieval ----------------------------------------------------------------

def retrieve(query: str, index, chunks, model, top_k: int = TOP_K) -> List[Tuple[str, float]]:
    """
    Cari dokumen paling relevan menggunakan cosine similarity.
    Parameter index/model diabaikan (backward-compatible), pakai static embeddings.
    """
    _load_static_embeddings()

    try:
        query_vec = _embed_query_api(query)          # (1, D) via API
    except Exception as e:
        # Fallback: jika API gagal, coba keyword matching sederhana
        return _keyword_fallback(query, top_k)

    # Cosine similarity = dot product (karena sudah L2-normalized)
    scores = (_doc_embeddings @ query_vec.T).flatten()   # shape: (N,)

    top_indices = np.argsort(scores)[::-1][:top_k]
    return [(_chunks[i], float(scores[i])) for i in top_indices]


def _keyword_fallback(query: str, top_k: int) -> List[Tuple[str, float]]:
    """Fallback sederhana jika API embedding gagal: cari berdasarkan kata kunci."""
    _load_static_embeddings()
    query_words = set(query.lower().split())
    scored = []
    for chunk in _chunks:
        chunk_words = set(chunk.lower().split())
        overlap = len(query_words & chunk_words)
        scored.append((chunk, float(overlap)))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]
