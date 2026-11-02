# Evaluation set

`questions.jsonl` holds 70 questions in Indonesian about the ITS academic regulation
(Peraturan Rektor ITS No. 33 Tahun 2025):

- 60 answerable questions, each labelled with the Pasal (article) numbers that answer it
  (`gold_pasal`). 18 use student abbreviations (SKS, IPS, FRS, TA, DO, SKPI), 14 paraphrase the
  rule without the regulation's own words (`note`).
- 10 questions the regulation does not answer (library hours, tuition amount, other universities),
  used to check that the assistant says so instead of guessing.

How it was made: the questions were drafted with an AI assistant from the extracted text of each
Pasal and reviewed by the author. Gold labels come from reading the Pasal text, not from retrieval
output. The set was written and frozen before any retrieval setting was tuned; any later edit is
logged below with its reason.

## Change log

- 2026-11-02: initial set.
