#!/bin/bash

# 🐳 Docker Entrypoint Script
# This script provides option to choose development or production mode in Docker container

set -e

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

# Check environment
check_environment() {
    log_step "Checking environment..."
    
    # Check model
    if [ ! -f "/app/model/mnist_cnn.pth" ]; then
        log_error "Model not found. Training first..."
        python /app/scripts/train_cnn.py
    fi
    
    log_success "Environment ready"
}

# Development mode
start_development() {
    log_step "Starting in development mode..."
    log_info "With Uvicorn + auto-reload"
    log_success "Application will open at http://localhost:8000"
    log_info "Press Ctrl+C to stop"
    
    export ENVIRONMENT=development
    uvicorn app.asgi:app \
        --host 0.0.0.0 \
        --port 8000 \
        --reload \
        --log-level info \
        --access-log
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

# Choose mode
choose_mode() {
    echo -e "${CYAN}"
    echo "🐳 Paint Digit Recognizer - Docker Mode"
    echo "======================================"
    echo -e "${NC}"
    
    # Check environment
    check_environment
    
    # Choose mode
    echo
    echo -e "${YELLOW}Choose run mode:${NC}"
    echo "1) Development mode (uvicorn + auto-reload)"
    echo "2) Production mode (gunicorn + uvicorn worker)"
    echo "3) Exit"
    
    read -p "Choose (1-3): " choice
    
    case $choice in
        1)
            start_development
            ;;
        2)
            start_production
            ;;
        3)
            log_info "Exiting..."
            exit 0
            ;;
        *)
            log_error "Invalid choice"
            exit 1
            ;;
    esac
}

# Main function
main() {
    # Docker environment settings
    export PYTHONPATH=/app
    
    # Choose mode
    choose_mode
}

# Run script
main "$@" 