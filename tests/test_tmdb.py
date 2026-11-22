import requests

from src.services.tmdb import LOGGER, TMDbClient


def test_explicit_blank_key_forces_offline_mode(monkeypatch):
    monkeypatch.setenv("TMDB_API_KEY", "configured-but-not-used")

    client = TMDbClient(api_key="")

    assert client.is_live is False


def test_offline_search_supports_fuzzy_titles(monkeypatch):
    monkeypatch.delenv("TMDB_API_KEY", raising=False)
    client = TMDbClient(api_key="")

    movie = client.search_movie("interstelar")

    assert movie is not None
    assert movie["title"] == "Interstellar"


def test_offline_details_include_director():
    client = TMDbClient(api_key="")
    movie = client.search_movie("Parasite")

    details = client.movie_details(movie["id"])

    assert details is not None
    assert details["director"] == "Bong Joon Ho"


def test_offline_similar_movies_have_expected_shape():
    client = TMDbClient(api_key="")

    movies = client.similar_movies(1, limit=3)

    assert len(movies) == 3
    assert all({"id", "title", "overview"}.issubset(movie) for movie in movies)
    assert all(movie["id"] != 1 for movie in movies)


def test_failed_upstream_requests_do_not_log_api_credentials(caplog, monkeypatch):
    secret = "private-tmdb-test-key"
    # Streamlit configures logging during its UI tests. Capture this logger
    # directly so test ordering cannot remove the root capture handler.
    monkeypatch.setattr(LOGGER, "disabled", False)
    monkeypatch.setattr(LOGGER, "handlers", [caplog.handler])

    class FailingSession:
        def get(self, url, **kwargs):
            response = requests.Response()
            response.status_code = 401
            response.url = f"{url}?api_key={kwargs['params']['api_key']}"
            response.raise_for_status()

    client = TMDbClient(api_key=secret, session=FailingSession())

    movie = client.search_movie("Inception")

    assert movie["title"] == "Inception"
    assert secret not in caplog.text
    assert "HTTPError" in caplog.text
    assert "search/movie" in caplog.text


def test_failed_live_details_and_similar_calls_do_not_resolve_local_fixture_ids(monkeypatch):
    client = TMDbClient(api_key="configured-key")
    monkeypatch.setattr(client, "_get", lambda *args, **kwargs: None)

    assert client.movie_details(1) is None
    assert client.similar_movies(1) == []
    assert client.movie_details(1, offline=True)["title"] == "Inception"
    assert len(client.similar_movies(1, limit=3, offline=True)) == 3
