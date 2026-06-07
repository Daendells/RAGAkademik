"""
PRE-COMPUTE EMBEDDINGS - Jalankan SEKALI di lokal sebelum deploy!
=================================================================
Script ini membaca knowledge_base.py, menghitung embedding semua dokumen
menggunakan sentence-transformers, lalu menyimpannya sebagai file statis
di folder embeddings/.

Setelah selesai, kamu bisa:
  1. Commit folder embeddings/ ke GitHub
  2. Deploy ke Streamlit Cloud - TIDAK perlu model lokal lagi!

Cara menjalankan:
  python precompute_embeddings.py
"""

import os
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer

from knowledge_base import get_all_chunks

# --- Config -------------------------------------------------------------------
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
OUTPUT_DIR      = os.path.join(os.path.dirname(os.path.abspath(__file__)), "embeddings")

# --- Main ---------------------------------------------------------------------

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("[1/4] Membaca knowledge base...")
    chunks = get_all_chunks()
    print(f"   -> {len(chunks)} dokumen ditemukan")

    print(f"\n[2/4] Memuat model: {EMBEDDING_MODEL}")
    print("   (Download otomatis jika belum ada, ~500MB, tunggu sebentar...)")
    model = SentenceTransformer(EMBEDDING_MODEL)

    print(f"\n[3/4] Menghitung embedding untuk {len(chunks)} dokumen...")
    embeddings = model.encode(
        chunks,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,   # L2-normalize untuk cosine similarity via dot product
        batch_size=32,
    ).astype(np.float32)

    print(f"   -> Shape embedding: {embeddings.shape}")

    # Simpan sebagai file statis
    emb_path    = os.path.join(OUTPUT_DIR, "doc_embeddings.npy")
    chunks_path = os.path.join(OUTPUT_DIR, "chunks.pkl")

    np.save(emb_path, embeddings)
    with open(chunks_path, "wb") as f:
        pickle.dump(chunks, f)

    print(f"\n[4/4] SELESAI!")
    print(f"   Embeddings : {emb_path}  ({os.path.getsize(emb_path) / 1024:.1f} KB)")
    print(f"   Chunks     : {chunks_path}  ({os.path.getsize(chunks_path) / 1024:.1f} KB)")
    print(f"\nLangkah selanjutnya:")
    print(f"   1. git add embeddings/")
    print(f"   2. git commit -m 'Add pre-computed embeddings'")
    print(f"   3. git push")
    print(f"   4. Deploy ke Streamlit Cloud - tidak perlu model lokal!")


if __name__ == "__main__":
    main()
