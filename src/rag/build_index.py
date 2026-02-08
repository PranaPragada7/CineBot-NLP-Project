from __future__ import annotations

from pathlib import Path


def main():
    Path("data/index").mkdir(parents=True, exist_ok=True)
    # TODO: implement embeddings build here
    print("Index directory created/refreshed at data/index")


if __name__ == "__main__":
    main()
