/**
 * Chat functionality for the secure chat application
 */

// Use global socket from main.js
let currentRoom = 'general';
let userId = '';
let username = '';
let isTyping = false;
let typingTimeout;

// Chat message handling
function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();
    const mediaInput = document.getElementById('mediaInput');
    
    if (window.isSocketConnected && window.isSocketConnected()) {
        if (message || mediaInput.files.length > 0) {
            // Clear input first
            input.value = '';
            
            // If there's a media file to upload
            if (mediaInput.files.length > 0) {
                const file = mediaInput.files[0];
                if (file.size > 5 * 1024 * 1024) { // Reduced to 5MB limit
                    alert('File size exceeds 5MB limit');
                    return;
                }
                
                // Show loading indicator
                const sendButton = document.querySelector('.message-input button:last-child');
                const originalText = sendButton.innerHTML;
                sendButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
                sendButton.disabled = true;
                
                const reader = new FileReader();
                reader.onload = function(e) {
                    const base64Data = e.target.result;
                    
                    // Send message with media
                    window.socket.emit('message', {
                        room: currentRoom,
                        user_id: userId,
                        message: message || '',
                        media: {
                            type: file.type,
                            data: base64Data,
                            name: file.name
                        }
                    }, function(ack) {
                        // Callback when server acknowledges receipt
                        console.log("Media message acknowledged:", ack);
                        
                        // Reset button
                        sendButton.innerHTML = originalText;
                        sendButton.disabled = false;
                    });
                    
                    // Reset media input and button
                    mediaInput.value = '';
                    document.getElementById('mediaBtn').innerHTML = '<i class="fas fa-image"></i>';
                    document.getElementById('mediaBtn').style.color = 'var(--text-secondary)';
                    
                    console.log("Media message sent:", {
                        type: file.type,
                        size: base64Data.length,
                        name: file.name
                    });
                };
                
                reader.onerror = function(e) {
                    console.error("FileReader error:", e);
                    alert("Error reading file: " + e);
                    
                    // Reset button
                    sendButton.innerHTML = originalText;
                    sendButton.disabled = false;
                };
                
                reader.readAsDataURL(file);
            } else {
                // Send text-only message
                window.socket.emit('message', {
                    room: currentRoom,
                    user_id: userId,
                    message: message
                });
            }
        }
    } else {
        alert("You are not connected. Please refresh the page and try again.");
    }
}

// Load existing messages when joining a room
function loadRoomMessages(room) {
    fetch(`/chat/${room}/messages?user_id=${userId}`)
        .then(response => response.json())
        .then(messages => {
            const messageContainer = document.getElementById('messageContainer');
            messageContainer.innerHTML = '';
            
            let currentDate = null;
            messages.forEach(msg => {
                // Add date separator if needed
                if (currentDate !== msg.date) {
                    currentDate = msg.date;
                    const dateDiv = document.createElement('div');
                    dateDiv.className = 'message-date';
                    dateDiv.textContent = msg.date;
                    messageContainer.appendChild(dateDiv);
                }
                
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${msg.is_sent ? 'sent' : ''}`;
                messageDiv.setAttribute('data-message-id', msg.id || msg.timestamp);
                
                const messageWrapper = document.createElement('div');
                messageWrapper.className = 'message-wrapper';
                
                const content = document.createElement('div');
                content.className = 'message-content';
                content.textContent = msg.message;
                content.dataset.date = msg.date;
                
                const timeDiv = document.createElement('div');
                timeDiv.className = 'message-time';
                timeDiv.textContent = msg.time;
                
                const reactions = document.createElement('div');
                reactions.className = 'reactions';
                
                messageWrapper.appendChild(content);
                messageWrapper.appendChild(timeDiv);
                messageDiv.appendChild(messageWrapper);
                messageDiv.appendChild(reactions);
                messageContainer.appendChild(messageDiv);
            });
            messageContainer.scrollTop = messageContainer.scrollHeight;
        })
        .catch(error => {
            console.error('Error loading messages:', error);
        });
}

// Event listeners for chat input
document.addEventListener('DOMContentLoaded', function() {
    const messageInput = document.getElementById('messageInput');
    
    if (messageInput) {
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });

        messageInput.addEventListener('input', () => {
            if (!isTyping) {
                isTyping = true;
                window.socket.emit('typing', {
                    room: currentRoom,
                    user_id: userId,
                    is_typing: true
                });
            }

            clearTimeout(typingTimeout);
            typingTimeout = setTimeout(() => {
                isTyping = false;
                window.socket.emit('typing', {
                    room: currentRoom,
                    user_id: userId,
                    is_typing: false
                });
            }, 1000);
        });
    }
});

// Socket event handlers
window.socket.on('connect', () => {
    document.getElementById('status').textContent = 'Online';
    // Join the room after profile and room setup is complete
});

window.socket.on('disconnect', () => {
    document.getElementById('status').textContent = 'Offline';
    // Reset online count when disconnected
    const countElement = document.getElementById('onlineCount');
    countElement.innerHTML = `<i class="fas fa-circle"></i><span>0 online</span>`;
});

window.socket.on('message', (data) => {
    console.log("Received message data:", Object.keys(data));
    if (data.media) {
        console.log("Received media message:", {
            type: data.media.type,
            size: data.media.data.length,
            name: data.media.name
        });
    }
    
    const messageContainer = document.getElementById('messageContainer');
    
    // Check if we need to add a date separator
    const lastMessage = messageContainer.lastElementChild;
    if (!lastMessage || lastMessage.classList.contains('message-date') || 
        lastMessage.querySelector('.message-content').dataset.date !== data.date) {
        const dateDiv = document.createElement('div');
        dateDiv.className = 'message-date';
        dateDiv.textContent = data.date;
        messageContainer.appendChild(dateDiv);
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${data.user_id === userId ? 'sent' : ''}`;
    messageDiv.setAttribute('data-message-id', data.id || data.timestamp);
    
    const messageWrapper = document.createElement('div');
    messageWrapper.className = 'message-wrapper';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    
    // Add text message if it exists
    if (data.message && data.message.trim()) {
        content.textContent = data.message;
    }
    content.dataset.date = data.date;
    
    // Handle media content if present
    if (data.media && data.media.data) {
        if (data.media.type.startsWith('image/')) {
            const img = document.createElement('img');
            img.src = data.media.data;
            img.className = 'media-preview';
            img.alt = data.media.name || 'Image';
            img.loading = 'lazy';
            img.onclick = function() {
                openLightbox(data.media.data, 'image');
            };
            
            // If there's no text message, just show the image without the <br>
            if (!data.message || !data.message.trim()) {
                content.textContent = '';
            } else {
                content.appendChild(document.createElement('br'));
            }
            
            content.appendChild(img);
        } else if (data.media.type.startsWith('video/')) {
            const video = document.createElement('video');
            video.src = data.media.data;
            video.className = 'media-preview';
            video.controls = true;
            video.preload = 'metadata';
            video.onclick = function(e) {
                if (e.target === video) {
                    openLightbox(data.media.data, 'video');
                }
            };
            
            // If there's no text message, just show the video without the <br>
            if (!data.message || !data.message.trim()) {
                content.textContent = '';
            } else {
                content.appendChild(document.createElement('br'));
            }
            
            content.appendChild(video);
        }
    }
    
    const timeDiv = document.createElement('div');
    timeDiv.className = 'message-time';
    timeDiv.textContent = data.time;
    
    const reactions = document.createElement('div');
    reactions.className = 'reactions';
    
    messageWrapper.appendChild(content);
    messageWrapper.appendChild(timeDiv);
    messageDiv.appendChild(messageWrapper);
    messageDiv.appendChild(reactions);
    messageContainer.appendChild(messageDiv);
    messageContainer.scrollTop = messageContainer.scrollHeight;
});

window.socket.on('online_count', (data) => {
    if (data.room === currentRoom) {  // Only update count for current room
        const countElement = document.getElementById('onlineCount');
        countElement.innerHTML = `<i class="fas fa-circle"></i><span>${data.count} online</span>`;
    }
});

window.socket.on('status', (data) => {
    const messageContainer = document.getElementById('messageContainer');
    
    // Create a wrapper div for status messages if it doesn't exist
    let statusWrapper = document.getElementById('statusMessagesWrapper');
    if (!statusWrapper) {
        statusWrapper = document.createElement('div');
        statusWrapper.id = 'statusMessagesWrapper';
        statusWrapper.style.display = 'flex';
        statusWrapper.style.flexDirection = 'column';
        statusWrapper.style.alignItems = 'center';
        statusWrapper.style.width = '100%';
        messageContainer.appendChild(statusWrapper);
    }
    
    const statusDiv = document.createElement('div');
    statusDiv.className = 'status-message';
    statusDiv.textContent = data.msg;
    statusWrapper.appendChild(statusDiv);
    messageContainer.scrollTop = messageContainer.scrollHeight;

    // Remove the status message after 5 seconds
    setTimeout(() => {
        statusDiv.style.opacity = '0';
        statusDiv.style.transform = 'translateY(-10px)';
        setTimeout(() => {
            statusDiv.remove();
            // Remove wrapper if empty
            if (statusWrapper.children.length === 0) {
                statusWrapper.remove();
            }
        }, 300);
    }, 5000);
});

window.socket.on('typing_status', (data) => {
    const indicator = document.getElementById('typingIndicator');
    if (data.typing_users && data.typing_users.length > 0) {
        const typingUsers = data.typing_users.filter(id => id !== userId);
        if (typingUsers.length > 0) {
            indicator.textContent = `${typingUsers.join(', ')} ${typingUsers.length === 1 ? 'is' : 'are'} typing...`;
        } else {
            indicator.textContent = '';
        }
    } else {
        indicator.textContent = '';
    }
});

window.socket.on('reaction_update', (data) => {
    const messageElement = document.querySelector(`[data-message-id="${data.message_id}"]`);
    if (messageElement) {
        const reactionsDiv = messageElement.querySelector('.reactions');
        reactionsDiv.innerHTML = '';
        
        Object.entries(data.reactions).forEach(([reaction, users]) => {
            const reactionSpan = document.createElement('span');
            reactionSpan.className = 'reaction';
            reactionSpan.textContent = `${reaction} ${users.length}`;
            reactionsDiv.appendChild(reactionSpan);
        });
    }
});

// Handle file uploads
window.socket.on('file_uploaded', (fileInfo) => {
    const messageContainer = document.getElementById('messageContainer');
    
    // Create a message for the file upload
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${fileInfo.uploaded_by === userId ? 'sent' : ''}`;
    
    const messageWrapper = document.createElement('div');
    messageWrapper.className = 'message-wrapper';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    
    // Create file attachment
    const fileLink = document.createElement('a');
    fileLink.href = `/chat/${currentRoom}/files/${fileInfo.stored_filename}?password=${document.getElementById('setupRoomPassword').value}`;
    fileLink.target = "_blank";
    fileLink.innerHTML = `<i class="fas fa-file"></i> ${fileInfo.filename} (${Math.round(fileInfo.size / 1024)} KB)`;
    fileLink.style.display = 'block';
    fileLink.style.textDecoration = 'none';
    fileLink.style.color = 'inherit';
    fileLink.style.padding = '8px';
    
    content.appendChild(fileLink);
    
    const timeDiv = document.createElement('div');
    timeDiv.className = 'message-time';
    const date = new Date(fileInfo.uploaded_at);
    timeDiv.textContent = date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    
    messageWrapper.appendChild(content);
    messageWrapper.appendChild(timeDiv);
    messageDiv.appendChild(messageWrapper);
    messageContainer.appendChild(messageDiv);
    messageContainer.scrollTop = messageContainer.scrollHeight;
});

// Message deletion handler
window.socket.on('message_deleted', (data) => {
    const message = document.querySelector(`[data-message-id="${data.message_id}"]`);
    if (message) {
        message.style.opacity = '0.5';
        message.querySelector('.message-content').textContent = 'This message was deleted';
    }
});

// Export functions for use in other modules
window.chatFunctions = {
    sendMessage,
    loadRoomMessages
}; 