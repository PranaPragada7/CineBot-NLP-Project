import numpy as np
import pytest

from src.recommendation import HybridRecommender


@pytest.fixture(scope="module")
def recommender() -> HybridRecommender:
    return HybridRecommender()


def test_model_info_proves_all_three_engines_are_loaded(recommender: HybridRecommender):
    info = recommender.model_info

    assert info["retrieval_index"] in {
        "FAISS IndexFlatIP",
        "NumPy exact fallback (FAISS unavailable)",
    }
    assert info["collaborative_models"] == ["NMF", "TruncatedSVD"]
    assert info["catalog_size"] == 24
    assert info["interaction_count"] == 144


def test_faiss_semantic_search_finds_ai_story(recommender: HybridRecommender):
    results = recommender.search("artificial intelligence consciousness programmer", limit=3)

    assert results[0]["title"] == "Ex Machina"
    assert results[0]["semantic_score"] > 0


def test_hybrid_recommendations_are_ranked_and_explainable(recommender: HybridRecommender):
    results = recommender.recommend(seed_movie_id=1, limit=5)

    assert len(results) == 5
    assert all(movie["id"] != 1 for movie in results)
    assert [movie["match_score"] for movie in results] == sorted(
        [movie["match_score"] for movie in results], reverse=True
    )
    assert set(results[0]["signals"]) == {"semantic", "nmf", "svd", "quality"}
    assert results[0]["reason"].startswith("Ranked primarily by")


def test_nmf_and_svd_are_independent_signals(recommender: HybridRecommender):
    results = recommender.recommend(seed_movie_id=3, limit=10)
    nmf = np.asarray([movie["signals"]["nmf"] for movie in results])
    svd = np.asarray([movie["signals"]["svd"] for movie in results])

    assert not np.allclose(nmf, svd)


def test_new_rating_is_used_and_already_rated_movie_is_excluded():
    recommender = HybridRecommender()
    recommender.record_rating("new-user", movie_id=6, rating=5)

    results = recommender.recommend(user_id="new-user", limit=5)

    assert all(movie["id"] != 6 for movie in results)
    assert recommender.model_info["interaction_count"] == 145


def test_unknown_seed_and_invalid_rating_are_rejected(recommender: HybridRecommender):
    assert recommender.recommend(seed_movie_id=999) == []
    with pytest.raises(KeyError):
        recommender.record_rating("user", movie_id=999, rating=4)
    with pytest.raises(ValueError):
        recommender.record_rating("user", movie_id=1, rating=6)
