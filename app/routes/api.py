"""
API routes for Paint Digit Recognizer.

Provides RESTful API endpoints for external frontend applications.
"""

import logging
from typing import Any, Dict

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool

from app.models.predictor import Predictor

# Setup logging
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/v1", tags=["api"])

# Global predictor instance (will be set by lifespan)
predictor = None


def get_predictor() -> Predictor:
    """Get the global predictor instance."""
    global predictor
    if predictor is None:
        predictor = Predictor()
    return predictor


@router.post("/predict")
async def predict_digit(
    image: str = Form(..., description="Base64 encoded image data"),
):
    """
    Predict digit from base64 encoded image.

    Args:
        image: Base64 encoded image data (e.g., "data:image/png;base64,...")

    Returns:
        JSON response with prediction and confidence
    """
    try:
        if not image or image.strip() == "":
            raise HTTPException(status_code=400, detail="No image data provided")

        # Get predictor instance
        predictor_instance = get_predictor()

        # Get prediction and confidence
        digit, confidence = await run_in_threadpool(
            predictor_instance.get_prediction_confidence, image
        )

        response: Dict[str, Any] = {
            "success": True,
            "prediction": digit,
            "confidence": confidence,
            "confidence_percentage": f"{confidence * 100:.1f}%",
            "message": "Prediction successful",
        }

        logger.info(f"API prediction: {digit} (confidence: {confidence:.3f})")
        return JSONResponse(content=response, status_code=200)

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except ValueError as e:
        logger.warning(f"Invalid input in API: {e}")
        raise HTTPException(status_code=400, detail="Invalid image data")

    except Exception as e:
        logger.error(f"API prediction error: {e}")
        raise HTTPException(status_code=500, detail="Prediction failed")


@router.post("/predict/file")
async def predict_digit_file(file: UploadFile = File(..., description="Image file")):
    """
    Predict digit from uploaded image file.

    Args:
        file: Image file (PNG, JPEG, etc.)

    Returns:
        JSON response with prediction and confidence
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")

        # Read file content
        content = await file.read()

        # Convert to base64
        import base64

        image_data = base64.b64encode(content).decode("utf-8")
        data_url = f"data:{file.content_type};base64,{image_data}"

        # Get predictor instance
        predictor_instance = get_predictor()

        # Get prediction
        digit, confidence = await run_in_threadpool(
            predictor_instance.get_prediction_confidence, data_url
        )

        response: Dict[str, Any] = {
            "success": True,
            "prediction": digit,
            "confidence": confidence,
            "confidence_percentage": f"{confidence * 100:.1f}%",
            "filename": file.filename,
            "message": "Prediction successful",
        }

        logger.info(f"API file prediction: {digit} (confidence: {confidence:.3f})")
        return JSONResponse(content=response, status_code=200)

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"API file prediction error: {e}")
        raise HTTPException(status_code=500, detail="File prediction failed")


@router.get("/health")
async def api_health():
    """
    API health check endpoint.

    Returns:
        JSON response with service status
    """
    try:
        # Test model availability
        predictor_instance = get_predictor()
        test_input = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        await run_in_threadpool(predictor_instance.predict_from_base64, test_input)

        response: Dict[str, Any] = {
            "status": "healthy",
            "message": "Service is running and model is loaded",
            "version": "1.0.0",
        }

        return JSONResponse(content=response, status_code=200)

    except Exception as e:
        logger.error(f"API health check failed: {e}")
        response: Dict[str, Any] = {
            "status": "unhealthy",
            "message": f"Service error: {str(e)}",
            "version": "1.0.0",
        }
        return JSONResponse(content=response, status_code=503)


@router.get("/model/info")
async def model_info():
    """
    Get model information.

    Returns:
        JSON response with model details
    """
    try:
        response: Dict[str, Any] = {
            "model_type": "PyTorch CNN",
            "dataset": "MNIST",
            "input_size": "28x28",
            "output_classes": 10,
            "accuracy": "~99%",
            "version": "2.0.0",
            "architecture": "2 Conv layers + 2 FC layers",
            "device": "CPU optimized",
        }

        return JSONResponse(content=response, status_code=200)

    except Exception as e:
        logger.error(f"Model info error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get model info")


@router.post("/batch-predict")
async def batch_predict(
    images: list[str] = Form(..., description="List of base64 encoded images"),
):
    """
    Predict multiple digits from a list of images.

    Args:
        images: List of base64 encoded image data

    Returns:
        JSON response with predictions for all images
    """
    try:
        if not images or len(images) == 0:
            raise HTTPException(status_code=400, detail="No images provided")

        if len(images) > 10:
            raise HTTPException(
                status_code=400, detail="Maximum 10 images allowed per batch"
            )

        results = []

        for i, image in enumerate(images):
            try:
                predictor_instance = get_predictor()
                digit, confidence = await run_in_threadpool(
                    predictor_instance.get_prediction_confidence, image
                )

                results.append(
                    {
                        "index": i,
                        "prediction": digit,
                        "confidence": confidence,
                        "confidence_percentage": f"{confidence * 100:.1f}%",
                        "success": True,
                    }
                )

            except Exception as e:
                results.append(
                    {
                        "index": i,
                        "prediction": None,
                        "confidence": 0.0,
                        "confidence_percentage": "0.0%",
                        "success": False,
                        "error": str(e),
                    }
                )

        response: Dict[str, Any] = {
            "success": True,
            "total_images": len(images),
            "successful_predictions": len([r for r in results if r["success"]]),
            "results": results,
            "message": "Batch prediction completed",
        }

        logger.info(f"API batch prediction: {len(images)} images")
        return JSONResponse(content=response, status_code=200)

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"API batch prediction error: {e}")
        raise HTTPException(status_code=500, detail="Batch prediction failed")
