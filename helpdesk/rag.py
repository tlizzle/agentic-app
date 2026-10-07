"""Handbook retrieval: split markdown into Passages, embed once, search by cosine (see ADR 0001)."""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from .config import EMBEDDING_MODEL

Embedder = Callable[[list[str]], list[list[float]]]

HANDBOOK_DIR = Path(__file__).resolve().parent / "handbook"
CACHE_PATH = HANDBOOK_DIR.parent.parent / ".cache" / "handbook_embeddings.json"
EMBED_BATCH_SIZE = 100  # Gemini batchEmbedContents accepts at most 100 texts per request.
MIN_SCORE = 0.66  # measured with gemini-embedding-001: relevant passages 0.70-0.80, unrelated 0.50-0.64

_HEADING = re.compile(r"^#{1,2}\s+(.+?)\s*$")


@dataclass(frozen=True)
class Passage:
    document: str
    heading: str
    text: str


@dataclass(frozen=True)
class Citation:
    document: str
    heading: str


@dataclass(frozen=True)
class SearchResult:
    passage: Passage
    score: float

    @property
    def citation(self) -> Citation:
        return Citation(self.passage.document, self.passage.heading)


def split_passages(markdown_text: str, document_name: str) -> list[Passage]:
    """One Passage per `#`/`##` heading; sections with no body text are dropped."""
    passages: list[Passage] = []
    heading = ""
    lines: list[str] = []

    def flush() -> None:
        text = "\n".join(lines).strip()
        if heading and text:
            passages.append(Passage(document_name, heading, text))

    for line in markdown_text.splitlines():
        match = _HEADING.match(line)
        if match:
            flush()
            heading, lines = match.group(1), []
        else:
            lines.append(line)
    flush()
    return passages


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))
    return dot / norm if norm else 0.0


def _key(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


class HandbookIndex:
    """In-process index over every .md file in a directory, with vectors cached on disk by content hash."""

    def __init__(self, handbook_dir: Path, embed: Embedder, cache_path: Path):
        self._embed = embed
        self._cache_path = cache_path
        self.passages = [
            p for path in sorted(handbook_dir.glob("*.md")) for p in split_passages(path.read_text(), path.name)
        ]
        cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}
        missing = [p.text for p in self.passages if _key(p.text) not in cache]
        if missing:
            cache.update(zip(map(_key, missing), self._embed(missing)))
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_text(json.dumps(cache))
        self._vectors = [cache[_key(p.text)] for p in self.passages]

    def search(self, query: str, k: int = 3) -> list[SearchResult]:
        [query_vector] = self._embed([query])
        scored = [SearchResult(p, _cosine(query_vector, v)) for p, v in zip(self.passages, self._vectors)]
        return sorted(scored, key=lambda r: r.score, reverse=True)[:k]


_client = None


def gemini_embed(texts: list[str]) -> list[list[float]]:
    """Default embedder: Gemini embeddings through google-genai, chunked to the API batch limit."""
    global _client
    if _client is None:
        from google import genai

        _client = genai.Client()
    client = _client
    vectors: list[list[float]] = []
    for start in range(0, len(texts), EMBED_BATCH_SIZE):
        response = client.models.embed_content(model=EMBEDDING_MODEL, contents=texts[start : start + EMBED_BATCH_SIZE])
        vectors.extend(list(e.values) for e in response.embeddings)
    return vectors


_index: HandbookIndex | None = None


def search_handbook(query: str) -> dict:
    """Search the Acme Corp employee handbook for passages relevant to a policy question.

    Args:
        query: The employee's question in plain language.

    Returns:
        passages: up to three matching passages, best first, each with document, heading, text and score.
        found: False when nothing in the handbook is relevant enough to answer from.
    """
    global _index
    if _index is None:
        _index = HandbookIndex(HANDBOOK_DIR, gemini_embed, CACHE_PATH)
    results = _index.search(query, k=3)
    return {
        "passages": [
            {
                "document": r.citation.document,
                "heading": r.citation.heading,
                "text": r.passage.text,
                "score": round(r.score, 3),
            }
            for r in results
        ],
        "found": bool(results) and results[0].score >= MIN_SCORE,
    }
