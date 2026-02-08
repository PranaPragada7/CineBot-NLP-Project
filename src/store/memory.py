from __future__ import annotations

import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from .services.tmdb import TMDbClient


class MemoryStore:
    def __init__(self, tmdb_client: TMDbClient):
        self.tmdb_client = tmdb_client
        # Define paths for the index and the ID map
        self.index_path = Path(__file__).parent.parent.parent / "data" / "faiss.index"
        self.id_map_path = Path(__file__).parent.parent.parent / "data" / "id_map.json"
        self.movies = []
        self.index = None
        self.id_map = {}
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def get_all_movies(self) -> list:
        return self.movies

    def build(self):
        # Ensure the data directory exists
        self.index_path.parent.mkdir(exist_ok=True)

        if self.index_path.exists() and self.id_map_path.exists():
            print("Loading existing FAISS index and ID map from disk...")
            # Load the core index
            core_index = faiss.read_index(str(self.index_path))
            # Load the ID map
            with open(self.id_map_path) as f:
                # JSON saves integer keys as strings, so we convert them back
                self.id_map = {int(k): v for k, v in json.load(f).items()}

            # Re-wrap the core index with an IndexIDMap
            self.index = faiss.IndexIDMap(core_index)
            # The index is already populated, so we just need to add the IDs from the map
            self.index.add_with_ids(
                core_index.reconstruct_n(0, core_index.ntotal), np.array(list(self.id_map.values()))
            )

            print(f"FAISS index with {self.index.ntotal} vectors loaded.")
            return

        print("Building FAISS index from scratch...")
        self.movies = self.tmdb_client.get_all_movies_for_vector_store()
        if not self.movies:
            print("No movies fetched, aborting index build.")
            return

        overviews = [movie["overview"] for movie in self.movies if movie["overview"]]
        vectors = self.model.encode(overviews, convert_to_tensor=True).cpu().numpy()

        d = vectors.shape[1]
        core_index = faiss.IndexFlatL2(d)
        self.index = faiss.IndexIDMap(core_index)

        movie_ids = np.array([movie["id"] for movie in self.movies if movie["overview"]])
        self.index.add_with_ids(vectors, movie_ids)

        # Create the simple integer-to-ID map for saving
        self.id_map = {i: int(movie_id) for i, movie_id in enumerate(movie_ids)}

        # --- Save the unwrapped index and the ID map separately ---
        print(f"Saving FAISS core index to {self.index_path}")
        faiss.write_index(self.index.index, str(self.index_path))  # Save the inner index

        print(f"Saving ID map to {self.id_map_path}")
        with open(self.id_map_path, "w") as f:
            json.dump(self.id_map, f)

    def search_similar_movies(self, query: str, top_k: int = 5) -> list[int]:
        if not self.index or self.index.ntotal == 0:
            print("Index is not built or is empty.")
            return []

        query_vector = self.model.encode([query], convert_to_tensor=True).cpu().numpy()
        D, I = self.index.search(query_vector, top_k)
        return I[0].tolist()
