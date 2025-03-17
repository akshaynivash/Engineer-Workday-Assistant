import streamlit as st
from transformers import BlenderbotSmallTokenizer, BlenderbotSmallForConditionalGeneration
import torch

# Check if CUDA is available
device = "cuda" if torch.cuda.is_available() else "cpu"

# Load the Blenderbot model and tokenizer
@st.cache_resource
def load_model():
    model_directory = "models/model_blenderbot"
    tokenizer = BlenderbotSmallTokenizer.from_pretrained(model_directory)
    model = BlenderbotSmallForConditionalGeneration.from_pretrained(model_directory)
    model.to(device)  # Move the model to GPU if available
    return model, tokenizer

model, tokenizer = load_model()

# Function to generate chatbot response
def generate_response(prompt):
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    reply_ids = model.generate(**inputs)
    response = tokenizer.batch_decode(reply_ids, skip_special_tokens=True)[0]
    return response

# Chatbot Page Function
def chatbot_page():
    st.title("💬 Personal Assistant Chatbot (Offline + CUDA)")

    # Initialize chat history
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    # Display chat history
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("What is up?"):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate chatbot response
        response = generate_response(prompt)

        with st.chat_message("assistant"):
            st.markdown(response)

        st.session_state.chat_messages.append({"role": "assistant", "content": response})
