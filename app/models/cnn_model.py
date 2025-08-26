"""
PyTorch CNN Model for MNIST Digit Recognition

This module defines a lightweight CNN architecture optimized for CPU inference
and provides training functionality for the MNIST dataset.
"""

import logging
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

logger = logging.getLogger(__name__)

# Model configuration
MODEL_INPUT_SIZE = (28, 28)
MODEL_PATH = Path("model/mnist_cnn.pth")
DEVICE = torch.device("cpu")


class MNISTCNN(nn.Module):
    """
    Lightweight CNN for MNIST digit recognition.

    Architecture optimized for CPU inference with minimal memory usage:
    - 2 Conv layers with max pooling
    - 2 Fully connected layers
    - Dropout for regularization
    """

    def __init__(self, num_classes: int = 10):
        super(MNISTCNN, self).__init__()

        # Convolutional layers
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)

        # Pooling layer
        self.pool = nn.MaxPool2d(2, 2)

        # Dropout for regularization
        self.dropout = nn.Dropout(0.25)

        # Fully connected layers
        self.fc1 = nn.Linear(64 * 7 * 7, 128)
        self.fc2 = nn.Linear(128, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass through the network."""
        # First conv block
        x = self.pool(F.relu(self.conv1(x)))

        # Second conv block
        x = self.pool(F.relu(self.conv2(x)))

        # Flatten for fully connected layers
        x = x.view(-1, 64 * 7 * 7)

        # Fully connected layers with dropout
        x = self.dropout(F.relu(self.fc1(x)))
        x = self.fc2(x)

        return x


class CNNPredictor:
    """Handles CNN model loading, training, and prediction."""

    def __init__(self):
        """Initialize the CNN predictor."""
        self.model: Optional[MNISTCNN] = None
        self.device = DEVICE
        self._load_model()

    def _load_model(self) -> None:
        """Load the trained CNN model."""
        try:
            if MODEL_PATH.exists():
                self.model = MNISTCNN()
                self.model.load_state_dict(
                    torch.load(MODEL_PATH, map_location=self.device)
                )
                self.model.eval()
                logger.info(f"CNN model loaded successfully from {MODEL_PATH}")
            else:
                logger.warning(
                    f"Model not found at {MODEL_PATH}. Please train the model first."
                )
                self.model = None
        except Exception as e:
            logger.error(f"Failed to load CNN model: {e}")
            self.model = None

    def train_model(
        self, epochs: int = 10, batch_size: int = 64, lr: float = 0.001
    ) -> None:
        """
        Train the CNN model on MNIST dataset.

        Args:
            epochs: Number of training epochs
            batch_size: Batch size for training
            lr: Learning rate
        """
        logger.info("Starting CNN model training...")

        # Data transformations
        transform = transforms.Compose(
            [
                transforms.ToTensor(),
                transforms.Normalize((0.1307,), (0.3081,)),  # MNIST mean and std
            ]
        )

        # Load MNIST dataset
        train_dataset = datasets.MNIST(
            "data", train=True, download=True, transform=transform
        )
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

        # Initialize model
        self.model = MNISTCNN().to(self.device)
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(self.model.parameters(), lr=lr)

        # Training loop
        self.model.train()
        for epoch in range(epochs):
            running_loss = 0.0
            correct = 0
            total = 0

            for batch_idx, (data, target) in enumerate(train_loader):
                data, target = data.to(self.device), target.to(self.device)

                optimizer.zero_grad()
                output = self.model(data)
                loss = criterion(output, target)
                loss.backward()
                optimizer.step()

                running_loss += loss.item()
                _, predicted = torch.max(output.data, 1)
                total += target.size(0)
                correct += (predicted == target).sum().item()

                if batch_idx % 100 == 0:
                    logger.info(
                        f"Epoch {epoch + 1}/{epochs}, Batch {batch_idx}, "
                        f"Loss: {loss.item():.4f}, "
                        f"Accuracy: {100 * correct / total:.2f}%"
                    )

            epoch_loss = running_loss / len(train_loader)
            epoch_acc = 100 * correct / total
            logger.info(
                f"Epoch {epoch + 1}/{epochs} completed - "
                f"Loss: {epoch_loss:.4f}, Accuracy: {epoch_acc:.2f}%"
            )

        # Save the trained model
        MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
        torch.save(self.model.state_dict(), MODEL_PATH)
        logger.info(f"Model saved to {MODEL_PATH}")

        # Set model to evaluation mode
        self.model.eval()

    def preprocess_image(self, image_array: np.ndarray) -> torch.Tensor:
        """
        Preprocess image array for CNN input.

        Args:
            image_array: Input image as numpy array (28x28)

        Returns:
            Preprocessed tensor ready for model input
        """
        # Ensure correct shape and type
        if image_array.shape != MODEL_INPUT_SIZE:
            raise ValueError(
                f"Expected shape {MODEL_INPUT_SIZE}, got {image_array.shape}"
            )

        # Normalize to [0, 1] and convert to tensor
        image_tensor = torch.from_numpy(image_array).float() / 255.0

        # Add batch and channel dimensions: (H, W) -> (1, 1, H, W)
        image_tensor = image_tensor.unsqueeze(0).unsqueeze(0)

        # Apply MNIST normalization
        image_tensor = (image_tensor - 0.1307) / 0.3081

        return image_tensor.to(self.device)

    def predict(self, image_tensor: torch.Tensor) -> int:
        """
        Predict digit from preprocessed image tensor.

        Args:
            image_tensor: Preprocessed image tensor

        Returns:
            Predicted digit (0-9)
        """
        if self.model is None:
            raise RuntimeError("Model not loaded")

        with torch.no_grad():
            output = self.model(image_tensor)
            _, predicted = torch.max(output, 1)
            return int(predicted.item())

    def predict_with_confidence(self, image_tensor: torch.Tensor) -> Tuple[int, float]:
        """
        Predict digit with confidence score.

        Args:
            image_tensor: Preprocessed image tensor

        Returns:
            Tuple of (predicted_digit, confidence_score)
        """
        if self.model is None:
            raise RuntimeError("Model not loaded")

        with torch.no_grad():
            output = self.model(image_tensor)
            probabilities = F.softmax(output, dim=1)
            confidence, predicted = torch.max(probabilities, 1)
            return int(predicted.item()), float(confidence.item())


def train_cnn_model(epochs: int = 10) -> None:
    """
    Convenience function to train the CNN model.

    Args:
        epochs: Number of training epochs
    """
    predictor = CNNPredictor()
    predictor.train_model(epochs=epochs)
    logger.info("CNN model training completed!")


if __name__ == "__main__":
    # Train the model if run directly
    train_cnn_model()
