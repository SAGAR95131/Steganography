// CyberCloak - Main JavaScript with God-like Animations

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all systems
    initializeTheme();
    initializeDragAndDrop();
    initializeForms();
    initializeAnimations();
    initializeScrollAnimations();
    initializeParticles();
    initializeCounters();
    
    // Add loading screen fade out
    setTimeout(() => {
        document.body.classList.add('loaded');
    }, 500);
});

// Theme Management
function initializeTheme() {
    // Load saved theme or default
    const savedTheme = localStorage.getItem('cybercloak-theme') || 'default';
    applyTheme(savedTheme);
    
    // Theme switcher buttons
    document.querySelectorAll('.theme-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const theme = this.getAttribute('data-theme');
            applyTheme(theme);
            localStorage.setItem('cybercloak-theme', theme);
            
            // Visual feedback
            showNotification(`Theme changed to ${theme}`, 'success');
        });
    });
}

function applyTheme(theme) {
    document.body.setAttribute('data-theme', theme);
    
    // Update active state in dropdown
    document.querySelectorAll('.theme-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.getAttribute('data-theme') === theme) {
            btn.classList.add('active');
        }
    });
}

// Drag and Drop File Upload
function initializeDragAndDrop() {
    const uploadAreas = document.querySelectorAll('.upload-area');
    
    uploadAreas.forEach(area => {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            area.addEventListener(eventName, preventDefaults, false);
        });
        
        ['dragenter', 'dragover'].forEach(eventName => {
            area.addEventListener(eventName, () => area.classList.add('dragover'), false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            area.addEventListener(eventName, () => area.classList.remove('dragover'), false);
        });
        
        area.addEventListener('drop', handleDrop, false);
        area.addEventListener('click', () => {
            const fileInput = area.querySelector('input[type="file"]') || 
                            document.getElementById('inputImage');
            if (fileInput) fileInput.click();
        });
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            const fileInput = e.target.querySelector('input[type="file"]') || 
                            document.getElementById('inputImage');
            if (fileInput) {
                fileInput.files = files;
                fileInput.dispatchEvent(new Event('change'));
            }
        }
    }
}

// Form Enhancements
function initializeForms() {
    // Auto-resize textareas
    document.querySelectorAll('textarea').forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    });
    
    // Form validation feedback
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
                showNotification('Please fill in all required fields', 'error');
            }
            form.classList.add('was-validated');
        });
    });
    
    // Password strength indicator
    const passwordInputs = document.querySelectorAll('input[type="password"]');
    passwordInputs.forEach(input => {
        if (input.id === 'encryptionPassword') {
            input.addEventListener('input', updatePasswordStrength);
        }
    });
}

function updatePasswordStrength(e) {
    const password = e.target.value;
    const strength = calculatePasswordStrength(password);
    
    // Remove existing strength indicator
    const existingIndicator = e.target.parentNode.querySelector('.password-strength');
    if (existingIndicator) {
        existingIndicator.remove();
    }
    
    if (password.length > 0) {
        const indicator = document.createElement('div');
        indicator.className = 'password-strength mt-1';
        indicator.innerHTML = `
            <div class="progress" style="height: 6px;">
                <div class="progress-bar bg-${strength.color}" 
                     style="width: ${strength.percentage}%"></div>
            </div>
            <small class="text-${strength.color}">${strength.text}</small>
        `;
        e.target.parentNode.appendChild(indicator);
    }
}

function calculatePasswordStrength(password) {
    let score = 0;
    
    if (password.length >= 8) score += 25;
    if (password.match(/[a-z]/)) score += 25;
    if (password.match(/[A-Z]/)) score += 25;
    if (password.match(/[0-9]/)) score += 15;
    if (password.match(/[^a-zA-Z0-9]/)) score += 10;
    
    if (score < 30) return { color: 'danger', text: 'Weak', percentage: 25 };
    if (score < 60) return { color: 'warning', text: 'Fair', percentage: 50 };
    if (score < 90) return { color: 'info', text: 'Good', percentage: 75 };
    return { color: 'success', text: 'Strong', percentage: 100 };
}

// Animations
function initializeAnimations() {
    // Intersection Observer for fade-in animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    document.querySelectorAll('.feature-card, .step-card, .stat-card').forEach(el => {
        observer.observe(el);
    });
    
    // Add hover effects
    document.querySelectorAll('.btn').forEach(btn => {
        btn.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        btn.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
}

// Notification System
function showNotification(message, type = 'info', duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = `
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    `;
    
    const iconMap = {
        success: 'check-circle',
        error: 'exclamation-triangle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    
    notification.innerHTML = `
        <i class="fas fa-${iconMap[type]} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, duration);
}

// Utility Functions
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatDate(date) {
    return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copied to clipboard!', 'success');
    }).catch(() => {
        showNotification('Failed to copy to clipboard', 'error');
    });
}

// Loading States
function showLoading(element, text = 'Loading...') {
    element.classList.add('loading');
    element.disabled = true;
    element.dataset.originalText = element.innerHTML;
    element.innerHTML = `
        <span class="spinner-border spinner-border-sm me-2" role="status"></span>
        ${text}
    `;
}

function hideLoading(element) {
    element.classList.remove('loading');
    element.disabled = false;
    if (element.dataset.originalText) {
        element.innerHTML = element.dataset.originalText;
        delete element.dataset.originalText;
    }
}

// Image Preview
function previewImage(input, previewElement) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            previewElement.src = e.target.result;
            previewElement.style.display = 'block';
        };
        reader.readAsDataURL(input.files[0]);
    }
}

// Progress Bar
function updateProgress(percentage, element) {
    if (element) {
        element.style.width = percentage + '%';
        element.setAttribute('aria-valuenow', percentage);
        element.textContent = Math.round(percentage) + '%';
    }
}

// File Validation
function validateImageFile(file) {
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/bmp', 'image/webp'];
    const maxSize = 16 * 1024 * 1024; // 16MB
    
    if (!allowedTypes.includes(file.type)) {
        throw new Error('Please select a valid image file (JPEG, PNG, GIF, BMP, WebP)');
    }
    
    if (file.size > maxSize) {
        throw new Error('File size must be less than 16MB');
    }
    
    return true;
}

// API Helper Functions
async function makeAPICall(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

// Export for global access
window.CyberCloak = {
    showNotification,
    formatFileSize,
    formatDate,
    copyToClipboard,
    showLoading,
    hideLoading,
    previewImage,
    updateProgress,
    validateImageFile,
    makeAPICall
};