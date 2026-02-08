import re

MOVIE_PAT = re.compile(r"(?i)\b(movie|film)\b")
QUOTED_MOVIE_PAT = re.compile(r'"([^"]+)"|\'([^\']+)\'')


def classify_intent(text: str, context: dict) -> str:
    s = text.lower().strip()
    if any(g in s for g in ["hi", "hello", "hey"]):
        return "greet"
    if "who directed" in s:
        return "who_directed"
    if any(k in s for k in ["recommend", "suggest"]):
        return "recommend"
    if any(k in s for k in ["tell me about", "plot", "info"]) or MOVIE_PAT.search(s):
        return "movie_info"
    return "fallback"


def extract_entities(text: str) -> dict:
    entities: dict = {}
    m = QUOTED_MOVIE_PAT.search(text)
    if m:
        title = m.group(1) or m.group(2)
        entities["movies"] = [title]
    return entities
