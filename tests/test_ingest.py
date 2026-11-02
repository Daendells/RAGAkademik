from pathlib import Path

import pytest

from rag.ingest import chunk_regulation, extract_pages, read_chunks, write_chunks

PDF = Path(__file__).resolve().parent.parent / "data" / "peraturan-rektor-33-2025.pdf"


@pytest.fixture(scope="module")
def pages():
    return extract_pages(PDF)


@pytest.fixture(scope="module")
def chunks(pages):
    return chunk_regulation(pages, doc_id="pr33")


def test_every_pasal_once(chunks):
    assert sorted({c.pasal for c in chunks}) == list(range(1, 92))
    order = [c.pasal for c in chunks]
    # Each Pasal's chunks are contiguous and in document order.
    assert order == sorted(order)


def test_pages_are_one_based_and_in_range(pages, chunks):
    assert len(pages) == 57
    assert all(1 <= p <= 57 for c in chunks for p in c.pages)
    pasal_2 = next(c for c in chunks if c.pasal == 2)
    assert 11 in pasal_2.pages


def test_long_pasal_split_by_ayat(chunks):
    assert max(len(c.text) for c in chunks) <= 1800
    split = [c for c in chunks if c.ayat and sum(x.pasal == c.pasal for x in chunks) > 1]
    assert split, "expected at least one Pasal split by ayat"
    for c in split:
        assert c.text.startswith(f"Pasal {c.pasal}")
        assert c.ayat.startswith("(") or c.ayat.startswith("angka ")


def test_pasal_1_split_by_numbered_definitions(chunks):
    pasal_1 = [c for c in chunks if c.pasal == 1]
    assert len(pasal_1) > 3
    assert any("Mata Kuliah Wajib adalah" in c.text for c in pasal_1)
    assert all(c.ayat and c.ayat.startswith("angka ") for c in pasal_1)


def test_bab_assigned(chunks):
    pasal_2 = next(c for c in chunks if c.pasal == 2)
    assert pasal_2.bab.startswith("BAB II")


def test_ids_unique_and_stable(pages, chunks, tmp_path):
    ids = [c.id for c in chunks]
    assert len(ids) == len(set(ids))
    assert ids[0] == "pr33-p1-1"
    again = chunk_regulation(pages, doc_id="pr33")
    assert again == chunks
    path = tmp_path / "chunks.jsonl"
    write_chunks(chunks, path)
    assert read_chunks(path) == chunks


def test_citation_text():
    from rag.models import Chunk

    c = Chunk(id="x", doc_id="pr33", bab="BAB II", pasal=12, ayat="(2)–(3)", pages=(18,), text="Pasal 12 ...")
    assert c.citation() == "Pasal 12 ayat (2)–(3), hal. 18"
    c2 = Chunk(id="y", doc_id="pr33", bab="BAB II", pasal=5, ayat=None, pages=(12, 13), text="Pasal 5 ...")
    assert c2.citation() == "Pasal 5, hal. 12–13"
