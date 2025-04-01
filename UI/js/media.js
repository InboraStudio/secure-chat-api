/**
 * Media handling functionality for the secure chat application
 */

// Toggle media upload dialog
function toggleMediaUpload() {
    document.getElementById('mediaInput').click();
}

// Handle media file selection
document.addEventListener('DOMContentLoaded', function() {
    const mediaInput = document.getElementById('mediaInput');
    
    if (mediaInput) {
        mediaInput.addEventListener('change', function(e) {
            if (this.files.length > 0) {
                const file = this.files[0];
                // Update the media button to show file name
                document.getElementById('mediaBtn').innerHTML = '<i class="fas fa-check"></i>';
                document.getElementById('mediaBtn').style.color = 'var(--primary-color)';
            } else {
                document.getElementById('mediaBtn').innerHTML = '<i class="fas fa-image"></i>';
                document.getElementById('mediaBtn').style.color = 'var(--text-secondary)';
            }
        });
    }
});

// Media lightbox functionality
function openLightbox(src, type) {
    const lightbox = document.getElementById('mediaLightbox');
    const lightboxImage = document.getElementById('lightboxImage');
    const lightboxVideo = document.getElementById('lightboxVideo');
    
    if (type === 'image') {
        lightboxImage.src = src;
        lightboxImage.style.display = 'block';
        lightboxVideo.style.display = 'none';
    } else if (type === 'video') {
        lightboxVideo.src = src;
        lightboxVideo.style.display = 'block';
        lightboxImage.style.display = 'none';
    }
    
    lightbox.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeLightbox() {
    const lightbox = document.getElementById('mediaLightbox');
    lightbox.classList.remove('active');
    document.body.style.overflow = 'auto';
    
    // Reset sources
    document.getElementById('lightboxImage').src = '';
    document.getElementById('lightboxVideo').src = '';
}

// Export functions for use in other modules
window.mediaFunctions = {
    toggleMediaUpload,
    openLightbox,
    closeLightbox
}; 