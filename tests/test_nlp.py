import pytest

from src.catalog import OFFLINE_MOVIES
from src.nlp.pipeline import NLPPipeline


@pytest.fixture
def pipeline() -> NLPPipeline:
    return NLPPipeline([movie["title"] for movie in OFFLINE_MOVIES])


@pytest.mark.parametrize(
    ("message", "intent"),
    [
        ("Hello CineBot", "greet"),
        ("Who directed Inception?", "who_directed"),
        ("Recommend movies like Arrival", "recommend"),
        ("What is trending?", "trending"),
        ("Show upcoming releases", "upcoming_releases"),
        ("Tell me about Parasite", "movie_info"),
        ("Help", "help"),
    ],
)
def test_intent_detection(pipeline: NLPPipeline, message: str, intent: str):
    assert pipeline.run(message)["intent"] == intent


def test_known_movie_title_is_extracted(pipeline: NLPPipeline):
    result = pipeline.run("I loved The Dark Knight. Who directed it?")

    assert result["movie_title"] == "The Dark Knight"
    assert result["sentiment"]["label"] == "positive"


def test_quoted_movie_title_is_extracted(pipeline: NLPPipeline):
    result = pipeline.run('Tell me about "A Movie Not In The Catalog"')

    assert result["movie_title"] == "A Movie Not In The Catalog"


def test_negative_sentiment_is_reported(pipeline: NLPPipeline):
    result = pipeline.run("I hated that boring movie")

    assert result["sentiment"]["label"] == "negative"
