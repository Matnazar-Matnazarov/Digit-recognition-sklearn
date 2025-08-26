"""
Home routes for the Paint Digit Recognizer application.

Handles the main page and prediction endpoints with HTMX integration.
"""

import logging
from typing import Any, Dict

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.concurrency import run_in_threadpool
from starlette.templating import _TemplateResponse

from app.core import APP_NAME, TEMPLATES_DIR
from app.models.predictor import Predictor

# Setup logging
logger = logging.getLogger(__name__)

# Initialize router and templates
router = APIRouter()
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Global predictor instance (will be set by lifespan)
predictor = None


def get_predictor() -> Predictor:
    """Get the global predictor instance."""
    global predictor
    if predictor is None:
        predictor = Predictor()
    return predictor


@router.get("/", response_class=HTMLResponse)
async def index(request: Request) -> _TemplateResponse:
    """
    Render the main page with canvas for digit drawing.

    Args:
        request: FastAPI request object

    Returns:
        Rendered HTML template
    """
    try:
        context: Dict[str, Any] = {
            "request": request,
            "app_name": APP_NAME,
            "canvas_size": "280x280",
        }
        return templates.TemplateResponse("index.html", context)
    except Exception as e:
        logger.error(f"Error rendering index page: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/predict", response_class=HTMLResponse)
async def predict(request: Request, image: str = Form(...)) -> _TemplateResponse:
    """
    Handle digit prediction from canvas image.

    This endpoint receives base64 encoded image data from HTMX form submission
    and returns a partial HTML response with the prediction result.

    Args:
        request: FastAPI request object
        image: Base64 encoded image data from canvas

    Returns:
        Partial HTML template with prediction result
    """
    try:
        logger.info(f"Received image data length: {len(image) if image else 0}")
        logger.info(f"Image data starts with: {image[:50] if image else 'None'}")

        if not image or image.strip() == "":
            raise ValueError("No image data provided")

        # Validate image data format
        if not image.startswith("data:image/"):
            raise ValueError("Invalid image data format")

        # Get predictor instance
        predictor_instance = get_predictor()

        # Run prediction in threadpool to avoid blocking
        logger.info("Starting prediction...")
        await run_in_threadpool(predictor_instance.predict_from_base64, image)

        # Get confidence score for better UX
        logger.info("Getting confidence score...")
        digit, confidence = await run_in_threadpool(
            predictor_instance.get_prediction_confidence, image
        )

        context: Dict[str, Any] = {
            "request": request,
            "result": digit,
            "confidence": confidence,
            "confidence_percentage": f"{confidence * 100:.1f}%",
        }

        logger.info(f"Prediction successful: {digit} (confidence: {confidence:.3f})")
        return templates.TemplateResponse("partial_result.html", context)

    except ValueError as e:
        logger.warning(f"Invalid input: {e}")
        context = {
            "request": request,
            "error": "Invalid image data. Please draw a digit and try again.",
        }
        return templates.TemplateResponse("partial_error.html", context)

    except Exception as e:
        logger.error(f"Prediction error: {e}")
        context = {"request": request, "error": "Prediction failed. Please try again."}
        return templates.TemplateResponse("partial_error.html", context)


@router.get("/health", response_class=HTMLResponse)
async def health_check(request: Request) -> _TemplateResponse:
    """
    Health check endpoint to verify application status.

    Args:
        request: FastAPI request object

    Returns:
        Simple HTML response indicating service status
    """
    try:
        # Test model availability
        predictor_instance = get_predictor()
        test_input = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        await run_in_threadpool(predictor_instance.predict_from_base64, test_input)

        context = {
            "request": request,
            "status": "healthy",
            "message": "Service is running and model is loaded",
        }
        return templates.TemplateResponse("health.html", context)

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        context = {
            "request": request,
            "status": "unhealthy",
            "message": f"Service error: {str(e)}",
        }
        return templates.TemplateResponse("health.html", context)
