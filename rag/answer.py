"""Grounded answers: the model may only cite retrieved chunks, and the server checks that it did."""

from __future__ import annotations

import json
import os
import re
from collections.abc import AsyncIterator
from typing import Protocol

import httpx

from rag.models import Chunk
from rag.retrieve import Hit

REFUSAL = "Informasi ini tidak ditemukan dalam Peraturan Akademik ITS 2025."
ERROR_MESSAGE = "Layanan AI sedang tidak tersedia. Coba lagi beberapa saat lagi."
TOP_K = 5
DEFAULT_MODELS = "nvidia/nemotron-3-ultra-550b-a55b:free, google/gemma-4-31b-it:free"

SYSTEM = f"""Kamu menjawab pertanyaan mahasiswa tentang Peraturan Rektor ITS Nomor 33 Tahun 2025 tentang
Peraturan Akademik. Aturan:
1. Jawab hanya dari kutipan peraturan yang diberikan. Jangan memakai pengetahuan lain.
2. Setiap kalimat yang berisi aturan diakhiri label kutipan sumbernya, misalnya [C1] atau [C2][C3].
3. Jika kutipan tidak memuat jawabannya, balas persis: "{REFUSAL}"
4. Jawab dalam bahasa Indonesia yang singkat dan jelas. Sebutkan angka (sks, semester, nilai) persis seperti di
   kutipan. Teks kutipan berasal dari hasil OCR, jadi abaikan salah ketik kecil.
5. Jika pertanyaan tidak menyebut jenjang, jawab untuk Program Sarjana (S1). Tambahkan satu kalimat bahwa
   jenjang lain diatur berbeda hanya bila kutipannya memuat aturan jenjang lain.
6. Boleh memakai **tebal** untuk angka penting dan daftar berawalan "- ". Jangan memakai judul atau tabel."""


class LLMClient(Protocol):
    def stream(self, messages: list[dict]) -> AsyncIterator[str]: ...


def build_prompt(question: str, hits: list[Hit]) -> list[dict]:
    context = "\n\n".join(f"[C{i}] ({h.chunk.citation()})\n{h.chunk.text}" for i, h in enumerate(hits, start=1))
    return [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": f"Kutipan peraturan:\n\n{context}\n\nPertanyaan: {question}"},
    ]


def parse_citations(text: str, hits: list[Hit]) -> tuple[str, list[Chunk], bool]:
    """Replace [Cn] labels with [1], [2]... in order of first use; drop labels for unretrieved chunks."""
    order: list[int] = []

    def renumber(match: re.Match) -> str:
        n = int(match.group(1))
        if not 1 <= n <= len(hits):
            return ""
        if n not in order:
            order.append(n)
        return f"[{order.index(n) + 1}]"

    clean = re.sub(r"\[C(\d+)\]", renumber, text)
    clean = re.sub(r"\s+([.,;])", r"\1", clean).strip()
    cited = [hits[n - 1].chunk for n in order]
    return clean, cited, bool(cited)


def _source(chunk: Chunk) -> dict:
    return {"id": chunk.id, "pasal": chunk.pasal, "citation": chunk.citation(), "bab": chunk.bab, "text": chunk.text}


async def stream_answer(question: str, retriever, client: LLMClient) -> AsyncIterator[dict]:
    hits = retriever.search(question, k=TOP_K)
    if not hits:
        yield {"type": "token", "text": REFUSAL}
        yield {"type": "sources", "answer": REFUSAL, "sources": [], "cited": False, "refused": True}
        yield {"type": "done"}
        return

    parts: list[str] = []
    try:
        async for token in client.stream(build_prompt(question, hits)):
            parts.append(token)
            yield {"type": "token", "text": token}
    except httpx.HTTPError:
        yield {"type": "error", "message": ERROR_MESSAGE}
        yield {"type": "done"}
        return

    raw = "".join(parts)
    refused = REFUSAL.rstrip(".") in raw
    answer, cited, ok = parse_citations(raw, hits)
    if refused:
        answer, cited, ok = REFUSAL, [], False
    yield {"type": "sources", "answer": answer, "sources": [_source(c) for c in cited], "cited": ok, "refused": refused}
    yield {"type": "done"}


class StreamError(httpx.HTTPError):
    """An error the provider reported inside a 200 stream."""


def parse_stream_line(line: str) -> str | None:
    """Return the text delta of one SSE line; comments, usage-only chunks and [DONE] give None."""
    if not line.startswith("data: ") or line == "data: [DONE]":
        return None
    data = json.loads(line[6:])
    if "error" in data:
        raise StreamError(str(data["error"].get("message", data["error"])))
    choices = data.get("choices") or []
    return (choices[0].get("delta") or {}).get("content") if choices else None


class OpenRouterClient:
    url = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(self, api_key: str | None = None, model: str | None = None, timeout: float = 30.0):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY", "")
        # Comma-separated list: OpenRouter tries the next model when one is rate-limited or down.
        names = model or os.getenv("OPENROUTER_MODEL") or DEFAULT_MODELS
        self.models = [m.strip() for m in names.split(",") if m.strip()]
        self.timeout = timeout

    def payload(self, messages: list[dict]) -> dict:
        return {"models": self.models, "messages": messages, "stream": True, "temperature": 0}

    async def stream(self, messages: list[dict]) -> AsyncIterator[str]:
        payload = self.payload(messages)
        headers = {"Authorization": f"Bearer {self.api_key}", "X-Title": "RAG Akademik ITS"}
        async with httpx.AsyncClient(timeout=self.timeout) as http:
            async with http.stream("POST", self.url, json=payload, headers=headers) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    delta = parse_stream_line(line)
                    if delta:
                        yield delta
