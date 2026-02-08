from src.data.dataset import Dataset
from src.evaluation.metrics import accuracy, f1_score
from src.features.vectorization import Vectorizer
from src.models.model import NLPModel
from src.preprocessing.text_cleaning import lowercase_text, remove_punctuation, remove_stopwords
from src.training.train import train_model


def main():
    # Load and preprocess the dataset
    dataset = Dataset()
    data = dataset.load_data()
    cleaned_data = [remove_stopwords(lowercase_text(remove_punctuation(text))) for text in data]

    # Vectorize the cleaned data
    vectorizer = Vectorizer()
    X = vectorizer.fit_transform(cleaned_data)

    # Initialize and train the NLP model
    model = NLPModel()
    train_model(model, X)

    # Evaluate the model
    predictions = model.predict(X)
    acc = accuracy(predictions, dataset.get_samples())
    f1 = f1_score(predictions, dataset.get_samples())

    print(f"Accuracy: {acc}")
    print(f"F1 Score: {f1}")


if __name__ == "__main__":
    main()
