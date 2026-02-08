from __future__ import annotations

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer


class SentimentAnalyzer:
    def __init__(self, model_name: str = "cardiffnlp/twitter-roberta-base-sentiment") -> None:
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.labels = ["negative", "neutral", "positive"]

    def score(self, text: str) -> dict:
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True)
        with torch.no_grad():
            logits = self.model(**inputs).logits
        probs = torch.softmax(logits, dim=-1).flatten().tolist()
        return {label: float(prob) for label, prob in zip(self.labels, probs)}
