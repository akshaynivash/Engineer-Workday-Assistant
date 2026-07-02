"""LangChain tool-calling agent for the personal assistant: routes chat to the
right capability (study assistant over a local FAISS index, daily schedule
lookup, weekly meal planning, general chat) instead of matching on hardcoded
keywords.

Uses langchain.agents.create_agent -- LangChain 1.x's unified agent
constructor, built on tool-calling rather than the older text-parsing ReAct
format (AgentExecutor/create_react_agent no longer exist in current
LangChain). Tool-calling agents need a chat model with native tool-calling
support: plain "llama2" (2023) predates Ollama's tool-calling feature and
will not work reliably. Defaults to "mistral" -- override via OLLAMA_MODEL
(e.g. "llama3.1" or "qwen2.5" for more reliable tool adherence).
"""

import os
from functools import lru_cache

from app.data import REPO_ROOT
from app.services.vectorstore import load_or_build_vectorstore

CHROMA_DB_DIR = REPO_ROOT / "data" / "chroma_db"

GREETINGS = {"hi", "hello", "hey", "greetings", "how are you?"}

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")

SYSTEM_PROMPT = (
    "You are a helpful personal assistant. Use the StudyAssistant tool for questions about study "
    "material or PDF content, ScheduleLookup for the user's daily schedule (input: a day name like "
    "'Monday'), MealPlanner for weekly meal planning requests, and GeneralAssistant for anything else. "
    "Always use a tool -- don't answer from your own knowledge alone."
)


def greeting_response(message: str) -> str | None:
    """Fast path for trivial greetings -- skips the agent/LLM call entirely."""
    lower = message.lower().strip()
    if lower not in GREETINGS:
        return None
    if lower == "how are you?":
        return "I'm doing well, thanks for asking! How are you doing?"
    return "Hello! I'm here to help. How are you doing today?"


def _rag_response(llm, vectorstore, prompt_template: str, query: str) -> str:
    retriever = vectorstore.as_retriever()
    docs = retriever.get_relevant_documents(query)
    context_str = "\n\n".join(doc.page_content for doc in docs) if docs else ""
    return llm.invoke(prompt_template.format(query=query, context=context_str)).content


def _build_tools(llm, vectorstore, schedule_collection):
    from langchain_core.tools import Tool

    def study_tool(query: str) -> str:
        return _rag_response(
            llm, vectorstore,
            "You are my dedicated study assistant. Based on the following study material from my PDF, "
            "please provide me with the key study topics and any related details. Focus solely on the "
            "study content.\n\nQuery: {query}\n\nStudy Material: {context}\n\n"
            "List the main study topics and any important points.",
            query,
        )

    def schedule_tool(day: str) -> str:
        day = day.strip().capitalize()
        results = schedule_collection.query(query_texts=[day], n_results=1)
        # query() nests results per query-text ([[doc, ...]]), so [0] alone is still a
        # list, not the document string -- need [0][0] to get the actual text.
        schedule_info = (
            results["documents"][0][0] if results["documents"] and results["documents"][0] else f"No schedule found for {day}."
        )
        return llm.invoke(
            "You are my personal assistant who is very familiar with my daily schedule. "
            f"I have the following schedule for {day}:\n\n{schedule_info}\n\n"
            "Explain this schedule in a friendly, personalized tone."
        ).content

    def meal_plan_tool(query: str) -> str:
        return llm.invoke(
            "You are my personal meal planning assistant. Based on the following user input, generate a "
            "weekly meal plan for the entire week, with breakfast/lunch/dinner ideas and a complete "
            f"ingredients list for each day.\n\nUser Input: {query}\n\n"
            "Generate the plan in a clear, organized format."
        ).content

    def general_tool(query: str) -> str:
        return _rag_response(
            llm, vectorstore,
            "You are my personal assistant. Answer the following question in a friendly, conversational "
            "tone. Incorporate any relevant information from the PDF context below, but only if it helps "
            "answer the query.\n\nQuestion: {query}\n\nPDF Context: {context}\n\n"
            "Also, feel free to ask how I'm doing if it fits naturally into the conversation.",
            query,
        )

    return [
        Tool(
            name="StudyAssistant",
            func=study_tool,
            description=(
                "Answers questions about study material or PDF content (e.g. 'explain today's topic', "
                "'summarize the study material'). Input: the user's question, as-is."
            ),
        ),
        Tool(
            name="ScheduleLookup",
            func=schedule_tool,
            description=(
                "Looks up the user's schedule for a specific day and explains it. "
                "Input: a single day of the week, e.g. 'Monday'."
            ),
        ),
        Tool(
            name="MealPlanner",
            func=meal_plan_tool,
            description=(
                "Generates a weekly meal plan with recipes and ingredients. "
                "Input: the user's meal-planning request, as-is."
            ),
        ),
        Tool(
            name="GeneralAssistant",
            func=general_tool,
            description=(
                "Handles general conversation or anything that doesn't clearly fit the other tools. "
                "Input: the user's message, as-is."
            ),
        ),
    ]


def _build_agent(llm, tools):
    from langchain.agents import create_agent

    return create_agent(llm, tools, system_prompt=SYSTEM_PROMPT)


@lru_cache
def _get_chroma_client():
    import chromadb

    return chromadb.PersistentClient(path=str(CHROMA_DB_DIR))


@lru_cache
def get_tasks_collection():
    """ChromaDB only -- no Ollama needed, so daily-task tracking works
    independently of whether the chat agent is available."""
    return _get_chroma_client().get_or_create_collection(name="daily_tasks")


@lru_cache
def get_schedule_collection():
    """ChromaDB only, like get_tasks_collection() -- also used by main.py at
    startup to seed the predefined weekly schedule (see schedule_seed.py)."""
    return _get_chroma_client().get_or_create_collection(name="daily_schedule")


@lru_cache
def get_agent():
    """Lazily connects to Ollama/FAISS and builds the routing agent. Raises
    with a clear message on failure -- callers (the assistant router) turn
    that into a clean 503 rather than a raw 500."""
    from langchain_ollama import ChatOllama, OllamaEmbeddings

    embeddings = OllamaEmbeddings(model=OLLAMA_MODEL)
    llm = ChatOllama(model=OLLAMA_MODEL)
    vectorstore = load_or_build_vectorstore(embeddings)

    tools = _build_tools(llm, vectorstore, get_schedule_collection())
    return _build_agent(llm, tools)


async def ask_agent(message: str) -> str:
    greeting = greeting_response(message)
    if greeting is not None:
        return greeting

    agent = get_agent()
    result = await agent.ainvoke({"messages": [{"role": "user", "content": message}]})
    return result["messages"][-1].content
