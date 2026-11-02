import numpy as np
import pytest

from rag.models import Chunk
from rag.retrieve import Retriever, rrf, tokenize

TEXTS = [
    "Pasal 50\nMahasiswa dapat mengubah rencana studi dalam FRS paling lambat minggu ketiga.",
    "Pasal 72\nBatas waktu studi Program Sarjana adalah 14 semester.",
    "Pasal 74\nMahasiswa diperbolehkan mengajukan cuti studi paling lama 4 semester.",
    "Pasal 68\nNilai huruf A untuk nilai angka 86 sampai 100.",
    "Pasal 91\nPeraturan ini mulai berlaku pada tanggal ditetapkan.",
]
CHUNKS = [
    Chunk(id=f"t-{i}", doc_id="t", bab="BAB", pasal=int(t.split()[1]), ayat=None, pages=(1,), text=t)
    for i, t in enumerate(TEXTS)
]


class FakeEncoder:
    """Embeds by word presence, so 'cuti' questions land on the cuti chunk."""

    vocab = sorted({w for t in TEXTS for w in tokenize(t)})

    def _encode(self, texts):
        out = np.array([[w in tokenize(t) for w in self.vocab] for t in texts], dtype=float)
        return out / np.maximum(np.linalg.norm(out, axis=1, keepdims=True), 1e-9)

    encode_queries = encode_passages = _encode


@pytest.fixture
def retriever():
    enc = FakeEncoder()
    return Retriever(CHUNKS, enc.encode_passages([c.text for c in CHUNKS]), enc)


def test_tokenize_keeps_numbers_and_lowercases():
    assert tokenize("Pasal 50: FRS, minggu ke-3!") == ["pasal", "50", "frs", "minggu", "ke", "3"]


def test_bm25_ranks_rare_term_first(retriever):
    hits = retriever.search("kapan FRS bisa diubah", k=3, mode="bm25")
    assert hits[0].chunk.pasal == 50


def test_rrf_hand_computed():
    scores = rrf([[0, 1, 2], [2, 0]], c=60)
    assert scores[0] == pytest.approx(1 / 61 + 1 / 62)
    assert scores[2] == pytest.approx(1 / 63 + 1 / 61)
    assert scores[1] == pytest.approx(1 / 62)


@pytest.mark.parametrize("mode", ["bm25", "dense", "hybrid"])
def test_search_returns_at_most_k_sorted(retriever, mode):
    hits = retriever.search("cuti studi berapa semester", k=2, mode=mode)
    assert 1 <= len(hits) <= 2
    assert [h.score for h in hits] == sorted((h.score for h in hits), reverse=True)
    assert hits[0].chunk.pasal == 74


def test_unknown_mode_raises(retriever):
    with pytest.raises(ValueError):
        retriever.search("cuti", mode="magic")


def test_rerank_without_reranker_raises(retriever):
    with pytest.raises(ValueError):
        retriever.search("cuti", mode="hybrid_rerank")
