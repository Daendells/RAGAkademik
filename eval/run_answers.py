"""Answer-level evaluation on the frozen question set (calls the LLM; not run in CI).

    python eval/run_answers.py   # writes eval/answers.jsonl and eval/answer_results.md
"""

import asyncio
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv  # noqa: E402

from rag.answer import OpenRouterClient, stream_answer  # noqa: E402
from rag.retrieve import Retriever  # noqa: E402

# A different model family from the answering model, so it does not grade its own style.
JUDGE_MODEL = "google/gemma-4-31b-it:free, nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"


PARTIAL = ROOT / "eval" / "answers.partial.jsonl"


async def answer_all(retriever, client, rows):
    # Each answer is appended as soon as it exists, so an interrupted run resumes where it stopped.
    out = [json.loads(line) for line in open(PARTIAL, encoding="utf-8")] if PARTIAL.exists() else []
    done = {r["id"] for r in out}
    for r in rows:
        if r["id"] in done:
            continue
        start, result, error = time.perf_counter(), None, None
        for attempt in range(3):
            async for event in stream_answer(r["question"], retriever, client):
                if event["type"] == "sources":
                    result = event
                elif event["type"] == "error":
                    error = event["message"]
            if result:
                break
            await asyncio.sleep(10 * (attempt + 1))
        out.append({**r, "seconds": round(time.perf_counter() - start, 1), "error": error,
                    "answer": result and result["answer"], "refused": bool(result and result["refused"]),
                    "cited_pasal": [s["pasal"] for s in result["sources"]] if result else [],
                    "sources": result["sources"] if result else []})
        with open(PARTIAL, "a", encoding="utf-8") as f:
            f.write(json.dumps(out[-1], ensure_ascii=False) + "\n")
        print(r["id"], out[-1]["refused"], out[-1]["cited_pasal"], (out[-1]["answer"] or error or "")[:80])
    return out


async def judge(rows):
    client = OpenRouterClient(model=JUDGE_MODEL)
    template = (ROOT / "eval" / "judge_prompt.md").read_text(encoding="utf-8")
    for r in rows:
        if not r["answerable"] or r["refused"] or not r["answer"]:
            continue
        sources = "\n\n".join(f"({s['citation']})\n{s['text']}" for s in r["sources"]) or "(tidak ada)"
        prompt = template.format(sources=sources, question=r["question"], answer=r["answer"])
        for attempt in range(3):
            try:
                text = "".join([t async for t in client.stream([{"role": "user", "content": prompt}])])
                r["judge"] = json.loads(re.search(r"\{.*\}", text, re.S).group(0))
                break
            except Exception as e:  # rate limits and malformed JSON are retried, then recorded
                r["judge"] = {"faithful": None, "reason": f"judge failed: {type(e).__name__}"}
                await asyncio.sleep(10 * (attempt + 1))


def report(rows):
    ans = [r for r in rows if r["answerable"]]
    una = [r for r in rows if not r["answerable"]]
    answered = [r for r in ans if not r["refused"] and r["answer"]]
    correct = [r for r in answered if set(r["cited_pasal"]) & set(r["gold_pasal"])]
    judged = [r for r in answered if r.get("judge", {}).get("faithful") is not None]
    faithful = [r for r in judged if r["judge"]["faithful"]]
    pct = lambda a, b: f"{100 * len(a) / len(b):.0f}% ({len(a)}/{len(b)})" if b else "n/a"
    lines = [
        "# Answer results",
        "",
        f"Answering models: `{OpenRouterClient().models}`. Judge: `{JUDGE_MODEL}`.",
        "",
        "| Metric | Value |",
        "| --- | --- |",
        f"| Answerable questions answered (not refused) | {pct(answered, ans)} |",
        f"| Answers citing at least one gold Pasal | {pct(correct, answered)} |",
        f"| Answers judged faithful to their sources | {pct(faithful, judged)} |",
        f"| Unanswerable questions correctly refused | {pct([r for r in una if r['refused']], una)} |",
        f"| Requests that failed after retries | {len([r for r in rows if r['error'] and not r['answer']])} |",
        f"| Median seconds per answer | {sorted(r['seconds'] for r in rows)[len(rows) // 2]} |",
    ]
    (ROOT / "eval" / "answer_results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


async def main():
    load_dotenv(ROOT / ".env")
    rows = [json.loads(line) for line in open(ROOT / "eval" / "questions.jsonl", encoding="utf-8")]
    out = await answer_all(Retriever.load(ROOT / "data"), OpenRouterClient(), rows)
    await judge(out)
    with open(ROOT / "eval" / "answers.jsonl", "w", encoding="utf-8") as f:
        for r in out:
            f.write(json.dumps({k: v for k, v in r.items() if k != "sources"}, ensure_ascii=False) + "\n")
    report(out)


if __name__ == "__main__":
    asyncio.run(main())
