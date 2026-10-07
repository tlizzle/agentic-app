"""Retrieval seam: Passages, ranked search with Citations, and cache reuse."""

import hashlib

from helpdesk.rag import HandbookIndex, Passage, split_passages

DIMS = 32


def fake_embed(texts: list[str]) -> list[list[float]]:
    """Deterministic bag-of-words hashing into a small vector."""
    vectors = []
    for text in texts:
        vec = [0.0] * DIMS
        for word in text.lower().split():
            digest = hashlib.sha256(word.encode()).digest()
            vec[digest[0] % DIMS] += 1.0
        vectors.append(vec)
    return vectors


class CountingEmbedder:
    def __init__(self):
        self.calls = 0

    def __call__(self, texts: list[str]) -> list[list[float]]:
        self.calls += 1
        return fake_embed(texts)


LEAVE = """# Leave Policy

## Annual leave
Every employee gets 20 days of annual leave per year.

## Sick leave
Tell your manager before 10:00 on the first day.
"""

EXPENSES = """# Expenses

## Meal limit
Meals are capped at 40 USD per day while travelling.
"""


def write_knowledge(tmp_path):
    knowledge = tmp_path / "knowledge"
    knowledge.mkdir()
    (knowledge / "leave.md").write_text(LEAVE)
    (knowledge / "expenses.md").write_text(EXPENSES)
    return knowledge


def test_split_passages_at_headings():
    passages = split_passages(LEAVE, "leave.md")

    assert [p.heading for p in passages] == ["Annual leave", "Sick leave"]
    assert all(p.document == "leave.md" for p in passages)
    assert passages[0] == Passage("leave.md", "Annual leave", "Every employee gets 20 days of annual leave per year.")


def test_split_ignores_blank_sections():
    assert split_passages("# Title\n\n## Body\nSome text.\n", "x.md") == [Passage("x.md", "Body", "Some text.")]


def test_search_ranks_matching_passage_first_with_citation(tmp_path):
    index = HandbookIndex(write_knowledge(tmp_path), fake_embed, tmp_path / "cache.json")

    results = index.search("How many days of annual leave do I get?", k=2)

    assert len(results) == 2
    best = results[0]
    assert best.citation.document == "leave.md"
    assert best.citation.heading == "Annual leave"
    assert "20 days" in best.passage.text
    assert results[0].score >= results[1].score


def test_second_build_reuses_cache_without_embedding(tmp_path):
    knowledge = write_knowledge(tmp_path)
    cache = tmp_path / "cache.json"
    first = CountingEmbedder()
    HandbookIndex(knowledge, first, cache)
    assert first.calls >= 1

    second = CountingEmbedder()
    HandbookIndex(knowledge, second, cache)

    assert second.calls == 0


def test_changed_passage_is_re_embedded(tmp_path):
    knowledge = write_knowledge(tmp_path)
    cache = tmp_path / "cache.json"
    HandbookIndex(knowledge, fake_embed, cache)
    (knowledge / "expenses.md").write_text(EXPENSES.replace("40 USD", "50 USD"))

    embedded: list[str] = []

    def recording_embed(texts):
        embedded.extend(texts)
        return fake_embed(texts)

    HandbookIndex(knowledge, recording_embed, cache)

    assert embedded == ["Meals are capped at 50 USD per day while travelling."]
