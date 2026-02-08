from __future__ import annotations

import spacy


class EntityRecognizer:
    def __init__(self, model_name: str = "en_core_web_md") -> None:
        try:
            self.nlp = spacy.load(model_name)
        except OSError:
            self.nlp = spacy.load("en_core_web_sm")

    def extract(self, text: str) -> dict[str, list[str]]:
        doc = self.nlp(text)
        movies = [ent.text for ent in doc.ents if ent.label_ in {"WORK_OF_ART", "ORG"}]
        people = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
        return {"movies": movies, "people": people}
