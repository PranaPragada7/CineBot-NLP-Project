class Vectorizer:
    def __init__(self):
        self.vocabulary = {}

    def fit(self, documents):
        for doc in documents:
            for word in doc.split():
                if word not in self.vocabulary:
                    self.vocabulary[word] = len(self.vocabulary)

    def transform(self, documents):
        vectorized_docs = []
        for doc in documents:
            vector = [0] * len(self.vocabulary)
            for word in doc.split():
                if word in self.vocabulary:
                    vector[self.vocabulary[word]] += 1
            vectorized_docs.append(vector)
        return vectorized_docs
