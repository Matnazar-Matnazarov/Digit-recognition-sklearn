#!/bin/bash

# 🎨 Paint Digit Recognizer - Smart Runner Script
# This script runs the project completely

set -e  # Stop on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Log functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_step() {
    echo -e "${PURPLE}🔧 $1${NC}"
}

# Check model availability
check_model() {
    if [ ! -f "model/mnist_cnn.pth" ]; then
        log_warning "Model not found. Training needed..."
        return 1
    else
        log_success "Model available: model/mnist_cnn.pth"
        return 0
    fi
}

# Check virtual environment
check_venv() {
    if [ -z "$VIRTUAL_ENV" ]; then
        log_warning "Virtual environment not active"
        if [ -d ".venv" ]; then
            log_info "Activating virtual environment..."
            source .venv/bin/activate
            log_success "Virtual environment activated"
        else
            log_error "Virtual environment not found. Please install first"
            exit 1
        fi
    else
        log_success "Virtual environment active: $VIRTUAL_ENV"
    fi
}

# Check dependencies
check_dependencies() {
    log_step "Checking packages..."
    
    # Check PyTorch
    if ! python -c "import torch; print('PyTorch:', torch.__version__)" 2>/dev/null; then
        log_warning "PyTorch not found. Installing..."
        pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
        log_success "PyTorch installed"
    fi
    
    # Other packages
    if ! python -c "import fastapi, htmx, pytest" 2>/dev/null; then
        log_warning "Installing packages..."
        pip install -r requirements.txt
        log_success "Packages installed"
    fi
}

# Train model
train_model() {
    log_step "Training model..."
    if python scripts/train_cnn.py; then
        log_success "Model trained successfully"
    else
        log_error "Error training model"
        exit 1
    fi
}

# Run tests
run_tests() {
    log_step "Running tests..."
    if python -m pytest tests/ -v; then
        log_success "All tests passed successfully"
    else
        log_warning "Some tests failed"
        read -p "Do you want to continue? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Check code quality
check_code_quality() {
    log_step "Checking code quality..."
    if python scripts/clean_code.py; then
        log_success "Code quality check successful"
    else
        log_warning "Code quality issues found"
        read -p "Do you want to continue? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Development mode
start_development() {
    log_step "Starting in development mode..."
    log_info "With Uvicorn + auto-reload"
    log_success "Application will open at http://localhost:8000"
    log_info "Press Ctrl+C to stop"
    
    export ENVIRONMENT=development
    python main.py
}

# Production mode
start_production() {
    log_step "Starting in production mode..."
    log_info "With Gunicorn + Uvicorn worker"
    
    # Calculate CPU cores
    CPU_CORES=$(nproc)
    WORKERS=$((CPU_CORES * 2 + 1))
    
    log_info "CPU cores: $CPU_CORES, Workers: $WORKERS"
    log_success "Application will open at http://localhost:8000"
    log_info "Press Ctrl+C to stop"
    
    export ENVIRONMENT=production
    gunicorn \
        -k uvicorn.workers.UvicornWorker \
        app.asgi:app \
        --bind 0.0.0.0:8000 \
        --workers $WORKERS \
        --worker-class uvicorn.workers.UvicornWorker \
        --worker-connections 1000 \
        --max-requests 1000 \
        --max-requests-jitter 100 \
        --timeout 30 \
        --keep-alive 2 \
        --log-level info \
        --access-logfile - \
        --error-logfile - \
        --preload \
        --worker-tmp-dir /dev/shm \
        --graceful-timeout 30 \
        --limit-request-line 4094 \
        --limit-request-fields 100 \
        --limit-request-field_size 8190
}

# Docker mode
start_docker() {
    log_step "Starting with Docker..."
    
    # Create Docker image
    log_info "Creating Docker image..."
    if docker build -t digit-recognizer .; then
        log_success "Docker image created"
    else
        log_error "Error creating Docker image"
        exit 1
    fi
    
    log_info "Starting Docker container..."
    log_success "Application will open at http://localhost:8000"
    log_info "Press Ctrl+C to stop"
    
    docker run -p 8000:8000 digit-recognizer
}

# Main function
main() {
    echo -e "${CYAN}"
    echo "🎨 Paint Digit Recognizer - Smart Runner"
    echo "========================================"
    echo -e "${NC}"
    
    # 1. Check virtual environment
    check_venv
    
    # 2. Check dependencies
    check_dependencies
    
    # 3. Check and train model
    if ! check_model; then
        train_model
    fi
    
    # 4. Run tests
    echo
    read -p "Do you want to run tests? (Y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        log_info "Tests skipped"
    else
        run_tests
    fi
    
    # 5. Check code quality
    echo
    read -p "Do you want to check code quality? (Y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        log_info "Code quality check skipped"
    else
        check_code_quality
    fi
    
    # 6. Choose run method
    echo
    echo -e "${YELLOW}Choose run method:${NC}"
    echo "1) Development mode (uvicorn + auto-reload)"
    echo "2) Production mode (gunicorn + uvicorn worker)"
    echo "3) With Docker"
    echo "4) Exit"
    
    read -p "Choose (1-4): " choice
    
    case $choice in
        1)
            start_development
            ;;
        2)
            start_production
            ;;
        3)
            start_docker
            ;;
        4)
            log_info "Exiting..."
            exit 0
            ;;
        *)
            log_error "Invalid choice"
            exit 1
            ;;
    esac
}

# Run script
main "$@" 