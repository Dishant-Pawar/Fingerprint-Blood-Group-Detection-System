/**
 * Main JavaScript file for Fingerprint Blood Group Detection System
 * Handles common functionality and utilities
 */

// API Base URL
const API_BASE_URL = 'http://localhost:5000';

/**
 * Utility function to format dates
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

/**
 * Utility function to display toast messages
 */
function showToast(message, type = 'info') {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    // Style toast
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background-color: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
        color: white;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        z-index: 9999;
        max-width: 300px;
        word-wrap: break-word;
    `;
    
    // Add to body
    document.body.appendChild(toast);
    
    // Remove after 3 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

/**
 * Check if API is running
 */
async function checkAPIStatus() {
    try {
        const response = await fetch(API_BASE_URL + '/');
        const data = await response.json();
        return data.status === 'success';
    } catch (error) {
        console.error('API connection failed:', error);
        return false;
    }
}

/**
 * Validate email format
 */
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

/**
 * Validate blood group
 */
function validateBloodGroup(bloodGroup) {
    const validGroups = ['O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-'];
    return validGroups.includes(bloodGroup);
}

/**
 * Convert file to base64 (if needed for alternative implementations)
 */
function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => resolve(reader.result);
        reader.onerror = error => reject(error);
    });
}

/**
 * Disable form elements
 */
function disableFormElements(form, disabled = true) {
    const elements = form.querySelectorAll('input, select, button, textarea');
    elements.forEach(element => {
        element.disabled = disabled;
    });
}

// Log on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Fingerprint Blood Group Detection System loaded');
});
