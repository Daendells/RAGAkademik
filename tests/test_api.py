import json

import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from tests.test_answer import HITS, FakeClient, FakeRetriever


def events(response):
    return [json.loads(line[6:]) for line in response.text.splitlines() if line.startswith("data: ")]


@pytest.fixture
def client():
    retriever = FakeRetriever(HITS)
    retriever.chunks = [h.chunk for h in HITS]
    return TestClient(create_app(retriever=retriever, client=FakeClient(tokens=["Cuti 4 semester [C1]."])))


def test_health(client):
    assert client.get("/health").json() == {"status": "ok", "chunks": 2}


def test_search_shape(client):
    body = client.get("/search", params={"q": "cuti", "k": 2}).json()
    assert body[0]["citation"] == "Pasal 74, hal. 74"
    assert set(body[0]) >= {"id", "pasal", "citation", "text", "score"}


def test_ask_streams_tokens_sources_done(client):
    r = client.post("/ask", json={"question": "Berapa lama cuti?"})
    assert r.headers["content-type"].startswith("text/event-stream")
    kinds = [e["type"] for e in events(r)]
    assert kinds[0] == "token" and kinds[-2:] == ["sources", "done"]


@pytest.mark.parametrize("question", ["", "   ", "x" * 501])
def test_ask_rejects_bad_questions(client, question):
    assert client.post("/ask", json={"question": question}).status_code == 422


def test_ask_llm_failure_streams_error():
    retriever = FakeRetriever(HITS)
    retriever.chunks = [h.chunk for h in HITS]
    app = create_app(retriever=retriever, client=FakeClient(error=httpx.ReadTimeout("slow")))
    r = TestClient(app).post("/ask", json={"question": "Berapa lama cuti?"})
    assert [e["type"] for e in events(r)] == ["error", "done"]


def test_index_page_served(client):
    r = client.get("/")
    assert r.status_code == 200 and "<form" in r.text
