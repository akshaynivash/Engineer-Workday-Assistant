# app.py
import os
import re
import streamlit as st
from dotenv import load_dotenv
import chromadb
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain.llms.ollama import Ollama  # Ensure the correct version is installed
from langchain_ollama import OllamaEmbeddings
from langchain.chains import RetrievalQA

# Import your ChromaDB-based tasks module
import tasks

# ----------------------------
# Load Environment Variables
# ----------------------------
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

# ----------------------------
# Backend Setup for Chat: Pinecone & LangChain for PDF Responses
# ----------------------------
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)

embeddings = OllamaEmbeddings(model="llama2")
llm = Ollama(model="llama2")

# Create vector store for PDF content (using field "text")
vectorstore = PineconeVectorStore(index, embeddings, text_key="text")

def generate_combined_response(query: str) -> str:
    retriever = vectorstore.as_retriever()
    docs = retriever.get_relevant_documents(query)
    context_str = "\n\n".join([doc.page_content for doc in docs]) if docs else ""
    prompt_template = (
        "You are my personal assistant. Answer the following question in a friendly, conversational tone. "
        "Incorporate any relevant information from the PDF context below, but only if it helps answer the query.\n\n"
        "Question: {query}\n\n"
        "PDF Context: {context}\n\n"
        "Also, feel free to ask how I'm doing if it fits naturally into the conversation."
    )
    final_prompt = prompt_template.format(query=query, context=context_str)
    response = llm(final_prompt)
    return response

def generate_study_response(query: str) -> str:
    retriever = vectorstore.as_retriever()
    docs = retriever.get_relevant_documents(query)
    context_str = "\n\n".join([doc.page_content for doc in docs]) if docs else ""
    prompt_template = (
        "You are my dedicated study assistant. Based on the following study material from my PDF, "
        "please provide me with the key study topics and any related details. Focus solely on the study content.\n\n"
        "Query: {query}\n\n"
        "Study Material: {context}\n\n"
        "List the main study topics and any important points."
    )
    final_prompt = prompt_template.format(query=query, context=context_str)
    response = llm(final_prompt)
    return response

def generate_personalized_content(query: str) -> str:
    personal_details = "I am a computer science student who loves AI, machine learning, and creative writing."
    prompt_template = (
        "You are my creative personal assistant. Based on my personal details: {personal_details}, "
        "please create a personalized content piece in response to the following request:\n\n"
        "Request: {query}\n\n"
        "Make the content engaging, friendly, and tailored to my interests."
    )
    final_prompt = prompt_template.format(personal_details=personal_details, query=query)
    response = llm(final_prompt)
    return response

def generate_meal_plan(query: str) -> str:
    """
    Generate a detailed weekly meal plan based on the user's input.
    The plan should include dish ideas for breakfast, lunch, and dinner for each day,
    along with an ingredients list.
    """
    prompt_template = (
        "You are my personal meal planning assistant. "
        "Based on the following user input, generate a weekly meal plan for the entire week. "
        "The meal plan should include breakfast, lunch, and dinner for each day. "
        "For each meal, provide a dish idea along with a complete ingredients list and any preparation instructions. "
        "User Input: {query}\n\n"
        "Generate the plan in a clear, organized format."
    )
    final_prompt = prompt_template.format(query=query)
    response = llm(final_prompt)
    return response

# ----------------------------
# ChromaDB for Schedule Queries (if needed)
# ----------------------------
chroma_client = chromadb.PersistentClient(path="./data/chroma_db")
schedule_collection = chroma_client.get_collection("daily_schedule")

def get_study_schedule(day: str) -> str:
    results = schedule_collection.query(query_texts=[day], n_results=1)
    return results["documents"][0] if results["documents"] else "No schedule found."

def extract_day(query: str) -> str:
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    for day in days:
        if day in query.lower():
            return day.capitalize()
    return None

def generate_schedule_response(day: str, query: str) -> str:
    schedule_info = get_study_schedule(day)
    prompt_template = (
        "You are my personal assistant who is very familiar with my daily schedule. "
        "I have the following schedule for {day}:\n\n{schedule_info}\n\n"
        "User asks: {query}\n\n"
        "Please answer interactively, explaining how this schedule works and asking follow-up questions if needed. "
        "Keep the tone friendly and personalized."
    )
    final_prompt = prompt_template.format(day=day, schedule_info=schedule_info, query=query)
    response = llm(final_prompt)
    return response

# ----------------------------
# Streamlit Frontend
# ----------------------------
GREETINGS = {"hi", "hello", "hey", "greetings", "how are you?"}

st.set_page_config(page_title="🦙💬 Personal Assistant (Meal Plan, Study, Chat & Daily Tasks)")

# Sidebar Navigation: Chat or Daily Tasks
app_mode = st.sidebar.radio("Choose the app mode:", ["Chat", "Daily Tasks"])

if app_mode == "Daily Tasks":
    st.header("Daily Tasks Check-In (ChromaDB)")

    # Single Task
    st.subheader("Store a Single Task")
    single_task = st.text_input("Task:", key="single_task")
    single_answer = st.text_input("Answer:", key="single_answer")
    single_day = st.text_input("Day (YYYY-MM-DD)", value="")  # if blank, defaults to today's date

    if st.button("Save Single Task"):
        if single_task and single_answer:
            result = tasks.store_task(single_task, single_answer, day=single_day if single_day else None)
            st.write(result)
        else:
            st.warning("Please provide both a task and an answer.")

    # Multiple Daily Tasks
    st.subheader("Store Multiple Daily Tasks")
    daily_tasks = [
        "Complete Duolingo",
        "Take vitamins",
        "Drink 3 L water",
        "Snapscore check",
        "Prepare a topic for stat exam",
        "Surf new tech update",
        "Good moment of a day",
        "Bad moment of a day",
        "Today's affirmation"
    ]

    day_for_all = st.text_input("Day for all tasks (YYYY-MM-DD)", value="")
    responses = {}
    for dt in daily_tasks:
        responses[dt] = st.text_input(f"{dt}:", key=dt)

    if st.button("Save All Listed Tasks"):
        for task_name, answer in responses.items():
            if answer:
                tasks.store_task(task=task_name, answer=answer, day=day_for_all if day_for_all else None)
        st.success("All entered tasks have been saved!")

    # Show Recent Tasks
    st.subheader("Show Recent Tasks")
    if st.button("Show Recent 5 Tasks"):
        recent_tasks = tasks.get_recent_tasks(n=5)
        st.write("Recent Tasks:\n", recent_tasks)

else:
    st.header("Chat with Your Assistant")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! How are you doing today? How may I assist you?"}
        ]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    def clear_chat_history():
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! How are you doing today? How may I assist you?"}
        ]
    st.sidebar.button("Clear Chat History", on_click=clear_chat_history)

    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        lower_prompt = prompt.lower().strip()
        response = ""
        day = extract_day(prompt)
        
        # Branching logic for chat
        if lower_prompt in GREETINGS:
            if lower_prompt == "how are you?":
                response = "I'm doing well, thanks for asking! How are you doing?"
            else:
                response = "Hello! I'm here to help. How are you doing today?"
        elif day and ("schedule" in lower_prompt or "plan" in lower_prompt or "study time" in lower_prompt):
            response = generate_schedule_response(day, prompt)
        elif "pdf" in lower_prompt:
            response = generate_study_response(prompt)
        elif "today's topic" in lower_prompt or ("study" in lower_prompt and "explain" in lower_prompt):
            response = generate_combined_response(prompt)
        elif "weekly plan" in lower_prompt and "study" in lower_prompt:
            response = generate_combined_response(prompt)
        elif "personalized content" in lower_prompt or "create content" in lower_prompt:
            response = generate_personalized_content(prompt)
        elif "meal plan" in lower_prompt or ("fridge" in lower_prompt and "buy" in lower_prompt):
            response = generate_meal_plan(prompt)
        else:
            response = generate_combined_response(prompt)
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.write(response)
