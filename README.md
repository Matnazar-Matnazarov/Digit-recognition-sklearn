# 🎨 Paint Digit Recognizer

A professional FastAPI application for digit recognition using PyTorch CNN, HTMX, and modern web technologies.

## 🚀 Quick Start

### Easiest Way
```bash
# Complete installation and setup
./install.sh
# or
make install-app
```

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Usage](#-usage)
- [Development](#-development)
- [Production](#-production)
- [Docker](#-docker)
- [Testing](#-testing)
- [API Documentation](#-api-documentation)
- [Performance](#-performance)
- [Security](#-security)
- [Monitoring](#-monitoring)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

### 🎯 Core Features
- ✅ **PyTorch CNN Model** - High-accuracy digit recognition
- ✅ **FastAPI Backend** - Modern, fast REST API
- ✅ **HTMX Frontend** - Dynamic web interface
- ✅ **Real-time Prediction** - Instant digit recognition
- ✅ **Batch Processing** - Multiple image support
- ✅ **File Upload** - Direct image upload support

### 🛠 Technical Features
- ✅ **Professional Architecture** - Clean, modular code structure
- ✅ **Type Safety** - Full type hints and validation
- ✅ **Error Handling** - Comprehensive error management
- ✅ **Logging** - Structured logging with different levels
- ✅ **Caching** - Static file caching and optimization
- ✅ **Security Headers** - XSS, CSRF protection
- ✅ **Compression** - GZip middleware for performance

### 🚀 Performance Features
- ✅ **uvloop** - High-performance event loop
- ✅ **Gunicorn + Uvicorn** - Production-ready server
- ✅ **Worker Management** - Dynamic worker scaling
- ✅ **Connection Pooling** - Optimized connection handling
- ✅ **Memory Optimization** - Low memory footprint

## 🏗 Architecture

```
fastapi_htmx_paint/
├── app/
│   ├── models/          # ML models and predictors
│   ├── routes/          # API endpoints
│   ├── static/          # Static files (CSS, JS, images)
│   ├── templates/       # HTML templates
│   └── asgi.py          # FastAPI application
├── scripts/             # Utility scripts
├── tests/               # Test suite
├── model/               # Trained model files
├── data/                # Dataset files
├── main.py              # Application entry point
├── install.sh           # Installation script
├── run.sh               # Smart runner script
├── docker-entrypoint.sh # Docker entrypoint
└── requirements.txt     # Dependencies
```

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip or uv
- Docker (optional)

### Method 1: Automated Installation (Recommended)
```bash
# Clone repository
git clone <repository-url>
cd fastapi_htmx_paint

# Run installation script
./install.sh
```

### Method 2: Manual Installation
```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install gunicorn

# Train model
python scripts/train_cnn.py

# Run tests
python -m pytest tests/ -v
```

## 🎮 Usage

### Development Mode
```bash
# Start with auto-reload
make run-dev
# or
ENVIRONMENT=development python main.py
```

**Features:**
- ✅ **Uvicorn + Auto-reload** - Fast development cycle
- ✅ **Hot Reload** - Code changes reflect immediately
- ✅ **Debug Mode** - Detailed error messages
- ✅ **Access Logs** - Request/response logging

### Production Mode
```bash
# Start with Gunicorn + Uvicorn worker
make run-prod
# or
make start-prod
# or
./scripts/start_production.sh
```

**Features:**
- ✅ **Gunicorn + Uvicorn Worker** - Optimal performance
- ✅ **Automatic Workers** - Based on CPU cores (CPU * 2 + 1)
- ✅ **Worker Management** - Crash recovery and load balancing
- ✅ **Connection Pooling** - 1000 connections
- ✅ **Request Limiting** - Prevents memory leaks
- ✅ **Preload** - Fast startup
- ✅ **Production Logging** - Access and error logs
- ✅ **Security Limits** - Request size and field limits
- ✅ **Graceful Shutdown** - Safe stopping

### Docker Mode
```bash
# With Docker (provides option to choose development or production)
docker run -p 8000:8000 digit-recognizer
```

**Features:**
- ✅ **Interactive Mode Selection** - Choose Development or Production
- ✅ **Development Mode** - Uvicorn + auto-reload
- ✅ **Production Mode** - Gunicorn + Uvicorn worker
- ✅ **Environment Isolation** - Complete isolation
- ✅ **Easy Deployment** - Start with one command

## 🧪 Testing

### Run All Tests
```bash
# Run with pytest
make test
# or
python -m pytest tests/ -v

# Run with coverage
make test-cov
```

### Test Categories
- ✅ **API Tests** - Endpoint functionality
- ✅ **Model Tests** - ML model predictions
- ✅ **Integration Tests** - Full workflow testing
- ✅ **Performance Tests** - Load testing

### Code Quality
```bash
# Lint and format
make lint
make format

# Type checking
make type-check

# All quality checks
make quality
```

## 📚 API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### Health Check
```http
GET /api/v1/health
```

#### Model Information
```http
GET /api/v1/model/info
```

#### Single Prediction
```http
POST /api/v1/predict
Content-Type: application/json

{
  "image": "base64_encoded_image"
}
```

#### Batch Prediction
```http
POST /api/v1/predict/batch
Content-Type: application/json

{
  "images": ["base64_encoded_image1", "base64_encoded_image2"]
}
```

#### File Upload
```http
POST /api/v1/predict/file
Content-Type: multipart/form-data

file: image_file
```

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## ⚡ Performance

### Benchmarks
- **Model Accuracy**: ~99% on MNIST test set
- **Inference Time**: <50ms per prediction
- **Memory Usage**: <500MB total
- **Concurrent Requests**: 1000+ with Gunicorn

### Optimization Features
- ✅ **Model Optimization** - CPU-optimized PyTorch
- ✅ **Image Preprocessing** - Efficient resizing and normalization
- ✅ **Caching** - Static file and response caching
- ✅ **Compression** - GZip compression for responses
- ✅ **Connection Reuse** - Persistent connections

## 🔒 Security

### Security Features
- ✅ **Input Validation** - Comprehensive request validation
- ✅ **File Upload Security** - Safe file handling
- ✅ **CORS Protection** - Cross-origin request control
- ✅ **Security Headers** - XSS, CSRF protection
- ✅ **Rate Limiting** - Request rate control
- ✅ **Error Sanitization** - Safe error messages

### Best Practices
- ✅ **Environment Variables** - Secure configuration
- ✅ **Dependency Scanning** - Regular security updates
- ✅ **Code Review** - Security-focused development
- ✅ **Testing** - Security test coverage

## 📊 Monitoring

### Logging
- ✅ **Structured Logging** - JSON format logs
- ✅ **Log Levels** - DEBUG, INFO, WARNING, ERROR
- ✅ **Request Logging** - Access and error logs
- ✅ **Performance Logging** - Response time tracking

### Metrics
- ✅ **Health Checks** - Application health monitoring
- ✅ **Performance Metrics** - Response time, throughput
- ✅ **Error Tracking** - Error rate and types
- ✅ **Resource Usage** - CPU, memory monitoring

## 🛠 Development

### Makefile Commands
```bash
# Installation
make install-app          # Run installation script

# Development
make run                  # Start application
make run-dev              # Development mode
make run-prod             # Production mode
make start-prod           # Production startup script

# Testing
make test                 # Run tests
make test-cov             # Run tests with coverage
make lint                 # Run linter
make format               # Format code
make type-check           # Type checking
make quality              # All quality checks

# Docker
make docker-build         # Build Docker image
make docker-run           # Run Docker container

# Utilities
make clean                # Clean cache files
make help                 # Show help
```

### Development Workflow
1. **Setup**: Run `./install.sh`
2. **Development**: Use `make run-dev`
3. **Testing**: Run `make test`
4. **Quality**: Check with `make quality`
5. **Production**: Deploy with `make run-prod`

## 🐳 Docker

### Build Image
```bash
# Build Docker image
make docker-build
# or
docker build -t digit-recognizer .
```

### Run Container
```bash
# Run with interactive mode selection
docker run -p 8000:8000 digit-recognizer

# Run in specific mode
docker run -p 8000:8000 -e ENVIRONMENT=production digit-recognizer
```

### Docker Features
- ✅ **Multi-stage Build** - Optimized image size
- ✅ **Health Checks** - Container health monitoring
- ✅ **Environment Variables** - Configurable settings
- ✅ **Volume Mounting** - Persistent data storage
- ✅ **Network Configuration** - Port mapping

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Make changes and test: `make test`
4. Check quality: `make quality`
5. Commit changes: `git commit -m 'Add feature'`
6. Push branch: `git push origin feature-name`
7. Create Pull Request

### Code Standards
- ✅ **Type Hints** - Full type annotation
- ✅ **Docstrings** - Comprehensive documentation
- ✅ **Error Handling** - Proper exception handling
- ✅ **Testing** - High test coverage
- ✅ **Formatting** - Consistent code style

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **PyTorch** - Deep learning framework
- **FastAPI** - Modern web framework
- **HTMX** - Dynamic web interface
- **MNIST** - Digit recognition dataset
- **Gunicorn** - Production WSGI server
- **Uvicorn** - Lightning-fast ASGI server

---

**Made with ❤️ for digit recognition**