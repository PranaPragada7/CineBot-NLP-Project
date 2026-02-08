# NLP Project

This project is a Natural Language Processing (NLP) application designed to handle various tasks such as data preprocessing, feature extraction, model training, and evaluation. 

## Project Structure

```
nlp-project
├── src
│   ├── __init__.py
│   ├── main.py
│   ├── data
│   │   ├── __init__.py
│   │   └── dataset.py
│   ├── preprocessing
│   │   ├── __init__.py
│   │   └── text_cleaning.py
│   ├── features
│   │   ├── __init__.py
│   │   └── vectorization.py
│   ├── models
│   │   ├── __init__.py
│   │   └── model.py
│   ├── training
│   │   ├── __init__.py
│   │   └── train.py
│   └── evaluation
│       ├── __init__.py
│       └── metrics.py
├── configs
│   └── default.yaml
├── notebooks
│   └── exploration.ipynb
├── tests
│   ├── __init__.py
│   └── test_pipeline.py
├── .gitignore
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Installation

To set up the project, clone the repository and install the required dependencies:

```bash
git clone <repository-url>
cd nlp-project
pip install -r requirements.txt
```

## Usage

To run the application, execute the main script:

```bash
python src/main.py
```

## Components

- **Data Handling**: The `Dataset` class in `src/data/dataset.py` manages loading and preprocessing of the dataset.
- **Preprocessing**: Text cleaning functions are available in `src/preprocessing/text_cleaning.py`.
- **Feature Extraction**: The `Vectorizer` class in `src/features/vectorization.py` handles text vectorization.
- **Modeling**: The `NLPModel` class in `src/models/model.py` defines the architecture of the NLP model.
- **Training**: The training process is orchestrated in `src/training/train.py`.
- **Evaluation**: Model performance can be evaluated using functions in `src/evaluation/metrics.py`.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.