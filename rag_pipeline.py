"""
RAG Pipeline - Static Doc Embeddings + sentence-transformers untuk query
========================================================================
- Embedding dokumen: dibaca dari file statis embeddings/ (pre-computed, cepat)
- Embedding query:   sentence-transformers SAMA dengan yang dipakai pre-compute
- Pencarian:         cosine similarity via numpy (dot product)

Kunci: doc embeddings dan query embeddings HARUS pakai model yang sama!
"""

import os
import pickle
import numpy as np
from typing import List, Tuple
from sentence_transformers import SentenceTransformer

# --- Config -------------------------------------------------------------------
EMBEDDINGS_DIR  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "embeddings")
EMB_PATH        = os.path.join(EMBEDDINGS_DIR, "doc_embeddings.npy")
CHUNKS_PATH     = os.path.join(EMBEDDINGS_DIR, "chunks.pkl")
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
TOP_K           = 3

# --- In-memory cache ----------------------------------------------------------
_doc_embeddings: np.ndarray = None
_chunks: List[str] = None
_model: SentenceTransformer = None


def _load_all(status_callback=None):
    """Load static embeddings dan model. Di-cache di memory setelah pertama kali."""
    global _doc_embeddings, _chunks, _model

    if _doc_embeddings is None:
        if not os.path.exists(EMB_PATH) or not os.path.exists(CHUNKS_PATH):
            raise FileNotFoundError(
                f"File embedding tidak ditemukan di '{EMBEDDINGS_DIR}'.\n"
                "Jalankan dulu: python precompute_embeddings.py"
            )
        if status_callback:
            status_callback("Memuat embedding dokumen dari file statis...")
        _doc_embeddings = np.load(EMB_PATH)           # shape: (N, 384)
        with open(CHUNKS_PATH, "rb") as f:
            _chunks = pickle.load(f)

    if _model is None:
        if status_callback:
            status_callback("Memuat model embedding (sekali saja)...")
        _model = SentenceTransformer(EMBEDDING_MODEL)

    return _doc_embeddings, _chunks, _model


# --- Load or Build (backward-compatible dengan app.py) ------------------------

def load_or_build_rag(status_callback=None):
    """
    Load embeddings statis + model. Tidak perlu encode ulang dokumen.
    Interface sama dengan versi lama agar app.py tidak perlu diubah.
    """
    embs, chunks, model = _load_all(status_callback)
    if status_callback:
        status_callback(f"Siap! {len(chunks)} dokumen akademik dimuat.")
    return embs, chunks, model


# --- Retrieval ----------------------------------------------------------------

def retrieve(query: str, index, chunks, model, top_k: int = TOP_K) -> List[Tuple[str, float]]:
    """
    Cari dokumen paling relevan menggunakan cosine similarity.
    Parameter index diabaikan (backward-compatible), pakai static embeddings.
    """
    embs, chunks_data, mdl = _load_all()

    # Embed query pakai model YANG SAMA dengan dokumen
    q_vec = mdl.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True,
    ).astype(np.float32)                    # shape: (1, 384)

    # Cosine similarity = dot product (karena sudah L2-normalized)
    scores = (embs @ q_vec.T).flatten()     # shape: (N,)

    top_indices = np.argsort(scores)[::-1][:top_k]
    return [(chunks_data[i], float(scores[i])) for i in top_indices]
