"""
LLM Module — OpenRouter API (streaming)
Mendukung ratusan model via satu API key
"""

import os
import json
from typing import List, Tuple, Generator
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_API_KEY  = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL    = os.getenv("OPENROUTER_MODEL", "google/gemma-3-4b-it:free")

SYSTEM_ROLE = (
    "Kamu adalah asisten akademik kampus yang membantu mahasiswa. "
    "Jawab pertanyaan SECARA JELAS dan LENGKAP berdasarkan konteks yang diberikan. "
    "Gunakan bahasa Indonesia yang baik. "
    "Jika informasi tidak ada di konteks, katakan dengan jujur bahwa kamu tidak tahu."
)


def check_api_status() -> dict:
    """Cek apakah API key valid dan model tersedia."""
    if not OPENROUTER_API_KEY:
        return {"ok": False, "error": "API key tidak ditemukan di .env"}
    try:
        r = requests.get(
            f"{OPENROUTER_BASE_URL}/models",
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
            timeout=5,
        )
        if r.status_code == 200:
            return {"ok": True, "error": "", "model": OPENROUTER_MODEL}
        return {"ok": False, "error": f"HTTP {r.status_code}: {r.text[:100]}"}
    except requests.ConnectionError:
        return {"ok": False, "error": "Tidak dapat terhubung ke OpenRouter"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _build_prompt(question: str, contexts: List[Tuple[str, float]]) -> str:
    ctx = "\n\n".join(f"[Konteks {i}]\n{c}" for i, (c, _) in enumerate(contexts, 1))
    return (
        f"Berikut adalah informasi yang relevan:\n\n"
        f"{ctx}\n\n"
        f"Pertanyaan mahasiswa: {question}\n\n"
        f"Berikan jawaban yang jelas dan lengkap:"
    )


def stream_answer(question: str, contexts: List[Tuple[str, float]]) -> Generator[str, None, None]:
    """Generator: yield token satu per satu untuk streaming di Streamlit."""
    if not OPENROUTER_API_KEY:
        yield "❌ API key OpenRouter tidak ditemukan. Pastikan `.env` sudah berisi `OPENROUTER_API_KEY`."
        return

    try:
        r = requests.post(
            f"{OPENROUTER_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/Daendells/RAGAkademik",
                "X-Title": "RAG Akademik",
            },
            json={
                "model": OPENROUTER_MODEL,
                "stream": True,
                "temperature": 0.2,
                "max_tokens": 512,
                "messages": [
                    {"role": "system", "content": SYSTEM_ROLE},
                    {"role": "user",   "content": _build_prompt(question, contexts)},
                ],
            },
            stream=True,
            timeout=60,
        )
        r.raise_for_status()

        for line in r.iter_lines():
            if not line:
                continue
            decoded = line.decode("utf-8")
            if decoded.startswith("data: "):
                decoded = decoded[6:]
            if decoded.strip() == "[DONE]":
                break
            try:
                data  = json.loads(decoded)
                token = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                if token:
                    yield token
            except json.JSONDecodeError:
                continue

    except requests.HTTPError as e:
        yield f"\n\n❌ HTTP Error {e.response.status_code}: {e.response.text[:200]}"
    except requests.Timeout:
        yield "\n\n❌ Timeout. Coba lagi."
    except Exception as e:
        yield f"\n\n❌ Error: {e}"


# Backward compat non-streaming
def generate_answer(question: str, contexts: List[Tuple[str, float]]) -> str:
    return "".join(stream_answer(question, contexts))
