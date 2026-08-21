# ruff: noqa: E501 -- embedded CSS and HTML are clearer when selectors and markup stay intact.

from __future__ import annotations

import html
import os
from uuid import uuid4

import requests
import streamlit as st

API_URL = os.getenv("CINEBOT_API_URL", "http://127.0.0.1:8000").rstrip("/")
if not API_URL.startswith(("http://", "https://")):
    API_URL = f"http://{API_URL}"

DEFAULT_SUGGESTIONS = [
    "What is trending?",
    "Who directed Inception?",
    "Recommend movies like Arrival",
]

st.set_page_config(
    page_title="CineBot · AI Movie Discovery",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        :root {
            --canvas: #071019;
            --panel-raised: #14263a;
            --line: rgba(148, 177, 201, .18);
            --line-strong: rgba(148, 177, 201, .32);
            --ink: #f7f9fc;
            --muted: #a7b5c3;
            --accent: #ffb454;
            --accent-hot: #ff6b4a;
            --mint: #61d9aa;
            --blue: #77bdfb;
            --danger: #ff7a85;
        }

        html, body, [class*="css"] { font-family: Inter, ui-sans-serif, system-ui, sans-serif; }
        .stApp {
            background:
                radial-gradient(circle at 74% -8%, rgba(47, 117, 154, .25), transparent 32rem),
                radial-gradient(circle at 14% 30%, rgba(255, 107, 74, .08), transparent 28rem),
                var(--canvas);
            color: var(--ink);
        }
        [data-testid="stAppViewContainer"], [data-testid="stMain"],
        [data-testid="stBottom"], [data-testid="stBottomBlockContainer"] {
            background: transparent !important;
        }
        header[data-testid="stHeader"] { background: rgba(7, 16, 25, .82) !important; }
        [data-testid="stToolbar"], .stDeployButton { display: none !important; }
        .block-container { max-width: 1240px; padding: 2.4rem 2.5rem 6rem; }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0b1724 0%, #08131e 100%);
            border-right: 1px solid var(--line);
        }
        [data-testid="stSidebar"] > div:first-child { padding-top: 1.7rem; }
        [data-testid="stSidebar"] * { color: var(--ink); }
        [data-testid="stSidebar"] hr { border-color: var(--line); }
        [data-testid="stSidebar"] a { color: var(--blue) !important; }

        .brand-lockup { display: flex; align-items: center; gap: .8rem; margin-bottom: .35rem; }
        .brand-mark {
            display: grid; place-items: center; width: 2.35rem; height: 2.35rem;
            border-radius: .72rem; color: #08111a; font-size: 1.15rem;
            background: linear-gradient(135deg, var(--accent), var(--accent-hot));
            box-shadow: 0 9px 24px rgba(255, 107, 74, .2);
        }
        .brand-name { font-size: 1.12rem; font-weight: 800; letter-spacing: -.02em; }
        .brand-subtitle { color: var(--muted); font-size: .76rem; letter-spacing: .02em; }

        .status-panel {
            margin: 1rem 0 1.1rem; padding: .95rem; border: 1px solid var(--line);
            border-radius: .9rem; background: rgba(20, 38, 58, .66);
        }
        .status-row { display: flex; align-items: center; justify-content: space-between; gap: .8rem; }
        .status-label { color: var(--muted); font-size: .76rem; }
        .status-value { color: var(--ink); font-size: .78rem; font-weight: 650; text-align: right; }
        .status-divider { height: 1px; margin: .62rem 0; background: var(--line); }
        .live-dot {
            display: inline-block; width: .48rem; height: .48rem; margin-right: .38rem;
            border-radius: 50%; background: var(--mint); box-shadow: 0 0 0 .24rem rgba(97,217,170,.12);
        }
        .offline-dot { background: var(--danger); box-shadow: 0 0 0 .24rem rgba(255,122,133,.12); }

        .hero-shell {
            position: relative; overflow: hidden; min-height: 245px; padding: 2.5rem 2.65rem;
            border: 1px solid rgba(255, 180, 84, .28); border-radius: 1.35rem;
            background:
                linear-gradient(100deg, rgba(8, 19, 30, .98) 0%, rgba(15, 35, 51, .92) 53%, rgba(48, 42, 38, .7) 100%),
                repeating-linear-gradient(90deg, transparent 0 30px, rgba(255,255,255,.025) 30px 31px);
            box-shadow: 0 30px 80px rgba(0, 0, 0, .28);
        }
        .hero-shell::before {
            content: ""; position: absolute; width: 22rem; height: 22rem; right: -7rem; top: -9rem;
            border-radius: 50%; border: 2.2rem solid rgba(255, 180, 84, .08);
            box-shadow: 0 0 0 2.2rem rgba(119, 189, 251, .035), 0 0 0 4.4rem rgba(255,255,255,.018);
        }
        .hero-shell::after {
            content: "CINEMA / INTELLIGENCE"; position: absolute; right: 2.2rem; bottom: 1.4rem;
            color: rgba(247,249,252,.14); font-size: .68rem; font-weight: 800; letter-spacing: .22em;
        }
        .eyebrow {
            position: relative; z-index: 1; color: var(--accent); font-size: .72rem;
            font-weight: 800; letter-spacing: .18em; text-transform: uppercase;
        }
        .hero-shell h1 {
            position: relative; z-index: 1; max-width: 750px; margin: .72rem 0 .8rem;
            color: var(--ink) !important; font-size: clamp(2.35rem, 5vw, 4.1rem);
            line-height: .98; letter-spacing: -.055em;
        }
        .hero-shell p {
            position: relative; z-index: 1; max-width: 680px; margin: 0;
            color: #c6d2dd !important; font-size: 1rem; line-height: 1.6;
        }
        .hero-badges { position: relative; z-index: 1; display: flex; gap: .55rem; margin-top: 1.35rem; flex-wrap: wrap; }
        .hero-badge {
            padding: .38rem .65rem; border: 1px solid var(--line-strong); border-radius: 99px;
            color: #dce6ef; background: rgba(7,16,25,.46); font-size: .7rem; font-weight: 650;
        }

        .metric-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: .8rem; margin: 1rem 0 1.8rem; }
        .metric-card {
            min-height: 90px; padding: 1rem 1.05rem; border: 1px solid var(--line);
            border-radius: .95rem; background: rgba(16,31,47,.72);
        }
        .metric-value { margin-top: .35rem; color: var(--ink); font-size: 1.05rem; font-weight: 780; letter-spacing: -.02em; }
        .metric-label { color: var(--muted); font-size: .69rem; font-weight: 700; letter-spacing: .11em; text-transform: uppercase; }

        .section-kicker { color: var(--accent); font-size: .68rem; font-weight: 800; letter-spacing: .15em; text-transform: uppercase; }
        .section-title { margin: .28rem 0 .2rem; color: var(--ink); font-size: 1.65rem; font-weight: 800; letter-spacing: -.035em; }
        .section-copy { color: var(--muted); font-size: .88rem; line-height: 1.55; }
        .empty-state {
            margin: .8rem 0 1rem; padding: 1.05rem 1.1rem; border: 1px dashed var(--line-strong);
            border-radius: .9rem; color: #bdcad5; background: rgba(11, 23, 36, .58); font-size: .88rem;
        }

        [data-testid="stTabs"] [data-baseweb="tab-list"] {
            gap: .4rem; padding: .3rem; border: 1px solid var(--line); border-radius: .85rem;
            background: rgba(11,23,36,.72);
        }
        [data-testid="stTabs"] [data-baseweb="tab"] {
            height: 2.65rem; padding: 0 1rem; border-radius: .62rem; color: var(--muted);
        }
        [data-testid="stTabs"] [aria-selected="true"] { color: var(--ink); background: var(--panel-raised); }
        [data-testid="stTabs"] [data-baseweb="tab-highlight"] { display: none; }
        [data-testid="stTabs"] [data-baseweb="tab-panel"] { padding-top: 1.35rem; }

        [data-testid="stChatMessage"] {
            margin-bottom: .65rem; padding: .7rem .8rem; border: 1px solid var(--line);
            border-radius: .9rem; background: rgba(16,31,47,.76);
        }
        [data-testid="stChatInput"] {
            overflow: hidden; border: 1px solid var(--line-strong); border-radius: .9rem;
            background: var(--panel-raised) !important; box-shadow: 0 14px 36px rgba(0,0,0,.2);
        }
        [data-testid="stChatInput"] > div, [data-testid="stChatInput"] > div > div,
        [data-testid="stChatInput"] textarea {
            background: var(--panel-raised) !important; color: var(--ink) !important;
            -webkit-text-fill-color: var(--ink) !important;
        }
        [data-testid="stChatInput"] textarea::placeholder { color: #8496a7 !important; -webkit-text-fill-color: #8496a7 !important; }

        [data-testid="stTextInput"] input {
            min-height: 2.8rem; border: 1px solid var(--line-strong); border-radius: .7rem;
            background: rgba(9,21,33,.92); color: var(--ink); -webkit-text-fill-color: var(--ink);
        }
        [data-testid="stTextInput"] input::placeholder { color: #6f8294; -webkit-text-fill-color: #6f8294; }
        [data-testid="stTextInput"] label p { color: #c7d2dc !important; font-size: .78rem; font-weight: 700; }

        div.stButton > button {
            min-height: 2.62rem; border: 1px solid var(--line-strong); border-radius: .68rem;
            background: rgba(20,38,58,.78); color: var(--ink); font-weight: 650;
        }
        div.stButton > button:hover { border-color: var(--accent); color: var(--ink); background: rgba(45,54,60,.96); }
        div.stButton > button[kind="primary"] {
            border: 0; color: #14100a; background: linear-gradient(135deg, var(--accent), #ff9060);
            box-shadow: 0 10px 25px rgba(255,144,96,.18);
        }
        div.stButton > button p { color: inherit !important; }
        [data-testid="stSidebar"] div.stButton > button { width: 100%; background: transparent; }

        .result-card {
            margin: .85rem 0; padding: 1.05rem 1.1rem; border: 1px solid var(--line);
            border-radius: .95rem; background: linear-gradient(135deg, rgba(20,38,58,.94), rgba(10,24,37,.9));
        }
        .result-top { display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem; }
        .result-title { color: var(--ink); font-size: 1.04rem; font-weight: 800; letter-spacing: -.015em; }
        .result-meta { margin-top: .2rem; color: var(--muted); font-size: .74rem; }
        .match-score {
            flex: 0 0 auto; padding: .35rem .55rem; border-radius: .55rem; color: #0b1a22;
            background: var(--mint); font-size: .72rem; font-weight: 850;
        }
        .result-overview { margin: .75rem 0; color: #c1ced9; font-size: .8rem; line-height: 1.55; }
        .signal-row { display: flex; gap: .42rem; flex-wrap: wrap; }
        .signal-chip {
            padding: .28rem .48rem; border: 1px solid var(--line); border-radius: .45rem;
            color: #aebdca; background: rgba(6,15,24,.45); font-size: .67rem;
        }
        .reason-line { margin-top: .65rem; color: var(--blue); font-size: .72rem; }

        [data-testid="stAlert"] { border: 1px solid var(--line); border-radius: .8rem; background: rgba(20,38,58,.78); }
        [data-testid="stAlert"] p { color: #dce6ef !important; }
        [data-testid="stCaptionContainer"] p { color: var(--muted) !important; }

        @media (max-width: 900px) {
            .block-container { padding: 1.5rem 1rem 5rem; }
            .hero-shell { min-height: 220px; padding: 1.7rem 1.35rem; }
            .metric-grid { grid-template-columns: repeat(2, 1fr); }
        }
        @media (max-width: 600px) {
            .hero-shell h1 { font-size: 2.25rem; }
            .metric-grid { grid-template-columns: 1fr; }
            .hero-shell::after { display: none; }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def api_status() -> tuple[bool, str, dict, dict]:
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        response.raise_for_status()
        payload = response.json()
        return (
            True,
            payload.get("data_source", "unknown source"),
            payload.get("recommender", {}),
            {
                "database": payload.get("database", {}),
                "rate_limit": payload.get("rate_limit", {}),
            },
        )
    except requests.RequestException:
        return False, "API unavailable", {}, {}


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
        reply = "I could not reach the local CineBot API. Start it on port 8000 and try again."
        st.session_state.suggestions = []
    st.session_state.messages.append({"role": "assistant", "content": reply})


def render_metric(label: str, value: str) -> str:
    return (
        '<div class="metric-card">'
        f'<div class="metric-label">{html.escape(label)}</div>'
        f'<div class="metric-value">{html.escape(value)}</div>'
        "</div>"
    )


def render_result_card(movie: dict) -> None:
    signals = movie.get("signals", {})
    genres = " · ".join(movie.get("genres", [])) or "Genre unavailable"
    release_year = str(movie.get("release_date", ""))[:4] or "Year unavailable"
    director = movie.get("director") or "Director unavailable"
    match_score = float(movie.get("match_score", 0))
    chips = "".join(
        f'<span class="signal-chip">{name} {float(signals.get(key, 0)):.0%}</span>'
        for name, key in (
            ("Semantic", "semantic"),
            ("NMF", "nmf"),
            ("SVD", "svd"),
            ("Quality", "quality"),
        )
    )
    st.markdown(
        f"""
        <article class="result-card">
          <div class="result-top">
            <div>
              <div class="result-title">{html.escape(str(movie.get("title", "Untitled")))}</div>
              <div class="result-meta">{html.escape(release_year)} · {html.escape(director)} · {html.escape(genres)}</div>
            </div>
            <div class="match-score">{match_score:.0%} match</div>
          </div>
          <div class="result-overview">{html.escape(str(movie.get("overview", "No overview available.")))}</div>
          <div class="signal-row">{chips}</div>
          <div class="reason-line">↳ {html.escape(str(movie.get("reason", "Hybrid model recommendation")))}</div>
        </article>
        """,
        unsafe_allow_html=True,
    )


if "session_id" not in st.session_state:
    st.session_state.session_id = uuid4().hex
if "messages" not in st.session_state:
    st.session_state.messages = []
if "suggestions" not in st.session_state:
    st.session_state.suggestions = list(DEFAULT_SUGGESTIONS)
if "recommendation_results" not in st.session_state:
    st.session_state.recommendation_results = []

available, source, model, infrastructure = api_status()
database = infrastructure.get("database", {})
rate_limit = infrastructure.get("rate_limit", {})
catalog_size = int(model.get("catalog_size", 0))
index_name = str(model.get("retrieval_index", "Unavailable"))
collaborative_models = model.get("collaborative_models", [])

with st.sidebar:
    st.markdown(
        """
        <div class="brand-lockup">
          <div class="brand-mark">▶</div>
          <div><div class="brand-name">CineBot</div><div class="brand-subtitle">MOVIE INTELLIGENCE</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div class="status-panel">
          <div class="status-row"><span class="status-label">Local API</span><span class="status-value"><i class="live-dot {'offline-dot' if not available else ''}"></i>{'Online' if available else 'Offline'}</span></div>
          <div class="status-divider"></div>
          <div class="status-row"><span class="status-label">Data source</span><span class="status-value">{html.escape(source)}</span></div>
          <div class="status-divider"></div>
          <div class="status-row"><span class="status-label">Database</span><span class="status-value">{html.escape(str(database.get('backend', 'unknown')).title())}</span></div>
          <div class="status-divider"></div>
          <div class="status-row"><span class="status-label">Rate limiting</span><span class="status-value">{html.escape(str(rate_limit.get('backend', 'memory')).title())}</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Local development mode · no public hosting or cloud billing")
    st.markdown("---")
    st.markdown("**Session controls**")
    if st.button("Clear conversation", use_container_width=True):
        try:
            requests.delete(f"{API_URL}/history/{st.session_state.session_id}", timeout=2)
        except requests.RequestException:
            pass
        st.session_state.messages = []
        st.session_state.suggestions = list(DEFAULT_SUGGESTIONS)
        st.rerun()
    st.caption(f"API endpoint · {API_URL}")

st.markdown(
    """
    <section class="hero-shell">
      <div class="eyebrow">AI-powered movie discovery</div>
      <h1>Find the next film worth your time.</h1>
      <p>Ask naturally, explore explainable recommendations, and build a taste profile—all from a local, privacy-friendly workspace.</p>
      <div class="hero-badges">
        <span class="hero-badge">Semantic search</span>
        <span class="hero-badge">Hybrid ranking</span>
        <span class="hero-badge">Conversation memory</span>
      </div>
    </section>
    """,
    unsafe_allow_html=True,
)

collaborative_label = " + ".join(
    str(item).replace("Truncated", "") for item in collaborative_models
)
metrics = "".join(
    [
        render_metric("Catalog", f"{catalog_size or 24} curated films"),
        render_metric("Retrieval", index_name.replace("IndexFlatIP", "semantic index")),
        render_metric("Personalization", collaborative_label or "NMF + SVD"),
        render_metric("Storage", f"{str(database.get('backend', 'SQLite')).title()} · persistent"),
    ]
)
st.markdown(f'<section class="metric-grid">{metrics}</section>', unsafe_allow_html=True)

assistant_tab, discovery_tab = st.tabs(["✦ Movie assistant", "◎ Recommendation lab"])

with assistant_tab:
    st.markdown(
        '<div class="section-kicker">Conversational discovery</div>', unsafe_allow_html=True
    )
    st.markdown('<div class="section-title">Ask CineBot</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-copy">Ask about a director, follow up on a film, or describe the mood you want.</div>',
        unsafe_allow_html=True,
    )

    if not st.session_state.messages:
        st.markdown(
            '<div class="empty-state">Start with a movie title, a director question, or a recommendation request. CineBot will keep context for follow-up questions.</div>',
            unsafe_allow_html=True,
        )

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if st.session_state.suggestions:
        st.caption("QUICK STARTS")
        columns = st.columns(min(len(st.session_state.suggestions), 3))
        for index, suggestion in enumerate(st.session_state.suggestions[:3]):
            if columns[index].button(
                suggestion, use_container_width=True, key=f"suggestion-{index}"
            ):
                submit_message(suggestion)
                st.rerun()

    if prompt := st.chat_input("Ask about a movie, director, genre, or mood…"):
        submit_message(prompt)
        st.rerun()

with discovery_tab:
    st.markdown(
        '<div class="section-kicker">Explainable recommendations</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="section-title">Recommendation lab</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-copy">Combine a seed film with a natural-language brief. Every result exposes the signals behind its rank.</div>',
        unsafe_allow_html=True,
    )

    with st.form("recommendation-form"):
        seed_column, query_column = st.columns([1, 2])
        with seed_column:
            seed_title = st.text_input("Seed movie", placeholder="Arrival")
        with query_column:
            discovery_query = st.text_input(
                "Discovery brief", placeholder="Thoughtful science fiction about identity"
            )
        generate = st.form_submit_button("Generate recommendations", type="primary")

    if generate:
        if not seed_title.strip() and not discovery_query.strip():
            st.warning("Enter a seed movie or a discovery brief.")
        else:
            try:
                response = requests.post(
                    f"{API_URL}/recommendations",
                    json={
                        "seed_title": seed_title.strip() or None,
                        "query": discovery_query.strip() or None,
                        "user_id": st.session_state.session_id,
                        "limit": 5,
                    },
                    timeout=15,
                )
                response.raise_for_status()
                st.session_state.recommendation_results = response.json().get("recommendations", [])
            except requests.RequestException:
                st.error("The local recommendation service could not complete this request.")

    if not st.session_state.recommendation_results:
        st.markdown(
            '<div class="empty-state">Your ranked shortlist will appear here with match confidence, model signals, and a concise explanation.</div>',
            unsafe_allow_html=True,
        )

    for movie in st.session_state.recommendation_results:
        render_result_card(movie)
        if st.button("Add to taste profile", key=f"like-{movie['id']}"):
            try:
                response = requests.post(
                    f"{API_URL}/ratings",
                    json={
                        "user_id": st.session_state.session_id,
                        "movie_id": movie["id"],
                        "rating": 5,
                    },
                    timeout=15,
                )
                response.raise_for_status()
                st.success(f"{movie['title']} was added to this session's taste profile.")
            except requests.RequestException:
                st.error("The rating could not be saved locally.")
