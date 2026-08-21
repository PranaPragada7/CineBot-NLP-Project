# Contributing

1. Create a branch from `main`.
2. Keep TMDB credentials in environment variables.
3. Preserve deterministic tests by using the local catalog instead of live requests.
4. Add tests for new intents, endpoints, or recommendation behavior.
5. Run the quality checks in the README before opening a pull request.
6. Run `python -m scripts.evaluate_recommender` when ranking logic or fixtures change.

Do not present the seeded demo ratings or their evaluation metrics as real-user
performance. Changes to ranking weights should include a brief tradeoff note and
must keep component scores visible in the API response.

Interface changes should remain responsive and retain CineBot's cinema-focused
visual design.
