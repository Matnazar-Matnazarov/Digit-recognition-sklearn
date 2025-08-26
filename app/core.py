"""Core configuration and path definitions for the FastAPI HTMX Paint application."""

from pathlib import Path

# Base directory configuration
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "app" / "templates"
STATIC_DIR = BASE_DIR / "app" / "static"
MODEL_DIR = BASE_DIR / "model"
MODEL_PATH = MODEL_DIR / "mnist_lr."

# Application settings
APP_NAME = "Paint Digit Recognizer"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "FastAPI + HTMX + sklearn demo for digit recognition"

# Model settings
MODEL_INPUT_SIZE = (28, 28)  # MNIST standard size
CANVAS_SIZE = (280, 280)  # Frontend canvas size
