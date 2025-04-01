/**
 * Setup functionality for the secure chat application
 */

let currentTab = 'profile';

// Setup wizard tab switching
function switchTab(tab) {
    document.querySelectorAll('.setup-tab').forEach(t => {
        t.classList.remove('active');
    });
    document.querySelectorAll('.setup-tab-content').forEach(c => {
        c.classList.remove('active');
    });
    
    document.querySelector(`.setup-tab:nth-child(${tab === 'profile' ? 1 : 2})`).classList.add('active');
    document.getElementById(`${tab}Tab`).classList.add('active');
    
    currentTab = tab;
    
    // Update buttons
    if (tab === 'profile') {
        document.getElementById('setupBack').style.display = 'none';
        document.getElementById('setupNext').style.display = 'inline-flex';
        document.getElementById('setupComplete').style.display = 'none';
    } else {
        document.getElementById('setupBack').style.display = 'inline-flex';
        document.getElementById('setupNext').style.display = 'none';
        document.getElementById('setupComplete').style.display = 'inline-flex';
    }
}

// Handle avatar file selection
function handleAvatarUpload() {
    const fileInput = document.getElementById('setupAvatarFile');
    const preview = document.getElementById('avatarPreview');
    const hiddenInput = document.getElementById('setupAvatar');
    
    fileInput.addEventListener('change', function() {
        // Clear preview
        preview.innerHTML = '';
        
        if (fileInput.files && fileInput.files[0]) {
            const file = fileInput.files[0];
            
            // Check file size (max 2MB)
            if (file.size > 2 * 1024 * 1024) {
                alert('Image size must be less than 2MB');
                fileInput.value = '';
                return;
            }
            
            const reader = new FileReader();
            
            reader.onload = function(e) {
                // Store base64 data in hidden input
                hiddenInput.value = e.target.result;
                
                // Show preview
                const img = document.createElement('img');
                img.src = e.target.result;
                img.style.maxWidth = '100px';
                img.style.maxHeight = '100px';
                img.style.borderRadius = '50%';
                preview.appendChild(img);
            };
            
            reader.readAsDataURL(file);
        }
    });
}

// Move to next setup step
function setupNext() {
    // Validate profile data
    userId = document.getElementById('setupUserId').value.trim();
    username = document.getElementById('setupUsername').value.trim();
    
    if (!userId || !username) {
        alert('Please enter a User ID and Display Name');
        return;
    }
    
    // Create the profile on the server
    const avatarUrl = document.getElementById('setupAvatar').value;
    
    fetch('/user/profile', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            user_id: userId,
            username: username,
            avatar: avatarUrl
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to create profile');
        }
        return response.json();
    })
    .then(data => {
        // Switch to room tab
        switchTab('room');
    })
    .catch(error => {
        console.error('Error creating profile:', error);
        alert('Failed to create profile. Please try again.');
    });
}

// Go back to previous setup step
function setupBack() {
    switchTab('profile');
}

// Complete setup and join chat
function completeSetup() {
    const roomId = document.getElementById('setupRoomId').value.trim();
    const roomPassword = document.getElementById('setupRoomPassword').value.trim();
    
    if (!roomId || !roomPassword) {
        alert('Please enter a Room ID and Password');
        return;
    }
    
    // Show loading indicator
    const setupCompleteBtn = document.getElementById('setupComplete');
    const originalText = setupCompleteBtn.innerHTML;
    setupCompleteBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
    setupCompleteBtn.disabled = true;
    
    // Create or join the room
    fetch('/room/create', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            room_id: roomId,
            password: roomPassword
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Server responded with status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (!data.success) {
            throw new Error(data.error || 'Unknown error occurred');
        }
        
        console.log('Room created/joined successfully:', data);
        
        // Hide setup modal and show chat
        document.getElementById('setupModal').style.display = 'none';
        document.getElementById('chatContainer').style.display = 'flex';
        
        // Update UI with user info
        document.getElementById('username').textContent = username;
        document.getElementById('currentRoom').textContent = roomId;
        document.getElementById('currentRoomSidebar').textContent = roomId;
        
        // Update avatar if provided
        const avatarUrl = document.getElementById('setupAvatar').value;
        if (avatarUrl) {
            document.getElementById('userAvatar').innerHTML = `<img src="${avatarUrl}" alt="${username}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 50%;">`;
        }
        
        // Connect to the room
        currentRoom = roomId;
        // Use the global socket
        if (window.socket) {
            if (window.isSocketConnected && window.isSocketConnected()) {
                window.socket.emit('join', { room: currentRoom, user_id: userId });
                console.log('Joined room:', currentRoom);
            } else {
                console.log('Socket not connected. Setting up connection event...');
                // Set up a one-time connection event
                window.socket.once('connect', function() {
                    window.socket.emit('join', { room: currentRoom, user_id: userId });
                    console.log('Connected and joined room:', currentRoom);
                });
            }
        } else {
            console.error('Socket not initialized');
            alert('Connection issue. Please refresh the page and try again.');
        }
        
        // Load messages
        if (window.chatFunctions) {
            window.chatFunctions.loadRoomMessages(currentRoom);
        } else {
            console.error('Chat functions not loaded');
        }
    })
    .catch(error => {
        console.error('Error creating/joining room:', error);
        
        // Reset button
        setupCompleteBtn.innerHTML = originalText;
        setupCompleteBtn.disabled = false;
        
        // Check if the error is related to network issues
        if (error.name === 'TypeError' && error.message.includes('Failed to fetch')) {
            alert('Network error: Could not connect to the server. Please check your internet connection.');
        } else {
            alert('Failed to create or join room: ' + error.message);
        }
    });
}

// Handle page visibility and window closing
document.addEventListener('DOMContentLoaded', function() {
    // Initialize avatar file upload handler
    handleAvatarUpload();
    
    // Handle window/tab closing
    window.addEventListener('beforeunload', () => {
        if (typeof isConnected !== 'undefined' && isConnected) {
            socket.emit('leave', { room: currentRoom, user_id: userId });
        }
    });

    // Handle page visibility change
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            if (typeof isConnected !== 'undefined' && isConnected) {
                socket.emit('leave', { room: currentRoom, user_id: userId });
            }
        } else {
            if (typeof isConnected !== 'undefined' && isConnected) {
                socket.emit('join', { room: currentRoom, user_id: userId });
            }
        }
    });
});

// Export functions for use in other modules
window.setupFunctions = {
    switchTab,
    setupNext,
    setupBack,
    completeSetup
}; 