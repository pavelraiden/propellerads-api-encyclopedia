/**
 * PropellerAds Web Interface JavaScript
 * Handles real-time updates, API communication, and UI interactions
 */

// Global application state
window.PropellerApp = {
    socket: null,
    isConnected: false,
    apiStatus: {
        propellerads: false,
        claude: false
    },
    lastUpdate: null
};

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * Initialize the application
 */
function initializeApp() {
    console.log('Initializing PropellerAds Web Interface...');
    
    // Initialize Socket.IO connection
    initializeSocket();
    
    // Set up periodic status checks
    setInterval(checkConnectionStatus, 30000); // Every 30 seconds
    
    // Initialize tooltips
    initializeTooltips();
    
    // Set up global error handling
    setupErrorHandling();
    
    console.log('PropellerAds Web Interface initialized successfully');
}

/**
 * Initialize Socket.IO connection for real-time updates
 */
function initializeSocket() {
    try {
        PropellerApp.socket = io();
        
        PropellerApp.socket.on('connect', function() {
            console.log('Connected to server via WebSocket');
            PropellerApp.isConnected = true;
            updateConnectionStatus(true);
        });
        
        PropellerApp.socket.on('disconnect', function() {
            console.log('Disconnected from server');
            PropellerApp.isConnected = false;
            updateConnectionStatus(false);
        });
        
        PropellerApp.socket.on('status', function(data) {
            console.log('Status update:', data);
            showNotification(data.message, 'info');
        });
        
        PropellerApp.socket.on('live_stats', function(data) {
            console.log('Live stats update:', data);
            if (data.success && data.balance !== undefined) {
                updateBalanceDisplay(data.balance);
            }
        });
        
        PropellerApp.socket.on('error', function(error) {
            console.error('Socket error:', error);
            showNotification('Connection error occurred', 'error');
        });
        
    } catch (error) {
        console.error('Failed to initialize Socket.IO:', error);
        PropellerApp.isConnected = false;
    }
}

/**
 * Update connection status indicator
 */
function updateConnectionStatus(isConnected) {
    const statusElement = document.getElementById('connection-status');
    if (statusElement) {
        const icon = statusElement.querySelector('i');
        const text = statusElement.querySelector('span') || statusElement;
        
        if (isConnected) {
            icon.className = 'bi bi-circle-fill text-success';
            text.textContent = ' Connected';
        } else {
            icon.className = 'bi bi-circle-fill text-danger';
            text.textContent = ' Disconnected';
        }
    }
}

/**
 * Check API connection status
 */
async function checkConnectionStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        PropellerApp.apiStatus = {
            propellerads: data.propellerads || false,
            claude: data.claude || false
        };
        
        PropellerApp.lastUpdate = new Date();
        
        // Update UI elements if they exist
        updateApiStatusIndicators(data);
        
    } catch (error) {
        console.error('Failed to check API status:', error);
        PropellerApp.apiStatus = { propellerads: false, claude: false };
    }
}

/**
 * Update API status indicators in the UI
 */
function updateApiStatusIndicators(statusData) {
    // Update PropellerAds status
    const propellerStatus = document.querySelector('[data-status="propellerads"]');
    if (propellerStatus) {
        updateStatusElement(propellerStatus, statusData.propellerads);
    }
    
    // Update Claude status
    const claudeStatus = document.querySelector('[data-status="claude"]');
    if (claudeStatus) {
        updateStatusElement(claudeStatus, statusData.claude);
    }
    
    // Update balance if available
    if (statusData.balance !== undefined) {
        updateBalanceDisplay(statusData.balance);
    }
}

/**
 * Update a status element
 */
function updateStatusElement(element, isOnline) {
    const indicator = element.querySelector('.status-indicator');
    const text = element.querySelector('.status-text');
    
    if (indicator) {
        indicator.className = `status-indicator ${isOnline ? 'status-online' : 'status-offline'}`;
    }
    
    if (text) {
        text.textContent = isOnline ? 'Connected' : 'Disconnected';
    }
}

/**
 * Update balance display
 */
function updateBalanceDisplay(balance) {
    const balanceElements = document.querySelectorAll('[data-balance]');
    balanceElements.forEach(element => {
        element.textContent = formatCurrency(balance);
    });
}

/**
 * Format currency value
 */
function formatCurrency(amount) {
    if (amount === null || amount === undefined || isNaN(amount)) {
        return '$0.00';
    }
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

/**
 * Show notification to user
 */
function showNotification(message, type = 'info', duration = 5000) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${getBootstrapAlertClass(type)} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto-remove after duration
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, duration);
}

/**
 * Convert notification type to Bootstrap alert class
 */
function getBootstrapAlertClass(type) {
    const typeMap = {
        'success': 'success',
        'error': 'danger',
        'warning': 'warning',
        'info': 'info'
    };
    return typeMap[type] || 'info';
}

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Setup global error handling
 */
function setupErrorHandling() {
    window.addEventListener('error', function(event) {
        console.error('Global error:', event.error);
        showNotification('An unexpected error occurred', 'error');
    });
    
    window.addEventListener('unhandledrejection', function(event) {
        console.error('Unhandled promise rejection:', event.reason);
        showNotification('A network error occurred', 'error');
    });
}

/**
 * API Helper Functions
 */
window.PropellerAPI = {
    /**
     * Make API request with error handling
     */
    async request(url, options = {}) {
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    },
    
    /**
     * Get account balance
     */
    async getBalance() {
        return this.request('/api/balance');
    },
    
    /**
     * Get campaigns
     */
    async getCampaigns() {
        return this.request('/api/campaigns');
    },
    
    /**
     * Get statistics
     */
    async getStatistics(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const url = `/api/statistics${queryString ? '?' + queryString : ''}`;
        return this.request(url);
    },
    
    /**
     * Send message to Claude
     */
    async chatWithClaude(message) {
        return this.request('/api/chat', {
            method: 'POST',
            body: JSON.stringify({ message })
        });
    }
};

/**
 * Utility Functions
 */
window.PropellerUtils = {
    /**
     * Debounce function calls
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    /**
     * Format date for display
     */
    formatDate(date) {
        return new Intl.DateTimeFormat('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }).format(new Date(date));
    },
    
    /**
     * Copy text to clipboard
     */
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            showNotification('Copied to clipboard', 'success');
        } catch (error) {
            console.error('Failed to copy to clipboard:', error);
            showNotification('Failed to copy to clipboard', 'error');
        }
    },
    
    /**
     * Download data as JSON file
     */
    downloadJSON(data, filename = 'data.json') {
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
};

/**
 * Request live statistics update via WebSocket
 */
function requestLiveStats() {
    if (PropellerApp.socket && PropellerApp.isConnected) {
        PropellerApp.socket.emit('get_live_stats');
    }
}

/**
 * Export for global access
 */
window.PropellerApp = PropellerApp;
window.showNotification = showNotification;
window.requestLiveStats = requestLiveStats;
