from __future__ import annotations

import re
from threading import RLock
from typing import Any

import numpy as np
from sklearn.decomposition import NMF, TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

from src.catalog import DEMO_RATINGS, OFFLINE_MOVIES

try:
    import faiss
except (ImportError, OSError):  # pragma: no cover - depends on host native-library policy
    faiss = None


class _NumpyFlatIP:
    """Exact inner-product fallback for hosts that block FAISS native libraries."""

    def __init__(self, dimensions: int) -> None:
        self.dimensions = dimensions
        self._vectors = np.empty((0, dimensions), dtype="float32")

    def add(self, vectors: np.ndarray) -> None:
        self._vectors = np.asarray(vectors, dtype="float32")

    def search(self, queries: np.ndarray, limit: int) -> tuple[np.ndarray, np.ndarray]:
        scores = np.asarray(queries, dtype="float32") @ self._vectors.T
        indices = np.argsort(-scores, axis=1)[:, :limit]
        distances = np.take_along_axis(scores, indices, axis=1)
        return distances, indices


class HybridRecommender:
    """FAISS retrieval blended with NMF and SVD collaborative signals.

    The content index is always available offline. Collaborative models begin with
    reproducible demo interactions and can be updated with ratings through the API.
    """

    def __init__(
        self,
        movies: list[dict[str, Any]] | None = None,
        ratings: dict[str, dict[int, float]] | None = None,
    ) -> None:
        self.movies = [dict(movie) for movie in (movies or OFFLINE_MOVIES)]
        self._movie_index = {movie["id"]: index for index, movie in enumerate(self.movies)}
        self._ratings = {
            user_id: dict(user_ratings)
            for user_id, user_ratings in (ratings or DEMO_RATINGS).items()
        }
        self._lock = RLock()
        self._build_content_index()
        self._fit_collaborative_models()

    @staticmethod
    def _document(movie: dict[str, Any]) -> str:
        genres = " ".join(movie.get("genres") or [])
        return " ".join(
            [
                movie["title"],
                movie.get("director") or "",
                genres,
                genres,
                movie.get("overview") or "",
            ]
        )

    def _build_content_index(self) -> None:
        documents = [self._document(movie) for movie in self.movies]
        self._vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            strip_accents="unicode",
        )
        tfidf = self._vectorizer.fit_transform(documents)
        dimensions = max(2, min(16, tfidf.shape[0] - 1, tfidf.shape[1] - 1))
        self._semantic_model = TruncatedSVD(n_components=dimensions, random_state=42)
        embeddings = self._semantic_model.fit_transform(tfidf)
        self._content_embeddings = normalize(embeddings).astype("float32")
        if faiss is not None:
            self._faiss_index = faiss.IndexFlatIP(dimensions)
            self._retrieval_backend = "FAISS IndexFlatIP"
        else:
            self._faiss_index = _NumpyFlatIP(dimensions)
            self._retrieval_backend = "NumPy exact fallback (FAISS unavailable)"
        self._faiss_index.add(self._content_embeddings)

    def _fit_collaborative_models(self) -> None:
        self._user_ids = sorted(self._ratings)
        self._user_index = {user_id: index for index, user_id in enumerate(self._user_ids)}
        matrix = np.full((len(self._user_ids), len(self.movies)), np.nan, dtype=np.float64)
        for user_id, user_ratings in self._ratings.items():
            for movie_id, rating in user_ratings.items():
                if movie_id in self._movie_index:
                    matrix[self._user_index[user_id], self._movie_index[movie_id]] = rating

        global_mean = float(np.nanmean(matrix))
        item_means = np.nanmean(matrix, axis=0)
        item_means = np.where(np.isnan(item_means), global_mean, item_means)
        completed = np.where(np.isnan(matrix), item_means[np.newaxis, :], matrix)

        factors = max(2, min(6, completed.shape[0] - 1, completed.shape[1] - 1))
        self._nmf = NMF(
            n_components=factors,
            init="nndsvda",
            max_iter=1_000,
            random_state=42,
            tol=1e-4,
        )
        nmf_users = self._nmf.fit_transform(completed)
        self._nmf_predictions = nmf_users @ self._nmf.components_
        self._nmf_items = normalize(self._nmf.components_.T)

        user_means = completed.mean(axis=1, keepdims=True)
        centered = completed - user_means
        self._svd = TruncatedSVD(n_components=factors, random_state=42)
        svd_users = self._svd.fit_transform(centered)
        self._svd_predictions = svd_users @ self._svd.components_ + user_means
        self._svd_items = normalize(self._svd.components_.T)

    @staticmethod
    def _scale(values: np.ndarray) -> np.ndarray:
        minimum = float(values.min())
        span = float(values.max() - minimum)
        if span <= 1e-9:
            return np.zeros_like(values, dtype=np.float64)
        return (values - minimum) / span

    def _semantic_scores(self, query: str) -> np.ndarray:
        query_tfidf = self._vectorizer.transform([query])
        if query_tfidf.nnz == 0:
            return np.zeros(len(self.movies), dtype=np.float64)
        query_embedding = normalize(self._semantic_model.transform(query_tfidf)).astype("float32")
        distances, indices = self._faiss_index.search(query_embedding, len(self.movies))
        scores = np.zeros(len(self.movies), dtype=np.float64)
        for index, distance in zip(indices[0], distances[0], strict=True):
            if index >= 0:
                scores[index] = max(0.0, float(distance))
        return scores

    def _collaborative_similarity(self, seed_index: int) -> tuple[np.ndarray, np.ndarray]:
        nmf_scores = self._nmf_items @ self._nmf_items[seed_index]
        svd_scores = self._svd_items @ self._svd_items[seed_index]
        return self._scale(nmf_scores), self._scale(svd_scores)

    def _personal_scores(self, user_id: str) -> tuple[np.ndarray, np.ndarray]:
        user_index = self._user_index[user_id]
        return (
            self._scale(self._nmf_predictions[user_index]),
            self._scale(self._svd_predictions[user_index]),
        )

    def _user_content_scores(self, user_id: str) -> np.ndarray:
        profile = np.zeros(self._content_embeddings.shape[1], dtype=np.float64)
        for movie_id, rating in self._ratings[user_id].items():
            movie_index = self._movie_index.get(movie_id)
            if movie_index is not None:
                profile += self._content_embeddings[movie_index] * (rating - 3.0)
        norm = np.linalg.norm(profile)
        if norm <= 1e-9:
            return np.zeros(len(self.movies), dtype=np.float64)
        similarities = self._content_embeddings @ (profile / norm)
        return self._scale(similarities)

    def search(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        scores = self._semantic_scores(query.strip())
        ranked = np.argsort(-scores)[:limit]
        return [
            {**self.movies[index], "semantic_score": round(float(scores[index]), 4)}
            for index in ranked
            if scores[index] > 0
        ]

    def recommend(
        self,
        *,
        seed_movie_id: int | None = None,
        query: str | None = None,
        user_id: str | None = None,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        if seed_movie_id is None and not query and not user_id:
            raise ValueError("A seed movie, natural-language query, or user ID is required.")
        if seed_movie_id is not None and seed_movie_id not in self._movie_index:
            return []

        with self._lock:
            seed_index = self._movie_index.get(seed_movie_id) if seed_movie_id else None
            semantic_query = query
            if seed_index is not None:
                semantic_query = f"{semantic_query or ''} {self._document(self.movies[seed_index])}"
            semantic = (
                self._semantic_scores(semantic_query.strip())
                if semantic_query and semantic_query.strip()
                else np.zeros(len(self.movies))
            )

            nmf = np.zeros(len(self.movies))
            svd = np.zeros(len(self.movies))
            if seed_index is not None:
                nmf, svd = self._collaborative_similarity(seed_index)
            if user_id and user_id in self._user_index:
                personal_nmf, personal_svd = self._personal_scores(user_id)
                nmf = (nmf + personal_nmf) / (2 if seed_index is not None else 1)
                svd = (svd + personal_svd) / (2 if seed_index is not None else 1)
                profile_semantic = self._user_content_scores(user_id)
                semantic = (semantic + profile_semantic) / 2 if semantic.any() else profile_semantic

            quality = self._scale(
                np.asarray([movie.get("vote_average", 0.0) for movie in self.movies])
            )
            has_collaborative_signal = seed_index is not None or (
                user_id is not None and user_id in self._user_index
            )
            if has_collaborative_signal and semantic.any():
                weights = {"semantic": 0.45, "nmf": 0.2, "svd": 0.2, "quality": 0.15}
            elif has_collaborative_signal:
                weights = {"semantic": 0.0, "nmf": 0.4, "svd": 0.4, "quality": 0.2}
            else:
                weights = {"semantic": 0.8, "nmf": 0.0, "svd": 0.0, "quality": 0.2}

            final = (
                semantic * weights["semantic"]
                + nmf * weights["nmf"]
                + svd * weights["svd"]
                + quality * weights["quality"]
            )
            excluded = set()
            if seed_index is not None:
                excluded.add(seed_index)
            if user_id and user_id in self._ratings:
                excluded.update(
                    self._movie_index[movie_id]
                    for movie_id in self._ratings[user_id]
                    if movie_id in self._movie_index
                )

            ranked = [index for index in np.argsort(-final) if index not in excluded][:limit]
            results = []
            for index in ranked:
                strongest_signal = max(
                    ("semantic match", semantic[index]),
                    ("NMF neighbors", nmf[index]),
                    ("SVD neighbors", svd[index]),
                    key=lambda item: item[1],
                )[0]
                results.append(
                    {
                        **self.movies[index],
                        "match_score": round(float(final[index]), 4),
                        "signals": {
                            "semantic": round(float(semantic[index]), 4),
                            "nmf": round(float(nmf[index]), 4),
                            "svd": round(float(svd[index]), 4),
                            "quality": round(float(quality[index]), 4),
                        },
                        "reason": f"Ranked primarily by {strongest_signal}.",
                    }
                )
            return results

    def recommend_by_title(
        self,
        title: str,
        *,
        user_id: str | None = None,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        movie_id = self.movie_id_for_title(title)
        if movie_id is None:
            return []
        return self.recommend(seed_movie_id=movie_id, user_id=user_id, limit=limit)

    def movie_id_for_title(self, title: str) -> int | None:
        normalized = re.sub(r"\W+", " ", title).strip().casefold()
        movie = next(
            (
                item
                for item in self.movies
                if re.sub(r"\W+", " ", item["title"]).strip().casefold() == normalized
            ),
            None,
        )
        return int(movie["id"]) if movie else None

    def record_rating(self, user_id: str, movie_id: int, rating: float) -> None:
        if movie_id not in self._movie_index:
            raise KeyError(movie_id)
        if not 1 <= rating <= 5:
            raise ValueError("Ratings must be between 1 and 5.")
        with self._lock:
            self._ratings.setdefault(user_id, {})[movie_id] = float(rating)
            self._fit_collaborative_models()

    @property
    def model_info(self) -> dict[str, Any]:
        return {
            "catalog_size": len(self.movies),
            "interaction_count": sum(len(ratings) for ratings in self._ratings.values()),
            "retrieval_index": self._retrieval_backend,
            "semantic_features": "TF-IDF + latent semantic analysis",
            "collaborative_models": ["NMF", "TruncatedSVD"],
        }
