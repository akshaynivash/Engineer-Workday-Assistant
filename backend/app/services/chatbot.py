"""General-purpose Quick Chat, backed by a locally running Ollama model.

No tool-calling needed here (unlike the Workday Help agent in
assistant_agent.py), so any plain chat model works -- defaults to "mistral"
since it's small and commonly already pulled. Override via OLLAMA_CHAT_MODEL.
"""

import os
from functools import lru_cache

OLLAMA_CHAT_MODEL = os.getenv("OLLAMA_CHAT_MODEL", "mistral")


@lru_cache
def _get_llm():
    from langchain_ollama import ChatOllama

    return ChatOllama(model=OLLAMA_CHAT_MODEL)


def generate_response(prompt: str) -> str:
    """Raises if Ollama isn't reachable or the model isn't pulled -- callers
    (the /api/chat router) turn that into a clean 503 rather than a raw 500."""
    return _get_llm().invoke(prompt).content
