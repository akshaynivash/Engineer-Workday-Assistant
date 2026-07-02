import streamlit as st
from utils.home import home_page
from utils.chatbot import chatbot_page
from utils.alternate_part import alternative_part_page
from utils.personal_assistant import personal_assistant_page

st.set_page_config(page_title="Alternative Part Finder", page_icon="🔧", layout="wide")

# Sidebar for navigation
st.sidebar.title("🔧 Alternative Part Finder")
st.sidebar.caption("Find replacement parts, chat, and manage your day — one app, three tools.")
page = st.sidebar.radio(
    "Select a Page",
    ["🏠 Home", "🔍 Alternative Part Finder", "💬 Chatbot", "🦙 Personal Assistant"],
)

# Page Routing
if page == "🏠 Home":
    home_page()
elif page == "💬 Chatbot":
    chatbot_page()
elif page == "🔍 Alternative Part Finder":
    alternative_part_page()
elif page == "🦙 Personal Assistant":
    personal_assistant_page()
