# Answer results

Answering models: `['nvidia/nemotron-3-ultra-550b-a55b:free', 'google/gemma-4-31b-it:free']`. Judge: `google/gemma-4-31b-it:free, nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free`.

| Metric | Value |
| --- | --- |
| Answerable questions answered (not refused) | 95% (57/60) |
| Answers citing at least one gold Pasal | 91% (52/57) |
| Answers judged faithful to their sources | 88% (50/57) |
| Unanswerable questions correctly refused | 100% (10/10) |
| Requests that failed after retries | 0 |
| Median seconds per answer | 10.4 |

## Hand check of the judge

15 answers were checked by reading the cited Pasal text: the 7 the judge marked unfaithful and 8 it marked
faithful (q002, q003, q011, q016, q017, q020, q028, q031, q037, q041, q044, q047, q050, q052, q056).

- By hand, 13 of the 15 are faithful. The two that are not: q047 lists Joint/Double Degree classes as
  English-taught, but the definition of Kelas Internasional in Pasal 1 does not include them; q056 ends with a
  sentence about other study levels that the source does not support.
- The judge agreed with the hand check on 10 of 15. All 5 disagreements are faithful answers it marked
  unfaithful, for example correcting the OCR typo "Mengundurkan Din" to "Diri" (q017) or restating an
  OCR-garbled formula correctly (q037). The judge is stricter than a human reader, so the faithfulness figure
  above is more likely an underestimate than an overestimate.

## Failure examples

- q023 "Saya bisa kena DO kalau apa saja?": refused. The slang "DO" never appears in the text (Pasal 75 says
  "berhenti studi atau diberhentikan"), and retrieval missed Pasal 75 in the top 5.
- q060 "Kapan peraturan akademik ini mulai berlaku?": refused. Pasal 91 is one sentence plus the signature
  block and ranks below longer articles that mention "berlaku".
- q054 "Jalur masuk program sarjana ITS lewat apa saja?": cites Pasal 19 (types of admission paths) instead of
  Pasal 40 (selection routes for Sarjana). The answer is related but not the article that answers it.
- Known prompt issue: the rule "answer for S1 when no level is given" sometimes adds an unsupported closing
  sentence about other levels (q056).
