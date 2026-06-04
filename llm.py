"""
LLM Module — Ollama streaming
"""

import os, json
from typing import List, Tuple, Generator
import requests

OLLAMA_BASE_URL = os.getenv("OLLAMA_HOST", "http://localhost:11434")
#OLLAMA_MODEL    = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
OLLAMA_MODEL    = os.getenv("OLLAMA_MODEL", "gemma3:latest")

# Prompt sederhana — model kecil tidak mampu mengikuti instruksi panjang
SYSTEM_ROLE = (
    "Kamu asisten akademik. "
    "Jawab SINGKAT dan JELAS berdasarkan konteks yang diberikan. "
    "Gunakan bahasa Indonesia. "
    "Jika tidak ada di konteks, katakan tidak tahu."
)


def check_ollama_status() -> dict:
    try:
        r      = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=3)
        models = [m["name"] for m in r.json().get("models", [])]
        avail  = any(OLLAMA_MODEL.split(":")[0] in m for m in models)
        return {"running": True, "model_available": avail, "models": models, "error": ""}
    except requests.ConnectionError:
        return {"running": False, "model_available": False, "models": [],
                "error": "Ollama tidak berjalan"}
    except Exception as e:
        return {"running": False, "model_available": False, "models": [], "error": str(e)}


def _build_prompt(question: str, contexts: List[Tuple[str, float]]) -> str:
    ctx = "\n\n".join(f"[{i}] {c[:400]}" for i, (c, _) in enumerate(contexts, 1))
    return f"Konteks:\n{ctx}\n\nPertanyaan: {question}\n\nJawab singkat:"


def stream_answer(question: str, contexts: List[Tuple[str, float]]) -> Generator[str, None, None]:
    """Generator: yield token satu per satu untuk streaming di Streamlit."""
    status = check_ollama_status()

    if not status["running"]:
        yield "❌ Ollama tidak berjalan. Jalankan: `ollama serve`"
        return
    if not status["model_available"]:
        yield f"❌ Model `{OLLAMA_MODEL}` tidak ditemukan. Jalankan: `ollama pull {OLLAMA_MODEL}`"
        return

    try:
        r = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json={
                "model":  OLLAMA_MODEL,
                "stream": True,                # ← streaming aktif
                "options": {
                    "temperature": 0.1,
                    "num_predict": 300,        # batasi panjang jawaban
                    "top_p": 0.85,
                },
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
            data  = json.loads(line.decode("utf-8"))
            token = data.get("message", {}).get("content", "")
            if token:
                yield token
            if data.get("done"):
                break

    except requests.Timeout:
        yield "\n\n❌ Timeout. Coba lagi."
    except Exception as e:
        yield f"\n\n❌ Error: {e}"


# Backward compat untuk non-streaming (dipakai di source expander)
def generate_answer(question: str, contexts: List[Tuple[str, float]]) -> str:
    return "".join(stream_answer(question, contexts))
