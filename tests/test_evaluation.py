from scripts.evaluate_recommender import leave_one_out_metrics


def test_seeded_leave_one_out_ranking_regression():
    metrics = leave_one_out_metrics(limit=5)

    assert metrics == {
        "users": 12,
        "catalog_size": 24,
        "k": 5,
        "hit_rate_at_k": 0.5833,
        "mean_reciprocal_rank": 0.3083,
    }
