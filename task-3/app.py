import streamlit as st
from utils.chatbot import chatbot_page
from utils.alternate_part import alternative_part_page
from utils.alternate_part_without_genai import alternative_part_pagenogenai
# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select a Page", ["💬 Chatbot", "🔍 Alternative Part Finder","Alternative part- nogenai"])

# Page Routing
if page == "💬 Chatbot":
    chatbot_page()
elif page == "🔍 Alternative Part Finder":
    alternative_part_page()
elif page == "Alternative part- nogenai":
    alternative_part_pagenogenai()
