"""Tests for the ChromaDB-backed task/schedule storage.

Unlike Pinecone (needs a cloud account) and Ollama (needs a locally running
server), ChromaDB is an embedded, file-backed local database -- no external
service or credentials needed, so this is safe to run in CI.
"""

import chromadb
import pytest

from app.services.schedule_seed import seed_schedule
from app.services.task_storage import get_recent_tasks, store_task


@pytest.fixture
def tasks_collection(tmp_path):
    client = chromadb.PersistentClient(path=str(tmp_path / "chroma_db"))
    return client.get_or_create_collection(name="daily_tasks")


@pytest.fixture
def schedule_collection(tmp_path):
    client = chromadb.PersistentClient(path=str(tmp_path / "chroma_db"))
    return client.get_or_create_collection(name="daily_schedule")


def test_store_task_roundtrips(tasks_collection):
    message = store_task(tasks_collection, "Drink water", "Done, 2L so far", day="2026-07-02")
    assert "Drink water" in message
    assert "2026-07-02" in message

    stored = get_recent_tasks(tasks_collection, n=5)
    assert len(stored) == 1
    assert "Drink water" in stored[0]
    assert "Done, 2L so far" in stored[0]


def test_store_task_defaults_day_to_today_when_omitted(tasks_collection):
    store_task(tasks_collection, "Read a chapter", "Finished chapter 3")
    stored = get_recent_tasks(tasks_collection, n=1)
    assert "Date:" in stored[0]


def test_multiple_tasks_accumulate(tasks_collection):
    store_task(tasks_collection, "Task A", "Answer A", day="2026-07-01")
    store_task(tasks_collection, "Task B", "Answer B", day="2026-07-02")
    assert len(get_recent_tasks(tasks_collection, n=10)) == 2


def test_get_recent_tasks_empty_returns_empty_list(tasks_collection):
    assert get_recent_tasks(tasks_collection, n=5) == []


def test_schedule_seed_is_idempotent(schedule_collection):
    """seed_schedule() must be safe to call more than once (regression test --
    the original chroma_db.py unconditionally re-added fixed IDs and errored
    on the second run)."""
    seed_schedule(schedule_collection)
    assert schedule_collection.count() == 7  # one entry per day of the week

    seed_schedule(schedule_collection)  # must not raise on the second call
    assert schedule_collection.count() == 7

    results = schedule_collection.query(query_texts=["Monday"], n_results=1)
    monday = results["documents"][0][0]
    assert "Gym" in monday
