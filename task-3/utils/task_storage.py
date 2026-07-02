"""Pure ChromaDB task-storage logic -- no Streamlit dependency, so it's testable
without installing the UI framework (see tests/test_chromadb_storage.py)."""

from datetime import datetime

DAILY_TASKS = [
    "Complete Duolingo",
    "Take vitamins",
    "Drink 3 L water",
    "Snapscore check",
    "Prepare a topic for stat exam",
    "Surf new tech update",
    "Good moment of a day",
    "Bad moment of a day",
    "Today's affirmation",
]


def store_task(collection, task: str, answer: str, day: str | None = None) -> str:
    if not day:
        day = datetime.now().strftime("%Y-%m-%d")
    doc_id = f"{task}-{datetime.now().isoformat()}"
    document_content = f"Task: {task}\nAnswer: {answer}\nDate: {day}"
    collection.add(ids=[doc_id], documents=[document_content], metadatas={"day": day, "timestamp": datetime.now().isoformat()})
    return f"Task '{task}' stored successfully for {day}!"
