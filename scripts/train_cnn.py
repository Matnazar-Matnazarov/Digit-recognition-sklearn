#!/usr/bin/env python3
"""
CNN Model Training Script

This script trains the PyTorch CNN model on MNIST dataset.
Run this script to create a trained model for digit recognition.
"""

import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.models.cnn_model import train_cnn_model  # noqa: E402

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Main training function."""
    try:
        logger.info("Starting CNN model training...")

        # Train the model with 5 epochs for faster training
        train_cnn_model(epochs=5)

        logger.info("CNN model training completed successfully!")
        logger.info("Model saved to: model/mnist_cnn.pth")

    except Exception as e:
        logger.error(f"Training failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
