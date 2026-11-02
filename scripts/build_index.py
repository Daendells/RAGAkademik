"""Rebuild data/chunks.jsonl, data/embeddings.npy and data/index.json from the regulation PDF."""

import argparse
import json
from pathlib import Path

import numpy as np

from rag.encoders import load_encoder
from rag.ingest import chunk_regulation, extract_pages, write_chunks

DATA = Path(__file__).resolve().parent.parent / "data"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--encoder", required=True)
    parser.add_argument("--mode", required=True, choices=["bm25", "dense", "hybrid", "hybrid_rerank"])
    parser.add_argument("--reranker", default=None)
    args = parser.parse_args()

    chunks = chunk_regulation(extract_pages(DATA / "peraturan-rektor-33-2025.pdf"), doc_id="pr33")
    write_chunks(chunks, DATA / "chunks.jsonl")
    embeddings = load_encoder(args.encoder).encode_passages([c.text for c in chunks])
    np.save(DATA / "embeddings.npy", embeddings.astype(np.float32))
    config = {"encoder": args.encoder, "mode": args.mode, "reranker": args.reranker}
    (DATA / "index.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    print(f"{len(chunks)} chunks, embeddings {embeddings.shape}, config {config}")


if __name__ == "__main__":
    main()
