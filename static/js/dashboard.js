// Navigation functionality
function switchToSection(sectionName) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });

    // Show selected section
    const targetSection = document.getElementById(sectionName + '-section');
    if (targetSection) {
        targetSection.classList.add('active');
    }

    // Update navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });

    const activeNav = document.querySelector(`[data-section="${sectionName}"]`);
    if (activeNav) {
        activeNav.classList.add('active');
    }
}

// Sidebar toggle
function toggleSidebar() {
    const sidebar = document.getElementById('dashboard-sidebar');
    const main = document.getElementById('dashboard-main');

    if (sidebar && main) {
        sidebar.classList.toggle('sidebar-collapsed');
        main.classList.toggle('sidebar-collapsed');
    }
}

// File upload preview for encryption
document.getElementById('inputImage').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('previewImg').src = e.target.result;
            document.getElementById('imagePreview').style.display = 'block';
            document.getElementById('imageUploadZone').style.display = 'none';
        };
        reader.readAsDataURL(file);
    }
});

// File upload preview for decryption
document.getElementById('encryptedImage').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('encryptedPreviewImg').src = e.target.result;
            document.getElementById('encryptedImagePreview').style.display = 'block';
            document.getElementById('encryptedImageUploadZone').style.display = 'none';
        };
        reader.readAsDataURL(file);
    }
});

// Drag and drop for encryption
const imageUploadZone = document.getElementById('imageUploadZone');
imageUploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    imageUploadZone.classList.add('dragover');
});

imageUploadZone.addEventListener('dragleave', () => {
    imageUploadZone.classList.remove('dragover');
});

imageUploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    imageUploadZone.classList.remove('dragover');

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        document.getElementById('inputImage').files = files;
        document.getElementById('inputImage').dispatchEvent(new Event('change'));
    }
});

// Drag and drop for decryption
const encryptedImageUploadZone = document.getElementById('encryptedImageUploadZone');
encryptedImageUploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    encryptedImageUploadZone.classList.add('dragover');
});

encryptedImageUploadZone.addEventListener('dragleave', () => {
    encryptedImageUploadZone.classList.remove('dragover');
});

encryptedImageUploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    encryptedImageUploadZone.classList.remove('dragover');

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        document.getElementById('encryptedImage').files = files;
        document.getElementById('encryptedImage').dispatchEvent(new Event('change'));
    }
});

// AI Message Generation
async function generateAIMessage() {
    const prompt = document.getElementById('aiPrompt').value.trim();
    const context = document.getElementById('aiContext').value.trim();
    const maxLength = document.getElementById('aiMaxLength').value;
    const generateBtn = document.getElementById('aiGenerateBtn');
    const resultDiv = document.getElementById('aiResult');

    if (!prompt) {
        alert('Please enter a prompt');
        return;
    }

    // Show loading
    generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Generating...';
    generateBtn.disabled = true;

    try {
        const response = await fetch('/api/ai/generate-message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                prompt: prompt,
                context: context,
                max_length: maxLength
            })
        });

        const data = await response.json();

        if (data.success) {
            resultDiv.innerHTML = `
                <div style="text-align: left; padding: 2rem;">
                    <div style="background: var(--bg-glass); border-radius: var(--border-radius); padding: 1.5rem; margin-bottom: 1rem;">
                        <h5 style="color: var(--text-primary); margin-bottom: 1rem;">Generated Message:</h5>
                        <p style="color: var(--text-secondary); font-size: 1.1rem; line-height: 1.6;">${data.message}</p>
                    </div>
                    <div style="font-size: 0.875rem; color: var(--text-muted);">
                        <i class="fas fa-info-circle me-1"></i>
                        Tokens used: ${data.usage.prompt_tokens} prompt + ${data.usage.completion_tokens} completion = ${data.usage.total_tokens} total
                    </div>
                </div>
            `;
            document.getElementById('aiActions').style.display = 'block';
        } else {
            resultDiv.innerHTML = `
                <div style="text-align: center; padding: 2rem;">
                    <div style="font-size: 3rem; color: var(--error); margin-bottom: 1rem;">
                        <i class="fas fa-exclamation-triangle"></i>
                    </div>
                    <h5 style="color: var(--text-primary); margin-bottom: 1rem;">Generation Failed</h5>
                    <p style="color: var(--text-secondary);">${data.error || 'Unknown error occurred'}</p>
                </div>
            `;
        }
    } catch (error) {
        resultDiv.innerHTML = `
            <div style="text-align: center; padding: 2rem;">
                <div style="font-size: 3rem; color: var(--error); margin-bottom: 1rem;">
                    <i class="fas fa-exclamation-triangle"></i>
                </div>
                <h5 style="color: var(--text-primary); margin-bottom: 1rem;">Network Error</h5>
                <p style="color: var(--text-secondary);">Failed to connect to AI service</p>
            </div>
        `;
    } finally {
        generateBtn.innerHTML = '<i class="fas fa-magic me-2"></i>Generate Message';
        generateBtn.disabled = false;
    }
}

function useGeneratedMessage() {
    const messageElement = document.querySelector('#aiResult p');
    if (messageElement) {
        // Copy to encryption message field
        document.getElementById('secretMessage').value = messageElement.textContent;
        switchToSection('encrypt');
        alert('Message copied to encryption form!');
    }
}

function regenerateMessage() {
    generateAIMessage();
}

// Encryption functionality
async function processEncryption() {
    const imageInput = document.getElementById('inputImage');
    const messageInput = document.getElementById('secretMessage');
    const passwordInput = document.getElementById('encryptPassword');
    const encryptBtn = document.getElementById('encryptBtn');
    const resultsDiv = document.getElementById('encryptResults');

    if (!imageInput.files[0]) {
        alert('Please select an image first');
        return;
    }

    if (!messageInput.value.trim()) {
        alert('Please enter a secret message');
        return;
    }

    // Show loading
    encryptBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Encrypting...';
    encryptBtn.disabled = true;

    try {
        const formData = new FormData();
        formData.append('image', imageInput.files[0]);
        formData.append('message', messageInput.value.trim());
        if (passwordInput.value) {
            formData.append('password', passwordInput.value);
        }

        const response = await fetch('/encrypt', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            resultsDiv.innerHTML = `
                <div style="text-align: center;">
                    <div style="font-size: 3rem; color: var(--success); margin-bottom: 1rem;">
                        <i class="fas fa-check-circle"></i>
                    </div>
                    <h5 style="color: var(--text-primary); margin-bottom: 1rem;">Encryption Successful!</h5>
                    <p style="color: var(--text-secondary); margin-bottom: 2rem;">Your message has been securely hidden in the image.</p>
                    <div style="background: var(--bg-secondary); border-radius: var(--border-radius); padding: 1rem; margin-bottom: 1rem;">
                        <img src="${data.image_data}" style="max-width: 200px; max-height: 200px; border-radius: 8px; box-shadow: var(--shadow-md);" alt="Encrypted Image">
                    </div>
                    <p style="font-size: 0.9rem; color: var(--text-muted);">Job ID: ${data.job_id}</p>
                </div>
            `;
            document.getElementById('encryptActions').style.display = 'block';
        } else {
            resultsDiv.innerHTML = `
                <div style="text-align: center;">
                    <div style="font-size: 3rem; color: var(--error); margin-bottom: 1rem;">
                        <i class="fas fa-exclamation-triangle"></i>
                    </div>
                    <h5 style="color: var(--text-primary); margin-bottom: 1rem;">Encryption Failed</h5>
                    <p style="color: var(--text-secondary);">${data.error || 'Unknown error occurred'}</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error:', error);
        resultsDiv.innerHTML = `
            <div style="text-align: center;">
                <div style="font-size: 3rem; color: var(--error); margin-bottom: 1rem;">
                    <i class="fas fa-exclamation-triangle"></i>
                </div>
                <h5 style="color: var(--text-primary); margin-bottom: 1rem;">Network Error</h5>
                <p style="color: var(--text-secondary);">Failed to connect to encryption service</p>
            </div>
        `;
    } finally {
        encryptBtn.innerHTML = '<i class="fas fa-magic me-2"></i>Encrypt & Hide Message';
        encryptBtn.disabled = false;
    }
}

// Store the download URL from the encryption response
let currentDownloadUrl = null;

function downloadEncrypted() {
    if (currentDownloadUrl) {
        // Create a temporary link element
        const link = document.createElement('a');
        link.href = currentDownloadUrl;
        link.download = 'encrypted_image.png';

        // Append to body, click, and remove
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        showNotification('Encrypted image downloaded successfully!', 'success');
    } else {
        // Fallback: try to get from displayed image
        const resultsDiv = document.getElementById('encryptResults');
        const imgElement = resultsDiv.querySelector('img');

        if (imgElement && imgElement.src) {
            const link = document.createElement('a');
            link.href = imgElement.src;
            link.download = 'encrypted_image.png';

            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            showNotification('Encrypted image downloaded successfully!', 'success');
        } else {
            showNotification('No encrypted image available for download', 'error');
        }
    }
}

function resetEncryption() {
    document.getElementById('inputImage').value = '';
    document.getElementById('secretMessage').value = '';
    document.getElementById('encryptPassword').value = '';
    document.getElementById('imagePreview').style.display = 'none';
    document.getElementById('imageUploadZone').style.display = 'block';
    document.getElementById('encryptResults').innerHTML = `
        <div style="text-align: center;">
            <div style="font-size: 3rem; color: var(--text-muted); margin-bottom: 1rem; opacity: 0.5;">
                <i class="fas fa-chart-line"></i>
            </div>
            <h5 style="color: var(--text-primary); margin-bottom: 1rem;">Ready for Analysis</h5>
            <p style="color: var(--text-secondary); text-align: center;">Upload an image and enter a message to see security analysis and capacity information.</p>
        </div>
    `;
    document.getElementById('encryptActions').style.display = 'none';
}

// Decryption functionality
async function processDecryption() {
    const imageInput = document.getElementById('encryptedImage');
    const passwordInput = document.getElementById('decryptPassword');
    const decryptBtn = document.getElementById('decryptBtn');
    const resultsDiv = document.getElementById('decryptResults');

    if (!imageInput.files[0]) {
        alert('Please select an encrypted image first');
        return;
    }

    // Check if password is required but not provided
    const hasPassword = passwordInput.value.trim();
    if (!hasPassword) {
        // Show a warning but don't block - let the backend handle it
        if (!confirm('No password entered. If the message was encrypted, you may see encrypted data. Continue?')) {
            return;
        }
    }

    // Show loading
    decryptBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Extracting...';
    decryptBtn.disabled = true;

    try {
        const formData = new FormData();
        formData.append('encrypted_image', imageInput.files[0]);
        if (passwordInput.value.trim()) {
            formData.append('decrypt_password', passwordInput.value.trim());
        }

        const response = await fetch('/api/extract_decrypt', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            // Check if the message looks like encrypted data (base64 blob)
            const isEncryptedBlob = data.message && data.message.length > 100 && !data.message.includes(' ') && /^[A-Za-z0-9+/=]+$/.test(data.message.replace(/[^A-Za-z0-9+/=]/g, ''));

            if (isEncryptedBlob && !data.was_encrypted) {
                // This looks like encrypted data but no password was provided
                resultsDiv.innerHTML = `
                    <div style="text-align: center;">
                        <div style="font-size: 3rem; color: var(--warning); margin-bottom: 1rem;">
                            <i class="fas fa-key"></i>
                        </div>
                        <h5 style="color: var(--text-primary); margin-bottom: 1rem;">Password Required</h5>
                        <p style="color: var(--text-secondary); margin-bottom: 1rem;">This message appears to be encrypted. Please enter the password used during encryption.</p>
                        <div style="background: var(--bg-secondary); border-radius: var(--border-radius); padding: 1rem; margin-bottom: 1rem;">
                            <small style="color: var(--text-muted);">Encrypted data detected: ${data.message.substring(0, 50)}...</small>
                        </div>
                        <button onclick="retryDecryption()" class="btn btn-primary">
                            <i class="fas fa-redo me-2"></i>Try Again with Password
                        </button>
                    </div>
                `;
            } else {
                // Normal successful decryption
                resultsDiv.innerHTML = `
                    <div style="text-align: center;">
                        <div style="font-size: 3rem; color: var(--success); margin-bottom: 1rem;">
                            <i class="fas fa-unlock"></i>
                        </div>
                        <h5 style="color: var(--text-primary); margin-bottom: 1rem;">Message Extracted!</h5>
                        <div style="background: var(--bg-secondary); border-radius: var(--border-radius); padding: 1.5rem; margin-bottom: 1rem; text-align: left;">
                            <h6 style="color: var(--text-primary); margin-bottom: 0.5rem;">Hidden Message:</h6>
                            <p style="color: var(--text-secondary); font-size: 1.1rem; line-height: 1.6; word-wrap: break-word;">${data.message}</p>
                        </div>
                        ${data.was_encrypted ? '<p style="font-size: 0.9rem; color: var(--success);"><i class="fas fa-shield-alt me-1"></i>Message was password-protected</p>' : '<p style="font-size: 0.9rem; color: var(--text-muted);"><i class="fas fa-info-circle me-1"></i>No password protection used</p>'}
                    </div>
                `;
                document.getElementById('decryptActions').style.display = 'block';
            }
        } else {
            resultsDiv.innerHTML = `
                <div style="text-align: center;">
                    <div style="font-size: 3rem; color: var(--warning); margin-bottom: 1rem;">
                        <i class="fas fa-exclamation-triangle"></i>
                    </div>
                    <h5 style="color: var(--text-primary); margin-bottom: 1rem;">No Hidden Message Found</h5>
                    <p style="color: var(--text-secondary);">${data.error || 'This image does not contain any hidden messages'}</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error:', error);
        resultsDiv.innerHTML = `
            <div style="text-align: center;">
                <div style="font-size: 3rem; color: var(--error); margin-bottom: 1rem;">
                    <i class="fas fa-exclamation-triangle"></i>
                </div>
                <h5 style="color: var(--text-primary); margin-bottom: 1rem;">Network Error</h5>
                <p style="color: var(--text-secondary);">Failed to connect to decryption service</p>
            </div>
        `;
    } finally {
        decryptBtn.innerHTML = '<i class="fas fa-search me-2"></i>Extract Message';
        decryptBtn.disabled = false;
    }
}

function copyMessage() {
    const messageElement = document.querySelector('#decryptResults p');
    if (messageElement) {
        navigator.clipboard.writeText(messageElement.textContent).then(() => {
            alert('Message copied to clipboard!');
        }).catch(() => {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = messageElement.textContent;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            alert('Message copied to clipboard!');
        });
    }
}

function resetDecryption() {
    document.getElementById('encryptedImage').value = '';
    document.getElementById('decryptPassword').value = '';
    document.getElementById('encryptedImagePreview').style.display = 'none';
    document.getElementById('encryptedImageUploadZone').style.display = 'block';
    document.getElementById('decryptResults').innerHTML = `
        <div style="text-align: center;">
            <div style="font-size: 3rem; color: var(--text-muted); margin-bottom: 1rem; opacity: 0.5;">
                <i class="fas fa-message"></i>
            </div>
            <h5 style="color: var(--text-primary); margin-bottom: 1rem;">Ready for Extraction</h5>
            <p style="color: var(--text-secondary); text-align: center;">Upload an encrypted image to reveal any hidden messages.</p>
        </div>
    `;
    document.getElementById('decryptActions').style.display = 'none';
}

function retryDecryption() {
    // Focus on the password field to prompt user to enter password
    const passwordInput = document.getElementById('decryptPassword');
    passwordInput.focus();
    passwordInput.scrollIntoView({ behavior: 'smooth' });

    // Add a visual indicator
    passwordInput.style.borderColor = 'var(--primary)';
    passwordInput.style.boxShadow = '0 0 0 2px rgba(102, 126, 234, 0.2)';

    // Remove the indicator after 3 seconds
    setTimeout(() => {
        passwordInput.style.borderColor = '';
        passwordInput.style.boxShadow = '';
    }, 3000);

    showNotification('Please enter the password used to encrypt this message', 'info');
}

// Combined initialization function
function initializeDashboard() {
    // Add click handlers to nav items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const section = this.getAttribute('data-section');
            switchToSection(section);

            // Initialize analytics when switching to analytics section
            if (section === 'analytics') {
                initializeAnalyticsSection();
            }
        });
    });

    // Initialize tooltips
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });

    // Initialize animations on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, observerOptions);

    // Observe elements for animation
    document.querySelectorAll('.animate-on-scroll').forEach(element => {
        observer.observe(element);
    });

    // Initialize search functionality
    const searchInput = document.getElementById('fileSearch');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            // Debounce search
            clearTimeout(this.searchTimeout);
            this.searchTimeout = setTimeout(() => {
                searchFiles();
            }, 300);
        });
    }

    // Initialize filter functionality
    const fileTypeFilter = document.getElementById('fileTypeFilter');
    const fileDateFilter = document.getElementById('fileDateFilter');

    if (fileTypeFilter) {
        fileTypeFilter.addEventListener('change', searchFiles);
    }

    if (fileDateFilter) {
        fileDateFilter.addEventListener('change', searchFiles);
    }
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
});

// Tooltip functionality
function showTooltip(e) {
    const tooltip = e.target.getAttribute('data-tooltip');
    if (!tooltip) return;

    // Remove existing tooltips
    document.querySelectorAll('.tooltip').forEach(t => t.remove());

    const tooltipElement = document.createElement('div');
    tooltipElement.className = 'tooltip';
    tooltipElement.textContent = tooltip;
    tooltipElement.style.cssText = `
        position: absolute;
        background: var(--bg-card);
        color: var(--text-primary);
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 0.875rem;
        box-shadow: var(--shadow-lg);
        border: 1px solid var(--border-color);
        z-index: 1000;
        pointer-events: none;
        white-space: nowrap;
        top: ${e.target.offsetTop - 40}px;
        left: ${e.target.offsetLeft + (e.target.offsetWidth / 2)}px;
        transform: translateX(-50%);
        opacity: 0;
        transition: opacity 0.2s ease;
    `;

    document.body.appendChild(tooltipElement);

    // Position tooltip
    const rect = tooltipElement.getBoundingClientRect();
    if (rect.left < 10) {
        tooltipElement.style.left = '10px';
        tooltipElement.style.transform = 'none';
    }
    if (rect.right > window.innerWidth - 10) {
        tooltipElement.style.left = `${window.innerWidth - rect.width - 10}px`;
        tooltipElement.style.transform = 'none';
    }

    // Show tooltip
    setTimeout(() => {
        tooltipElement.style.opacity = '1';
    }, 10);
}

function hideTooltip() {
    const tooltips = document.querySelectorAll('.tooltip');
    tooltips.forEach(tooltip => {
        tooltip.style.opacity = '0';
        setTimeout(() => tooltip.remove(), 200);
    });
}

// Utility functions
function showNotification(message, type = 'info') {
    // Remove existing notifications
    document.querySelectorAll('.notification').forEach(n => n.remove());

    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-triangle' : type === 'warning' ? 'exclamation-triangle' : 'info-circle'} notification-icon"></i>
            <div class="notification-message">${message}</div>
            <button class="notification-close" onclick="this.parentElement.parentElement.remove()">&times;</button>
        </div>
    `;

    document.body.appendChild(notification);

    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

// Loading state management
function setLoading(element, loading = true) {
    if (loading) {
        element.disabled = true;
        element.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Loading...';
    } else {
        element.disabled = false;
        // Restore original content (this would need to be enhanced for production)
        element.innerHTML = element.getAttribute('data-original-content') || element.innerHTML;
    }
}

// Form validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    const inputs = form.querySelectorAll('input[required], textarea[required]');
    let isValid = true;

    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });

    return isValid;
}

// File size formatting
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Image validation
function validateImage(file) {
    const maxSize = 16 * 1024 * 1024; // 16MB
    const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/bmp', 'image/webp'];

    if (!allowedTypes.includes(file.type)) {
        showNotification('Please select a valid image file (PNG, JPEG, GIF, BMP, WebP)', 'error');
        return false;
    }

    if (file.size > maxSize) {
        showNotification('File size must be less than 16MB', 'error');
        return false;
    }

    return true;
}

// Error handling
function handleError(error, context = 'operation') {
    console.error(`Error in ${context}:`, error);
    showNotification(`An error occurred during ${context}. Please try again.`, 'error');
}

// Success feedback
function showSuccess(message) {
    showNotification(message, 'success');
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + Enter to submit forms
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const activeSection = document.querySelector('.section.active');
        if (activeSection) {
            const submitBtn = activeSection.querySelector('button[type="submit"], button[onclick*="process"]');
            if (submitBtn) {
                submitBtn.click();
            }
        }
    }

    // Escape to close modals or reset forms
    if (e.key === 'Escape') {
        // Add modal closing logic here if needed
    }
});

// Performance monitoring
function measurePerformance(operation, startTime) {
    const endTime = performance.now();
    const duration = endTime - startTime;
    console.log(`${operation} took ${duration.toFixed(2)}ms`);

    // Send to analytics if available
    if (window.gtag) {
        gtag('event', 'performance', {
            event_category: 'engagement',
            event_label: operation,
            value: Math.round(duration)
        });
    }
}

// Initialize performance observer
if ('PerformanceObserver' in window) {
    const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
            if (entry.entryType === 'measure') {
                console.log(`${entry.name}: ${entry.duration}ms`);
            }
        }
    });
    observer.observe({ entryTypes: ['measure'] });
}

// Analytics functionality
let activityChart, securityChart, fileTypesChart, performanceChart;

function refreshAnalytics() {
    const timeRange = document.getElementById('analyticsTimeRange').value;
    const metricType = document.getElementById('analyticsMetricType').value;

    showNotification('Analytics refreshed successfully', 'success');

    // In a real implementation, this would fetch new data from the server
    // For now, we'll just show a success message
    console.log(`Refreshing analytics for ${timeRange} with metric type: ${metricType}`);
}

function exportChart(chartType) {
    // In a real implementation, this would export the chart as an image
    showNotification(`${chartType} chart exported successfully`, 'success');
}

// Initialize charts when analytics section is loaded
function initializeCharts() {
    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'bottom',
                labels: {
                    usePointStyle: true,
                    padding: 20
                }
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                grid: {
                    color: 'rgba(255, 255, 255, 0.1)'
                },
                ticks: {
                    color: 'var(--text-muted)'
                }
            },
            x: {
                grid: {
                    color: 'rgba(255, 255, 255, 0.1)'
                },
                ticks: {
                    color: 'var(--text-muted)'
                }
            }
        }
    };

    // Activity Chart
    const activityCtx = document.getElementById('activityChart');
    if (activityCtx) {
        activityChart = new Chart(activityCtx, {
            type: 'line',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Encryption',
                    data: [12, 19, 15, 25, 22, 18, 14],
                    borderColor: 'var(--primary)',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4,
                    fill: true
                }, {
                    label: 'Decryption',
                    data: [8, 12, 10, 15, 18, 12, 9],
                    borderColor: 'var(--success)',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: chartOptions
        });
    }

    // Security Chart
    const securityCtx = document.getElementById('securityChart');
    if (securityCtx) {
        securityChart = new Chart(securityCtx, {
            type: 'doughnut',
            data: {
                labels: ['AES-256', 'Password Protected', '2FA Enabled'],
                datasets: [{
                    data: [85, 65, 95],
                    backgroundColor: [
                        'var(--primary)',
                        'var(--secondary)',
                        'var(--success)'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            usePointStyle: true,
                            padding: 20,
                            color: 'var(--text-light)'
                        }
                    }
                }
            }
        });
    }

    // File Types Chart
    const fileTypesCtx = document.getElementById('fileTypesChart');
    if (fileTypesCtx) {
        fileTypesChart = new Chart(fileTypesCtx, {
            type: 'bar',
            data: {
                labels: ['PNG', 'JPEG', 'GIF', 'BMP', 'WebP'],
                datasets: [{
                    label: 'Files Processed',
                    data: [45, 32, 18, 12, 8],
                    backgroundColor: 'var(--primary)',
                    borderRadius: 4
                }]
            },
            options: chartOptions
        });
    }

    // Performance Chart
    const performanceCtx = document.getElementById('performanceChart');
    if (performanceCtx) {
        performanceChart = new Chart(performanceCtx, {
            type: 'line',
            data: {
                labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                datasets: [{
                    label: 'Processing Time (seconds)',
                    data: [2.8, 2.3, 2.1, 1.9],
                    borderColor: 'var(--accent)',
                    backgroundColor: 'rgba(245, 158, 11, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: chartOptions
        });
    }
}

// Analytics tabs functionality
function initializeAnalyticsTabs() {
    const tabButtons = document.querySelectorAll('.analytics-tab');
    const tabContents = document.querySelectorAll('.analytics-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remove active class from all tabs
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            // Add active class to clicked tab
            button.classList.add('active');
            const tabId = button.getAttribute('data-tab') + '-tab';
            document.getElementById(tabId).classList.add('active');
        });
    });
}

// Security functions
function toggle2FA() {
    showNotification('2FA settings updated successfully', 'success');
}

function changePassword() {
    // In a real implementation, this would open a password change modal
    showNotification('Password change initiated', 'info');
}

function manageSessions() {
    // In a real implementation, this would open a session management modal
    showNotification('Session management opened', 'info');
}

function toggleAnalytics() {
    showNotification('Analytics tracking updated', 'success');
}

function configureRetention() {
    // In a real implementation, this would open retention settings
    showNotification('Data retention configured', 'success');
}

function exportData() {
    // In a real implementation, this would start data export
    showNotification('Data export started. You will receive an email when ready.', 'info');
}

// File management functions
function searchFiles() {
    const searchTerm = document.getElementById('fileSearch').value.toLowerCase();
    const fileType = document.getElementById('fileTypeFilter').value;
    const dateFilter = document.getElementById('fileDateFilter').value;

    // In a real implementation, this would filter the files table
    console.log(`Searching for: ${searchTerm}, Type: ${fileType}, Date: ${dateFilter}`);
    showNotification('File search completed', 'success');
}

// Enhanced initialization function with analytics support
function initializeAnalyticsSection() {
    // Initialize charts when analytics section is activated
    setTimeout(() => {
        initializeCharts();
        initializeAnalyticsTabs();
    }, 100);
}

// Enhanced file upload with progress
function updateFileUploadProgress(file, progress) {
    // In a real implementation, this would update a progress bar
    console.log(`Upload progress for ${file.name}: ${progress}%`);
}

// Enhanced error handling
function handleFileError(error, fileName) {
    console.error(`Error processing file ${fileName}:`, error);
    showNotification(`Error processing ${fileName}. Please try again.`, 'error');
}

// Enhanced success feedback
function handleFileSuccess(fileName, operation) {
    showNotification(`${operation} completed successfully for ${fileName}`, 'success');
}

// Keyboard shortcuts for power users
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + Enter to submit forms
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const activeSection = document.querySelector('.section.active');
        if (activeSection) {
            const submitBtn = activeSection.querySelector('button[type="submit"], button[onclick*="process"]');
            if (submitBtn) {
                submitBtn.click();
            }
        }
    }

    // Ctrl/Cmd + K to focus search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.getElementById('fileSearch') || document.querySelector('.search-input');
        if (searchInput) {
            searchInput.focus();
        }
    }

    // Escape to close modals or reset forms
    if (e.key === 'Escape') {
        // Add modal closing logic here if needed
        const activeSection = document.querySelector('.section.active');
        if (activeSection && activeSection.id !== 'home-section') {
            switchToSection('home');
        }
    }
});

// Performance monitoring with detailed metrics
function measurePerformance(operation, startTime) {
    const endTime = performance.now();
    const duration = endTime - startTime;
    console.log(`${operation} took ${duration.toFixed(2)}ms`);

    // Send to analytics if available
    if (window.gtag) {
        gtag('event', 'performance', {
            event_category: 'engagement',
            event_label: operation,
            value: Math.round(duration)
        });
    }

    // Update performance metrics in UI if visible
    const performanceMetric = document.querySelector('.metric-data h4');
    if (performanceMetric && operation.includes('process')) {
        // Update the displayed performance metric
        performanceMetric.textContent = `${(duration / 1000).toFixed(1)}s`;
    }
}

// Initialize performance observer with more detailed tracking
if ('PerformanceObserver' in window) {
    const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
            if (entry.entryType === 'measure') {
                console.log(`${entry.name}: ${entry.duration}ms`);
            }
        }
    });
    observer.observe({ entryTypes: ['measure'] });
}

// Enhanced Header Functions
function toggleNotifications() {
    const dropdown = document.getElementById('notificationDropdown');
    const profileDropdown = document.getElementById('profileDropdown');

    // Close profile dropdown if open
    if (profileDropdown && profileDropdown.style.display !== 'none') {
        profileDropdown.style.display = 'none';
    }

    // Toggle notifications dropdown
    if (dropdown) {
        dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
    }
}

function toggleProfileMenu() {
    const dropdown = document.getElementById('profileDropdown');
    const notificationDropdown = document.getElementById('notificationDropdown');

    // Close notifications dropdown if open
    if (notificationDropdown && notificationDropdown.style.display !== 'none') {
        notificationDropdown.style.display = 'none';
    }

    // Toggle profile dropdown
    if (dropdown) {
        dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
    }
}

function markAllRead() {
    const unreadItems = document.querySelectorAll('.notification-item.unread');
    unreadItems.forEach(item => {
        item.classList.remove('unread');
    });

    // Update notification count
    const countElement = document.getElementById('notificationCount');
    if (countElement) {
        countElement.textContent = '0';
    }

    showNotification('All notifications marked as read', 'success');
}

// Enhanced Search Functionality
function initializeSearch() {
    const searchInput = document.getElementById('globalSearch');
    const suggestionsContainer = document.getElementById('searchSuggestions');

    if (!searchInput || !suggestionsContainer) return;

    let searchTimeout;

    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        const query = this.value.trim();

        if (query.length < 2) {
            suggestionsContainer.style.display = 'none';
            return;
        }

        searchTimeout = setTimeout(() => {
            showSearchSuggestions(query);
        }, 300);
    });

    // Close suggestions when clicking outside
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !suggestionsContainer.contains(e.target)) {
            suggestionsContainer.style.display = 'none';
        }
    });
}

function showSearchSuggestions(query) {
    const suggestionsContainer = document.getElementById('searchSuggestions');

    // Mock search suggestions - in real implementation, this would come from backend
    const suggestions = [
        { type: 'file', title: 'encrypted_image.png', meta: 'Encrypted 2 hours ago' },
        { type: 'message', title: 'Birthday message', meta: 'AI Generated' },
        { type: 'section', title: 'Analytics Dashboard', meta: 'View your statistics' },
        { type: 'section', title: 'Security Settings', meta: 'Manage your security' }
    ].filter(item =>
        item.title.toLowerCase().includes(query.toLowerCase()) ||
        item.meta.toLowerCase().includes(query.toLowerCase())
    );

    if (suggestions.length === 0) {
        suggestionsContainer.style.display = 'none';
        return;
    }

    suggestionsContainer.innerHTML = suggestions.map(suggestion => `
        <div class="search-suggestion-item" onclick="handleSearchSuggestion('${suggestion.type}', '${suggestion.title}')">
            <div class="search-suggestion-icon">
                <i class="fas fa-${getSuggestionIcon(suggestion.type)}"></i>
            </div>
            <div class="search-suggestion-content">
                <div class="search-suggestion-title">${suggestion.title}</div>
                <div class="search-suggestion-meta">${suggestion.meta}</div>
            </div>
        </div>
    `).join('');

    suggestionsContainer.style.display = 'block';
}

function getSuggestionIcon(type) {
    const icons = {
        'file': 'file',
        'message': 'message',
        'section': 'folder'
    };
    return icons[type] || 'search';
}

function handleSearchSuggestion(type, title) {
    const suggestionsContainer = document.getElementById('searchSuggestions');
    suggestionsContainer.style.display = 'none';

    // Handle different suggestion types
    switch(type) {
        case 'section':
            if (title.includes('Analytics')) {
                switchToSection('analytics');
            } else if (title.includes('Security')) {
                switchToSection('security');
            }
            break;
        case 'file':
            switchToSection('files');
            break;
        case 'message':
            switchToSection('ai');
            break;
    }

    // Clear search input
    const searchInput = document.getElementById('globalSearch');
    if (searchInput) {
        searchInput.value = '';
    }
}

// Update breadcrumb when switching sections
function updateBreadcrumb(sectionName) {
    const breadcrumbElement = document.getElementById('current-section-name');
    if (breadcrumbElement) {
        const sectionTitles = {
            'home': 'Overview',
            'analytics': 'Analytics',
            'encrypt': 'Encrypt',
            'decrypt': 'Decrypt',
            'ai': 'AI Assistant',
            'files': 'My Files',
            'security': 'Security'
        };
        breadcrumbElement.textContent = sectionTitles[sectionName] || 'Overview';
    }
}

// Enhanced section switching with breadcrumb update
function switchToSectionEnhanced(sectionName) {
    switchToSection(sectionName);
    updateBreadcrumb(sectionName);

    // Initialize analytics when switching to analytics section
    if (sectionName === 'analytics') {
        initializeAnalyticsSection();
    }

    // Close any open dropdowns
    const dropdowns = ['notificationDropdown', 'profileDropdown'];
    dropdowns.forEach(id => {
        const dropdown = document.getElementById(id);
        if (dropdown) {
            dropdown.style.display = 'none';
        }
    });
}

// Initialize enhanced features
document.addEventListener('DOMContentLoaded', function() {
    // Initialize search functionality
    initializeSearch();

    // Override the original switchToSection with enhanced version
    window.originalSwitchToSection = switchToSection;
    window.switchToSection = switchToSectionEnhanced;

    // Close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        const notificationDropdown = document.getElementById('notificationDropdown');
        const profileDropdown = document.getElementById('profileDropdown');
        const notificationBtn = e.target.closest('.notification-btn');
        const profileTrigger = e.target.closest('.profile-trigger');

        if (notificationDropdown && !notificationBtn && !notificationDropdown.contains(e.target)) {
            notificationDropdown.style.display = 'none';
        }

        if (profileDropdown && !profileTrigger && !profileDropdown.contains(e.target)) {
            profileDropdown.style.display = 'none';
        }
    });

    // Add keyboard shortcuts for enhanced features
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K to focus search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.getElementById('globalSearch');
            if (searchInput) {
                searchInput.focus();
            }
        }

        // Escape to close dropdowns
        if (e.key === 'Escape') {
            const dropdowns = ['notificationDropdown', 'profileDropdown'];
            dropdowns.forEach(id => {
                const dropdown = document.getElementById(id);
                if (dropdown) {
                    dropdown.style.display = 'none';
                }
            });
        }
    });
});

// Floating Action Button Functions
function showQuickActions() {
    const modal = document.getElementById('quickActionsModal');
    if (modal) {
        modal.style.display = 'flex';
        // Animate the FAB
        const fab = document.querySelector('.fab');
        if (fab) {
            fab.style.transform = 'rotate(45deg)';
        }
    }
}

function hideQuickActions() {
    const modal = document.getElementById('quickActionsModal');
    if (modal) {
        modal.style.display = 'none';
        // Reset FAB rotation
        const fab = document.querySelector('.fab');
        if (fab) {
            fab.style.transform = 'rotate(0deg)';
        }
    }
}

// Enhanced Notification System
function addNotification(title, message, type = 'info', duration = 5000) {
    const notificationContainer = document.createElement('div');
    notificationContainer.className = `notification notification-${type}`;
    notificationContainer.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${getNotificationIcon(type)} notification-icon"></i>
            <div class="notification-message">
                <strong>${title}</strong><br>
                ${message}
            </div>
            <button class="notification-close" onclick="this.parentElement.parentElement.remove()">&times;</button>
        </div>
    `;

    document.body.appendChild(notificationContainer);

    // Auto remove after duration
    if (duration > 0) {
        setTimeout(() => {
            if (notificationContainer.parentElement) {
                notificationContainer.remove();
            }
        }, duration);
    }

    return notificationContainer;
}

function getNotificationIcon(type) {
    const icons = {
        'success': 'check-circle',
        'error': 'exclamation-triangle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// Enhanced Success Feedback
function showSuccessAnimation(element) {
    element.classList.add('success-animation');
    setTimeout(() => {
        element.classList.remove('success-animation');
    }, 2000);
}

// Loading States Management
function setLoadingState(element, loading = true, text = 'Loading...') {
    if (loading) {
        element.disabled = true;
        element.dataset.originalText = element.innerHTML;
        element.innerHTML = `
            <i class="fas fa-spinner fa-spin me-2"></i>
            ${text}
        `;
        element.classList.add('loading-shimmer');
    } else {
        element.disabled = false;
        element.innerHTML = element.dataset.originalText || element.innerHTML;
        element.classList.remove('loading-shimmer');
    }
}

// Progress Animation
function animateProgress(element, targetValue, duration = 1000) {
    const startValue = 0;
    const startTime = performance.now();

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);

        const currentValue = Math.floor(startValue + (targetValue - startValue) * progress);
        element.textContent = currentValue;

        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }

    requestAnimationFrame(update);
}

// Enhanced Analytics
function updateAnalyticsData() {
    // Simulate real-time data updates
    const metrics = document.querySelectorAll('.metric-data h4');
    metrics.forEach((metric, index) => {
        if (metric.textContent.includes('s')) {
            // Skip time metrics
            return;
        }

        const currentValue = parseInt(metric.textContent.replace(/[^\d]/g, ''));
        const newValue = currentValue + Math.floor(Math.random() * 5);
        animateProgress(metric, newValue, 2000);
    });

    showNotification('Analytics data updated', 'success');
}

// Keyboard Shortcuts Enhancement
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K to focus search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.getElementById('globalSearch');
        if (searchInput) {
            searchInput.focus();
        }
    }

    // Ctrl/Cmd + / to show quick actions
    if ((e.ctrlKey || e.metaKey) && e.key === '/') {
        e.preventDefault();
        showQuickActions();
    }

    // Escape to close modals
    if (e.key === 'Escape') {
        hideQuickActions();
        const dropdowns = ['notificationDropdown', 'profileDropdown'];
        dropdowns.forEach(id => {
            const dropdown = document.getElementById(id);
            if (dropdown) {
                dropdown.style.display = 'none';
            }
        });
    }
});

// Auto-refresh analytics every 30 seconds
setInterval(() => {
    if (document.querySelector('.analytics-content.active')) {
        updateAnalyticsData();
    }
}, 30000);

// Performance Monitoring
function trackPerformance(action, callback) {
    const startTime = performance.now();

    callback().then(() => {
        const endTime = performance.now();
        const duration = endTime - startTime;
        console.log(`${action} completed in ${duration.toFixed(2)}ms`);

        // Track in analytics if available
        if (window.gtag) {
            gtag('event', 'performance', {
                event_category: 'engagement',
                event_label: action,
                value: Math.round(duration)
            });
        }
    });
}

// Activity Log Functions
function refreshActivity() {
    showNotification('Activity log refreshed successfully', 'success');
    // In a real implementation, this would fetch new activity data
}

function filterActivity(type, timePeriod) {
    // Filter activity items based on type and time period
    const items = document.querySelectorAll('.timeline-item');
    items.forEach(item => {
        const itemType = item.querySelector('.timeline-marker').classList[1];
        // Add filtering logic here
    });
}

// Batch Processing Functions
function startBatchProcessing() {
    const files = document.getElementById('batchImages').files;
    if (files.length === 0) {
        showNotification('Please select images first', 'error');
        return;
    }

    const progressDiv = document.getElementById('batchProgress');
    const resultsDiv = document.getElementById('batchResults');
    const processBtn = document.getElementById('batchProcessBtn');

    progressDiv.style.display = 'block';
    resultsDiv.style.display = 'none';
    processBtn.disabled = true;
    processBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';

    // Simulate batch processing
    let processed = 0;
    const total = files.length;
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');

    const processNext = () => {
        if (processed < total) {
            processed++;
            const percentage = (processed / total) * 100;
            progressFill.style.width = percentage + '%';
            progressText.textContent = `${processed} of ${total} completed`;

            // Simulate processing time
            setTimeout(processNext, 1000);
        } else {
            // Processing complete
            processBtn.disabled = false;
            processBtn.innerHTML = '<i class="fas fa-check me-2"></i>Complete';
            progressDiv.style.display = 'none';
            resultsDiv.style.display = 'block';
            showNotification(`Successfully processed ${total} images`, 'success');
        }
    };

    processNext();
}

function downloadBatchResults() {
    showNotification('Batch download started', 'info');
    // In a real implementation, this would download the processed files
}

// Template Functions
function useTemplate(templateId) {
    // Copy template content to encryption form
    switchToSection('encrypt');
    showNotification('Template loaded successfully', 'success');
}

function previewTemplate(templateId) {
    // Show template preview modal
    showNotification('Template preview opened', 'info');
}

function showTemplateCreator() {
    // Show custom template creation modal
    showNotification('Custom template creator opened', 'info');
}

function filterTemplates(category) {
    const templates = document.querySelectorAll('.template-card');
    templates.forEach(template => {
        if (category === 'all' || template.dataset.category === category) {
            template.style.display = 'block';
        } else {
            template.style.display = 'none';
        }
    });
}

// Settings Functions
function saveSettings() {
    // Collect all settings values
    const settings = {
        displayName: document.getElementById('displayName').value,
        emailAddress: document.getElementById('emailAddress').value,
        autoLockTime: document.getElementById('autoLockTime').value,
        defaultEncryption: document.getElementById('defaultEncryption').value,
        passwordComplexity: document.getElementById('passwordComplexity').checked,
        themeSelector: document.getElementById('themeSelector').value,
        sidebarCollapsed: document.getElementById('sidebarCollapsed').checked,
        showAnimations: document.getElementById('showAnimations').checked,
        emailNotifications: document.getElementById('emailNotifications').checked,
        pushNotifications: document.getElementById('pushNotifications').checked,
        weeklySummary: document.getElementById('weeklySummary').checked
    };

    // Save settings (in a real app, this would be sent to server)
    localStorage.setItem('cybercloak_settings', JSON.stringify(settings));
    showNotification('Settings saved successfully', 'success');
}

function resetSettings() {
    if (confirm('Are you sure you want to reset all settings to defaults?')) {
        // Reset all form values to defaults
        document.getElementById('autoLockTime').value = '15';
        document.getElementById('defaultEncryption').value = 'aes256';
        document.getElementById('passwordComplexity').checked = true;
        document.getElementById('themeSelector').value = 'dark';
        document.getElementById('sidebarCollapsed').checked = false;
        document.getElementById('showAnimations').checked = true;
        document.getElementById('emailNotifications').checked = true;
        document.getElementById('pushNotifications').checked = true;
        document.getElementById('weeklySummary').checked = false;

        showNotification('Settings reset to defaults', 'info');
    }
}

// Enhanced Template Category Filtering
document.addEventListener('DOMContentLoaded', function() {
    // Add click handlers for template categories
    const categoryBtns = document.querySelectorAll('.category-btn');
    categoryBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // Remove active class from all buttons
            categoryBtns.forEach(b => b.classList.remove('active'));
            // Add active class to clicked button
            this.classList.add('active');
            // Filter templates
            const category = this.dataset.category;
            filterTemplates(category);
        });
    });

    // Load saved settings
    const savedSettings = localStorage.getItem('cybercloak_settings');
    if (savedSettings) {
        const settings = JSON.parse(savedSettings);
        // Apply saved settings to form elements
        Object.keys(settings).forEach(key => {
            const element = document.getElementById(key);
            if (element) {
                if (element.type === 'checkbox') {
                    element.checked = settings[key];
                } else {
                    element.value = settings[key];
                }
            }
        });
    }
});

// Enhanced Activity Filtering
function initializeActivityFilters() {
    const typeFilter = document.getElementById('activityTypeFilter');
    const timeFilter = document.getElementById('activityTimeFilter');

    if (typeFilter) {
        typeFilter.addEventListener('change', function() {
            filterActivity(this.value, timeFilter ? timeFilter.value : 'all');
        });
    }

    if (timeFilter) {
        timeFilter.addEventListener('change', function() {
            filterActivity(typeFilter ? typeFilter.value : 'all', this.value);
        });
    }
}

// Initialize all dashboard functionality
function initializeDashboardFunctionality() {
    // Initialize activity filters
    initializeActivityFilters();

    // Initialize template category filtering
    initializeTemplateFilters();

    // Initialize settings functionality
    initializeSettings();

    // Initialize batch processing
    initializeBatchProcessing();

    // Initialize notifications
    initializeNotifications();

    // Initialize file management
    initializeFileManagement();

    // Initialize security features
    initializeSecurityFeatures();

    // Initialize theme switching
    initializeThemeFeatures();

    // Initialize analytics
    initializeAnalyticsFeatures();

    // Initialize profile dropdown functionality
    initializeProfileDropdown();
}

// Template filtering functionality
function initializeTemplateFilters() {
    const categoryBtns = document.querySelectorAll('.category-btn');
    categoryBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // Remove active class from all buttons
            categoryBtns.forEach(b => b.classList.remove('active'));
            // Add active class to clicked button
            this.classList.add('active');
            // Filter templates
            const category = this.dataset.category || this.getAttribute('data-category');
            filterTemplates(category);
        });
    });
}

// Settings functionality
function initializeSettings() {
    // Load saved settings
    loadSavedSettings();

    // Add settings change listeners
    const settingElements = [
        'displayName', 'emailAddress', 'autoLockTime', 'defaultEncryption',
        'passwordComplexity', 'themeSelector', 'sidebarCollapsed', 'showAnimations',
        'emailNotifications', 'pushNotifications', 'weeklySummary'
    ];

    settingElements.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.addEventListener('change', function() {
                // Auto-save settings when changed
                saveSettings();
                showNotification('Setting updated', 'success');
            });
        }
    });
}

function loadSavedSettings() {
    const savedSettings = localStorage.getItem('cybercloak_settings');
    if (savedSettings) {
        const settings = JSON.parse(savedSettings);
        Object.keys(settings).forEach(key => {
            const element = document.getElementById(key);
            if (element) {
                if (element.type === 'checkbox') {
                    element.checked = settings[key];
                } else {
                    element.value = settings[key];
                }
            }
        });
    }
}

// Batch processing functionality
function initializeBatchProcessing() {
    const batchImagesInput = document.getElementById('batchImages');
    const batchUploadZone = document.getElementById('batchUploadZone');

    if (batchImagesInput && batchUploadZone) {
        // File drag and drop for batch processing
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            batchUploadZone.addEventListener(eventName, preventDefaults, false);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            batchUploadZone.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            batchUploadZone.addEventListener(eventName, unhighlight, false);
        });

        batchUploadZone.addEventListener('drop', handleBatchDrop, false);

        // File input change
        batchImagesInput.addEventListener('change', handleBatchFileSelect, false);
    }
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function highlight() {
    const zone = document.getElementById('batchUploadZone');
    if (zone) zone.classList.add('dragover');
}

function unhighlight() {
    const zone = document.getElementById('batchUploadZone');
    if (zone) zone.classList.remove('dragover');
}

function handleBatchDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    handleBatchFiles(files);
}

function handleBatchFileSelect(e) {
    const files = e.target.files;
    handleBatchFiles(files);
}

function handleBatchFiles(files) {
    const fileList = document.getElementById('batchFileList');
    if (!fileList) return;

    fileList.innerHTML = '';

    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const fileItem = document.createElement('div');
        fileItem.className = 'batch-file-item';
        fileItem.innerHTML = `
            <div class="file-info">
                <i class="fas fa-file-image"></i>
                <span>${file.name}</span>
                <small>${formatFileSize(file.size)}</small>
            </div>
            <div class="file-status">
                <i class="fas fa-check-circle text-success"></i>
            </div>
        `;
        fileList.appendChild(fileItem);
    }

    showNotification(`${files.length} files selected for batch processing`, 'info');
}

// Notifications functionality
function initializeNotifications() {
    // Mark as read functionality
    const notificationItems = document.querySelectorAll('.notification-item');
    notificationItems.forEach(item => {
        item.addEventListener('click', function() {
            this.classList.remove('unread');
            updateNotificationCount();
        });
    });
}

function updateNotificationCount() {
    const unreadCount = document.querySelectorAll('.notification-item.unread').length;
    const countElement = document.getElementById('notificationCount');
    if (countElement) {
        countElement.textContent = unreadCount;
        if (unreadCount === 0) {
            countElement.style.display = 'none';
        }
    }
}

// File management functionality
function initializeFileManagement() {
    // File search functionality
    const fileSearch = document.getElementById('fileSearch');
    if (fileSearch) {
        fileSearch.addEventListener('input', function() {
            searchFiles();
        });
    }

    // File filter functionality
    const fileTypeFilter = document.getElementById('fileTypeFilter');
    const fileDateFilter = document.getElementById('fileDateFilter');

    if (fileTypeFilter) {
        fileTypeFilter.addEventListener('change', searchFiles);
    }

    if (fileDateFilter) {
        fileDateFilter.addEventListener('change', searchFiles);
    }
}

function searchFiles() {
    const searchTerm = document.getElementById('fileSearch')?.value.toLowerCase() || '';
    const fileType = document.getElementById('fileTypeFilter')?.value || 'all';
    const dateFilter = document.getElementById('fileDateFilter')?.value || 'all';

    // In a real implementation, this would filter the actual file list
    console.log(`Searching for: ${searchTerm}, Type: ${fileType}, Date: ${dateFilter}`);
    showNotification('File search completed', 'success');
}

// Security features functionality
function initializeSecurityFeatures() {
    // 2FA toggle
    const twoFactorToggle = document.querySelector('.btn-outline-primary.btn-sm');
    if (twoFactorToggle && twoFactorToggle.textContent.includes('Enabled')) {
        twoFactorToggle.addEventListener('click', function() {
            toggle2FA();
        });
    }

    // Password change
    const passwordBtn = document.querySelector('.btn-outline-secondary.btn-sm');
    if (passwordBtn && passwordBtn.textContent.includes('Change')) {
        passwordBtn.addEventListener('click', function() {
            changePassword();
        });
    }
}

function toggle2FA() {
    showNotification('2FA settings updated successfully', 'success');
}

function changePassword() {
    showNotification('Password change initiated', 'info');
}

function manageSessions() {
    showNotification('Session management opened', 'info');
}

function toggleAnalytics() {
    showNotification('Analytics tracking updated', 'success');
}

function configureRetention() {
    showNotification('Data retention configured', 'success');
}

function exportData() {
    showNotification('Data export started. You will receive an email when ready.', 'info');
}

// Theme features functionality
function initializeThemeFeatures() {
    const themeSelector = document.getElementById('themeSelector');
    if (themeSelector) {
        themeSelector.addEventListener('change', function() {
            changeTheme(this.value);
        });
    }
}

function changeTheme(theme) {
    // Apply theme changes
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('cybercloak_theme', theme);
    showNotification(`Theme changed to ${theme}`, 'success');
}

// Analytics features functionality
function initializeAnalyticsFeatures() {
    // Analytics controls
    const timeRange = document.getElementById('analyticsTimeRange');
    const metricType = document.getElementById('analyticsMetricType');

    if (timeRange) {
        timeRange.addEventListener('change', function() {
            updateAnalyticsData();
        });
    }

    if (metricType) {
        metricType.addEventListener('change', function() {
            updateAnalyticsData();
        });
    }
}

function updateAnalyticsData() {
    // Simulate real-time data updates
    const metrics = document.querySelectorAll('.metric-data h4');
    metrics.forEach((metric, index) => {
        if (metric.textContent.includes('s')) {
            // Skip time metrics
            return;
        }

        const currentValue = parseInt(metric.textContent.replace(/[^\d]/g, ''));
        const newValue = currentValue + Math.floor(Math.random() * 5);
        animateProgress(metric, newValue, 2000);
    });

    showNotification('Analytics data updated', 'success');
}

function animateProgress(element, targetValue, duration = 1000) {
    const startValue = parseInt(element.textContent) || 0;
    const startTime = performance.now();

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);

        const currentValue = Math.floor(startValue + (targetValue - startValue) * progress);
        element.textContent = currentValue;

        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }

    requestAnimationFrame(update);
}

// Profile dropdown functionality
function initializeProfileDropdown() {
    // Add click handlers for profile dropdown items
    const profileItems = document.querySelectorAll('.profile-menu-item');
    profileItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const action = this.textContent.trim().toLowerCase().replace(/\s+/g, '');

            switch(action) {
                case 'accountsettings':
                    switchToSection('settings');
                    break;
                case 'security&privacy':
                    switchToSection('security');
                    break;
                case 'notifications':
                    toggleNotifications();
                    break;
                case 'theme&appearance':
                    showThemeModal();
                    break;
                case 'exportdata':
                    exportData();
                    break;
                case 'help&support':
                    showHelpModal();
                    break;
                case 'rate&review':
                    showReviewModal();
                    break;
                case 'signout':
                    if (confirm('Are you sure you want to sign out?')) {
                        window.location.href = '/logout';
                    }
                    break;
            }
        });
    });
}

function showThemeModal() {
    showNotification('Theme settings opened', 'info');
}

function showHelpModal() {
    showNotification('Help & Support opened', 'info');
}

function showReviewModal() {
    showNotification('Rate & Review opened', 'info');
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboardFunctionality();
});

// Additional functionality for complete dashboard operation

// Quick Actions functionality
function initializeQuickActions() {
    const quickActionItems = document.querySelectorAll('.quick-action-item');
    quickActionItems.forEach(item => {
        item.addEventListener('click', function() {
            const action = this.querySelector('h5').textContent.toLowerCase().replace(/\s+/g, '');
            switch(action) {
                case 'encryptfile':
                    switchToSection('encrypt');
                    break;
                case 'decryptfile':
                    switchToSection('decrypt');
                    break;
                case 'aiassistant':
                    switchToSection('ai');
                    break;
                case 'viewanalytics':
                    switchToSection('analytics');
                    break;
                case 'myfiles':
                    switchToSection('files');
                    break;
                case 'security':
                    switchToSection('security');
                    break;
            }
            hideQuickActions();
        });
    });
}

// Enhanced navigation functionality
function initializeNavigation() {
    // Add click handlers for all navigation items
    const navItems = document.querySelectorAll('.nav-item[data-section]');
    navItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const section = this.getAttribute('data-section');
            switchToSection(section);

            // Special handling for certain sections
            if (section === 'analytics') {
                setTimeout(() => {
                    initializeCharts();
                    initializeAnalyticsTabs();
                }, 100);
            }
        });
    });

    // Initialize breadcrumb updates
    updateBreadcrumb('home');
}

// Initialize charts when analytics section is loaded
function initializeCharts() {
    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'bottom',
                labels: {
                    usePointStyle: true,
                    padding: 20
                }
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                grid: {
                    color: 'rgba(255, 255, 255, 0.1)'
                },
                ticks: {
                    color: 'var(--text-muted)'
                }
            },
            x: {
                grid: {
                    color: 'rgba(255, 255, 255, 0.1)'
                },
                ticks: {
                    color: 'var(--text-muted)'
                }
            }
        }
    };

    // Activity Chart
    const activityCtx = document.getElementById('activityChart');
    if (activityCtx) {
        activityChart = new Chart(activityCtx, {
            type: 'line',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Encryption',
                    data: [12, 19, 15, 25, 22, 18, 14],
                    borderColor: 'var(--primary)',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4,
                    fill: true
                }, {
                    label: 'Decryption',
                    data: [8, 12, 10, 15, 18, 12, 9],
                    borderColor: 'var(--success)',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: chartOptions
        });
    }

    // Security Chart
    const securityCtx = document.getElementById('securityChart');
    if (securityCtx) {
        securityChart = new Chart(securityCtx, {
            type: 'doughnut',
            data: {
                labels: ['AES-256', 'Password Protected', '2FA Enabled'],
                datasets: [{
                    data: [85, 65, 95],
                    backgroundColor: [
                        'var(--primary)',
                        'var(--secondary)',
                        'var(--success)'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            usePointStyle: true,
                            padding: 20,
                            color: 'var(--text-light)'
                        }
                    }
                }
            }
        });
    }

    // File Types Chart
    const fileTypesCtx = document.getElementById('fileTypesChart');
    if (fileTypesCtx) {
        fileTypesChart = new Chart(fileTypesCtx, {
            type: 'bar',
            data: {
                labels: ['PNG', 'JPEG', 'GIF', 'BMP', 'WebP'],
                datasets: [{
                    label: 'Files Processed',
                    data: [45, 32, 18, 12, 8],
                    backgroundColor: 'var(--primary)',
                    borderRadius: 4
                }]
            },
            options: chartOptions
        });
    }

    // Performance Chart
    const performanceCtx = document.getElementById('performanceChart');
    if (performanceCtx) {
        performanceChart = new Chart(performanceCtx, {
            type: 'line',
            data: {
                labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                datasets: [{
                    label: 'Processing Time (seconds)',
                    data: [2.8, 2.3, 2.1, 1.9],
                    borderColor: 'var(--accent)',
                    backgroundColor: 'rgba(245, 158, 11, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: chartOptions
        });
    }
}

// Analytics tabs functionality
function initializeAnalyticsTabs() {
    const tabButtons = document.querySelectorAll('.analytics-tab');
    const tabContents = document.querySelectorAll('.analytics-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remove active class from all tabs
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            // Add active class to clicked tab
            button.classList.add('active');
            const tabId = button.getAttribute('data-tab') + '-tab';
            const targetTab = document.getElementById(tabId);
            if (targetTab) {
                targetTab.classList.add('active');
            }
        });
    });
}

// Enhanced search functionality
function initializeSearch() {
    const globalSearch = document.getElementById('globalSearch');
    const searchSuggestions = document.getElementById('searchSuggestions');

    if (!globalSearch || !searchSuggestions) return;

    let searchTimeout;

    globalSearch.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        const query = this.value.trim();

        if (query.length < 2) {
            searchSuggestions.style.display = 'none';
            return;
        }

        searchTimeout = setTimeout(() => {
            showSearchSuggestions(query);
        }, 300);
    });

    // Close suggestions when clicking outside
    document.addEventListener('click', function(e) {
        if (!globalSearch.contains(e.target) && !searchSuggestions.contains(e.target)) {
            searchSuggestions.style.display = 'none';
        }
    });
}

function showSearchSuggestions(query) {
    const suggestionsContainer = document.getElementById('searchSuggestions');

    // Mock search suggestions - in real implementation, this would come from backend
    const suggestions = [
        { type: 'file', title: 'encrypted_image.png', meta: 'Encrypted 2 hours ago' },
        { type: 'message', title: 'Birthday message', meta: 'AI Generated' },
        { type: 'section', title: 'Analytics Dashboard', meta: 'View your statistics' },
        { type: 'section', title: 'Security Settings', meta: 'Manage your security' }
    ].filter(item =>
        item.title.toLowerCase().includes(query.toLowerCase()) ||
        item.meta.toLowerCase().includes(query.toLowerCase())
    );

    if (suggestions.length === 0) {
        suggestionsContainer.style.display = 'none';
        return;
    }

    suggestionsContainer.innerHTML = suggestions.map(suggestion => `
        <div class="search-suggestion-item" onclick="handleSearchSuggestion('${suggestion.type}', '${suggestion.title}')">
            <div class="search-suggestion-icon">
                <i class="fas fa-${getSuggestionIcon(suggestion.type)}"></i>
            </div>
            <div class="search-suggestion-content">
                <div class="search-suggestion-title">${suggestion.title}</div>
                <div class="search-suggestion-meta">${suggestion.meta}</div>
            </div>
        </div>
    `).join('');

    suggestionsContainer.style.display = 'block';
}

function getSuggestionIcon(type) {
    const icons = {
        'file': 'file',
        'message': 'message',
        'section': 'folder'
    };
    return icons[type] || 'search';
}

function handleSearchSuggestion(type, title) {
    const suggestionsContainer = document.getElementById('searchSuggestions');
    suggestionsContainer.style.display = 'none';

    // Handle different suggestion types
    switch(type) {
        case 'section':
            if (title.includes('Analytics')) {
                switchToSection('analytics');
            } else if (title.includes('Security')) {
                switchToSection('security');
            }
            break;
        case 'file':
            switchToSection('files');
            break;
        case 'message':
            switchToSection('ai');
            break;
    }

    // Clear search input
    const searchInput = document.getElementById('globalSearch');
    if (searchInput) {
        searchInput.value = '';
    }
}

// Enhanced breadcrumb functionality
function updateBreadcrumb(sectionName) {
    const breadcrumbElement = document.getElementById('current-section-name');
    if (breadcrumbElement) {
        const sectionTitles = {
            'home': 'Overview',
            'analytics': 'Analytics',
            'encrypt': 'Encrypt',
            'decrypt': 'Decrypt',
            'ai': 'AI Assistant',
            'files': 'My Files',
            'security': 'Security',
            'activity': 'Activity Log',
            'batch': 'Batch Processing',
            'templates': 'Templates',
            'settings': 'Settings'
        };
        breadcrumbElement.textContent = sectionTitles[sectionName] || 'Overview';
    }
}

// Enhanced section switching with breadcrumb update
function switchToSectionEnhanced(sectionName) {
    switchToSection(sectionName);
    updateBreadcrumb(sectionName);

    // Initialize section-specific features
    if (sectionName === 'analytics') {
        setTimeout(() => {
            initializeCharts();
            initializeAnalyticsTabs();
        }, 100);
    }
}

// Initialize all features when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboardFunctionality();
    initializeNavigation();
    initializeQuickActions();
    initializeSearch();

    // Override the original switchToSection with enhanced version
    window.originalSwitchToSection = switchToSection;
    window.switchToSection = switchToSectionEnhanced;
});

// Export functions for global access
window.CyberCloakDashboard = {
    switchToSection: switchToSectionEnhanced,
    toggleSidebar,
    generateAIMessage,
    processEncryption,
    processDecryption,
    showNotification,
    validateImage,
    formatFileSize,
    refreshAnalytics,
    exportChart,
    toggle2FA,
    changePassword,
    manageSessions,
    toggleAnalytics,
    configureRetention,
    exportData,
    searchFiles,
    toggleNotifications,
    toggleProfileMenu,
    markAllRead,
    showQuickActions,
    hideQuickActions,
    addNotification,
    showSuccessAnimation,
    setLoadingState,
    animateProgress,
    updateAnalyticsData,
    trackPerformance,
    // New functions
    refreshActivity,
    startBatchProcessing,
    downloadBatchResults,
    useTemplate,
    previewTemplate,
    showTemplateCreator,
    filterTemplates,
    saveSettings,
    resetSettings,
    // Enhanced functions
    initializeCharts,
    initializeAnalyticsTabs,
    showSearchSuggestions,
    handleSearchSuggestion,
    updateBreadcrumb
};