# Makefile for FastAPI HTMX Paint Digit Recognizer

.PHONY: help install train run test clean format lint type-check clean-code fix-code docker-build docker-run

# Default target
help:
	@echo "Available commands:"
	@echo "  install     - Install dependencies"
	@echo "  train       - Train the PyTorch CNN model"
	@echo "  run         - Run the application"
	@echo "  test        - Run tests"
	@echo "  clean       - Clean cache and temporary files"
	@echo "  format      - Format code with Black and Ruff"
	@echo "  lint        - Lint code with Ruff"
	@echo "  type-check  - Type check with MyPy"
	@echo "  clean-code  - Run all code quality checks"
	@echo "  fix-code    - Auto-fix code style issues"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run  - Run Docker container"
	@echo "  smart-run   - Interactive smart runner with Docker/local choice"
	@echo "  install-app - Complete installation and setup script"
	@echo "  run-dev     - Run in development mode"
	@echo "  run-prod    - Run in production mode"
	@echo "  start-prod  - Production startup script"

# Install dependencies
install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt

# Train the CNN model
train:
	@echo "Training PyTorch CNN model..."
	python scripts/train_cnn.py

# Run the application
run:
	@echo "Starting FastAPI application..."
	python main.py

# Run in development mode
run-dev:
	@echo "Starting in DEVELOPMENT mode..."
	ENVIRONMENT=development python main.py

# Run in production mode
run-prod:
	@echo "Starting in PRODUCTION mode..."
	@echo "CPU cores: $(shell nproc), Workers: $(shell echo $$(( $(shell nproc) * 2 + 1 )))"
	ENVIRONMENT=production gunicorn \
		-k uvicorn.workers.UvicornWorker \
		app.asgi:app \
		--bind 0.0.0.0:8000 \
		--workers $(shell echo $$(( $(shell nproc) * 2 + 1 ))) \
		--worker-class uvicorn.workers.UvicornWorker \
		--worker-connections 1000 \
		--max-requests 1000 \
		--max-requests-jitter 100 \
		--timeout 30 \
		--keep-alive 2 \
		--log-level info \
		--access-logfile - \
		--error-logfile - \
		--preload

# Run tests
test:
	@echo "Running tests..."
	pytest -v

# Clean cache and temporary files
clean:
	@echo "Cleaning cache and temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name "*.pyd" -delete
	find . -name ".coverage" -delete
	find . -name "htmlcov" -type d -exec rm -rf {} +

# Format code
format:
	@echo "Formatting code..."
	ruff format .
	black .

# Lint code
lint:
	@echo "Linting code..."
	ruff check .

# Type check
type-check:
	@echo "Type checking..."
	mypy app/ --ignore-missing-imports

# Run all code quality checks
clean-code:
	@echo "Running code quality checks..."
	python scripts/clean_code.py

# Auto-fix code style issues
fix-code:
	@echo "Auto-fixing code style issues..."
	python scripts/fix_code.py

# Build Docker image
docker-build:
	@echo "Building Docker image..."
	docker build -t fastapi-htmx-paint .

# Run Docker container
docker-run:
	@echo "Running Docker container..."
	docker run -p 8000:8000 fastapi-htmx-paint

# Development setup
dev-setup: install train
	@echo "Development setup completed!"

# Quick start
quick-start: dev-setup run

# Smart runner with interactive menu
smart-run:
	@echo "🎨 Smart Runner ishga tushirilmoqda..."
	@./run.sh

# Installation script
install-app:
	@echo "🎨 Installation script ishga tushirilmoqda..."
	@./install.sh

# Production startup script
start-prod:
	@echo "🏭 Production mode ishga tushirilmoqda..."
	@./scripts/start_production.sh 