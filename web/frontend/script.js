// Livestream Splitter Web UI JavaScript

let uploadedFile = null;
let currentJobId = null;
let pollInterval = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeFileUpload();
    loadRecentJobs();
});

// File Upload Handling
function initializeFileUpload() {
    const fileInput = document.getElementById('fileInput');
    const uploadArea = document.getElementById('uploadArea');
    const fileInfo = document.getElementById('fileInfo');
    const processBtn = document.getElementById('processBtn');

    // File input change handler
    fileInput.addEventListener('change', handleFileSelect);

    // Drag and drop handlers
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleFileDrop);

    function handleFileSelect(event) {
        const file = event.target.files[0];
        if (file) {
            uploadFile(file);
        }
    }

    function handleDragOver(event) {
        event.preventDefault();
        uploadArea.classList.add('dragover');
    }

    function handleDragLeave(event) {
        event.preventDefault();
        uploadArea.classList.remove('dragover');
    }

    function handleFileDrop(event) {
        event.preventDefault();
        uploadArea.classList.remove('dragover');
        
        const files = event.dataTransfer.files;
        if (files.length > 0) {
            uploadFile(files[0]);
        }
    }
}

async function uploadFile(file) {
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    const processBtn = document.getElementById('processBtn');

    try {
        // Validate file before upload
        if (!file) {
            throw new Error('No file selected');
        }

        // Check file size (optional - adjust limit as needed)
        const maxSize = 10 * 1024 * 1024 * 1024; // 10GB
        if (file.size > maxSize) {
            throw new Error('File too large. Maximum size is 10GB');
        }

        // Show file info
        fileName.textContent = file.name;
        fileSize.textContent = `Size: ${formatFileSize(file.size)}`;
        fileInfo.style.display = 'block';

        // Create FormData and append file
        const formData = new FormData();
        formData.append('file', file, file.name);

        // Create progress indicator
        const progressDiv = document.createElement('div');
        progressDiv.id = 'uploadProgress';
        progressDiv.style.cssText = `
            margin-top: 10px;
            padding: 10px;
            background: #f0f0f0;
            border-radius: 5px;
            display: none;
        `;
        progressDiv.innerHTML = `
            <div style="font-weight: bold; margin-bottom: 5px;">Uploading file...</div>
            <div style="background: #ddd; border-radius: 3px; overflow: hidden;">
                <div id="uploadProgressBar" style="width: 0%; height: 20px; background: #4CAF50; transition: width 0.3s;"></div>
            </div>
            <div id="uploadProgressText" style="margin-top: 5px; font-size: 12px;">0%</div>
        `;
        fileInfo.appendChild(progressDiv);

        // Show upload progress
        progressDiv.style.display = 'block';
        showNotification('Starting upload...', 'info');

        // Upload file to server with progress tracking
        const xhr = new XMLHttpRequest();
        
        // Track upload progress
        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                const percentComplete = (e.loaded / e.total) * 100;
                const progressBar = document.getElementById('uploadProgressBar');
                const progressText = document.getElementById('uploadProgressText');
                
                if (progressBar && progressText) {
                    progressBar.style.width = percentComplete + '%';
                    progressText.textContent = `${Math.round(percentComplete)}% (${formatFileSize(e.loaded)} of ${formatFileSize(e.total)})`;
                }
                
                // Update notification less frequently to avoid spam
                if (percentComplete % 10 === 0 || percentComplete > 95) {
                    showNotification(`Upload progress: ${Math.round(percentComplete)}%`, 'info');
                }
            }
        });

        // Handle completion
        xhr.addEventListener('load', () => {
            const progressDiv = document.getElementById('uploadProgress');
            if (progressDiv) {
                progressDiv.style.display = 'none';
            }
            
            if (xhr.status === 200) {
                const result = JSON.parse(xhr.responseText);
                uploadedFile = result;
                
                // Enable process button
                processBtn.disabled = false;
                
                showNotification('File uploaded successfully!', 'success');
            } else {
                throw new Error(`Upload failed with status: ${xhr.status}`);
            }
        });

        // Handle errors
        xhr.addEventListener('error', () => {
            const progressDiv = document.getElementById('uploadProgress');
            if (progressDiv) {
                progressDiv.style.display = 'none';
            }
            throw new Error('Network error during upload');
        });

        // Handle timeout
        xhr.addEventListener('timeout', () => {
            const progressDiv = document.getElementById('uploadProgress');
            if (progressDiv) {
                progressDiv.style.display = 'none';
            }
            throw new Error('Upload timed out');
        });

        // Send request
        xhr.open('POST', '/api/upload');
        xhr.send(formData);

    } catch (error) {
        showNotification('Upload failed: ' + error.message, 'error');
        console.error('Upload error:', error);
        
        // Reset UI on error
        const progressDiv = document.getElementById('uploadProgress');
        if (progressDiv) {
            progressDiv.style.display = 'none';
        }
        fileInfo.style.display = 'none';
        processBtn.disabled = true;
    }
}

// Start Processing
async function startProcessing() {
    if (!uploadedFile) {
        showNotification('Please upload a file first', 'error');
        return;
    }

    const settings = getFormSettings();
    const progressSection = document.getElementById('progressSection');
    const resultsSection = document.getElementById('resultsSection');

    try {
        // Hide results, show progress
        resultsSection.style.display = 'none';
        progressSection.style.display = 'block';

        // Start processing
        const response = await fetch('/api/split', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                filename: uploadedFile.filename,
                ...settings
            })
        });

        if (!response.ok) {
            throw new Error('Failed to start processing');
        }

        const result = await response.json();
        currentJobId = result.job_id;

        // Start polling for status
        startStatusPolling();

        showNotification('Processing started!', 'success');

    } catch (error) {
        showNotification('Failed to start processing: ' + error.message, 'error');
        console.error('Processing error:', error);
    }
}

// Get form settings
function getFormSettings() {
    return {
        max_length: parseInt(document.getElementById('maxLength').value),
        quality: document.getElementById('quality').value,
        format: document.getElementById('format').value,
        naming_pattern: document.getElementById('namingPattern').value
    };
}

// Status Polling
function startStatusPolling() {
    if (pollInterval) {
        clearInterval(pollInterval);
    }

    pollInterval = setInterval(async () => {
        try {
            const response = await fetch(`/api/jobs/${currentJobId}`);
            if (!response.ok) {
                throw new Error('Failed to get job status');
            }

            const job = await response.json();
            updateProgress(job);

            if (job.status === 'completed' || job.status === 'failed') {
                clearInterval(pollInterval);
                pollInterval = null;

                if (job.status === 'completed') {
                    showResults(job);
                } else {
                    showNotification('Processing failed: ' + job.error, 'error');
                }
            }

        } catch (error) {
            console.error('Polling error:', error);
        }
    }, 2000); // Poll every 2 seconds
}

// Update Progress Display
function updateProgress(job) {
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    const statusMessage = document.getElementById('statusMessage');

    progressFill.style.width = job.progress + '%';
    progressText.textContent = job.progress + '%';
    statusMessage.textContent = job.message;
}

// Show Results
function showResults(job) {
    const progressSection = document.getElementById('progressSection');
    const resultsSection = document.getElementById('resultsSection');
    const downloadList = document.getElementById('downloadList');

    // Hide progress, show results
    progressSection.style.display = 'none';
    resultsSection.style.display = 'block';

    // Generate download links
    downloadList.innerHTML = '';
    job.output_files.forEach(filename => {
        const downloadItem = document.createElement('div');
        downloadItem.className = 'download-item';
        downloadItem.innerHTML = `
            <span class="download-filename">${filename}</span>
            <a href="/api/download/${job.id}/${filename}" class="download-btn" download>
                📥 Download
            </a>
        `;
        downloadList.appendChild(downloadItem);
    });

    // Refresh jobs list
    loadRecentJobs();
}

// Load Recent Jobs
async function loadRecentJobs() {
    try {
        const response = await fetch('/api/jobs');
        if (!response.ok) {
            throw new Error('Failed to load jobs');
        }

        const jobs = await response.json();
        displayJobs(jobs);

    } catch (error) {
        console.error('Failed to load jobs:', error);
    }
}

// Display Jobs
function displayJobs(jobs) {
    const jobsList = document.getElementById('jobsList');
    
    if (jobs.length === 0) {
        jobsList.innerHTML = '<p class="no-jobs">No recent jobs</p>';
        return;
    }

    jobsList.innerHTML = '';
    jobs.slice(-5).reverse().forEach(job => { // Show last 5 jobs
        const jobItem = document.createElement('div');
        jobItem.className = `job-item ${job.status}`;
        jobItem.innerHTML = `
            <div class="job-header">
                <span class="job-id">Job #${job.id}</span>
                <span class="job-status ${job.status}">${job.status}</span>
            </div>
            <div class="job-message">${job.message}</div>
            <small>${formatDateTime(job.created_at)}</small>
        `;
        jobsList.appendChild(jobItem);
    });
}

// Reset Form
function resetForm() {
    // Reset file upload
    document.getElementById('fileInput').value = '';
    document.getElementById('fileInfo').style.display = 'none';
    document.getElementById('processBtn').disabled = true;
    
    // Hide sections
    document.getElementById('progressSection').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'none';
    
    // Reset variables
    uploadedFile = null;
    currentJobId = null;
    
    if (pollInterval) {
        clearInterval(pollInterval);
        pollInterval = null;
    }
}

// Utility Functions
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatDateTime(isoString) {
    const date = new Date(isoString);
    return date.toLocaleString();
}

function showNotification(message, type = 'info', persistent = false) {
    // Remove existing progress notifications if showing new one
    if (message.includes('Upload progress') || message.includes('Starting upload')) {
        const existing = document.querySelector('.notification-info');
        if (existing) {
            existing.remove();
        }
    }
    
    // Simple notification system
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'success' ? '#4CAF50' : type === 'error' ? '#f44336' : '#2196F3'};
        color: white;
        border-radius: 8px;
        z-index: 1000;
        animation: slideIn 0.3s ease;
        max-width: 300px;
        word-wrap: break-word;
    `;
    
    document.body.appendChild(notification);
    
    // Don't auto-remove if persistent or if it's a progress notification
    if (!persistent && !message.includes('Upload progress')) {
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.animation = 'slideOut 0.3s ease';
                setTimeout(() => {
                    if (notification.parentNode) {
                        document.body.removeChild(notification);
                    }
                }, 300);
            }
        }, 3000);
    }
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);