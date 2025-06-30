// Main JavaScript file for PDFProva
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    if (window.bootstrap) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Initialize file upload handlers
    initializeFileUploads();

    // Initialize form validations
    initializeFormValidations();

    // Initialize smooth scrolling
    initializeSmoothScrolling();

    // Initialize search functionality
    initializeSearch();

    // Initialize dark mode toggle
    initializeDarkMode();
});

// File upload functionality
function initializeFileUploads() {
    const fileInputs = document.querySelectorAll('input[type="file"]');

    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            validateFileUpload(this);
        });

        // Add drag and drop functionality
        const container = input.closest('.card-body') || input.closest('.container') || input.parentNode;
        if (container) {
            addDragDropFunctionality(container, input);
        }
    });
}

// Validate file uploads
function validateFileUpload(input) {
    const file = input.files[0];
    if (!file) return;

    const maxSize = 16 * 1024 * 1024; // 16MB
    const allowedTypes = ['application/pdf'];

    // Check file size
    if (file.size > maxSize) {
        showAlert('Arquivo muito grande. O tamanho máximo permitido é 16MB.', 'danger');
        input.value = '';
        return false;
    }

    // Check file type
    if (!allowedTypes.includes(file.type)) {
        showAlert('Tipo de arquivo não permitido. Apenas arquivos PDF são aceitos.', 'danger');
        input.value = '';
        return false;
    }

    // Show file info
    showFileInfo(input, file);
    return true;
}

// Show file information
function showFileInfo(input, file) {
    const fileSize = formatFileSize(file.size);
    const fileName = file.name;
    let container = input.closest('.mb-3') || input.parentNode;

    // Remove existing info
    const existingInfo = container.querySelector('.file-info');
    if (existingInfo) {
        existingInfo.remove();
    }

    // Create new info element
    const infoElement = document.createElement('div');
    infoElement.className = 'file-info alert alert-success mt-2';
    infoElement.innerHTML = `
        <i class="fas fa-file-pdf me-2"></i>
        <strong>${fileName}</strong> (${fileSize})
        <button type="button" class="btn-close float-end" onclick="clearFile('${input.id}')"></button>
    `;

    container.appendChild(infoElement);
}

// Clear file input
function clearFile(inputId) {
    const input = document.getElementById(inputId);
    if (input) {
        input.value = '';
        const fileInfo = input.closest('.mb-3')?.querySelector('.file-info');
        if (fileInfo) {
            fileInfo.remove();
        }
    }
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';

    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

// Add drag and drop functionality
function addDragDropFunctionality(container, input) {
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        container.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        container.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        container.addEventListener(eventName, unhighlight, false);
    });

    function highlight(e) {
        container.classList.add('dragover');
    }

    function unhighlight(e) {
        container.classList.remove('dragover');
    }

    container.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;

        if (files.length > 0) {
            input.files = files;
            validateFileUpload(input);
        }
    }
}

// Form validation
function initializeFormValidations() {
    const forms = document.querySelectorAll('form[data-validate="true"]');

    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                e.stopPropagation();
            }
            this.classList.add('was-validated');
        });
    });
}

// Validate form
function validateForm(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;

    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
            field.classList.add('is-valid');
        }
    });

    // Email validation
    const emailFields = form.querySelectorAll('input[type="email"]');
    emailFields.forEach(field => {
        if (field.value && !isValidEmail(field.value)) {
            field.classList.add('is-invalid');
            isValid = false;
        }
    });

    // Password validation
    const passwordFields = form.querySelectorAll('input[type="password"]');
    passwordFields.forEach(field => {
        if (field.value && field.value.length < 6) {
            field.classList.add('is-invalid');
            isValid = false;
        }
    });

    return isValid;
}

// Email validation
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Show alert messages
function showAlert(message, type = 'info', duration = 5000) {
    const alertContainer = document.createElement('div');
    alertContainer.className = `alert alert-${type} alert-dismissible fade show`;
    alertContainer.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    // Insert at top of main content
    const main = document.querySelector('main');
    if (main) {
        main.insertBefore(alertContainer, main.firstChild);
    } else {
        document.body.insertBefore(alertContainer, document.body.firstChild);
    }

    // Auto dismiss
    if (duration > 0) {
        setTimeout(() => {
            if (alertContainer.parentNode) {
                alertContainer.remove();
            }
        }, duration);
    }
}

// Smooth scrolling
function initializeSmoothScrolling() {
    const links = document.querySelectorAll('a[href^="#"]');

    links.forEach(link => {
        link.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);

            if (targetElement) {
                e.preventDefault();
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Search functionality
function initializeSearch() {
    const searchInputs = document.querySelectorAll('input[type="search"], input[placeholder*="buscar"], input[placeholder*="Buscar"]');

    searchInputs.forEach(input => {
        let searchTimeout;

        input.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                performSearch(this.value, input);
            }, 300);
        });
    });
}

// Perform search
function performSearch(query, input) {
    if (query.length < 2) return;

    // Add search logic here based on the page context
    console.log('Searching for:', query);

    // Show loading state
    input.classList.add('loading');

    // Simulate search delay
    setTimeout(() => {
        input.classList.remove('loading');
        // Handle search results here
    }, 500);
}

// Utility functions
const Utils = {
    // Debounce function
    debounce: function(func, wait, immediate) {
        let timeout;
        return function executedFunction() {
            const context = this;
            const args = arguments;

            const later = function() {
                timeout = null;
                if (!immediate) func.apply(context, args);
            };

            const callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);

            if (callNow) func.apply(context, args);
        };
    },

    // Throttle function
    throttle: function(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },

    // Generate UUID
    generateUUID: function() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0;
            const v = c == 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    },

    // Format date
    formatDate: function(date, options = {}) {
        const defaultOptions = {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        };

        return new Date(date).toLocaleDateString('pt-BR', { ...defaultOptions, ...options });
    },

    // Copy to clipboard
    copyToClipboard: function(text) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text).then(() => {
                showAlert('Texto copiado para a área de transferência!', 'success', 2000);
            }).catch(() => {
                this.fallbackCopyToClipboard(text);
            });
        } else {
            this.fallbackCopyToClipboard(text);
        }
    },

    // Fallback copy to clipboard
    fallbackCopyToClipboard: function(text) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();

        try {
            document.execCommand('copy');
            showAlert('Texto copiado para a área de transferência!', 'success', 2000);
        } catch (err) {
            showAlert('Erro ao copiar texto.', 'danger', 3000);
        }

        document.body.removeChild(textArea);
    }
};

// Progress bar utilities
const ProgressBar = {
    create: function(container, options = {}) {
        const progress = document.createElement('div');
        progress.className = 'progress';
        progress.innerHTML = `<div class="progress-bar" role="progressbar" style="width: 0%"></div>`;

        if (typeof container === 'string') {
            container = document.querySelector(container);
        }

        container.appendChild(progress);
        return progress.querySelector('.progress-bar');
    },

    update: function(progressBar, value, animated = true) {
        if (animated) {
            progressBar.classList.add('progress-bar-animated');
        }
        progressBar.style.width = value + '%';
        progressBar.setAttribute('aria-valuenow', value);
    },

    complete: function(progressBar) {
        this.update(progressBar, 100);
        setTimeout(() => {
            progressBar.classList.remove('progress-bar-animated');
            progressBar.classList.add('bg-success');
        }, 500);
    }
};

// Loading states
const Loading = {
    show: function(element, text = 'Carregando...') {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }

        element.dataset.originalContent = element.innerHTML;
        element.innerHTML = `<i class="fas fa-spinner fa-spin me-2"></i>${text}`;
        element.disabled = true;
        element.classList.add('loading');
    },

    hide: function(element) {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }

        if (element.dataset.originalContent) {
            element.innerHTML = element.dataset.originalContent;
            delete element.dataset.originalContent;
        }

        element.disabled = false;
        element.classList.remove('loading');
    }
};

// Dark mode toggle
function initializeDarkMode() {
    const btn = document.getElementById('toggle-dark');
    if (!btn) return;
    const body = document.body;
    if (localStorage.getItem('dark-mode') === 'true') {
        body.classList.add('dark-mode');
        btn.innerHTML = '<i class="fas fa-sun"></i>';
    }
    btn.addEventListener('click', function() {
        body.classList.toggle('dark-mode');
        const isDark = body.classList.contains('dark-mode');
        btn.innerHTML = isDark
            ? '<i class="fas fa-sun"></i>'
            : '<i class="fas fa-moon"></i>';
        localStorage.setItem('dark-mode', isDark);
    });
}

// Export utilities for use in other scripts
window.PDFProva = {
    Utils,
    ProgressBar,
    Loading,
    showAlert,
    validateFileUpload,
    formatFileSize
};