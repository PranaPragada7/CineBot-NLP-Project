from __future__ import annotations

from typing import Any

from sentence_transformers import SentenceTransformer, util

from .entity_linker import EntityLinker


class NLPPipeline:
    """
    A more advanced NLP pipeline using semantic similarity for intent detection
    and spaCy for entity recognition.
    """

    def __init__(self, movie_data: list):
        print("Loading NLP Pipeline models...")
        # Use a powerful model for understanding sentence meaning
        self.intent_model = SentenceTransformer("all-MiniLM-L6-v2")
        # Initialize our custom entity linker
        self.entity_linker = EntityLinker(movie_data)

        # Define intents with descriptive sentences that capture their meaning
        self.intent_map = {
            "upcoming_releases": "The user wants to know about new movies that are coming out soon.",
            "who_directed": "The user is asking for the name of the director of a specific film.",
            "recommend": "The user wants a movie recommendation similar to another movie they mentioned.",
        }
        # Pre-calculate the numerical representations (embeddings) for our intent descriptions
        self.intent_embeddings = self.intent_model.encode(list(self.intent_map.values()))
        print("NLP Pipeline loaded successfully.")

    def _get_intent(self, text: str) -> dict:
        """
        Calculates intent by finding the most semantically similar description.
        """
        text_embedding = self.intent_model.encode(text)
        similarities = util.cos_sim(text_embedding, self.intent_embeddings)[0]

        top_intent_index = similarities.argmax().item()
        top_intent_score = similarities[top_intent_index].item()
        top_intent_name = list(self.intent_map.keys())[top_intent_index]

        return {"intent": top_intent_name, "intent_confidence": top_intent_score}

    def _get_entities(self, text: str) -> dict:
        """
        Extracts entities using our custom EntityLinker.
        """
        return self.entity_linker.extract_entities(text)

    def run(self, text: str, ctx: dict = None) -> dict[str, Any]:
        """
        The main method to process a user's text input.
        """
        intent_result = self._get_intent(text)
        entities = self._get_entities(text)

        return {
            "intent": intent_result["intent"],
            "intent_confidence": intent_result["intent_confidence"],
            "entities": entities,
        }
