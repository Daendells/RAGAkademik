"""Streamlit front end for the free Streamlit Community Cloud demo.

It runs the same retrieval and answer code as the FastAPI app in app/; only the page is different.
"""

import re
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from rag.answer import OpenRouterClient, stream_answer_sync  # noqa: E402
from rag.retrieve import Retriever  # noqa: E402

EXAMPLES = [
    "Berapa semester maksimal boleh cuti untuk mahasiswa S1?",
    "Sampai minggu ke berapa saya masih bisa mengubah FRS?",
    "Berapa skor TOEFL minimal untuk daftar sidang TA S1?",
    "Apa syarat lulus program sarjana?",
]

st.set_page_config(page_title="Asisten Peraturan Akademik ITS", page_icon="📘", layout="centered")


@st.cache_resource(show_spinner="Menyiapkan model pencarian…")
def load():
    # Streamlit Cloud exposes root-level secrets as environment variables, which OpenRouterClient reads.
    return Retriever.load(ROOT / "data"), OpenRouterClient()


st.title("Asisten Peraturan Akademik ITS")
st.write(
    "Tanya aturan akademik ITS, misalnya batas sks, cuti, atau syarat lulus. Jawaban disusun dari teks "
    "Peraturan Rektor ITS Nomor 33 Tahun 2025 dan selalu menyebut pasal sumbernya."
)

retriever, client = load()

columns = st.columns(2)
for i, example in enumerate(EXAMPLES):
    if columns[i % 2].button(example, use_container_width=True):
        st.session_state.question = example

question = st.chat_input("Contoh: berapa sks maksimal kalau IPS saya 3,2?", max_chars=500)
question = question or st.session_state.pop("question", None)

if question:
    st.markdown(f"**Pertanyaan:** {question}")
    placeholder, streamed, final = st.empty(), "", None
    with st.spinner("Mencari pasal yang relevan…"):
        for event in stream_answer_sync(question.strip(), retriever, client):
            if event["type"] == "token":
                streamed += event["text"]
                placeholder.markdown(re.sub(r"\[C\d+\]", "", streamed))
            elif event["type"] == "sources":
                final = event
            elif event["type"] == "error":
                placeholder.error(event["message"])
    if final:
        placeholder.markdown(final["answer"])
        if final["sources"]:
            st.markdown("**Sumber**")
            for n, source in enumerate(final["sources"], start=1):
                with st.expander(f"[{n}] {source['citation']}"):
                    st.text(source["text"])
        elif not final["refused"]:
            st.info("Jawaban ini tidak menyebut pasal. Cek peraturan aslinya.")

st.caption("Jawaban disusun oleh AI dari teks peraturan. Cek pasal aslinya sebelum mengambil keputusan.")
st.caption(
    "Sumber: [Peraturan Akademik ITS 2025](https://www.its.ac.id/pendidikan/2026/01/23/peraturan-akademik-tahun-2025/)"
    " · [Kode dan hasil evaluasi](https://github.com/Daendells/RAGAkademik)"
)
