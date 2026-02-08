from __future__ import annotations

from typing import Any, Dict, List

import spacy


class EntityLinker:
    """
    A custom entity recognition and linking component.
    It uses spaCy's EntityRuler to efficiently find known movie titles,
    people, and genres, and links them to their TMDb IDs.
    """

    def __init__(self, movie_data: List[Dict[str, Any]]):
        print("Initializing EntityLinker...")
        self.nlp = spacy.blank("en")
        self.movie_data = {movie["id"]: movie for movie in movie_data}

        # Create patterns for the EntityRuler
        patterns = self._create_entity_patterns(movie_data)

        # The EntityRuler is extremely fast for dictionary-based matching
        ruler = self.nlp.add_pipe("entity_ruler", config={"overwrite_ents": True})
        ruler.add_patterns(patterns)
        print(f"EntityLinker initialized with {len(patterns)} patterns.")

    def _create_entity_patterns(self, movie_data: List[Dict[str, Any]]) -> List[Dict]:
        """Creates the pattern dictionary for the spaCy EntityRuler."""
        patterns = []

        # Movie Title Patterns
        for movie in movie_data:
            patterns.append(
                {
                    "label": "MOVIE",
                    "pattern": movie["title"],
                    "id": str(movie["id"]),  # EntityRuler IDs must be strings
                }
            )

        # We can expand this with people and genres in the future
        # For now, focusing on the most critical entity: movie titles.

        return patterns

    def extract_entities(self, text: str) -> Dict[str, Any]:
        """
        Processes text to find and link entities.
        Returns a dictionary of linked entities.
        """
        doc = self.nlp(text)
        entities = {"movies": [], "people": [], "genres": []}

        for ent in doc.ents:
            if ent.label_ == "MOVIE":
                movie_id = int(ent.ent_id_)
                entities["movies"].append(
                    {
                        "text": ent.text,
                        "id": movie_id,
                        "title": self.movie_data.get(movie_id, {}).get("title", ent.text),
                    }
                )

        return entities
