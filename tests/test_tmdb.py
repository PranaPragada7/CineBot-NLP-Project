from src.services.tmdb import TMDbClient


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
