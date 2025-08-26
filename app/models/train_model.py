# """
# MNIST Model Training Script

# This script downloads MNIST dataset, trains a RandomForest model,
# and saves it to the model directory. Run this once locally or on a powerful CI environment.
# """

# import logging
# import sys
# from pathlib import Path
# from typing import Tuple

# import joblib
# import numpy as np
# from sklearn.datasets import fetch_openml
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.metrics import accuracy_score, classification_report
# from sklearn.model_selection import train_test_split

# # Setup logging
# logging.basicConfig(
#     level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
# )
# logger = logging.getLogger(__name__)

# # Path configuration
# HERE = Path(__file__).resolve().parent.parent.parent
# MODEL_DIR = HERE / "model"
# MODEL_DIR.mkdir(parents=True, exist_ok=True)
# MODEL_PATH = MODEL_DIR / "mnist_rf.joblib"


# class Bird:
#     def __init__(self):
#         print("Bird is ready")

#     def whoisThis(self):
#         print("Bird")

#     def swim(self):
#         print("Swim faster")


# # child class
# class Penguin(Bird):
#     def __init__(self):
#         # call super() function
#         super().__init__()
#         print("Penguin is ready")

#     def whoisThis(self):
#         print("Penguin")

#     def run(self):
#         print("Run faster")


# peggy = Penguin()
# peggy.whoisThis()
# peggy.swim()
# peggy.run()


# def load_mnist_data() -> Tuple[np.ndarray, np.ndarray]:
#     """Load and preprocess MNIST dataset."""
#     logger.info("Loading MNIST dataset... (this may take a few minutes)")
#     try:
#         # fetch_openml returns a tuple, we need to handle it properly
#         dataset = fetch_openml(
#             "mnist_784", version=1, as_frame=False, cache=True, parser="liac-arff"
#         )
#         X, y = dataset.data, dataset.target
#         X = X / 255.0  # Normalize pixel values
#         y = y.astype(int)
#         logger.info(f"Loaded {len(X)} samples with {X.shape[1]} features")
#         return X, y
#     except Exception as e:
#         logger.error(f"Failed to load MNIST dataset: {e}")
#         sys.exit(1)


# def train_model(X: np.ndarray, y: np.ndarray) -> RandomForestClassifier:
#     """Train RandomForest model on MNIST data."""
#     logger.info("Splitting data into train/test sets...")
#     X_train, X_test, y_train, y_test = train_test_split(
#         X, y, test_size=0.2, random_state=42, stratify=y
#     )

#     logger.info(f"Training set: {len(X_train)} samples")
#     logger.info(f"Test set: {len(X_test)} samples")

#     logger.info("Training RandomForest model...")
#     clf = RandomForestClassifier(
#         n_estimators=100,
#         max_depth=20,
#         min_samples_split=5,
#         min_samples_leaf=2,
#         random_state=42,
#         n_jobs=-1,
#         verbose=1,
#     )

#     clf.fit(X_train, y_train)

#     # Evaluate model
#     y_pred = clf.predict(X_test)
#     accuracy = accuracy_score(y_test, y_pred)

#     logger.info(f"Test accuracy: {accuracy:.4f}")
#     logger.info("Classification report:")
#     logger.info(classification_report(y_test, y_pred))

#     return clf


# def save_model(model: RandomForestClassifier) -> None:
#     """Save trained model to disk."""
#     logger.info(f"Saving model to: {MODEL_PATH}")
#     try:
#         joblib.dump(model, MODEL_PATH)
#         logger.info("Model saved successfully!")
#     except Exception as e:
#         logger.error(f"Failed to save model: {e}")
#         sys.exit(1)


# def main():
#     """Main training pipeline."""
#     logger.info("Starting MNIST model training...")

#     # Load data
#     X, y = load_mnist_data()

#     # Train model
#     model = train_model(X, y)

#     # Save model
#     save_model(model)

#     logger.info("Training completed successfully!")


# if __name__ == "__main__":
#     main()
