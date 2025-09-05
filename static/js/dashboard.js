// Dashboard-specific JavaScript for CyberCloak

let currentStep = 1;
let sessionId = null;
let uploadedFile = null;

document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
});

function initializeDashboard() {
    // Initialize file upload handling
    const fileInput = document.getElementById('inputImage');
    if (fileInput) {
        fileInput.addEventListener('change', handleFileSelect);
    }
    
    // Initialize modal reset on close
    const uploadModal = document.getElementById('uploadModal');
    if (uploadModal) {
        uploadModal.addEventListener('hidden.bs.modal', resetUploadModal);
    }
    
    // Initialize drag and drop for upload area
    const uploadArea = document.getElementById('uploadArea');
    if (uploadArea) {
        setupDragAndDrop(uploadArea);
    }
}

function setupDragAndDrop(uploadArea) {
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
    });
    
    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, unhighlight, false);
    });
    
    uploadArea.addEventListener('drop', handleDrop, false);
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    function highlight() {
        uploadArea.classList.add('dragover');
    }
    
    function unhighlight() {
        uploadArea.classList.remove('dragover');
    }
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            const fileInput = document.getElementById('inputImage');
            fileInput.files = files;
            handleFileSelect({ target: fileInput });
        }
    }
}

async function handleFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    try {
        // Validate file
        CyberCloak.validateImageFile(file);
        
        uploadedFile = file;
        
        // Show image preview
        const previewImg = document.getElementById('previewImg');
        const imagePreview = document.getElementById('imagePreview');
        
        CyberCloak.previewImage(event.target, previewImg);
        imagePreview.style.display = 'block';
        
        // Upload and analyze image
        await uploadAndAnalyzeImage(file);
        
        // Enable next button
        const nextBtn = document.getElementById('nextBtn');
        nextBtn.disabled = false;
        nextBtn.textContent = 'Next: Enter Message';
        
    } catch (error) {
        CyberCloak.showNotification(error.message, 'error');
    }
}

async function uploadAndAnalyzeImage(file) {
    const formData = new FormData();
    formData.append('input_image', file);
    
    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            sessionId = result.session_id;
            displayImageAnalysis(result.analysis);
        } else {
            throw new Error(result.error || 'Upload failed');
        }
    } catch (error) {
        throw new Error('Failed to upload and analyze image: ' + error.message);
    }
}

function displayImageAnalysis(analysis) {
    const analysisDiv = document.getElementById('imageAnalysis');
    
    analysisDiv.innerHTML = `
        <div class="analysis-results p-3 border rounded">
            <h6><i class="fas fa-chart-line me-2"></i>Image Analysis</h6>
            <div class="row g-2">
                <div class="col-md-6">
                    <small class="text-muted">Dimensions:</small>
                    <div>${analysis.width} × ${analysis.height} pixels</div>
                </div>
                <div class="col-md-6">
                    <small class="text-muted">File Size:</small>
                    <div>${CyberCloak.formatFileSize(analysis.file_size)}</div>
                </div>
                <div class="col-md-6">
                    <small class="text-muted">Max Capacity:</small>
                    <div>${analysis.max_capacity_chars.toLocaleString()} characters</div>
                </div>
                <div class="col-md-6">
                    <small class="text-muted">Security Score:</small>
                    <div class="d-flex align-items-center">
                        <span class="badge bg-${getScoreColor(analysis.security_score)} me-2">
                            ${analysis.security_score}%
                        </span>
                        <small class="text-muted">${analysis.detectability_risk} risk</small>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function getScoreColor(score) {
    if (score >= 80) return 'success';
    if (score >= 60) return 'warning';
    return 'danger';
}

function nextStep() {
    const steps = document.querySelectorAll('.step');
    const nextBtn = document.getElementById('nextBtn');
    
    // Hide current step
    steps[currentStep - 1].style.display = 'none';
    
    currentStep++;
    
    // Show next step
    if (currentStep <= steps.length) {
        steps[currentStep - 1].style.display = 'block';
        
        switch (currentStep) {
            case 2:
                nextBtn.textContent = 'Process Message';
                break;
            case 3:
                nextBtn.style.display = 'none';
                processMessage();
                break;
            case 4:
                nextBtn.style.display = 'none';
                break;
        }
    }
}

async function processMessage() {
    const message = document.getElementById('secretMessage').value;
    const password = document.getElementById('encryptionPassword').value;
    
    if (!message.trim()) {
        CyberCloak.showNotification('Please enter a message to hide', 'error');
        return;
    }
    
    if (!sessionId) {
        CyberCloak.showNotification('No active session. Please upload an image first.', 'error');
        return;
    }
    
    try {
        const formData = new FormData();
        formData.append('session_id', sessionId);
        formData.append('message', message);
        formData.append('password', password);
        
        const response = await fetch('/api/encrypt_hide', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayResults(result);
            nextStep(); // Move to step 4
        } else {
            throw new Error(result.error || 'Processing failed');
        }
    } catch (error) {
        CyberCloak.showNotification(error.message, 'error');
        // Go back to step 2
        currentStep = 1;
        nextStep();
    }
}

function displayResults(result) {
    const securityAnalysis = document.getElementById('securityAnalysis');
    const downloadBtn = document.getElementById('downloadBtn');
    
    if (result.security_analysis) {
        const analysis = result.security_analysis;
        securityAnalysis.innerHTML = `
            <div class="security-analysis p-3 border rounded">
                <h6><i class="fas fa-shield-alt me-2"></i>Security Analysis</h6>
                <div class="row g-2">
                    <div class="col-md-6">
                        <small class="text-muted">Overall Security:</small>
                        <div class="d-flex align-items-center">
                            <div class="progress flex-grow-1 me-2" style="height: 20px;">
                                <div class="progress-bar bg-${getScoreColor(analysis.overall_security)}" 
                                     style="width: ${analysis.overall_security}%">
                                    ${analysis.overall_security}%
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <small class="text-muted">Detection Resistance:</small>
                        <div>
                            <span class="badge bg-${analysis.detection_resistance === 'Low' ? 'success' : 
                                                   analysis.detection_resistance === 'Medium' ? 'warning' : 'danger'}">
                                ${analysis.detection_resistance}
                            </span>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <small class="text-muted">LSB Efficiency:</small>
                        <div>${analysis.lsb_efficiency}%</div>
                    </div>
                    <div class="col-md-6">
                        <small class="text-muted">Encryption:</small>
                        <div>${analysis.encryption_strength}</div>
                    </div>
                </div>
            </div>
        `;
    }
    
    // Set up download button
    downloadBtn.onclick = () => {
        window.location.href = `/download/${result.output_file}`;
    };
}

function resetUploadModal() {
    // Reset all steps
    const steps = document.querySelectorAll('.step');
    steps.forEach((step, index) => {
        step.style.display = index === 0 ? 'block' : 'none';
    });
    
    // Reset variables
    currentStep = 1;
    sessionId = null;
    uploadedFile = null;
    
    // Reset form elements
    document.getElementById('inputImage').value = '';
    document.getElementById('secretMessage').value = '';
    document.getElementById('encryptionPassword').value = '';
    
    // Reset UI elements
    document.getElementById('imagePreview').style.display = 'none';
    document.getElementById('imageAnalysis').innerHTML = '';
    document.getElementById('securityAnalysis').innerHTML = '';
    
    // Reset buttons
    const nextBtn = document.getElementById('nextBtn');
    nextBtn.style.display = 'inline-block';
    nextBtn.disabled = true;
    nextBtn.textContent = 'Next';
    
    // Clear any existing notifications
    document.querySelectorAll('.alert.position-fixed').forEach(alert => {
        alert.remove();
    });
}

// Table row click handling for job details
document.addEventListener('click', function(e) {
    if (e.target.closest('.table tbody tr')) {
        const row = e.target.closest('tr');
        const downloadBtn = row.querySelector('.btn');
        
        if (downloadBtn && e.target !== downloadBtn) {
            // Add visual feedback for row interaction
            row.style.backgroundColor = 'var(--glass-border)';
            setTimeout(() => {
                row.style.backgroundColor = '';
            }, 200);
        }
    }
});

// Auto-refresh dashboard data (optional)
function refreshDashboard() {
    // Refresh page to get latest data
    // In a real application, this would be an AJAX call
    window.location.reload();
}

// Set up periodic refresh (every 5 minutes)
setInterval(refreshDashboard, 300000);

// Export functions for global access
window.Dashboard = {
    nextStep,
    resetUploadModal,
    refreshDashboard
};