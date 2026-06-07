"""
RAG Akademik — Streamlit Chatbot
"""

import streamlit as st
from rag_pipeline import load_or_build_rag, retrieve
from llm import stream_answer, check_api_status, OPENROUTER_MODEL

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RAG Akademik",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS — minimal, hanya untuk elemen kustom ─────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* ── Sembunyikan elemen bawaan Streamlit Cloud ── */
#MainMenu              { visibility: hidden; }
header                 { visibility: hidden; }
footer                 { visibility: hidden; }
[data-testid="stToolbar"]          { display: none !important; }
[data-testid="stDecoration"]       { display: none !important; }
[data-testid="stStatusWidget"]     { display: none !important; }
[data-testid="manage-app-button"]  { display: none !important; }

/* Font global */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* Header banner kustom */
.rag-header {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 55%, #2563eb 100%);
    border-radius: 14px;
    padding: 22px 30px;
    margin-bottom: 20px;
    box-shadow: 0 6px 30px rgba(79, 70, 229, 0.45);
}
.rag-header h1 {
    color: #ffffff;
    font-size: 1.55rem;
    font-weight: 700;
    margin: 0 0 5px 0;
    line-height: 1.3;
}
.rag-header p {
    color: rgba(255,255,255,0.85);
    margin: 0;
    font-size: 0.88rem;
    line-height: 1.5;
}

/* Tombol sidebar contoh pertanyaan */
section[data-testid="stSidebar"] .stButton > button {
    background: rgba(99, 102, 241, 0.15) !important;
    border: 1px solid rgba(99, 102, 241, 0.4) !important;
    border-radius: 8px !important;
    text-align: left !important;
    font-size: 0.82rem !important;
    padding: 8px 12px !important;
    transition: background 0.2s ease !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(99, 102, 241, 0.35) !important;
}

/* Tombol hapus percakapan */
.stButton > button[kind="secondary"] {
    border-radius: 8px !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-thumb { background: #4f46e5; border-radius: 3px; }
::-webkit-scrollbar-track { background: transparent; }
</style>
""", unsafe_allow_html=True)


# ─── Session State ────────────────────────────────────────────────────────────
defaults = {
    "messages": [],
    "rag_ready": False,
    "index": None,
    "chunks": None,
    "embed_model": None,
    "total_chunks": 0,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎓 RAG Akademik")
    st.caption("Asisten Peraturan Kampus — Ollama")
    st.divider()

    # Status OpenRouter
    api = check_api_status()
    if api["ok"]:
        st.success(f"✅ OpenRouter siap · `{OPENROUTER_MODEL}`")
    else:
        st.error(f"❌ {api['error']}")

    st.divider()

    # Status RAG
    st.markdown("**📊 Status Sistem**")
    col1, col2 = st.columns(2)
    col1.metric("Chunks", st.session_state.total_chunks if st.session_state.rag_ready else "—")
    col2.metric("Pesan", len(st.session_state.messages))

    if st.session_state.rag_ready:
        st.success("✅ Index siap")
    else:
        st.info("⏳ Memuat index…")

    st.divider()

    # Contoh pertanyaan
    st.markdown("**💡 Contoh Pertanyaan**")
    examples = [
        "Berapa maksimal SKS yang bisa diambil?",
        "Apa syarat dan prosedur cuti akademik?",
        "Bagaimana aturan seminar proposal skripsi?",
        "Apa konsekuensi IPK di bawah 2.0?",
        "Bagaimana cara urus surat keterangan aktif?",
        "Apa syarat wisuda dan predikat kelulusan?",
        "Bagaimana cara dapat beasiswa prestasi?",
    ]
    for q in examples:
        if st.button(q, key=f"ex_{q[:18]}", use_container_width=True):
            st.session_state["_prefill"] = q
            st.rerun()

    st.divider()

    if st.button("🗑️ Hapus Percakapan", use_container_width=True, type="secondary"):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption(
        "📚 Knowledge Base: 30+ topik akademik\n"
        f"🤖 LLM: `{OPENROUTER_MODEL}`\n"
        "🔍 Embedding: multilingual-MiniLM-L12"
    )


# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="rag-header">
    <h1>🎓 RAG Akademik — Asisten Peraturan Kampus</h1>
    <p>Tanyakan seputar SKS, nilai, cuti, skripsi, beasiswa, wisuda, dan peraturan akademik lainnya.</p>
</div>
""", unsafe_allow_html=True)


# ─── Load RAG Index ───────────────────────────────────────────────────────────
if not st.session_state.rag_ready:
    _status = st.empty()
    def _cb(msg): _status.info(msg)
    try:
        idx, chunks, em = load_or_build_rag(status_callback=_cb)
        st.session_state.update({
            "index": idx, "chunks": chunks, "embed_model": em,
            "total_chunks": len(chunks), "rag_ready": True,
        })
        _status.success(f"✅ Siap! **{len(chunks)}** dokumen berhasil diindex.", icon="🎉")
    except Exception as e:
        _status.error(f"❌ Error memuat RAG: {e}"); st.stop()


# ─── Riwayat Chat ─────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    avatar = "🧑‍🎓" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("sources"):
            with st.expander(f"📚 Lihat {len(msg['sources'])} sumber konteks"):
                for i, (chunk, score) in enumerate(msg["sources"], 1):
                    st.caption(f"Konteks {i} · relevansi {score:.1%}")
                    st.text(chunk[:380] + ("…" if len(chunk) > 380 else ""))
                    if i < len(msg["sources"]):
                        st.divider()


# ─── Input ────────────────────────────────────────────────────────────────────
prefill    = st.session_state.pop("_prefill", None)
user_input = st.chat_input("Tanyakan tentang peraturan akademik…")

if user_input is None and prefill:
    user_input = prefill

if user_input and user_input.strip():
    question = user_input.strip()

    # Pesan user
    with st.chat_message("user", avatar="🧑‍🎓"):
        st.markdown(question)
    st.session_state.messages.append({"role": "user", "content": question})

    # Retrieval
    contexts = retrieve(
        question,
        st.session_state.index,
        st.session_state.chunks,
        st.session_state.embed_model,
    )

    # Streaming jawaban AI
    with st.chat_message("assistant", avatar="🤖"):
        full_response = st.write_stream(stream_answer(question, contexts))

        if contexts:
            with st.expander(f"📚 {len(contexts)} sumber konteks yang digunakan"):
                for i, (chunk, score) in enumerate(contexts, 1):
                    st.caption(f"Konteks {i} · relevansi {score:.1%}")
                    st.text(chunk[:380] + ("…" if len(chunk) > 380 else ""))
                    if i < len(contexts):
                        st.divider()

    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response,
        "sources": contexts,
    })
