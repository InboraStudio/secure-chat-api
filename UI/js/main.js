/**
 * Main entry point for the secure chat application
 */

// Make the socket globally available
window.socket = io();
let socketConnected = false;

// When page loads
document.addEventListener('DOMContentLoaded', function() {
    // Update connection status when socket connects
    socket.on('connect', function() {
        console.log('Socket connected successfully');
        socketConnected = true;
        document.getElementById('status').textContent = 'Online';
    });
    
    socket.on('connect_error', function(error) {
        console.error('Connection error:', error);
        socketConnected = false;
        document.getElementById('status').textContent = 'Offline';
        alert('Connection error: ' + error.message);
    });
    
    socket.on('error', function(error) {
        console.error('Socket error:', error);
        alert('Socket error: ' + error);
    });
    
    socket.on('disconnect', function() {
        console.log('Socket disconnected');
        socketConnected = false;
        document.getElementById('status').textContent = 'Offline';
        // Reset online count when disconnected
        const countElement = document.getElementById('onlineCount');
        if (countElement) {
            countElement.innerHTML = `<i class="fas fa-circle"></i><span>0 online</span>`;
        }
    });
    
    // Create folders for JS files
    createJSFolders();
    
    // Initialize click handlers
    initializeClickHandlers();
});

// Helper function to check socket connection status
window.isSocketConnected = function() {
    return socketConnected;
};

// Create folders needed for JS files
function createJSFolders() {
    // This is just a placeholder - in a real application, 
    // this might create necessary local storage structures
    console.log('Application initialized');
}

// Initialize click handlers for buttons and other elements
function initializeClickHandlers() {
    // Handle setup tabs
    const setupTabs = document.querySelectorAll('.setup-tab');
    if (setupTabs) {
        setupTabs.forEach(tab => {
            tab.addEventListener('click', function() {
                const tabName = this.textContent.split('.')[1].trim().toLowerCase();
                if (window.setupFunctions && window.setupFunctions.switchTab) {
                    window.setupFunctions.switchTab(tabName);
                }
            });
        });
    }
    
    // Setup next button
    const setupNextBtn = document.getElementById('setupNext');
    if (setupNextBtn) {
        setupNextBtn.addEventListener('click', function() {
            if (window.setupFunctions && window.setupFunctions.setupNext) {
                window.setupFunctions.setupNext();
            }
        });
    }
    
    // Setup back button
    const setupBackBtn = document.getElementById('setupBack');
    if (setupBackBtn) {
        setupBackBtn.addEventListener('click', function() {
            if (window.setupFunctions && window.setupFunctions.setupBack) {
                window.setupFunctions.setupBack();
            }
        });
    }
    
    // Setup complete button
    const setupCompleteBtn = document.getElementById('setupComplete');
    if (setupCompleteBtn) {
        setupCompleteBtn.addEventListener('click', function() {
            if (window.setupFunctions && window.setupFunctions.completeSetup) {
                window.setupFunctions.completeSetup();
            }
        });
    }
    
    // Media upload button
    const mediaBtn = document.getElementById('mediaBtn');
    if (mediaBtn) {
        mediaBtn.addEventListener('click', function() {
            if (window.mediaFunctions && window.mediaFunctions.toggleMediaUpload) {
                window.mediaFunctions.toggleMediaUpload();
            }
        });
    }
    
    // Send message button
    const sendBtn = document.querySelector('.message-input button:last-child');
    if (sendBtn) {
        sendBtn.addEventListener('click', function() {
            if (window.chatFunctions && window.chatFunctions.sendMessage) {
                window.chatFunctions.sendMessage();
            }
        });
    }
    
    // Media lightbox close button
    const lightboxCloseBtn = document.querySelector('.media-lightbox-close');
    if (lightboxCloseBtn) {
        lightboxCloseBtn.addEventListener('click', function() {
            if (window.mediaFunctions && window.mediaFunctions.closeLightbox) {
                window.mediaFunctions.closeLightbox();
            }
        });
    }
}

// Expose socket to other modules
window.getSocket = function() {
    return socket;
}; 