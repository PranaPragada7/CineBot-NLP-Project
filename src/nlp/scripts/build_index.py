import sys
from pathlib import Path

import pandas as pd

# Add src to path to allow imports
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.rag.vector_retriever import VectorRetriever


def main():
    print("Loading data...")
    data_path = Path("data/movies.csv")
    docs = pd.read_csv(data_path)
    docs.set_index("id", inplace=True)

    print("Building vector index...")
    retriever = VectorRetriever()
    retriever.build_index(docs, text_column="overview")

    print("Saving index...")
    index_path = Path("data/index")
    retriever.save(index_path)

    print(f"Index built and saved to {index_path}")


if __name__ == "__main__":
    main()
