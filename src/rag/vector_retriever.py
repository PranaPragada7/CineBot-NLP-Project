from __future__ import annotations

from pathlib import Path

import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer


class VectorRetriever:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.index: faiss.Index | None = None
        self.documents: pd.DataFrame | None = None

    def build_index(self, docs: pd.DataFrame, text_column: str = "overview"):
        self.documents = docs.copy()
        embeddings = self.model.encode(docs[text_column].tolist(), convert_to_tensor=False)

        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)

        d = embeddings.shape[1]  # vector dimension
        self.index = faiss.IndexFlatIP(d)  # Use Inner Product for cosine similarity
        self.index = faiss.IndexIDMap(self.index)

        ids = np.array(docs.index.values).astype("int64")
        self.index.add_with_ids(embeddings.astype("float32"), ids)

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        if self.index is None or self.documents is None:
            return []

        query_vector = self.model.encode([query], convert_to_tensor=False)
        faiss.normalize_L2(query_vector)  # Normalize query vector
        scores, ids = self.index.search(query_vector.astype("float32"), top_k)

        results = []
        for i, doc_id in enumerate(ids[0]):
            if doc_id != -1:
                score = scores[0][i]  # For IndexFlatIP, the score is the cosine similarity
                doc = self.documents.loc[doc_id].to_dict()
                results.append({"score": float(score), **doc})
        return results

    def save(self, index_path: str | Path):
        p = Path(index_path)
        p.mkdir(exist_ok=True, parents=True)
        if self.index is not None:
            faiss.write_index(self.index, str(p / "faiss.index"))
        if self.documents is not None:
            self.documents.to_parquet(p / "documents.parquet")

    @classmethod
    def load(cls, index_path: str | Path) -> VectorRetriever:
        p = Path(index_path)
        retriever = cls()
        if (p / "faiss.index").exists():
            retriever.index = faiss.read_index(str(p / "faiss.index"))
        if (p / "documents.parquet").exists():
            retriever.documents = pd.read_parquet(p / "documents.parquet")
        return retriever
