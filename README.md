# RAG Akademik — Asisten Peraturan Kampus

Aplikasi AI Chatbot berbasis **Retrieval Augmented Generation (RAG)** untuk membantu mahasiswa memahami peraturan akademik kampus.

## 🏗️ Struktur Proyek

```
RAGAkademik/
├── app.py                  ← Aplikasi Streamlit (frontend chatbot)
├── rag_pipeline.py         ← Pipeline RAG (PDF loading, chunking, embedding, FAISS)
├── llm.py                  ← Integrasi Google Gemini API
├── requirements.txt        ← Daftar dependensi Python
├── .env.example            ← Template konfigurasi API key
├── .env                    ← File API key Anda (buat sendiri!)
├── SALINAN_Peraturan-...pdf ← Dokumen peraturan akademik
└── .cache/                 ← Cache FAISS index (auto-generated)
```

## ⚙️ Cara Setup

### 1. Install Dependensi

```bash
cd RAGAkademik
pip install -r requirements.txt
```

### 2. Konfigurasi API Key Gemini

**Buat file `.env`** di folder `RAGAkademik/` (bukan `.env.example`):

```
GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

> **Cara mendapatkan API Key (GRATIS):**
> 1. Buka https://aistudio.google.com/app/apikey
> 2. Login dengan akun Google
> 3. Klik **"Create API key"**
> 4. Salin key dan tempelkan di file `.env`

### 3. Jalankan Aplikasi

```bash
streamlit run app.py
```

Aplikasi akan terbuka otomatis di browser: `http://localhost:8501`

## 🚀 Cara Kerja (Arsitektur RAG)

```
PDF Dokumen
    ↓  (PyPDF)
Ekstraksi Teks
    ↓  (Chunking 600 char, overlap 100)
Chunk-chunk Teks
    ↓  (Sentence Transformers: multilingual-MiniLM)
Embedding Vectors
    ↓  (FAISS IndexFlatIP)
Vector Database
    
Pertanyaan User → Embedding → FAISS Search → Top-5 Chunks
                                                    ↓
                                          Gemini 1.5 Flash API
                                                    ↓
                                            Jawaban AI 🎓
```

## 💡 Fitur Utama

- ✅ Membaca dan mengekstrak isi PDF peraturan akademik
- ✅ Text chunking dengan overlap untuk konteks yang baik
- ✅ Embedding multilingual (mendukung Bahasa Indonesia)
- ✅ FAISS vector database dengan disk cache (tidak perlu rebuild setiap restart)
- ✅ Semantic similarity search (Top-K chunks)
- ✅ Jawaban berbasis dokumen via Gemini API (anti-hallucination)
- ✅ Transparansi sumber — tampilkan chunk yang digunakan
- ✅ UI chatbot modern dengan dark theme

## 📝 Contoh Pertanyaan

- "Berapa maksimal SKS yang dapat diambil?"
- "Apa syarat cuti akademik?"
- "Bagaimana aturan seminar proposal?"
- "Apa konsekuensi jika IPK di bawah 2.0?"
- "Bagaimana prosedur pengisian FRS?"
