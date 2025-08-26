#!/bin/bash

# 🏭 Production Startup Script
# This script starts the application in production mode with gunicorn + uvicorn worker

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Check environment
check_environment() {
    if [ -z "$VIRTUAL_ENV" ]; then
        log_error "Virtual environment not active"
        log_info "Activating virtual environment..."
        source .venv/bin/activate
    fi
    
    # Check model
    if [ ! -f "model/mnist_cnn.pth" ]; then
        log_error "Model not found. Please train first: python scripts/train_cnn.py"
        exit 1
    fi
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

# Main function
main() {
    echo -e "${YELLOW}"
    echo "🏭 Paint Digit Recognizer - Production Mode"
    echo "=========================================="
    echo -e "${NC}"
    
    # Check environment
    check_environment
    
    # Start production mode
    start_production
}

# Run script
main "$@" 