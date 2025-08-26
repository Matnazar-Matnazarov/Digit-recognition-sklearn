"""
API tests for Paint Digit Recognizer.
"""

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.asgi import app

client = TestClient(app)


class TestAPIEndpoints:
    """Test API endpoints."""

    def test_api_health(self):
        """Test API health endpoint."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "message" in data
        assert "version" in data

    def test_model_info(self):
        """Test model info endpoint."""
        response = client.get("/api/v1/model/info")
        assert response.status_code == 200
        data = response.json()
        assert data["model_type"] == "PyTorch CNN"
        assert data["dataset"] == "MNIST"
        assert data["input_size"] == "28x28"
        assert data["output_classes"] == 10
        assert data["architecture"] == "2 Conv layers + 2 FC layers"

    @patch("app.routes.api.get_predictor")
    def test_predict_digit_success(self, mock_get_predictor):
        """Test successful digit prediction."""
        # Mock predictor instance
        mock_predictor = MagicMock()
        mock_predictor.get_prediction_confidence.return_value = (5, 0.85)
        mock_get_predictor.return_value = mock_predictor

        # Test data
        test_image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="

        response = client.post("/api/v1/predict", data={"image": test_image})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["prediction"] == 5
        assert data["confidence"] == 0.85
        assert "confidence_percentage" in data

    def test_predict_digit_no_image(self):
        """Test prediction with no image data."""
        response = client.post("/api/v1/predict", data={"image": ""})
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

    @patch("app.routes.api.get_predictor")
    def test_predict_digit_invalid_image(self, mock_get_predictor):
        """Test prediction with invalid image data."""
        # Mock predictor instance
        mock_predictor = MagicMock()
        mock_predictor.get_prediction_confidence.side_effect = ValueError(
            "Invalid image data"
        )
        mock_get_predictor.return_value = mock_predictor

        response = client.post("/api/v1/predict", data={"image": "invalid"})
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

    @patch("app.routes.api.get_predictor")
    def test_batch_predict_success(self, mock_get_predictor):
        """Test successful batch prediction."""
        # Mock predictor instance
        mock_predictor = MagicMock()
        mock_predictor.get_prediction_confidence.side_effect = [
            (1, 0.9),
            (2, 0.8),
            (3, 0.7),
        ]
        mock_get_predictor.return_value = mock_predictor

        test_images = [
            "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
            "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
            "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
        ]

        response = client.post("/api/v1/batch-predict", data={"images": test_images})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["total_images"] == 3
        assert data["successful_predictions"] == 3
        assert len(data["results"]) == 3

    def test_batch_predict_no_images(self):
        """Test batch prediction with no images."""
        response = client.post("/api/v1/batch-predict", data={"images": []})
        assert response.status_code == 422  # FastAPI validation error
        data = response.json()
        assert "detail" in data

    def test_batch_predict_too_many_images(self):
        """Test batch prediction with too many images."""
        test_images = ["data:image/png;base64,test"] * 11
        response = client.post("/api/v1/batch-predict", data={"images": test_images})
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data


class TestFileUpload:
    """Test file upload functionality."""

    @patch("app.routes.api.get_predictor")
    def test_predict_file_success(self, mock_get_predictor):
        """Test successful file prediction."""
        # Mock predictor instance
        mock_predictor = MagicMock()
        mock_predictor.get_prediction_confidence.return_value = (7, 0.92)
        mock_get_predictor.return_value = mock_predictor

        # Create a simple test image
        test_image_content = b"fake_image_data"

        response = client.post(
            "/api/v1/predict/file",
            files={"file": ("test.png", test_image_content, "image/png")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["prediction"] == 7
        assert data["confidence"] == 0.92
        assert data["filename"] == "test.png"

    def test_predict_file_invalid_type(self):
        """Test file prediction with invalid file type."""
        test_file_content = b"not_an_image"

        response = client.post(
            "/api/v1/predict/file",
            files={"file": ("test.txt", test_file_content, "text/plain")},
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
