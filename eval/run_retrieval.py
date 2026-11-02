"""Compare retrieval setups on the frozen question set.

    python eval/run_retrieval.py            # full comparison -> eval/retrieval_results.md
    python eval/run_retrieval.py --check    # CI: the shipped index must not regress
"""

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402

from rag.encoders import load_encoder, load_reranker  # noqa: E402
from rag.ingest import read_chunks  # noqa: E402
from rag.metrics import summarize  # noqa: E402
from rag.retrieve import Retriever  # noqa: E402

ENCODERS = ["intfloat/multilingual-e5-small", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"]
RERANKER = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"
BASELINE = ROOT / "eval" / "retrieval_baseline.json"
MAX_MRR_DROP = 0.02


def questions():
    rows = [json.loads(line) for line in open(ROOT / "eval" / "questions.jsonl", encoding="utf-8")]
    return [r for r in rows if r["answerable"]]


def evaluate(retriever, mode, qs, k=10):
    rows, times = [], []
    for q in qs:
        start = time.perf_counter()
        hits = retriever.search(q["question"], k=k, mode=mode)
        times.append(time.perf_counter() - start)
        rows.append({"ranked": [h.chunk.pasal for h in hits], "gold": q["gold_pasal"], "id": q["id"]})
    out = summarize(rows)
    out["p50_ms"] = round(1000 * float(np.median(times)))
    out["p95_ms"] = round(1000 * float(np.percentile(times, 95)))
    misses = [r["id"] for r in rows if not set(r["ranked"][:5]) & set(r["gold"])]
    return out, misses


def compare():
    chunks, qs = read_chunks(ROOT / "data" / "chunks.jsonl"), questions()
    reranker = load_reranker(RERANKER)
    results = []
    for name in ENCODERS:
        enc = load_encoder(name)
        retriever = Retriever(chunks, enc.encode_passages([c.text for c in chunks]), enc, reranker=reranker)
        for mode in ("bm25", "dense", "hybrid", "hybrid_rerank"):
            if mode == "bm25" and results:
                continue  # BM25 does not depend on the encoder
            summary, misses = evaluate(retriever, mode, qs)
            label = "—" if mode == "bm25" else name.split("/")[-1]
            results.append({"mode": mode, "encoder": label, **summary, "misses@5": misses})
            print(results[-1])
    lines = [
        f"# Retrieval results ({len(qs)} answerable questions, CPU)",
        "",
        "| Mode | Encoder | hit@1 | hit@3 | hit@5 | MRR | p50 ms | p95 ms |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in results:
        lines.append(
            f"| {r['mode']} | {r['encoder']} | {r['hit@1']:.2f} | {r['hit@3']:.2f} | {r['hit@5']:.2f} "
            f"| {r['mrr']:.3f} | {r['p50_ms']} | {r['p95_ms']} |"
        )
    lines += ["", "Questions missed in the top 5:", ""]
    lines += [f"- {r['mode']} / {r['encoder']}: {', '.join(r['misses@5']) or 'none'}" for r in results]
    (ROOT / "eval" / "retrieval_results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def check():
    retriever = Retriever.load(ROOT / "data")
    summary, _ = evaluate(retriever, retriever.default_mode, questions())
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    print(f"MRR {summary['mrr']:.3f} (baseline {baseline['mrr']:.3f})")
    if summary["mrr"] < baseline["mrr"] - MAX_MRR_DROP:
        sys.exit(f"retrieval regressed: MRR {summary['mrr']:.3f} < {baseline['mrr']:.3f} - {MAX_MRR_DROP}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    check() if parser.parse_args().check else compare()
