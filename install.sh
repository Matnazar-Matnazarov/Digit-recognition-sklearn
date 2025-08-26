#!/bin/bash

# 🎨 Paint Digit Recognizer - Installation Script
# This script completely installs and configures the project

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

# Check Python version
check_python() {
    log_step "Checking Python version..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        log_success "Python $PYTHON_VERSION found"
        
        # Check Python version (3.8+ required)
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
            log_success "Python version is compatible"
        else
            log_error "Python 3.8+ required"
            exit 1
        fi
    else
        log_error "Python3 not found. Please install first"
        exit 1
    fi
}

# Create virtual environment
create_venv() {
    log_step "Creating virtual environment..."
    
    if [ -d ".venv" ]; then
        log_warning "Virtual environment already exists"
        read -p "Do you want to recreate it? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf .venv
            log_info "Old virtual environment removed"
        else
            log_info "Using existing virtual environment"
            return 0
        fi
    fi
    
    python3 -m venv .venv
    log_success "Virtual environment created"
    
    # Activate virtual environment
    source .venv/bin/activate
    log_success "Virtual environment activated"
}

# Install dependencies
install_dependencies() {
    log_step "Installing packages..."
    
    # Upgrade pip
    pip install --upgrade pip
    log_success "pip upgraded"
    
    # Main packages
    log_info "Installing main packages..."
    pip install -r requirements.txt
    log_success "Main packages installed"
    
    # PyTorch CPU version
    log_info "Installing PyTorch CPU version..."
    pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
    log_success "PyTorch installed"
    
    # Gunicorn for production
    log_info "Installing Gunicorn..."
    pip install gunicorn
    log_success "Gunicorn installed"
}

# Train model
train_model() {
    log_step "Training model..."
    
    if [ -f "model/mnist_cnn.pth" ]; then
        log_warning "Model already exists"
        read -p "Do you want to retrain it? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Using existing model"
            return 0
        fi
    fi
    
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

# Ask about Docker
ask_about_docker() {
    echo
    echo -e "${YELLOW}🐳 About Docker:${NC}"
    echo "Docker must be installed to use with Docker."
    echo "Is Docker installed?"
    
    read -p "Is Docker installed? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Docker available"
        
        # Create Docker image
        read -p "Do you want to create Docker image? (Y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            log_step "Creating Docker image..."
            if docker build -t digit-recognizer .; then
                log_success "Docker image created"
            else
                log_error "Error creating Docker image"
            fi
        fi
    else
        log_info "Docker not installed. Will use local environment"
    fi
}

# Development mode
start_development() {
    log_step "Starting in Development mode..."
    log_info "Uvicorn + auto-reload"
    log_success "Application will open at http://localhost:8000"
    log_info "Press Ctrl+C to stop"
    
    export ENVIRONMENT=development
    python main.py
}

# Production mode
start_production() {
    log_step "Starting in Production mode..."
    log_info "Gunicorn + Uvicorn worker"
    
    # Get CPU cores
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
    log_info "Starting Docker container..."
    log_success "Application will open at http://localhost:8000"
    log_info "Press Ctrl+C to stop"
    
    docker run -p 8000:8000 digit-recognizer
}

# Choose run method
choose_run_method() {
    echo
    echo -e "${YELLOW}🚀 Choose run method:${NC}"
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

# Main function
main() {
    echo -e "${CYAN}"
    echo "🎨 Paint Digit Recognizer - Installation"
    echo "========================================"
    echo -e "${NC}"
    
    # 1. Check Python
    check_python
    
    # 2. Create virtual environment
    create_venv
    
    # 3. Install dependencies
    install_dependencies
    
    # 4. Train model
    train_model
    
    # 5. Run tests
    echo
    read -p "Do you want to run tests? (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        run_tests
    fi
    
    # 6. Ask about Docker
    ask_about_docker
    
    # 7. Start application
    choose_run_method
}

# Run script
main "$@" 