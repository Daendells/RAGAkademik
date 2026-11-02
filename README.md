# RAG Akademik — Campus Regulation Assistant

A Retrieval-Augmented Generation (RAG) chatbot that answers students' questions about academic rules in Indonesian:
credit (SKS) limits, grading, academic leave, thesis requirements, sanctions, scholarships, and graduation.

**Live app:** https://ragakademik.streamlit.app/ (the interface is in Indonesian)

## How it works

1. **Knowledge base.** `knowledge_base.py` holds 30 hand-written summaries of common academic regulations,
   grouped into 11 categories. They are illustrative summaries, not the official text of a specific university.
2. **Embeddings, computed once.** `precompute_embeddings.py` encodes every entry with
   `paraphrase-multilingual-MiniLM-L12-v2` and saves the vectors to `embeddings/`, so the deployed app never
   re-encodes the documents.
3. **Retrieval.** Each question is encoded with the same model; cosine similarity (a dot product on normalised
   vectors) picks the 3 most relevant entries.
4. **Answer.** The question and the retrieved entries go to an LLM through the OpenRouter API, with an instruction
   to answer only from that context and to say so when the answer is not there. The reply streams into the chat.

```
question ──► embed ──► top-3 entries ──► prompt + context ──► LLM (OpenRouter) ──► streamed answer
```

| File | Role |
| --- | --- |
| `app.py` | Streamlit chat interface with example questions |
| `knowledge_base.py` | The 30 regulation entries |
| `precompute_embeddings.py` | Builds `embeddings/doc_embeddings.npy` and `embeddings/chunks.pkl` |
| `rag_pipeline.py` | Loads the embeddings and retrieves the closest entries |
| `llm.py` | Builds the prompt and streams the OpenRouter response |

## Run locally

```bash
pip install -r requirements.txt
cp .env.example .env          # then put your OpenRouter key in .env
python precompute_embeddings.py   # only after editing knowledge_base.py
streamlit run app.py
```

On Streamlit Community Cloud, set `OPENROUTER_API_KEY` (and optionally `OPENROUTER_MODEL`) as app secrets.

## Limitations

- Answers are only as good as the 30 summaries; anything outside them gets an "I don't know" answer.
- The summaries are general and may differ from a given campus's current rules, so treat answers as a starting
  point and check the official regulation.
