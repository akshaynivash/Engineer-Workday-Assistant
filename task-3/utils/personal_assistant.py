"""Personal assistant page: chat (LangChain agent over Pinecone + Ollama RAG) and daily task tracking (ChromaDB).

Ported from task-1_chatbot/. Unlike the Part Finder and Chatbot pages, this one
depends on external services (Pinecone credentials, a locally running Ollama
with the llama2 model pulled) that aren't required for the rest of the app.
All of those imports/connections are deferred until this page is actually
opened, and failures show a friendly message instead of crashing the whole app.

Chat routing is a LangChain ReAct agent with one tool per capability (study
assistant, schedule lookup, meal planner, general chat), replacing a brittle
keyword-matching if/elif chain (e.g. "pdf" in prompt) that broke on any
paraphrasing the exact keywords didn't anticipate.
"""

import os

import streamlit as st

from utils.task_storage import DAILY_TASKS, store_task

GREETINGS = {"hi", "hello", "hey", "greetings", "how are you?"}

REACT_PROMPT_TEMPLATE = """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}"""


def _rag_response(llm, vectorstore, prompt_template: str, query: str) -> str:
    retriever = vectorstore.as_retriever()
    docs = retriever.get_relevant_documents(query)
    context_str = "\n\n".join(doc.page_content for doc in docs) if docs else ""
    return llm(prompt_template.format(query=query, context=context_str))


def _build_tools(llm, vectorstore, schedule_collection):
    from langchain.tools import Tool

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
        return llm(
            "You are my personal assistant who is very familiar with my daily schedule. "
            f"I have the following schedule for {day}:\n\n{schedule_info}\n\n"
            "Explain this schedule in a friendly, personalized tone."
        )

    def meal_plan_tool(query: str) -> str:
        return llm(
            "You are my personal meal planning assistant. Based on the following user input, generate a "
            "weekly meal plan for the entire week, with breakfast/lunch/dinner ideas and a complete "
            f"ingredients list for each day.\n\nUser Input: {query}\n\n"
            "Generate the plan in a clear, organized format."
        )

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
    from langchain.agents import AgentExecutor, create_react_agent
    from langchain_core.prompts import PromptTemplate

    prompt = PromptTemplate.from_template(REACT_PROMPT_TEMPLATE)
    agent = create_react_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=False, handle_parsing_errors=True, max_iterations=4)


@st.cache_resource
def _get_services():
    """Lazily connect to Pinecone/Ollama/ChromaDB and build the routing agent. Raises with a clear message on failure."""
    from dotenv import load_dotenv
    from langchain.llms.ollama import Ollama
    from langchain_ollama import OllamaEmbeddings
    from langchain_pinecone import PineconeVectorStore
    from pinecone import Pinecone
    import chromadb

    load_dotenv()
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    pinecone_index_name = os.getenv("PINECONE_INDEX_NAME")
    if not pinecone_api_key or not pinecone_index_name:
        raise RuntimeError("PINECONE_API_KEY and PINECONE_INDEX_NAME must be set in .env")

    pc = Pinecone(api_key=pinecone_api_key)
    index = pc.Index(pinecone_index_name)
    embeddings = OllamaEmbeddings(model="llama2")
    llm = Ollama(model="llama2")
    vectorstore = PineconeVectorStore(index, embeddings, text_key="text")

    chroma_client = chromadb.PersistentClient(path="./data/chroma_db")
    tasks_collection = chroma_client.get_or_create_collection(name="daily_tasks")
    schedule_collection = chroma_client.get_or_create_collection(name="daily_schedule")

    tools = _build_tools(llm, vectorstore, schedule_collection)
    agent_executor = _build_agent(llm, tools)

    return agent_executor, tasks_collection


def personal_assistant_page():
    st.title("🦙 Personal Assistant (Chat, Study, Meal Plan & Daily Tasks)")

    try:
        agent_executor, tasks_collection = _get_services()
    except Exception as e:
        st.error(
            "⚠️ Personal Assistant is unavailable — it needs Pinecone credentials (`PINECONE_API_KEY`, "
            "`PINECONE_INDEX_NAME` in `.env`) and a locally running Ollama with the `llama2` model pulled "
            "(`ollama pull llama2`). The rest of the app works fine without this."
        )
        st.caption(f"Details: {e}")
        return

    mode = st.sidebar.radio("Assistant mode:", ["Chat", "Daily Tasks"])

    if mode == "Daily Tasks":
        st.header("Daily Tasks Check-In")

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
            result = agent_executor.invoke({"input": prompt})
            response = result["output"]

        st.session_state.assistant_messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.write(response)
