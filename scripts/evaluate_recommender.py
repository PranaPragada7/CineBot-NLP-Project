from __future__ import annotations

import json

from src.catalog import DEMO_RATINGS
from src.recommendation import HybridRecommender


def leave_one_out_metrics(limit: int = 5) -> dict[str, float | int]:
    """Evaluate personalization by hiding one positive interaction per demo user."""

    training: dict[str, dict[int, float]] = {}
    held_out: dict[str, int] = {}
    for user_id, ratings in DEMO_RATINGS.items():
        positives = sorted(
            ((movie_id, rating) for movie_id, rating in ratings.items() if rating >= 4),
            key=lambda item: (item[1], item[0]),
            reverse=True,
        )
        held_out_movie = positives[0][0]
        held_out[user_id] = held_out_movie
        training[user_id] = {
            movie_id: rating for movie_id, rating in ratings.items() if movie_id != held_out_movie
        }

    recommender = HybridRecommender(ratings=training)
    hits = 0
    reciprocal_rank = 0.0
    for user_id, expected_movie_id in held_out.items():
        ranked_ids = [movie["id"] for movie in recommender.recommend(user_id=user_id, limit=limit)]
        if expected_movie_id in ranked_ids:
            hits += 1
            reciprocal_rank += 1 / (ranked_ids.index(expected_movie_id) + 1)

    users = len(held_out)
    return {
        "users": users,
        "catalog_size": len(recommender.movies),
        "k": limit,
        "hit_rate_at_k": round(hits / users, 4),
        "mean_reciprocal_rank": round(reciprocal_rank / users, 4),
    }


if __name__ == "__main__":
    print(json.dumps(leave_one_out_metrics(), indent=2))
