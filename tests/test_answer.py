import httpx
import pytest

from rag.answer import REFUSAL, build_prompt, parse_citations, stream_answer
from rag.models import Chunk
from rag.retrieve import Hit


def chunk(pasal, text="..."):
    return Chunk(id=f"pr33-p{pasal}-1", doc_id="pr33", bab="BAB", pasal=pasal, ayat=None, pages=(pasal,), text=text)


HITS = [Hit(chunk(74, "Pasal 74\nCuti paling lama 4 semester."), 1.0), Hit(chunk(72, "Pasal 72\n14 semester."), 0.5)]


class FakeRetriever:
    def __init__(self, hits):
        self.hits = hits

    def search(self, query, k=5, mode=None):
        return self.hits


class FakeClient:
    def __init__(self, tokens=(), error=None):
        self.tokens, self.error, self.calls = tokens, error, 0

    async def stream(self, messages):
        self.calls += 1
        if self.error:
            raise self.error
        for t in self.tokens:
            yield t


async def collect(gen):
    return [event async for event in gen]


def test_prompt_labels_chunks_and_keeps_question():
    messages = build_prompt("Berapa lama cuti?", HITS)
    user = messages[-1]["content"]
    assert "[C1]" in user and "[C2]" in user
    assert "Cuti paling lama 4 semester." in user
    assert "Berapa lama cuti?" in user


def test_parse_citations_drops_unknown_ids():
    text, cited, ok = parse_citations("Cuti paling lama 4 semester [C1][C9].", HITS)
    assert text == "Cuti paling lama 4 semester [1]."
    assert [c.pasal for c in cited] == [74]
    assert ok


def test_parse_citations_renumbers_in_order_of_use():
    text, cited, _ = parse_citations("Batas studi 14 semester [C2], cuti 4 semester [C1].", HITS)
    assert text == "Batas studi 14 semester [1], cuti 4 semester [2]."
    assert [c.pasal for c in cited] == [72, 74]


def test_answer_without_citation_is_flagged():
    _, cited, ok = parse_citations("Cuti paling lama 4 semester.", HITS)
    assert cited == [] and not ok


@pytest.mark.asyncio
async def test_stream_answer_emits_tokens_then_sources():
    client = FakeClient(tokens=["Cuti paling lama ", "4 semester [C1]."])
    events = await collect(stream_answer("Berapa lama cuti?", FakeRetriever(HITS), client))
    kinds = [e["type"] for e in events]
    assert kinds[0] == "token" and kinds[-2:] == ["sources", "done"]
    sources = events[-2]
    assert sources["answer"] == "Cuti paling lama 4 semester [1]."
    assert sources["sources"][0]["citation"] == "Pasal 74, hal. 74"
    assert sources["cited"] is True


@pytest.mark.asyncio
async def test_refusal_has_no_sources():
    client = FakeClient(tokens=[REFUSAL])
    events = await collect(stream_answer("Jam buka perpustakaan?", FakeRetriever(HITS), client))
    sources = next(e for e in events if e["type"] == "sources")
    assert sources["sources"] == [] and sources["refused"] is True


@pytest.mark.asyncio
async def test_no_hits_refuses_without_calling_llm():
    client = FakeClient(tokens=["should not be used"])
    events = await collect(stream_answer("apa saja", FakeRetriever([]), client))
    assert client.calls == 0
    assert events[0] == {"type": "token", "text": REFUSAL}


@pytest.mark.asyncio
async def test_llm_failure_yields_one_error_then_done():
    client = FakeClient(error=httpx.ConnectError("down"))
    events = await collect(stream_answer("Berapa lama cuti?", FakeRetriever(HITS), client))
    assert [e["type"] for e in events] == ["error", "done"]
    assert "coba lagi" in events[0]["message"].lower()


def test_openrouter_payload_lists_fallback_models():
    from rag.answer import OpenRouterClient

    client = OpenRouterClient(api_key="k", model="a/one:free, b/two:free")
    payload = client.payload([{"role": "user", "content": "hi"}])
    assert payload["models"] == ["a/one:free", "b/two:free"]
    assert payload["stream"] is True and payload["temperature"] == 0


def test_stream_line_parsing_skips_empty_choices_and_raises_on_error():
    from rag.answer import StreamError, parse_stream_line

    assert parse_stream_line(': OPENROUTER PROCESSING') is None
    assert parse_stream_line('data: [DONE]') is None
    assert parse_stream_line('data: {"choices": [], "usage": {"total_tokens": 9}}') is None
    assert parse_stream_line('data: {"choices": [{"delta": {"content": "Merah."}}]}') == "Merah."
    with pytest.raises(StreamError):
        parse_stream_line('data: {"error": {"message": "Provider returned error"}, "choices": []}')
    assert issubclass(StreamError, httpx.HTTPError)


def test_sync_bridge_yields_the_same_events():
    from rag.answer import stream_answer_sync

    client = FakeClient(tokens=["Cuti 4 semester [C1]."])
    events = list(stream_answer_sync("Berapa lama cuti?", FakeRetriever(HITS), client))
    assert [e["type"] for e in events] == ["token", "sources", "done"]
    assert events[1]["answer"] == "Cuti 4 semester [1]."


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("Cuti 4 semester [C1 ayat (2)].", "Cuti 4 semester [1]."),
        ("Cuti 4 semester [C1, C2].", "Cuti 4 semester [1][2]."),
        ("Cuti 4 semester [C2; C1 ayat (3)].", "Cuti 4 semester [1][2]."),
    ],
)
def test_parse_citations_accepts_labels_with_extra_text(raw, expected):
    text, cited, ok = parse_citations(raw, HITS)
    assert text == expected and ok
    assert "C" not in text.replace("Cuti", "")
