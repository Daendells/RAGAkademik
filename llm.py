"""
LLM Module — OpenRouter API + Nemotron reasoning (streaming)
"""

import os
import json
from typing import List, Tuple, Generator
import requests
from dotenv import load_dotenv

load_dotenv()


def _get_secret(key: str, default: str = "") -> str:
    """Baca secret dari st.secrets (Streamlit Cloud) atau .env (lokal)."""
    # Coba dari environment variable / .env dulu
    val = os.getenv(key, "")
    if val:
        return val
    # Fallback: coba dari st.secrets (Streamlit Cloud)
    try:
        import streamlit as st
        return st.secrets.get(key, default)
    except Exception:
        return default


OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_API_KEY  = _get_secret("OPENROUTER_API_KEY")
OPENROUTER_MODEL    = _get_secret("OPENROUTER_MODEL", "nvidia/nemotron-3-super-120b-a12b:free")

SYSTEM_ROLE = (
    "Kamu adalah asisten akademik kampus yang membantu mahasiswa. "
    "Jawab pertanyaan SECARA JELAS dan LENGKAP berdasarkan konteks yang diberikan. "
    "Gunakan bahasa Indonesia yang baik. "
    "Jika informasi tidak ada di konteks, katakan dengan jujur bahwa kamu tidak tahu."
)


def check_api_status() -> dict:
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
        return {"ok": False, "error": f"HTTP {r.status_code}"}
    except requests.ConnectionError:
        return {"ok": False, "error": "Tidak dapat terhubung ke OpenRouter"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _build_prompt(question: str, contexts: List[Tuple[str, float]]) -> str:
    ctx = "\n\n".join(f"[Konteks {i}]\n{c}" for i, (c, _) in enumerate(contexts, 1))
    return (
        f"Berikut adalah informasi peraturan akademik yang relevan:\n\n"
        f"{ctx}\n\n"
        f"Pertanyaan mahasiswa: {question}\n\n"
        f"Berikan jawaban yang jelas dan lengkap berdasarkan konteks di atas:"
    )


def stream_answer(question: str, contexts: List[Tuple[str, float]]) -> Generator[str, None, None]:
    """Generator: yield token satu per satu untuk streaming di Streamlit."""
    if not OPENROUTER_API_KEY:
        yield "❌ API key OpenRouter tidak ditemukan. Tambahkan `OPENROUTER_API_KEY` di `.env`."
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
                "max_tokens": 1024,
                "reasoning": {"enabled": True},
                "messages": [
                    {"role": "system", "content": SYSTEM_ROLE},
                    {"role": "user",   "content": _build_prompt(question, contexts)},
                ],
            },
            stream=True,
            timeout=120,
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
                data = json.loads(decoded)
                delta = data.get("choices", [{}])[0].get("delta", {})
                # Skip reasoning tokens, hanya tampilkan content akhir
                token = delta.get("content", "")
                if token:
                    yield token
            except json.JSONDecodeError:
                continue

    except requests.HTTPError as e:
        yield f"\n\n❌ HTTP Error {e.response.status_code}: {e.response.text[:300]}"
    except requests.Timeout:
        yield "\n\n❌ Timeout. Coba lagi."
    except Exception as e:
        yield f"\n\n❌ Error: {e}"


def generate_answer(question: str, contexts: List[Tuple[str, float]]) -> str:
    return "".join(stream_answer(question, contexts))
