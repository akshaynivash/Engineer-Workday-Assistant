# tasks.py
import chromadb
from datetime import datetime
from langchain_ollama import OllamaEmbeddings
from langchain.vectorstores import Chroma

# 1. Initialize ChromaDB Persistent Client (stores data locally in './data/chroma_db')
chroma_client = chromadb.PersistentClient(path="./data/chroma_db")

# 2. Create (or get) the collection for storing daily tasks
collection = chroma_client.get_or_create_collection(name="daily_tasks")

def store_task(task: str, answer: str, day: str = None):
    """
    Stores a daily task and its answer in ChromaDB with day metadata.
    If day is not provided, defaults to today's date (YYYY-MM-DD).
    """
    if day is None or day.strip() == "":
        day = datetime.now().strftime('%Y-%m-%d')  # default to today's date

    doc_id = f"{task}-{datetime.now().isoformat()}"  # unique ID
    document_content = (
        f"Task: {task}\n"
        f"Answer: {answer}\n"
        f"Date: {day}"
    )
    # Store 'day' in metadata so we can filter by it later
    metadata = {"day": day, "timestamp": datetime.now().isoformat()}

    collection.add(
        ids=[doc_id],
        documents=[document_content],
        metadatas=[metadata]
    )
    return f"Task '{task}' stored successfully for {day}!"

def get_recent_tasks(n: int = 5):
    """Fetches the last N stored tasks from ChromaDB."""
    results = collection.get(limit=n)
    if not results["documents"]:
        return "No tasks found."
    return "\n\n".join(results["documents"])




