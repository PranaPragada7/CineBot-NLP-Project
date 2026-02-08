def train_model():
    from src.data.dataset import Dataset
    from src.models.model import NLPModel

    # Load the dataset
    dataset = Dataset()
    data = dataset.load_data()

    # Initialize the model
    model = NLPModel()

    # Train the model
    model.train(data)

    return model
