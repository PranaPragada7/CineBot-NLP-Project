from __future__ import annotations

import os
from uuid import uuid4

import requests
import streamlit as st

API_URL = os.getenv("CINEBOT_API_URL", "http://127.0.0.1:8000").rstrip("/")
DEFAULT_SUGGESTIONS = [
    "What is trending?",
    "Who directed Inception?",
    "Recommend movies like Arrival",
]

st.set_page_config(page_title="CineBot", page_icon="🎬", layout="wide")
st.markdown(
    """
    <style>
        .stApp { background: #f6f7fb; color: #111827; }
        [data-testid="stSidebar"] { background: #101827; }
        [data-testid="stSidebar"] * { color: #e5e7eb; }
        [data-testid="stSidebar"] a { color: #a5b4fc !important; }
        [data-testid="stSidebar"] button {
            background: #4f46e5;
            border-color: #6366f1;
        }
        [data-testid="stSidebar"] button p { color: #ffffff !important; }
        .hero {
            padding: 2rem 2.2rem;
            border-radius: 22px;
            color: white;
            background: linear-gradient(120deg, #111827 0%, #312e81 55%, #7c3aed 100%);
            box-shadow: 0 18px 45px rgba(49, 46, 129, 0.18);
            margin-bottom: 1.5rem;
        }
        .hero h1 { margin: 0; font-size: 2.8rem; }
        .hero p { margin: .45rem 0 0; color: #e0e7ff; font-size: 1.08rem; }
        .source-card {
            border: 1px solid #e5e7eb;
            border-radius: 14px;
            padding: .8rem 1rem;
            background: white;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def api_status() -> tuple[bool, str]:
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        response.raise_for_status()
        return True, response.json().get("data_source", "unknown source")
    except requests.RequestException:
        return False, "API unavailable"


def submit_message(message: str) -> None:
    st.session_state.messages.append({"role": "user", "content": message})
    try:
        response = requests.post(
            f"{API_URL}/chat",
            json={"session_id": st.session_state.session_id, "message": message},
            timeout=15,
        )
        response.raise_for_status()
        payload = response.json()
        reply = payload["reply"]
        st.session_state.suggestions = payload.get("suggestions", [])
    except requests.RequestException:
        reply = (
            "I could not reach the CineBot API. Start it with " "`uvicorn src.app:app --reload`."
        )
        st.session_state.suggestions = []
    st.session_state.messages.append({"role": "assistant", "content": reply})


if "session_id" not in st.session_state:
    st.session_state.session_id = uuid4().hex
if "messages" not in st.session_state:
    st.session_state.messages = []
if "suggestions" not in st.session_state:
    st.session_state.suggestions = list(DEFAULT_SUGGESTIONS)

available, source = api_status()

with st.sidebar:
    st.markdown("## CineBot")
    st.caption("Movie discovery workspace")
    st.markdown("---")
    st.markdown("**Service status**")
    if available:
        st.success("API connected")
    else:
        st.error("API disconnected")
    st.caption(f"Data: {source}")
    st.caption(f"Endpoint: {API_URL}")
    st.markdown("---")
    if st.button("Clear conversation", use_container_width=True):
        try:
            requests.delete(f"{API_URL}/history/{st.session_state.session_id}", timeout=2)
        except requests.RequestException:
            pass
        st.session_state.messages = []
        st.session_state.suggestions = list(DEFAULT_SUGGESTIONS)
        st.rerun()

st.markdown(
    """
    <section class="hero">
      <h1>🎬 CineBot</h1>
      <p>Explore movies, directors, recommendations, and what is trending.</p>
    </section>
    """,
    unsafe_allow_html=True,
)

left, right = st.columns([3, 1])
with left:
    st.subheader("Movie conversation")
    st.caption("CineBot keeps context within this browser session.")
with right:
    st.markdown(
        f'<div class="source-card"><b>Data source</b><br>{source}</div>',
        unsafe_allow_html=True,
    )

if not st.session_state.messages:
    st.info("Start with a movie title, a director question, or a recommendation request.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if st.session_state.suggestions:
    columns = st.columns(min(len(st.session_state.suggestions), 3))
    for index, suggestion in enumerate(st.session_state.suggestions[:3]):
        if columns[index].button(suggestion, use_container_width=True):
            submit_message(suggestion)
            st.rerun()

if prompt := st.chat_input("Ask about a movie..."):
    submit_message(prompt)
    st.rerun()
