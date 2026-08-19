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
        :root {
            --night: #08090d;
            --panel: #14161d;
            --panel-soft: #1b1e27;
            --line: #2d303b;
            --ink: #f8f4ed;
            --muted: #aaa6a0;
            --accent: #e35d3f;
            --accent-dark: #9e2f26;
            --gold: #d7a852;
        }

        .stApp {
            background:
                radial-gradient(circle at 80% -10%, rgba(158, 47, 38, .24), transparent 28rem),
                var(--night);
            color: var(--ink);
        }
        html,
        body,
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"],
        [data-testid="stBottom"],
        [data-testid="stBottomBlockContainer"] {
            background-color: var(--night) !important;
        }
        header[data-testid="stHeader"] {
            background: rgba(8, 9, 13, .96) !important;
        }
        .block-container { max-width: 1120px; padding-top: 2.6rem; }
        [data-testid="stMain"] h1,
        [data-testid="stMain"] h2,
        [data-testid="stMain"] h3,
        [data-testid="stMain"] p,
        [data-testid="stMain"] label { color: var(--ink) !important; }
        [data-testid="stMain"] [data-testid="stCaptionContainer"] p {
            color: var(--muted) !important;
        }
        [data-testid="stSidebar"] {
            background: #0d0f15;
            border-right: 1px solid #252831;
        }
        [data-testid="stSidebar"] * { color: #e8e4dc; }
        [data-testid="stSidebar"] a { color: #efaa87 !important; }
        [data-testid="stSidebar"] button {
            background: linear-gradient(135deg, var(--accent), var(--accent-dark));
            border: 0;
        }
        [data-testid="stSidebar"] button p { color: #ffffff !important; }
        .hero {
            position: relative;
            overflow: hidden;
            padding: 2rem 2.2rem;
            border: 1px solid #6e3029;
            border-radius: 10px;
            color: white;
            background:
                linear-gradient(90deg, rgba(8, 9, 13, .25), transparent 45%),
                linear-gradient(120deg, #2b1213 0%, #7a2924 58%, #b94d32 100%);
            box-shadow: 0 20px 55px rgba(0, 0, 0, .38);
            margin-bottom: 1.8rem;
        }
        .hero::after {
            content: "CINEMA";
            position: absolute;
            right: -1rem;
            bottom: -1.1rem;
            color: rgba(255, 235, 205, .08);
            font-size: clamp(4rem, 10vw, 7rem);
            font-weight: 900;
            letter-spacing: .04em;
        }
        .hero h1 {
            position: relative;
            z-index: 1;
            margin: 0;
            font-size: 2.8rem;
            letter-spacing: -.035em;
        }
        .hero p {
            position: relative;
            z-index: 1;
            margin: .45rem 0 0;
            color: #f5ded2 !important;
            font-size: 1.08rem;
        }
        .source-card {
            border: 1px solid var(--line);
            border-left: 3px solid var(--gold);
            border-radius: 8px;
            padding: .8rem 1rem;
            background: var(--panel);
            color: var(--ink);
        }
        [data-testid="stAlert"] {
            border: 1px solid var(--line);
            background: var(--panel-soft);
        }
        [data-testid="stAlert"] p { color: #dbe7f8 !important; }
        div.stButton > button {
            border: 1px solid #3a3d48;
            border-radius: 6px;
            background: var(--panel);
            color: var(--ink);
        }
        div.stButton > button:hover {
            border-color: var(--accent);
            color: #ffffff;
        }
        div.stButton > button p { color: inherit !important; }
        [data-testid="stChatMessage"] {
            border: 1px solid var(--line);
            border-radius: 8px;
            background: rgba(20, 22, 29, .92);
        }
        [data-testid="stChatInput"] {
            overflow: hidden;
            border: 1px solid #3b3e49;
            border-radius: 8px;
            background: var(--panel) !important;
        }
        [data-testid="stChatInput"] > div,
        [data-testid="stChatInput"] > div > div,
        [data-testid="stChatInput"] textarea {
            background: var(--panel) !important;
            color: var(--ink) !important;
            -webkit-text-fill-color: var(--ink) !important;
        }
        [data-testid="stChatInput"] textarea::placeholder {
            color: #85828a !important;
            -webkit-text-fill-color: #85828a !important;
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
