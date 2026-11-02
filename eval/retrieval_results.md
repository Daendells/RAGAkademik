# Retrieval results (60 answerable questions, CPU)

| Mode | Encoder | hit@1 | hit@3 | hit@5 | MRR | p50 ms | p95 ms |
| --- | --- | --- | --- | --- | --- | --- | --- |
| bm25 | — | 0.70 | 0.88 | 0.95 | 0.805 | 0 | 0 |
| dense | multilingual-e5-small | 0.73 | 0.87 | 0.90 | 0.801 | 20 | 69 |
| hybrid | multilingual-e5-small | 0.80 | 0.88 | 0.93 | 0.850 | 21 | 34 |
| hybrid_rerank | multilingual-e5-small | 0.85 | 0.92 | 0.97 | 0.893 | 1792 | 2881 |
| dense | paraphrase-multilingual-MiniLM-L12-v2 | 0.52 | 0.73 | 0.83 | 0.648 | 17 | 25 |
| hybrid | paraphrase-multilingual-MiniLM-L12-v2 | 0.72 | 0.88 | 0.95 | 0.819 | 17 | 22 |
| hybrid_rerank | paraphrase-multilingual-MiniLM-L12-v2 | 0.88 | 0.93 | 0.98 | 0.918 | 1741 | 2317 |

Questions missed in the top 5:

- bm25 / —: q009, q023, q054
- dense / multilingual-e5-small: q023, q034, q035, q054, q059, q060
- hybrid / multilingual-e5-small: q023, q035, q054, q059, q060
- hybrid_rerank / multilingual-e5-small: q023, q054
- dense / paraphrase-multilingual-MiniLM-L12-v2: q007, q027, q028, q029, q033, q036, q038, q054, q059, q060
- hybrid / paraphrase-multilingual-MiniLM-L12-v2: q028, q054, q060
- hybrid_rerank / paraphrase-multilingual-MiniLM-L12-v2: q054

## Shipped runtime

The app runs the quantised ONNX export of multilingual-e5-small (`onnx/model_qint8_avx512_vnni.onnx`, 118 MB)
with a SentencePiece tokenizer instead of PyTorch, so it fits a 512 MB container. Passages and queries are
embedded with the same model.

| Mode | Encoder | hit@1 | hit@3 | hit@5 | MRR | p50 ms | p95 ms |
| --- | --- | --- | --- | --- | --- | --- | --- |
| dense | e5-small ONNX qint8 | 0.72 | 0.85 | 0.88 | 0.793 | 4 | 7 |
| hybrid (shipped) | e5-small ONNX qint8 | 0.78 | 0.90 | 0.93 | 0.838 | 6 | 12 |
