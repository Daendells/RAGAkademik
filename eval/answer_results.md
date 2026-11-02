# Answer results

Answering models: `['nvidia/nemotron-3-ultra-550b-a55b:free', 'google/gemma-4-31b-it:free']`. Judge: `google/gemma-4-31b-it:free, nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free`.

| Metric | Value |
| --- | --- |
| Answerable questions answered (not refused) | 95% (57/60) |
| Answers citing at least one gold Pasal | 91% (52/57) |
| Answers judged faithful to their sources | 96% (55/57) |
| Unanswerable questions correctly refused | 100% (10/10) |
| Requests that failed after retries | 0 |
| Median seconds per answer | 8.4 |

## Hand check of the judge

10 answers from this run were checked by reading the cited Pasal text: the 2 the judge marked unfaithful and
8 it marked faithful (q003, q016, q017, q020, q025, q044, q045, q047, q054, q056).

- By hand, 8 of the 10 are faithful. Two are not: q054 lists IPP (a postgraduate class) among the admission
  paths for Sarjana, and q017 mixes "tidak sah" and "dibatalkan" into the list of academic statuses instead of
  giving the list in Pasal 58 ayat (1).
- The judge agreed on 8 of 10 and erred both ways: it flagged q025 (a correct one-line answer, confused by the
  citation marker) and passed q017. Treat the faithfulness figure as an estimate within a few points.

An earlier run, before the citation parser accepted labels such as "[C4 ayat (7)]", had three answers whose
citations were lost; this run has none.

## Failure examples

- q023 "Saya bisa kena DO kalau apa saja?": refused. The slang "DO" never appears in the text (Pasal 75 says
  "berhenti studi atau diberhentikan"), and retrieval missed Pasal 75 in the top 5.
- q060 "Kapan peraturan akademik ini mulai berlaku?": refused. Pasal 91 is one sentence plus the signature
  block and ranks below longer articles that mention "berlaku".
- q054 "Jalur masuk program sarjana ITS lewat apa saja?": cites Pasal 19 (admission paths for all programs)
  instead of Pasal 40 (selection routes for Sarjana) and includes paths that do not apply to Sarjana.
- q010: the regulation contradicts itself on whether leave counts toward the study period (Pasal 72 against
  Pasal 74 ayat (9)), so the answer depends on which article is retrieved.
