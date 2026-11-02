# Retrieval results (60 answerable questions, CPU)

| Mode | Encoder | hit@1 | hit@3 | hit@5 | MRR | p50 ms | p95 ms |
| --- | --- | --- | --- | --- | --- | --- | --- |
| bm25 | — | 0.70 | 0.87 | 0.95 | 0.800 | 0 | 0 |
| dense | multilingual-e5-small | 0.68 | 0.87 | 0.90 | 0.771 | 15 | 19 |
| hybrid | multilingual-e5-small | 0.80 | 0.87 | 0.93 | 0.849 | 15 | 19 |
| hybrid_rerank | multilingual-e5-small | 0.85 | 0.90 | 0.95 | 0.890 | 1475 | 2124 |
| dense | paraphrase-multilingual-MiniLM-L12-v2 | 0.48 | 0.72 | 0.77 | 0.612 | 14 | 28 |
| hybrid | paraphrase-multilingual-MiniLM-L12-v2 | 0.65 | 0.88 | 0.93 | 0.776 | 13 | 21 |
| hybrid_rerank | paraphrase-multilingual-MiniLM-L12-v2 | 0.87 | 0.92 | 0.97 | 0.906 | 1513 | 2208 |

Questions missed in the top 5:

- bm25 / —: q010, q023, q054
- dense / multilingual-e5-small: q023, q034, q035, q054, q059, q060
- hybrid / multilingual-e5-small: q023, q035, q054, q059, q060
- hybrid_rerank / multilingual-e5-small: q010, q023, q054
- dense / paraphrase-multilingual-MiniLM-L12-v2: q007, q011, q012, q013, q026, q027, q028, q029, q033, q036, q038, q042, q054, q059, q060
- hybrid / paraphrase-multilingual-MiniLM-L12-v2: q028, q038, q054, q060
- hybrid_rerank / paraphrase-multilingual-MiniLM-L12-v2: q010, q054
