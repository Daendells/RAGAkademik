"""
RAG Pipeline — HuggingFace Inference API + FAISS
Embedding via API, tidak ada model lokal yang diunduh
"""

import os
import pickle
import hashlib
import numpy as np
import faiss
import requests
from typing import List, Tuple
from dotenv import load_dotenv

from knowledge_base import get_all_chunks

load_dotenv()

# ─── Config ───────────────────────────────────────────────────────────────────
CACHE_DIR    = os.path.join(os.path.dirname(__file__), ".cache")
HF_API_TOKEN = os.getenv("HF_API_TOKEN", "")
HF_API_URL   = (
    "https://api-inference.huggingface.co/pipeline/feature-extraction/"
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)
TOP_K = 3


# ─── Embedding via HuggingFace API ────────────────────────────────────────────

def _headers() -> dict:
    h = {"Content-Type": "application/json"}
    if HF_API_TOKEN:
        h["Authorization"] = f"Bearer {HF_API_TOKEN}"
    return h


def _embed(texts: List[str], status_callback=None) -> np.ndarray:
    """Embed teks via HuggingFace Inference API (batch kecil agar tidak timeout)."""
    batch_size = 8
    all_vecs   = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        if status_callback:
            total = (len(texts) - 1) // batch_size + 1
            status_callback(f"🌐 Embedding batch {i // batch_size + 1}/{total}…")

        r = requests.post(
            HF_API_URL,
            headers=_headers(),
            json={"inputs": batch, "options": {"wait_for_model": True}},
            timeout=60,
        )
        r.raise_for_status()

        for item in r.json():
            # Tangani token-level output (ambil mean) vs sentence-level
            vec = np.mean(item, axis=0) if isinstance(item[0], list) else item
            all_vecs.append(vec)

    arr   = np.array(all_vecs, dtype=np.float32)
    norms = np.linalg.norm(arr, axis=1, keepdims=True)
    return arr / np.maximum(norms, 1e-8)   # normalize untuk cosine similarity


# ─── Cache ────────────────────────────────────────────────────────────────────

def _cache_key() -> str:
    chunks  = get_all_chunks()
    content = "\n---\n".join(chunks) + HF_API_URL
    return hashlib.md5(content.encode("utf-8")).hexdigest()


def _cache_paths(key: str) -> dict:
    os.makedirs(CACHE_DIR, exist_ok=True)
    return {
        "index":  os.path.join(CACHE_DIR, f"{key}.faiss"),
        "chunks": os.path.join(CACHE_DIR, f"{key}.pkl"),
    }


# ─── Load or Build ────────────────────────────────────────────────────────────

def load_or_build_rag(status_callback=None):
    key   = _cache_key()
    paths = _cache_paths(key)

    if os.path.exists(paths["index"]) and os.path.exists(paths["chunks"]):
        if status_callback: status_callback("📦 Memuat index dari cache…")
        index = faiss.read_index(paths["index"])
        with open(paths["chunks"], "rb") as f:
            chunks = pickle.load(f)
        return index, chunks

    if status_callback: status_callback("📚 Membaca knowledge base akademik…")
    chunks = get_all_chunks()

    embs  = _embed(chunks, status_callback)
    index = faiss.IndexFlatIP(embs.shape[1])
    index.add(embs)

    faiss.write_index(index, paths["index"])
    with open(paths["chunks"], "wb") as f:
        pickle.dump(chunks, f)

    return index, chunks


# ─── Retrieval ────────────────────────────────────────────────────────────────

def retrieve(query: str, index, chunks, top_k: int = TOP_K) -> List[Tuple[str, float]]:
    q_vec = _embed([query])
    scores, idxs = index.search(q_vec, top_k)
    return [(chunks[i], float(s)) for s, i in zip(scores[0], idxs[0]) if i != -1]
