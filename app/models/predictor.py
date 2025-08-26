"""
Digit Predictor Module

This module handles image preprocessing and prediction using the trained PyTorch CNN model.
"""

import base64
import io
import logging
from typing import Tuple

import numpy as np
from PIL import Image

from app.core import MODEL_INPUT_SIZE
from app.models.cnn_model import CNNPredictor

logger = logging.getLogger(__name__)


class Predictor:
    """Handles digit prediction from canvas images using PyTorch CNN."""

    def __init__(self):
        """Initialize predictor and load the trained CNN model."""
        self.cnn_predictor = CNNPredictor()
        if self.cnn_predictor.model is None:
            raise RuntimeError("Failed to load CNN model")

    def preprocess_base64(self, data_url: str) -> np.ndarray:
        """
        Preprocess base64 encoded image data for prediction.

        Args:
            data_url: Base64 encoded image data (e.g., "data:image/png;base64,...")

        Returns:
            Preprocessed image as numpy array (28x28)
        """
        try:
            logger.info(f"Processing image data: {len(data_url)} chars")

            # Extract base64 data
            if "," in data_url:
                header, b64 = data_url.split(",", 1)
                logger.info(f"Header: {header}")
            else:
                b64 = data_url

            # Decode base64 to image
            image_data = base64.b64decode(b64)
            logger.info(f"Decoded image size: {len(image_data)} bytes")

            img = Image.open(io.BytesIO(image_data)).convert(
                "L"
            )  # Convert to grayscale
            logger.info(f"Image size: {img.size}, mode: {img.mode}")

            # Convert to numpy array
            arr = np.array(img, dtype=np.float32)
            logger.info(
                f"Original array shape: {arr.shape}, min: {arr.min()}, max: {arr.max()}"
            )

            # Invert colors: canvas black digit (0) -> MNIST white digit (255)
            arr = 255.0 - arr

            # Apply threshold to make digit more prominent
            threshold = 50
            arr = np.where(arr > threshold, arr, 0)

            # Center the digit by finding bounding box
            rows = np.any(arr > 0, axis=1)
            cols = np.any(arr > 0, axis=0)

            if np.any(rows) and np.any(cols):
                rmin, rmax = np.where(rows)[0][[0, -1]]
                cmin, cmax = np.where(cols)[0][[0, -1]]

                # Add padding
                padding = 4
                rmin = max(0, rmin - padding)
                rmax = min(arr.shape[0], rmax + padding)
                cmin = max(0, cmin - padding)
                cmax = min(arr.shape[1], cmax + padding)

                # Crop to bounding box
                arr = arr[rmin:rmax, cmin:cmax]
                logger.info(f"Cropped array shape: {arr.shape}")

            # Resize to MNIST standard size with better interpolation
            img_resized = Image.fromarray(arr).resize(
                MODEL_INPUT_SIZE, Image.Resampling.LANCZOS
            )
            arr = np.array(img_resized, dtype=np.float32)

            logger.info(f"Final array shape: {arr.shape}")
            return arr

        except Exception as e:
            logger.error(f"Failed to preprocess image: {e}")
            raise ValueError(f"Invalid image data: {e}")

    def predict_from_base64(self, data_url: str) -> int:
        """
        Predict digit from base64 encoded image.

        Args:
            data_url: Base64 encoded image data

        Returns:
            Predicted digit (0-9)
        """
        try:
            # Preprocess image
            image_array = self.preprocess_base64(data_url)

            # Convert to tensor and predict
            image_tensor = self.cnn_predictor.preprocess_image(image_array)
            result = self.cnn_predictor.predict(image_tensor)

            logger.info(f"Predicted digit: {result}")
            return result

        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise

    def get_prediction_confidence(self, data_url: str) -> Tuple[int, float]:
        """
        Get prediction with confidence score.

        Args:
            data_url: Base64 encoded image data

        Returns:
            Tuple of (predicted_digit, confidence_score)
        """
        try:
            # Preprocess image
            image_array = self.preprocess_base64(data_url)

            # Convert to tensor and predict with confidence
            image_tensor = self.cnn_predictor.preprocess_image(image_array)
            digit, confidence = self.cnn_predictor.predict_with_confidence(image_tensor)

            # Ensure confidence is a valid float
            confidence = float(confidence)
            if not (0.0 <= confidence <= 1.0):
                confidence = 0.5  # Default confidence if out of range

            logger.info(f"Predicted digit: {digit} with confidence: {confidence:.3f}")
            return digit, confidence

        except Exception as e:
            logger.error(f"Confidence prediction failed: {e}")
            # Return default values on error
            return 0, 0.0
