/**
 * Paint Digit Recognizer - Main JavaScript
 * 
 * Handles canvas drawing, form submission, and UI interactions
 */

// Canvas drawing variables
let canvas, ctx;
let isDrawing = false;
let lastX = 0;
let lastY = 0;
let isSubmitting = false; // Prevent multiple submissions

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeCanvas();
    setupEventListeners();
});

/**
 * Initialize the canvas for drawing
 */
function initializeCanvas() {
    canvas = document.getElementById('paint');
    if (!canvas) {
        console.error('Canvas element not found');
        return;
    }
    
    ctx = canvas.getContext('2d');
    
    // Set canvas properties for better drawing
    ctx.strokeStyle = '#000000';
    ctx.lineWidth = 25; // Thicker lines for better recognition
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    
    // Set canvas background
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    console.log('Canvas initialized:', {
        width: canvas.width,
        height: canvas.height,
        strokeStyle: ctx.strokeStyle,
        lineWidth: ctx.lineWidth
    });
}

/**
 * Setup all event listeners
 */
function setupEventListeners() {
    // Canvas drawing events
    canvas.addEventListener('mousedown', startDrawing);
    canvas.addEventListener('mousemove', draw);
    canvas.addEventListener('mouseup', stopDrawing);
    canvas.addEventListener('mouseout', stopDrawing);
    
    // Touch events for mobile
    canvas.addEventListener('touchstart', handleTouchStart);
    canvas.addEventListener('touchmove', handleTouchMove);
    canvas.addEventListener('touchend', stopDrawing);
    
    // Button events
    const clearBtn = document.getElementById('clearBtn');
    if (clearBtn) {
        clearBtn.addEventListener('click', clearCanvas);
    }
    
    // Form submission - prevent default and handle manually
    const predictForm = document.getElementById('predictForm');
    if (predictForm) {
        predictForm.addEventListener('submit', handleFormSubmit);
    }
    
    // HTMX events
    document.body.addEventListener('htmx:beforeRequest', handleBeforeRequest);
    document.body.addEventListener('htmx:afterRequest', handleAfterRequest);
    document.body.addEventListener('htmx:responseError', handleResponseError);
}

/**
 * Start drawing on mouse down
 */
function startDrawing(e) {
    isDrawing = true;
    [lastX, lastY] = getMousePos(canvas, e);
    hideCanvasOverlay();
}

/**
 * Draw on mouse move
 */
function draw(e) {
    if (!isDrawing) return;
    
    e.preventDefault();
    
    const [currentX, currentY] = getMousePos(canvas, e);
    
    ctx.beginPath();
    ctx.moveTo(lastX, lastY);
    ctx.lineTo(currentX, currentY);
    ctx.stroke();
    
    [lastX, lastY] = [currentX, currentY];
}

/**
 * Stop drawing
 */
function stopDrawing() {
    isDrawing = false;
}

/**
 * Handle touch start for mobile devices
 */
function handleTouchStart(e) {
    e.preventDefault();
    const touch = e.touches[0];
    const mouseEvent = new MouseEvent('mousedown', {
        clientX: touch.clientX,
        clientY: touch.clientY
    });
    canvas.dispatchEvent(mouseEvent);
}

/**
 * Handle touch move for mobile devices
 */
function handleTouchMove(e) {
    e.preventDefault();
    const touch = e.touches[0];
    const mouseEvent = new MouseEvent('mousemove', {
        clientX: touch.clientX,
        clientY: touch.clientY
    });
    canvas.dispatchEvent(mouseEvent);
}

/**
 * Get mouse position relative to canvas
 */
function getMousePos(canvas, e) {
    const rect = canvas.getBoundingClientRect();
    return [
        e.clientX - rect.left,
        e.clientY - rect.top
    ];
}

/**
 * Clear the canvas
 */
function clearCanvas() {
    if (!ctx) return;
    
    // Clear the canvas
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Show overlay
    showCanvasOverlay();
    
    // Clear any existing results
    const resultSection = document.getElementById('result');
    if (resultSection) {
        resultSection.innerHTML = '';
    }
    
    // Reset form
    const imageInput = document.getElementById('imageInput');
    if (imageInput) {
        imageInput.value = '';
    }
    
    // Reset submission state
    isSubmitting = false;
}

/**
 * Show canvas overlay
 */
function showCanvasOverlay() {
    const overlay = document.getElementById('canvasOverlay');
    if (overlay) {
        overlay.classList.remove('hidden');
    }
}

/**
 * Hide canvas overlay
 */
function hideCanvasOverlay() {
    const overlay = document.getElementById('canvasOverlay');
    if (overlay) {
        overlay.classList.add('hidden');
    }
}

/**
 * Handle form submission
 */
function handleFormSubmit(e) {
    // Always prevent default form submission
    e.preventDefault();
    
    // Prevent multiple submissions
    if (isSubmitting) {
        console.log('Form submission already in progress');
        return;
    }
    
    console.log('Form submission started');
    
    // Check if canvas has any drawing
    const hasDrawingResult = hasDrawing();
    console.log('Has drawing:', hasDrawingResult);
    
    if (!hasDrawingResult) {
        alert('Please draw a digit first! Make sure to draw clearly in the center of the canvas.');
        return;
    }
    
    // Set submission flag
    isSubmitting = true;
    
    // Get canvas data and set form input
    const imageData = canvas.toDataURL('image/png', 1.0); // High quality
    console.log('Image data length:', imageData.length);
    console.log('Image data preview:', imageData.substring(0, 100));
    
    const imageInput = document.getElementById('imageInput');
    if (imageInput) {
        imageInput.value = imageData;
        console.log('Image data set to form input');
        console.log('Form input value length:', imageInput.value.length);
        
        // Manually trigger HTMX submission
        const form = document.getElementById('predictForm');
        if (form) {
            // Use HTMX's trigger method to submit the form
            htmx.trigger(form, 'submit');
        }
    } else {
        console.error('Image input not found!');
        isSubmitting = false;
    }
}

/**
 * Check if canvas has any drawing
 */
function hasDrawing() {
    if (!ctx) return false;
    
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const data = imageData.data;
    
    // Check if any pixel is not white (has drawing)
    // We check for black pixels (RGB values close to 0)
    let blackPixelCount = 0;
    let totalPixels = data.length / 4;
    
    for (let i = 0; i < data.length; i += 4) {
        const r = data[i];
        const g = data[i + 1];
        const b = data[i + 2];
        
        // Check if pixel is significantly darker than white (black drawing)
        if (r < 150 || g < 150 || b < 150) { // More strict threshold
            blackPixelCount++;
        }
    }
    
    // Calculate percentage of black pixels
    const blackPixelPercentage = (blackPixelCount / totalPixels) * 100;
    console.log('Canvas analysis:', {
        blackPixels: blackPixelCount,
        totalPixels: totalPixels,
        percentage: blackPixelPercentage.toFixed(2) + '%'
    });
    
    // Need at least 0.5% of pixels to be black (about 400 pixels on 280x280 canvas)
    const hasDrawing = blackPixelPercentage > 0.5;
    console.log('Canvas has drawing:', hasDrawing);
    return hasDrawing;
}

/**
 * Handle HTMX before request
 */
function handleBeforeRequest(event) {
    // Show loading indicator
    const loadingIndicator = document.getElementById('loadingIndicator');
    if (loadingIndicator) {
        loadingIndicator.style.display = 'flex';
    }
    
    // Disable predict button
    const predictBtn = document.getElementById('predictBtn');
    if (predictBtn) {
        predictBtn.disabled = true;
        predictBtn.textContent = 'Analyzing...';
    }
}

/**
 * Handle HTMX after request
 */
function handleAfterRequest(event) {
    // Reset submission flag
    isSubmitting = false;
    
    // Hide loading indicator
    const loadingIndicator = document.getElementById('loadingIndicator');
    if (loadingIndicator) {
        loadingIndicator.style.display = 'none';
    }
    
    // Re-enable predict button
    const predictBtn = document.getElementById('predictBtn');
    if (predictBtn) {
        predictBtn.disabled = false;
        predictBtn.innerHTML = '<span class="btn-icon">🔮</span>Predict';
    }
    
    // Scroll to results if they exist
    const resultSection = document.getElementById('result');
    if (resultSection && resultSection.innerHTML.trim()) {
        resultSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

/**
 * Handle HTMX response error
 */
function handleResponseError(event) {
    console.error('HTMX request failed:', event.detail);
    
    // Reset submission flag
    isSubmitting = false;
    
    // Show error message
    const resultSection = document.getElementById('result');
    if (resultSection) {
        resultSection.innerHTML = `
            <div class="prediction-error">
                <div class="error-header">
                    <h3>❌ Error</h3>
                </div>
                <div class="error-content">
                    <div class="error-icon">⚠️</div>
                    <p class="error-message">Request failed. Please try again.</p>
                </div>
                <div class="error-actions">
                    <button onclick="clearCanvas()" class="btn btn-outline">Try Again</button>
                </div>
            </div>
        `;
    }
}

/**
 * Utility function to check if element is visible
 */
function isElementVisible(element) {
    if (!element) return false;
    
    const rect = element.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

/**
 * Add smooth scrolling to all internal links
 */
document.addEventListener('click', function(e) {
    if (e.target.tagName === 'A' && e.target.getAttribute('href').startsWith('#')) {
        e.preventDefault();
        const target = document.querySelector(e.target.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth' });
        }
    }
});

// Export functions for global access
window.clearCanvas = clearCanvas;
window.showCanvasOverlay = showCanvasOverlay;
window.hideCanvasOverlay = hideCanvasOverlay; 