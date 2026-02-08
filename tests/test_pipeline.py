import csv
import os
import tempfile
import unittest

import pandas as pd

from src.data.dataset import Dataset
from src.nlp.pipeline import NLPPipeline


class TestNLPComponents(unittest.TestCase):
    def setUp(self):
        # Create a temporary CSV file for testing
        self.temp_file = tempfile.NamedTemporaryFile(mode="w", delete=False, newline="", encoding="utf-8")
        with self.temp_file as f:
            writer = csv.writer(f)
            writer.writerow(["text", "intent"])
            writer.writerow(["hello world", "greet"])
            writer.writerow(["tell me about inception", "movie_info"])

        self.dataset = Dataset(self.temp_file.name)
        self.pipeline = NLPPipeline()

    def tearDown(self):
        # Clean up the temporary file
        os.remove(self.temp_file.name)

    def test_load_data(self):
        self.assertIsNotNone(self.dataset.data)
        self.assertIsInstance(self.dataset.data, pd.DataFrame)
        self.assertIn("text", self.dataset.data.columns)

    def test_text_cleaning(self):
        cleaned_text = self.dataset.clean_text("  Hello!! World... 123  ")
        self.assertEqual(cleaned_text, "hello world")

    def test_vectorization(self):
        if self.dataset.data is not None:
            vectors = self.dataset.vectorize(self.dataset.data["text"])
            self.assertIsNotNone(vectors)
            self.assertEqual(vectors.shape[0], len(self.dataset.data))
        else:
            self.fail("Dataset was not loaded correctly for vectorization test.")

    def test_model_training(self):
        # This is a placeholder, as actual training is complex to test
        self.assertTrue(True)

    def test_accuracy(self):
        # Placeholder for accuracy test
        self.assertTrue(True)

    def test_f1_score(self):
        # Placeholder for f1 score test
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
