"""Personal assistant page: chat (LangChain agent over a local FAISS + Ollama RAG) and daily task tracking (ChromaDB).

Ported from task-1_chatbot/. Unlike the Part Finder and Chatbot pages, this one
depends on an external service (a locally running Ollama with a tool-calling-
capable model pulled -- see OLLAMA_MODEL below) that isn't required for the
rest of the app. The study/general-chat RAG tools use a local FAISS index (see
utils/vectorstore.py) instead of Pinecone -- no cloud account or API key
needed, only Ollama. All of this is deferred until the page is actually
opened, and failures show a friendly message instead of crashing the whole app.

Chat routing is a LangChain tool-calling agent (langchain.agents.create_agent,
the modern LangChain 1.x agent API -- the older text-parsing ReAct
AgentExecutor/create_react_agent no longer exists in current LangChain) with
one tool per capability (study assistant, schedule lookup, meal planner,
general chat), replacing a brittle keyword-matching if/elif chain (e.g.
"pdf" in prompt) that broke on any paraphrasing the exact keywords didn't
anticipate.

Tool-calling agents need a chat model that supports native tool calling.
Plain "llama2" (2023) predates Ollama's tool-calling support and will not
work reliably here -- use a tool-calling-capable model instead, e.g.
"llama3.1" (the default) or "qwen2.5". Override via the OLLAMA_MODEL env var.
"""

import os

import streamlit as st

from utils.task_storage import DAILY_TASKS, store_task
from utils.vectorstore import load_or_build_vectorstore

GREETINGS = {"hi", "hello", "hey", "greetings", "how are you?"}

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")

SYSTEM_PROMPT = (
    "You are a helpful personal assistant. Use the StudyAssistant tool for questions about study "
    "material or PDF content, ScheduleLookup for the user's daily schedule (input: a day name like "
    "'Monday'), MealPlanner for weekly meal planning requests, and GeneralAssistant for anything else. "
    "Always use a tool -- don't answer from your own knowledge alone."
)


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


@st.cache_resource
def _get_services():
    """Lazily connect to Ollama/FAISS/ChromaDB and build the routing agent. Raises with a clear message on failure."""
    from langchain_ollama import ChatOllama, OllamaEmbeddings
    import chromadb

    embeddings = OllamaEmbeddings(model=OLLAMA_MODEL)
    llm = ChatOllama(model=OLLAMA_MODEL)
    vectorstore = load_or_build_vectorstore(embeddings)

    chroma_client = chromadb.PersistentClient(path="./data/chroma_db")
    tasks_collection = chroma_client.get_or_create_collection(name="daily_tasks")
    schedule_collection = chroma_client.get_or_create_collection(name="daily_schedule")

    tools = _build_tools(llm, vectorstore, schedule_collection)
    agent = _build_agent(llm, tools)

    return agent, tasks_collection


def personal_assistant_page():
    st.title("🦙 Personal Assistant")
    st.caption(
        "A bonus sidekick, separate from part-finding: ask about your schedule, get a meal plan, "
        "get study help on indexed material, or just chat — a LangChain agent figures out which of "
        "those you mean instead of relying on exact keywords."
    )

    try:
        agent, tasks_collection = _get_services()
    except Exception as e:
        st.error(
            f"⚠️ Personal Assistant is unavailable — it needs a locally running Ollama with a "
            f"tool-calling-capable model pulled (default: `{OLLAMA_MODEL}` — run `ollama pull {OLLAMA_MODEL}`, "
            "or set the OLLAMA_MODEL env var to a different tool-calling model). "
            "The rest of the app works fine without this."
        )
        st.caption(f"Details: {e}")
        return

    mode = st.sidebar.radio("Assistant mode:", ["Chat", "Daily Tasks"])

    if mode == "Daily Tasks":
        st.header("Daily Tasks Check-In")
        st.caption("A simple daily journal/checklist, stored in ChromaDB — log a task and how it went.")

        st.subheader("Store a Single Task")
        single_task = st.text_input("Task:", key="single_task")
        single_answer = st.text_input("Answer:", key="single_answer")
        single_day = st.text_input("Day (YYYY-MM-DD)", value="", key="single_day")
        if st.button("Save Single Task"):
            if single_task and single_answer:
                st.write(store_task(tasks_collection, single_task, single_answer, single_day or None))
            else:
                st.warning("Please provide both a task and an answer.")

        st.subheader("Store Multiple Daily Tasks")
        day_for_all = st.text_input("Day for all tasks (YYYY-MM-DD)", value="", key="day_for_all")
        responses = {dt: st.text_input(f"{dt}:", key=dt) for dt in DAILY_TASKS}
        if st.button("Save All Listed Tasks"):
            for task_name, answer in responses.items():
                if answer:
                    store_task(tasks_collection, task_name, answer, day_for_all or None)
            st.success("All entered tasks have been saved!")

        st.subheader("Show Recent Tasks")
        if st.button("Show Recent 5 Tasks"):
            results = tasks_collection.get(limit=5)
            st.write("Recent Tasks:\n" + ("\n\n".join(results["documents"]) if results["documents"] else "No tasks found."))
        return

    st.header("Chat with Your Assistant")
    st.caption(
        "Try: *\"What's my schedule for Monday?\"* · *\"Plan my meals for this week\"* · "
        "*\"Explain today's topic from the study material\"* · or just say hi."
    )
    if "assistant_messages" not in st.session_state:
        st.session_state.assistant_messages = [
            {"role": "assistant", "content": "Hello! How are you doing today? How may I assist you?"}
        ]
    for message in st.session_state.assistant_messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if prompt := st.chat_input(key="assistant_chat_input"):
        st.session_state.assistant_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        lower_prompt = prompt.lower().strip()
        if lower_prompt in GREETINGS:
            # Fast path -- skip the agent for trivial greetings, no LLM call needed.
            response = (
                "I'm doing well, thanks for asking! How are you doing?"
                if lower_prompt == "how are you?"
                else "Hello! I'm here to help. How are you doing today?"
            )
        else:
            result = agent.invoke({"messages": [{"role": "user", "content": prompt}]})
            response = result["messages"][-1].content

        st.session_state.assistant_messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.write(response)
