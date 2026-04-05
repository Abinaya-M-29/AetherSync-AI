import streamlit as st
import requests

API_URL = "http://localhost:8000/chat_async"  # FastAPI endpoint for async chat

st.set_page_config(page_title="Chat UI", layout="wide")

st.title("💬 Chat App")

# Session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input box
user_input = st.chat_input("Type your message...")

if user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    # Call FastAPI backend
    try:
        response = requests.post(API_URL, json={"message": user_input})
        bot_reply = response.json()["response"]
    except Exception as e:
        bot_reply = f"Error: {e}"

    # Add bot response
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})

    with st.chat_message("assistant"):
        st.markdown(bot_reply)