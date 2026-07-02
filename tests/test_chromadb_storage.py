"""Tests for the ChromaDB-backed task/schedule storage.

Unlike Pinecone (needs a cloud account) and Ollama (needs a locally running
server), ChromaDB is an embedded, file-backed local database -- no external
service or credentials needed, so this is safe to run in CI.
"""

import sys
from pathlib import Path

import chromadb
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "task-3"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "task-1_chatbot" / "backend"))

from utils.personal_assistant import _store_task  # noqa: E402


@pytest.fixture
def tasks_collection(tmp_path):
    client = chromadb.PersistentClient(path=str(tmp_path / "chroma_db"))
    return client.get_or_create_collection(name="daily_tasks")


def test_store_task_roundtrips(tasks_collection):
    message = _store_task(tasks_collection, "Drink water", "Done, 2L so far", day="2026-07-02")
    assert "Drink water" in message
    assert "2026-07-02" in message

    stored = tasks_collection.get(limit=5)
    assert len(stored["documents"]) == 1
    assert "Drink water" in stored["documents"][0]
    assert "Done, 2L so far" in stored["documents"][0]


def test_store_task_defaults_day_to_today_when_omitted(tasks_collection):
    _store_task(tasks_collection, "Read a chapter", "Finished chapter 3")
    stored = tasks_collection.get(limit=1)
    assert "Date:" in stored["documents"][0]


def test_multiple_tasks_accumulate(tasks_collection):
    _store_task(tasks_collection, "Task A", "Answer A", day="2026-07-01")
    _store_task(tasks_collection, "Task B", "Answer B", day="2026-07-02")
    stored = tasks_collection.get(limit=10)
    assert len(stored["documents"]) == 2


def test_schedule_seed_is_idempotent(tmp_path, monkeypatch):
    """store_schedule() must be safe to call more than once (regression test --
    it used to unconditionally re-add fixed IDs and error on the second run)."""
    monkeypatch.chdir(tmp_path)
    import importlib

    import chroma_db  # the module under task-1_chatbot/backend

    importlib.reload(chroma_db)

    chroma_db.store_schedule()
    first_count = chroma_db.schedule_collection.count()
    assert first_count == 7  # one entry per day of the week

    chroma_db.store_schedule()  # must not raise on the second call
    assert chroma_db.schedule_collection.count() == first_count

    monday = chroma_db.retrieve_schedule("Monday")
    assert isinstance(monday, str), "retrieve_schedule must return the document text, not a nested list"
    assert "Gym" in monday
