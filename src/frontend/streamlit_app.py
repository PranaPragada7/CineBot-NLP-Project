import uuid

import requests
import streamlit as st

st.set_page_config(page_title="CineBot", page_icon="🎬")
st.title("🎬 CineBot")
st.write("Your AI Movie Companion. Ask me about movies, directors, or for recommendations!")

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Function to handle sending a message
def send_message(message):
    st.session_state.messages.append({"role": "user", "content": message})
    with st.chat_message("user"):
        st.markdown(message)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    "http://127.0.0.1:8000/chat",
                    json={"session_id": st.session_state.session_id, "message": message},
                    timeout=60,
                )
                response.raise_for_status()
                data = response.json()
                reply = data.get("reply", "Sorry, something went wrong.")
                suggestions = data.get("suggestions", [])
            except requests.RequestException as e:
                reply = f"Error: Could not connect to the chatbot service. {e}"
                suggestions = []

        st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})
        # Store suggestions for the next input
        st.session_state.suggestions = suggestions


# Handle user input
if prompt := st.chat_input("What's on your mind?"):
    send_message(prompt)
    # Rerun to clear the input box and display suggestions
    st.rerun()

# Display suggestions as buttons after the chat
if "suggestions" in st.session_state and st.session_state.suggestions:
    cols = st.columns(len(st.session_state.suggestions))
    for i, suggestion in enumerate(st.session_state.suggestions):
        with cols[i]:
            if st.button(suggestion, use_container_width=True):
                send_message(suggestion)
                # Clear suggestions after one is clicked
                st.session_state.suggestions = []
                st.rerun()
