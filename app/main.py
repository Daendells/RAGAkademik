from __future__ import annotations

import json
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from dotenv import load_dotenv
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, StringConstraints

from rag.answer import OpenRouterClient, stream_answer

ROOT = Path(__file__).resolve().parent.parent
STATIC = Path(__file__).resolve().parent / "static"


class Question(BaseModel):
    question: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]


def create_app(retriever=None, client=None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Models load once at startup; tests pass their own retriever and client instead.
        if app.state.retriever is None:
            from rag.retrieve import Retriever

            load_dotenv()
            app.state.retriever = Retriever.load(ROOT / "data")
            app.state.client = OpenRouterClient()
        yield

    app = FastAPI(title="RAG Akademik ITS", lifespan=lifespan)
    app.state.retriever, app.state.client = retriever, client

    @app.get("/health")
    def health():
        return {"status": "ok", "chunks": len(app.state.retriever.chunks)}

    @app.get("/search")
    def search(q: Annotated[str, Query(min_length=1, max_length=500)], k: Annotated[int, Query(ge=1, le=10)] = 5):
        return [
            {"id": h.chunk.id, "pasal": h.chunk.pasal, "citation": h.chunk.citation(), "text": h.chunk.text,
             "score": round(h.score, 4)}
            for h in app.state.retriever.search(q, k=k)
        ]

    @app.post("/ask")
    async def ask(body: Question):
        async def sse():
            async for event in stream_answer(body.question, app.state.retriever, app.state.client):
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

        return StreamingResponse(sse(), media_type="text/event-stream", headers={"Cache-Control": "no-cache"})

    @app.get("/")
    def index():
        return FileResponse(STATIC / "index.html")

    app.mount("/static", StaticFiles(directory=STATIC), name="static")
    return app


app = create_app()
