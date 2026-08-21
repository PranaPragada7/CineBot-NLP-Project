# Changelog

Notable changes to CineBot are documented here.

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
