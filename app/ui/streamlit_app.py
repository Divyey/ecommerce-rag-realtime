import streamlit as st
import requests

API_URL = "http://localhost:8000/api/chatbot"

st.set_page_config(page_title="E-Commerce Chatbot", page_icon="🛒")

st.title("🛒 E-Commerce Chatbot")
st.write("Ask anything about our products, orders, or offers!")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def get_bot_reply(message):
    resp = requests.post(API_URL, json={"message": message})
    if resp.status_code == 200:
        return resp.json().get("reply", "No reply")
    else:
        return f"Error: {resp.status_code} - {resp.text}"

# Chat UI
user_input = st.text_input("You:", key="user_input")
if st.button("Send") and user_input.strip():
    st.session_state.chat_history.append(("user", user_input))
    bot_reply = get_bot_reply(user_input)
    st.session_state.chat_history.append(("bot", bot_reply))
    st.session_state.user_input = ""  # Clear input box

# Display chat history
for sender, msg in st.session_state.chat_history:
    if sender == "user":
        st.markdown(f"**You:** {msg}")
    else:
        st.markdown(f"**Bot:** {msg}")
