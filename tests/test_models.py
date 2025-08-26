"""
Tests for the Predictor module with PyTorch CNN.

Tests image preprocessing, model loading, and prediction functionality.
"""

import base64
import io
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
import torch
from PIL import Image

from app.models.predictor import Predictor


class TestPredictor:
    """Test Predictor class functionality."""

    @patch("app.models.predictor.CNNPredictor")
    def test_predictor_initialization(self, mock_cnn_predictor):
        """Test predictor initialization and CNN model loading."""
        mock_cnn = MagicMock()
        mock_cnn.model = MagicMock()
        mock_cnn_predictor.return_value = mock_cnn

        predictor = Predictor()

        assert predictor.cnn_predictor is not None
        mock_cnn_predictor.assert_called_once()

    @patch("app.models.predictor.CNNPredictor")
    def test_predictor_model_not_found(self, mock_cnn_predictor):
        """Test predictor when CNN model doesn't exist."""
        mock_cnn = MagicMock()
        mock_cnn.model = None
        mock_cnn_predictor.return_value = mock_cnn

        with pytest.raises(RuntimeError, match="Failed to load CNN model"):
            Predictor()

    @patch("app.models.predictor.CNNPredictor")
    def test_preprocess_base64_valid_image(self, mock_cnn_predictor):
        """Test preprocessing of valid base64 image."""
        # Mock CNN predictor
        mock_cnn = MagicMock()
        mock_cnn.model = MagicMock()
        mock_cnn_predictor.return_value = mock_cnn

        # Create a simple test image
        img_draw = Image.new("L", (280, 280), color=0)

        # Convert to base64
        buffer = io.BytesIO()
        img_draw.save(buffer, format="PNG")
        img_data = base64.b64encode(buffer.getvalue()).decode("utf-8")
        data_url = f"data:image/png;base64,{img_data}"

        predictor = Predictor()
        result = predictor.preprocess_base64(data_url)

        assert result.shape == (28, 28)  # MNIST size
        assert result.dtype == np.float32

    @patch("app.models.predictor.CNNPredictor")
    def test_preprocess_base64_invalid_data(self, mock_cnn_predictor):
        """Test preprocessing of invalid base64 data."""
        # Mock CNN predictor
        mock_cnn = MagicMock()
        mock_cnn.model = MagicMock()
        mock_cnn_predictor.return_value = mock_cnn

        predictor = Predictor()

        with pytest.raises(ValueError):
            predictor.preprocess_base64("invalid_base64_data")

    @patch("app.models.predictor.CNNPredictor")
    def test_predict_from_base64(self, mock_cnn_predictor):
        """Test prediction from base64 image."""
        # Mock CNN predictor
        mock_cnn = MagicMock()
        mock_cnn.model = MagicMock()
        mock_cnn.preprocess_image.return_value = torch.tensor([[1.0]])
        mock_cnn.predict.return_value = 5
        mock_cnn_predictor.return_value = mock_cnn

        predictor = Predictor()

        # Create test image
        img = Image.new("L", (280, 280), color=0)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_data = base64.b64encode(buffer.getvalue()).decode("utf-8")
        data_url = f"data:image/png;base64,{img_data}"

        result = predictor.predict_from_base64(data_url)
        assert result == 5
        assert isinstance(result, int)

    @patch("app.models.predictor.CNNPredictor")
    def test_get_prediction_confidence(self, mock_cnn_predictor):
        """Test prediction with confidence score."""
        # Mock CNN predictor
        mock_cnn = MagicMock()
        mock_cnn.model = MagicMock()
        mock_cnn.preprocess_image.return_value = torch.tensor([[1.0]])
        mock_cnn.predict_with_confidence.return_value = (3, 0.9)
        mock_cnn_predictor.return_value = mock_cnn

        predictor = Predictor()

        # Create test image
        img = Image.new("L", (280, 280), color=0)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_data = base64.b64encode(buffer.getvalue()).decode("utf-8")
        data_url = f"data:image/png;base64,{img_data}"

        digit, confidence = predictor.get_prediction_confidence(data_url)
        assert digit == 3
        assert confidence == 0.9
        assert isinstance(digit, int)
        assert isinstance(confidence, float)
        assert 0 <= confidence <= 1


class TestImagePreprocessing:
    """Test image preprocessing functionality."""

    def test_image_resize(self):
        """Test image resizing to MNIST format."""
        # Create a large test image
        img = Image.new("L", (280, 280), color=255)

        # Resize to MNIST format
        resized = img.resize((28, 28), Image.Resampling.LANCZOS)

        assert resized.size == (28, 28)

    def test_image_color_inversion(self):
        """Test image color inversion."""
        # Create a test image with black digit on white background
        img = Image.new("L", (28, 28), color=255)
        # Draw a black digit (value 0)
        img.putpixel((14, 14), 0)

        # Convert to numpy array
        arr = np.array(img, dtype=np.float32)

        # Invert colors (black digit becomes white)
        arr_inverted = 255.0 - arr

        # Check that black pixel (0) became white (255)
        assert arr_inverted[14, 14] == 255.0
        # Check that white background (255) became black (0)
        assert arr_inverted[0, 0] == 0.0

    def test_image_normalization(self):
        """Test image normalization to [0, 1] range."""
        # Create a test image with values 0-255
        img = Image.new("L", (28, 28), color=128)

        # Convert to numpy array
        arr = np.array(img, dtype=np.float32)

        # Normalize to [0, 1]
        arr_normalized = arr / 255.0

        # Check that values are in [0, 1] range
        assert arr_normalized.min() >= 0.0
        assert arr_normalized.max() <= 1.0
        assert arr_normalized[0, 0] == 128.0 / 255.0
