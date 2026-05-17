// CyberCloak - Main JavaScript with God-like Animations

// Simple Theme Management
function initializeTheme() {
    // Load saved theme
    const savedTheme = localStorage.getItem('cybercloak-theme') || 'default';
    applyTheme(savedTheme);

    // Handle theme button clicks
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('theme-btn')) {
            e.preventDefault();
            const theme = e.target.getAttribute('data-theme');
            applyTheme(theme);
            localStorage.setItem('cybercloak-theme', theme);
        }
    });
}

function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
}

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


// Scroll Animations
function initializeScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.classList.add('animated');
                }, index * 100);
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    document.querySelectorAll('.floating-card, .workflow-step, .stat-item').forEach(el => {
        el.classList.add('animate-on-scroll');
        observer.observe(el);
    });
}

// Counter Animation
function initializeCounters() {
    const counterObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounter(entry.target);
                counterObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });
    
    document.querySelectorAll('.stat-number').forEach(counter => {
        counterObserver.observe(counter);
    });
}

function animateCounter(element) {
    const target = parseFloat(element.getAttribute('data-count'));
    const duration = 2000;
    const increment = target / (duration / 16);
    let current = 0;
    
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }
        
        if (target >= 1000) {
            element.textContent = Math.floor(current).toLocaleString();
        } else {
            element.textContent = current.toFixed(1);
        }
    }, 16);
}

// Particle System
function initializeParticles() {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    canvas.style.position = 'fixed';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    canvas.style.pointerEvents = 'none';
    canvas.style.zIndex = '1';
    canvas.style.opacity = '0.3';
    document.body.appendChild(canvas);
    
    let particles = [];
    let animationId;
    
    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    
    function createParticle() {
        return {
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            vx: (Math.random() - 0.5) * 0.5,
            vy: (Math.random() - 0.5) * 0.5,
            size: Math.random() * 2 + 1,
            opacity: Math.random() * 0.5 + 0.2,
            color: `hsl(${Math.random() * 60 + 240}, 70%, 60%)`
        };
    }
    
    function initParticles() {
        particles = [];
        for (let i = 0; i < 50; i++) {
            particles.push(createParticle());
        }
    }
    
    function updateParticles() {
        particles.forEach(particle => {
            particle.x += particle.vx;
            particle.y += particle.vy;
            
            if (particle.x < 0 || particle.x > canvas.width) particle.vx *= -1;
            if (particle.y < 0 || particle.y > canvas.height) particle.vy *= -1;
        });
    }
    
    function drawParticles() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        particles.forEach(particle => {
            ctx.beginPath();
            ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
            ctx.fillStyle = particle.color;
            ctx.globalAlpha = particle.opacity;
            ctx.fill();
        });
        
        // Draw connections
        particles.forEach((particle, i) => {
            particles.slice(i + 1).forEach(otherParticle => {
                const dx = particle.x - otherParticle.x;
                const dy = particle.y - otherParticle.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance < 100) {
                    ctx.beginPath();
                    ctx.moveTo(particle.x, particle.y);
                    ctx.lineTo(otherParticle.x, otherParticle.y);
                    ctx.strokeStyle = 'rgba(102, 126, 234, 0.2)';
                    ctx.globalAlpha = (100 - distance) / 100 * 0.5;
                    ctx.lineWidth = 1;
                    ctx.stroke();
                }
            });
        });
    }
    
    function animate() {
        updateParticles();
        drawParticles();
        animationId = requestAnimationFrame(animate);
    }
    
    resizeCanvas();
    initParticles();
    animate();
    
    window.addEventListener('resize', () => {
        resizeCanvas();
        initParticles();
    });
    
    // Pause animation when page is not visible
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            cancelAnimationFrame(animationId);
        } else {
            animate();
        }
    });
}

// Drag and Drop functionality
function initializeDragAndDrop() {
    document.querySelectorAll('.upload-zone').forEach(zone => {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            zone.addEventListener(eventName, preventDefaults, false);
        });
        
        ['dragenter', 'dragover'].forEach(eventName => {
            zone.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            zone.addEventListener(eventName, unhighlight, false);
        });
        
        zone.addEventListener('drop', handleDrop, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    function highlight(e) {
        e.currentTarget.classList.add('drag-over');
    }
    
    function unhighlight(e) {
        e.currentTarget.classList.remove('drag-over');
    }
    
    function handleDrop(e) {
        const files = e.dataTransfer.files;
        const input = e.currentTarget.querySelector('input[type="file"]') || 
                     document.querySelector('input[type="file"]');
        
        if (files.length > 0 && input) {
            input.files = files;
            input.dispatchEvent(new Event('change'));
        }
    }
}

// Form enhancements
function initializeForms() {
    // Enhance all forms with smooth validation
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', handleFormSubmit);
    });
    
    // Add real-time validation
    document.querySelectorAll('input, textarea, select').forEach(field => {
        field.addEventListener('blur', validateField);
        field.addEventListener('input', clearFieldError);
    });
}

function handleFormSubmit(e) {
    const form = e.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    
    if (submitBtn) {
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<div class="spinner-border spinner-border-sm me-2"></div>Sending...';
        submitBtn.disabled = true;
        
        // Re-enable after 3 seconds if no redirect
        setTimeout(() => {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }, 3000);
    }
}

function validateField(e) {
    const field = e.target;
    const value = field.value.trim();
    const type = field.type;
    
    clearFieldError(e);
    
    if (field.required && !value) {
        showFieldError(field, 'This field is required');
        return false;
    }
    
    if (type === 'email' && value && !isValidEmail(value)) {
        showFieldError(field, 'Please enter a valid email address');
        return false;
    }
    
    if (type === 'password' && value && value.length < 6) {
        showFieldError(field, 'Password must be at least 6 characters');
        return false;
    }
    
    return true;
}

function clearFieldError(e) {
    const field = e.target;
    const errorDiv = field.parentNode.querySelector('.field-error');
    if (errorDiv) {
        errorDiv.remove();
    }
    field.classList.remove('is-invalid');
}

function showFieldError(field, message) {
    field.classList.add('is-invalid');
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.textContent = message;
    field.parentNode.appendChild(errorDiv);
}

function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

// Animation system
function initializeAnimations() {
    // Stagger animations for cards
    document.querySelectorAll('.floating-card').forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
    });
    
    // Add hover effects
    document.querySelectorAll('.glow-btn').forEach(btn => {
        btn.addEventListener('mouseenter', () => {
            btn.style.transform = 'translateY(-3px) scale(1.05)';
        });
        
        btn.addEventListener('mouseleave', () => {
            btn.style.transform = 'translateY(0) scale(1)';
        });
    });
}

// Notification system
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <div class="notification-icon">${getNotificationIcon(type)}</div>
            <div class="notification-message">${message}</div>
            <button class="notification-close">&times;</button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        notification.remove();
    }, 5000);
    
    // Remove on click
    notification.querySelector('.notification-close').addEventListener('click', () => {
        notification.remove();
    });
}

function getNotificationIcon(type) {
    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };
    return icons[type] || icons.info;
}

// Utility functions
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

// API call wrapper
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
    makeAPICall,
    initializeCounters,
    animateCounter,
    applyTheme
};