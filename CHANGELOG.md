# Changelog

Notable changes to CineBot are documented here.

## 3.1.0 - 2026-08-21

- Added PostgreSQL-compatible persistence for conversations, feedback, ratings, and events.
- Added Alembic schema migrations and restart-persistence integration tests.
- Added Redis-backed fixed-window rate limiting with a health-reported local fallback.
- Added request IDs, structured JSON access logs, Prometheus metrics, and readiness probes.
- Expanded Docker Compose with PostgreSQL and Redis health checks and persistent volumes.
- Added a Render Blueprint and a PostgreSQL/Redis infrastructure CI job.

## 3.0.0 - 2026-08-21

- Replaced genre-overlap recommendations with an explainable hybrid ranker.
- Added FAISS semantic retrieval over latent TF-IDF movie embeddings.
- Added independent NMF and truncated-SVD collaborative models.
- Added natural-language discovery, personalized rating updates, and component scores.
- Added `/recommendations` and `/ratings` API endpoints plus a recommendation lab UI.
- Expanded deterministic fixtures to 24 movies and 144 seeded interactions.
- Added leave-one-out ranking evaluation and model-specific behavioral tests.

## 1.0.0 - 2026-08-19

- Consolidated the project into a FastAPI backend and Streamlit interface.
- Added movie intent detection, title extraction, follow-up context, and feedback.
- Added live TMDB integration with a deterministic local demonstration catalog.
- Added Docker support, API documentation, and a responsive movie-focused UI.
- Added behavioral tests, coverage enforcement, and multi-version CI.
