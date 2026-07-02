import streamlit as st
from utils.chatbot import chatbot_page
from utils.alternate_part import alternative_part_page
from utils.personal_assistant import personal_assistant_page

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select a Page", ["💬 Chatbot", "🔍 Alternative Part Finder", "🦙 Personal Assistant"])

# Page Routing
if page == "💬 Chatbot":
    chatbot_page()
elif page == "🔍 Alternative Part Finder":
    alternative_part_page()
elif page == "🦙 Personal Assistant":
    personal_assistant_page()
