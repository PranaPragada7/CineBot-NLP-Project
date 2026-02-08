import sys
from pathlib import Path

import pandas as pd

# Add the project root's 'src' directory to the Python path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.rag.vector_retriever import VectorRetriever


def main():
    """
    Loads movie data, builds a vector index from the overviews,
    and saves it to the 'data/index' directory.
    """
    print("Loading movie data from data/movies.csv...")
    data_path = Path("data/movies.csv")
    if not data_path.exists():
        print(f"Error: Data file not found at {data_path}")
        return

    docs = pd.read_csv(data_path)
    docs.set_index("id", inplace=True)

    print("Building vector index from movie overviews...")
    retriever = VectorRetriever()
    retriever.build_index(docs, text_column="overview")

    index_path = Path("data/index")
    print(f"Saving index to {index_path}...")
    retriever.save(index_path)

    print("Index build complete.")


if __name__ == "__main__":
    main()
