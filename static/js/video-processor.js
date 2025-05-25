/**
 * TikTok Downloader - Video Processor Module
 * Handles video information processing and display
 */
const VideoProcessor = {
    // Track active downloads to prevent duplicates
    activeDownloads: new Set(),
    
    /**
     * Process video information received from API
     * @param {Object} videoInfo - Video information from API
     * @param {boolean} isMP3Page - Whether we're on the MP3 page
     */
    processVideoInfo(videoInfo, isMP3Page) {
        try {
            // Ensure video has an ID - extract from formats if needed
            if (!videoInfo.id && videoInfo.formats && videoInfo.formats.length > 0) {
                // Try to extract ID from format URLs if available
                const firstFormat = videoInfo.formats[0];
                if (firstFormat.download_url) {
                    const urlMatch = firstFormat.download_url.match(/video_id=([0-9]+)/);
                    if (urlMatch && urlMatch[1]) {
                        videoInfo.id = urlMatch[1];
                    }
                }
            }
            
            // Clear previous results
            this.clearPreviousResults();
            
            // Hide the form container and show the result container
            document.querySelector('.url-form-container').classList.add('hidden');
            document.getElementById('result-container').classList.remove('hidden');
            
            // Render the video information
            this.renderVideoInfo(videoInfo, isMP3Page);
            
            // Add back button
            this.addBackButton();
            
            // Scroll to the result container to ensure it's visible
            document.getElementById('result-container').scrollIntoView({ behavior: 'smooth', block: 'start' });
        } catch (error) {
            App.showError('Error processing video information. Please try again.');
        }
    },
    
    /**
     * Add back button to return to form
     */
    addBackButton() {
        const resultContainer = document.getElementById('result-container');
        
        // Remove any existing back buttons first to prevent duplicates
        const existingBackButtons = document.querySelectorAll('#back-to-form-container');
        existingBackButtons.forEach(button => button.remove());
        
        const backButton = document.createElement('div');
        backButton.className = 'text-center mt-6';
        backButton.id = 'back-to-form-container';
        backButton.innerHTML = `
            <button class="text-primary-600 flex items-center mx-auto" id="back-to-form">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clip-rule="evenodd" />
                </svg>
                Try another link
            </button>
        `;
        
        resultContainer.appendChild(backButton);
        
        // Add event listener
        document.getElementById('back-to-form').addEventListener('click', () => {
            document.querySelector('.url-form-container').classList.remove('hidden');
            document.getElementById('result-container').classList.add('hidden');
            
            // Focus on the appropriate input field based on screen size
            setTimeout(() => {
                const isMobile = window.innerWidth < 768;
                const inputId = isMobile ? 'tiktok-url-mobile' : 'tiktok-url-desktop';
                const inputField = document.getElementById(inputId);
                
                if (inputField) {
                    inputField.focus();
                    inputField.select(); // Select the text for easy editing
                }
            }, 100);
        });
    },
    
    /**
     * Clear previous results
     */
    clearPreviousResults() {
        const resultContent = document.getElementById('result-content');
        if (resultContent) {
            resultContent.innerHTML = '';
        }
    },
    
    /**
     * Render video information to the UI
     * @param {Object} videoInfo - Video information from API
     * @param {boolean} isMP3Page - Whether we're on the MP3 page
     */
    renderVideoInfo(videoInfo, isMP3Page) {
        const resultContent = document.getElementById('result-content');
        if (!resultContent) return;
        
        // Create video info card with formats integrated
        const videoCard = this.createVideoCard(videoInfo, isMP3Page);
        resultContent.appendChild(videoCard);
    },
    
    /**
     * Create video info card with thumbnail and metadata
     * @param {Object} videoInfo - Video information from API
     * @param {boolean} isMP3Page - Whether we're on the MP3 page
     * @returns {HTMLElement} - Video card element
     */
    createVideoCard(videoInfo, isMP3Page) {
        // Ensure videoInfo has a valid ID - this is essential
        if (!videoInfo.id) {
            // Instead of logging an error, try to extract the ID from formats if available
            if (videoInfo.formats && videoInfo.formats.length > 0) {
                const firstFormat = videoInfo.formats[0];
                if (firstFormat.download_url) {
                    const urlMatch = firstFormat.download_url.match(/video_id=([0-9]+)/);
                    if (urlMatch && urlMatch[1]) {
                        videoInfo.id = urlMatch[1];
                    }
                }
            }
            
            // If still no ID, use a fallback that won't be used for actual API calls
            if (!videoInfo.id) {
                videoInfo.id = 'video_' + Date.now();
            }
        }
        
        const videoCard = document.createElement('div');
        videoCard.className = 'video-card bg-white rounded-2xl shadow-md overflow-hidden mx-auto max-w-600';
        
        const formats = videoInfo.formats || [];
        const bestFormat = formats.length > 0 ? formats[0] : null;
        const otherFormats = formats.slice(1);
        
        const bestFormatId = bestFormat ? (bestFormat.format_id || bestFormat.id || '') : '';
        
        // Extract the real video ID from format URLs if possible
        let realVideoId = videoInfo.id;
        if (bestFormat && bestFormat.download_url) {
            const urlMatch = bestFormat.download_url.match(/video_id=([0-9]+)/);
            if (urlMatch && urlMatch[1]) {
                realVideoId = urlMatch[1];
            }
        }
        
        const formatButtons = isMP3Page ? 
            `<div class="mt-4">
                <button 
                    class="download-btn gradient-bg text-white font-medium rounded-lg w-full py-3 flex items-center justify-center download-action" 
                    data-url="${bestFormat?.download_url || '#'}"
                    data-type="mp3"
                    data-id="${realVideoId}"
                    data-format-id="${bestFormatId}">
                    <svg xmlns="http://www.w3.org/2000/svg" class="download-icon h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd" />
                    </svg>
                    <span class="download-text">${videoTranslations.download}</span>
                    <div class="download-progress flex items-center hidden">
                        <div class="spinner mr-2"></div>
                        <span class="progress-text">${videoTranslations.processing}</span>
                    </div>
                </button>
            </div>` :
            `<div class="mt-4 flex flex-col sm:flex-row sm:gap-3">
                <button 
                    class="download-btn gradient-bg text-white font-medium rounded-lg py-3 w-full mb-2 sm:mb-0 flex items-center justify-center download-action" 
                    data-url="${bestFormat?.download_url || '#'}"
                    data-type="video"
                    data-id="${realVideoId}"
                    data-format-id="${bestFormatId}">
                    <svg xmlns="http://www.w3.org/2000/svg" class="download-icon h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd" />
                    </svg>
                    <span class="download-text">${videoTranslations.download}</span>
                </button>
                ${otherFormats.length > 0 ? 
                    `<button id="show-formats-btn" class="border border-primary-600 text-primary-600 font-medium rounded-lg py-3 w-full flex items-center justify-center" data-video-id="${realVideoId}">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
                        </svg>
                        ${videoTranslations.moreFormats}
                    </button>` : 
                    ''
                }
            </div>`;
        
        const cardContent = `
            <div class="flex flex-col md:flex-row">
                <div class="md:w-2/5 relative">
                    <div class="aspect-w-9">
                        <img 
                            src="${videoInfo.thumbnail || 'https://via.placeholder.com/300x500?text=No+Thumbnail'}" 
                            alt="${videoInfo.title || 'TikTok video'}" 
                            loading="lazy"
                            class="object-cover"
                        >
                    </div>
                </div>
                <div class="md:w-3/5 p-5">
                    <h3 class="text-lg font-semibold text-gray-900 line-clamp-2 mb-2">${videoInfo.title || 'TikTok Video'}</h3>
                    <div class="flex items-center mb-3">
                        <span class="text-sm text-gray-700">@${videoInfo.author || 'unknown'}</span>
                    </div>
                    <div class="grid grid-cols-2 gap-3 mb-3">
                        <div class="text-center p-2 bg-gray-50 rounded-lg">
                            <span class="block text-lg font-medium">${this.formatNumber(videoInfo.view_count || 0)}</span>
                            <span class="text-xs text-gray-500">${videoTranslations.views}</span>
                        </div>
                        <div class="text-center p-2 bg-gray-50 rounded-lg">
                            <span class="block text-lg font-medium">${this.formatNumber(videoInfo.like_count || 0)}</span>
                            <span class="text-xs text-gray-500">${videoTranslations.likes}</span>
                        </div>
                    </div>
                    <div class="text-sm text-gray-500 mb-3">
                        ${videoTranslations.duration}: ${this.formatDuration(videoInfo.duration || 0)}
                    </div>
                    ${formatButtons}
                </div>
            </div>
        `;
        
        videoCard.innerHTML = cardContent;
        
        // Store the video ID on the card itself
        videoCard.dataset.videoId = realVideoId;
        
        // Set up download buttons
        this.setupDownloadButtons(videoCard);
        
        // Create formats modal if there are other formats
        if (!isMP3Page && otherFormats.length > 0) {
            const formatsModal = this.createFormatsModal(otherFormats, realVideoId);
            document.body.appendChild(formatsModal);
            
            // Add event listener to show modal
            videoCard.querySelector('#show-formats-btn')?.addEventListener('click', () => {
                const formatModal = document.getElementById('formats-modal');
                if (formatModal) {
                    // Confirm the video ID is still available
                    const storedVideoId = formatModal.dataset.videoId;
                    
                    // Update all buttons in the modal with the correct ID if needed
                    if (!storedVideoId || storedVideoId !== realVideoId) {
                        const downloadButtons = formatModal.querySelectorAll('.download-action');
                        downloadButtons.forEach(btn => {
                            btn.dataset.id = realVideoId;
                        });
                        formatModal.dataset.videoId = realVideoId;
                    }
                    
                    formatModal.classList.remove('hidden');
                }
            });
        }
        
        return videoCard;
    },
    
    /**
     * Set up download buttons with progress tracking
     * @param {HTMLElement} container - Container with download buttons
     */
    setupDownloadButtons(container) {
        const downloadButtons = container.querySelectorAll('.download-action');
        downloadButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const url = button.dataset.url;
                
                // Prevent duplicate download requests for the same URL
                if (this.activeDownloads.has(url)) {
                    return;
                }
                
                const type = button.dataset.type;
                const id = button.dataset.id;
                const formatId = button.dataset.formatId || '';
                
                this.handleDownload(url, formatId, type);
            });
        });
    },
    
    /**
     * Handle download button click with retry logic
     * @param {string} url - Download URL
     * @param {string} formatId - Format ID
     * @param {string} type - File type (mp4/mp3)
     * @param {number} retryCount - Current retry attempt (internal use)
     */
    async handleDownload(url, formatId, type, retryCount = 0) {
        const MAX_RETRIES = 3;
        const RETRY_DELAY = 1000;
        const FETCH_TIMEOUT = 30000;
        
        const button = document.querySelector(`[data-url="${url}"]`);
        if (!button) return;
        
        // Check if download is already in progress
        if (this.activeDownloads.has(url)) {
            return;
        }
        
        // Mark this URL as having an active download
        this.activeDownloads.add(url);

        try {
            // Show processing state with spinner
            const icon = button.querySelector('.download-icon');
            const text = button.querySelector('.download-text');
            const progress = button.querySelector('.download-progress');
            
            if (icon && text) {
                icon.classList.add('hidden');
                text.classList.add('hidden');
                if (progress) {
                    progress.classList.remove('hidden');
                    const progressText = progress.querySelector('.progress-text');
                    if (progressText) {
                        // Simplified retry message
                        progressText.textContent = retryCount > 0 ? videoTranslations.retrying : videoTranslations.processing;
                    }
                } else {
                    const progressDiv = document.createElement('div');
                    progressDiv.className = 'download-progress flex items-center';
                    progressDiv.innerHTML = `
                        <div class="spinner mr-2"></div>
                        <span class="progress-text">${retryCount > 0 ? videoTranslations.retrying : videoTranslations.processing}</span>
                    `;
                    button.appendChild(progressDiv);
                }
            }
            
            button.disabled = true;

            // Create abort controller for timeout
            const controller = new AbortController();
            let timeoutId = null;
            
            // Function to clean up resources
            const cleanupDownload = () => {
                if (timeoutId) {
                    clearTimeout(timeoutId);
                    timeoutId = null;
                }
                this.activeDownloads.delete(url);
            };
            
            timeoutId = setTimeout(() => {
                controller.abort();
                // Automatically retry on timeout if we haven't reached max retries
                if (retryCount < MAX_RETRIES) {
                    // Clear from active downloads first
                    this.activeDownloads.delete(url);
                    // Delay before automatic retry
                    setTimeout(() => {
                        this.handleDownload(url, formatId, type, retryCount + 1);
                    }, RETRY_DELAY);
                } else {
                    // Reset button if we've exhausted retries
                    cleanupDownload();
                    this.resetButton(button);
                    this.showError('Download timed out. Please try again.');
                }
            }, FETCH_TIMEOUT);

            try {
                // Make the download request with timeout
                const response = await fetch(url, {
                    signal: controller.signal,
                    cache: 'no-store', // Prevent stale cache
                    headers: {
                        'Cache-Control': 'no-cache',
                        'Pragma': 'no-cache'
                    }
                });
                
                // Clear the timeout as soon as we get a response
                clearTimeout(timeoutId);
                timeoutId = null;

                if (!response.ok) {
                    // Try to parse error response
                    let errorData;
                    try {
                        errorData = await response.json();
                    } catch (e) {
                        errorData = { error: 'Download failed', code: 'UNKNOWN_ERROR' };
                    }
                    
                    // Handle specific error cases
                    switch (errorData.code) {
                        case 'FORMAT_NOT_AVAILABLE':
                            // Check if server returned available formats
                            if (errorData.availableFormats && errorData.availableFormats.length > 0) {
                                // Use the first available format from the list
                                const newFormatId = errorData.availableFormats[0];
                                
                                // Handle URL replacement for different format ID patterns
                                let newUrl = url;
                                if (url.includes(`format_id=${formatId}`)) {
                                    // Standard format ID parameter
                                    newUrl = url.replace(`format_id=${formatId}`, `format_id=${newFormatId}`);
                                } else if (url.match(/\/[^\/]+-\d+(&|$)/)) {
                                    // Format ID in the URL path using pattern format_name-number
                                    newUrl = url.replace(/\/([^\/]+)-\d+(&|$)/, `/${newFormatId}$2`);
                                } else {
                                    // Fallback: append format_id if it can't be replaced
                                    newUrl = url.includes('?') ? 
                                        `${url}&format_id=${newFormatId}` : 
                                        `${url}?format_id=${newFormatId}`;
                                }
                                
                                // Clear the current URL from active downloads before retrying
                                this.activeDownloads.delete(url);
                                return this.handleDownload(newUrl, newFormatId, type);
                            } else {
                                // Fallback to "best" format if no available formats list
                                let bestUrl = url;
                                
                                if (url.includes(`format_id=${formatId}`)) {
                                    bestUrl = url.replace(`format_id=${formatId}`, 'format_id=best');
                                } else {
                                    bestUrl = url.includes('?') ?
                                        `${url}&format_id=best` :
                                        `${url}?format_id=best`;
                                }
                                
                                // Clear the current URL from active downloads before retrying
                                this.activeDownloads.delete(url);
                                return this.handleDownload(bestUrl, 'best', type);
                            }
                            
                        case 'INVALID_FILE_TYPE':
                            const fixedUrl = url.replace(`type=${type}`, `type=${type === 'video' ? 'mp4' : type}`);
                            // Clear the current URL from active downloads before retrying
                            this.activeDownloads.delete(url);
                            return this.handleDownload(fixedUrl, formatId, type === 'video' ? 'mp4' : type);
                            
                        default:
                            // Retry with same parameters instead of throwing error
                            if (retryCount < MAX_RETRIES) {
                                this.activeDownloads.delete(url);
                                await new Promise(resolve => setTimeout(resolve, RETRY_DELAY));
                                return this.handleDownload(url, formatId, type, retryCount + 1);
                            }
                            
                            // Make sure to reset UI if we've exhausted retries
                            cleanupDownload();
                            this.resetButton(button);
                            throw new Error(errorData.error || 'Download failed');
                    }
                }
                
                // Check if response is JSON (error) or file
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    const errorData = await response.json();
                    
                    // Retry with same parameters on JSON error
                    if (retryCount < MAX_RETRIES) {
                        this.activeDownloads.delete(url);
                        await new Promise(resolve => setTimeout(resolve, RETRY_DELAY));
                        return this.handleDownload(url, formatId, type, retryCount + 1);
                    }
                    
                    cleanupDownload();
                    throw new Error(errorData.error || 'Download failed');
                }
                
                // Verify we have actual content
                const contentLength = response.headers.get('content-length');
                if (contentLength === '0' || !contentLength) {
                    if (retryCount < MAX_RETRIES) {
                        this.activeDownloads.delete(url);
                        await new Promise(resolve => setTimeout(resolve, RETRY_DELAY));
                        return this.handleDownload(url, formatId, type, retryCount + 1);
                    }
                    cleanupDownload();
                    throw new Error('Downloaded file is empty');
                }
                
                // Get filename from Content-Disposition header or use default
                let filename;
                const disposition = response.headers.get('content-disposition');
                if (disposition) {
                    // Try multiple regex patterns to handle different formats
                    let filenameMatch = 
                        // Standard format with quotes: filename="example.mp4"
                        disposition.match(/filename\s*=\s*"([^"]+)"/) ||
                        // Format without quotes: filename=example.mp4
                        disposition.match(/filename\s*=\s*([^;]+)/) ||
                        // Format with single quotes: filename='example.mp4'
                        disposition.match(/filename\s*=\s*'([^']+)'/) ||
                        // UTF-8 format: filename*=UTF-8''example.mp4
                        disposition.match(/filename\*=UTF-8''([^;]+)/);
                    
                    if (filenameMatch && filenameMatch[1]) {
                        filename = filenameMatch[1].trim();
                        // URL decode if needed (for UTF-8 encoded filenames)
                        try {
                            filename = decodeURIComponent(filename);
                        } catch (e) {
                            // If decoding fails, keep original filename
                        }
                    }
                }
                
                // Ensure correct file extension
                if (!filename) {
                    const extension = type === 'mp3' ? 'mp3' : 'mp4';
                    filename = `tiktok_${type === 'mp3' ? 'audio' : 'video'}_${Date.now()}.${extension}`;
                } else if (filename.endsWith('.video')) {
                    filename = filename.replace('.video', '.mp4');
                }
                
                try {
                // Create blob and verify its size
                const blob = await response.blob();
                if (blob.size === 0) {
                        if (retryCount < MAX_RETRIES) {
                            this.activeDownloads.delete(url);
                            await new Promise(resolve => setTimeout(resolve, RETRY_DELAY));
                            return this.handleDownload(url, formatId, type, retryCount + 1);
                        }
                        cleanupDownload();
                    throw new Error('Downloaded file is empty');
                }
                
                // Create and trigger download
                const downloadUrl = window.URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = downloadUrl;
                link.download = filename;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                window.URL.revokeObjectURL(downloadUrl);
                
                // Show success state briefly
                if (icon && text) {
                    // First hide the progress element completely
                    const progress = button.querySelector('.download-progress');
                    if (progress) {
                        progress.remove(); // Remove the progress element entirely
                    }
                    
                    // Then show the success state
                    icon.classList.remove('hidden');
                    text.classList.remove('hidden');
                    icon.innerHTML = '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>';
                    text.textContent = videoTranslations.downloaded;
                }
                    
                    // Clean up active downloads record
                    cleanupDownload();
                
                // Reset button state after 2 seconds
                setTimeout(() => {
                    this.resetButton(button);
                }, 2000);
                } catch (blobError) {
                    cleanupDownload();
                    this.resetButton(button);
                    this.showError('Error processing download. Please try again.');
                }
                
            } catch (fetchError) {
                if (timeoutId) {
                clearTimeout(timeoutId);
                    timeoutId = null;
                }
                
                // Handle retry logic
                if (retryCount < MAX_RETRIES) {
                    this.activeDownloads.delete(url);
                    await new Promise(resolve => setTimeout(resolve, RETRY_DELAY));
                    return this.handleDownload(url, formatId, type, retryCount + 1);
                }
                
                // If we've exhausted retries, show error
                cleanupDownload();
                throw fetchError;
            }
            
        } catch (error) {
            // Simplified error message
            const errorMessage = 'Failed to download. Please try again.';
            
            this.activeDownloads.delete(url);
            this.showError(errorMessage);
            this.resetButton(button);
        }
    },
    
    /**
     * Reset button to its original state
     * @param {HTMLElement} button - Button element
     */
    resetButton(button) {
        if (!button) return;
        
        button.disabled = false;
        
        const icon = button.querySelector('.download-icon');
        const text = button.querySelector('.download-text');
        const progress = button.querySelector('.download-progress');
        
        if (icon && text) {
            icon.classList.remove('hidden');
            text.classList.remove('hidden');
            icon.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd" /></svg>';
            text.textContent = videoTranslations.download;
        }
        
        if (progress) {
            progress.classList.add('hidden');
        }
    },
    
    /**
     * Show error message
     * @param {string} message - Error message to display
     */
    showError(message) {
        const errorAlert = document.getElementById('error-alert');
        const errorMessage = document.getElementById('error-message');
        
        if (errorAlert) {
            // Only update the error message if the element exists
            if (errorMessage) {
                errorMessage.textContent = message;
            }
            
            errorAlert.classList.remove('hidden');
            
            // Hide error after 5 seconds
            setTimeout(() => {
                if (errorAlert) {
                    errorAlert.classList.add('hidden');
                }
            }, 5000);
        }
        // No fallback - silently fail if UI elements don't exist
    },
    
    /**
     * Create formats modal with additional download options
     * @param {Array} formats - Video formats from API
     * @param {string} videoId - Video ID
     * @returns {HTMLElement} - Modal element
     */
    createFormatsModal(formats, videoId) {
        // First remove any existing formats modal to prevent duplicates
        const existingModal = document.getElementById('formats-modal');
        if (existingModal) {
            existingModal.remove();
        }

        const modal = document.createElement('div');
        modal.id = 'formats-modal';
        modal.className = 'hidden fixed inset-0 bg-gray-900 bg-opacity-50 z-50 flex items-center justify-center p-4';
        
        // Store the video ID as a data attribute on the modal itself
        modal.dataset.videoId = videoId;
        
        let formatsContent = '';
        formats.forEach((format, index) => {
            const formatId = format.format_id || format.id || '';
            
            // Extract videoId from URL if possible
            let formatVideoId = videoId;
            if (format.download_url) {
                const urlMatch = format.download_url.match(/video_id=([0-9]+)/);
                if (urlMatch && urlMatch[1]) {
                    formatVideoId = urlMatch[1];
                }
            }
            
            formatsContent += `
                <div class="format-option w-full" style="animation-delay: ${0.05 * (index + 1)}s">
                    <div class="flex flex-col md:flex-row md:items-center md:justify-between w-full">
                        <div class="flex items-center mb-2 md:mb-0">
                            <span class="format-badge ${format.quality === 'HD' ? 'hd' : 'sd'}">${format.quality}</span>
                            <span class="ml-2 font-medium">${format.resolution || format.quality}</span>
                            <span class="format-size ml-3">${format.filesize || 'Unknown size'}</span>
                        </div>
                        <div class="w-full md:w-auto">
                            <button class="download-format-btn secondary download-action w-full" 
                                data-url="${format.download_url}" 
                                data-type="video" 
                                data-id="${formatVideoId}" 
                                data-format-id="${formatId}">
                                <span class="download-text">${videoTranslations.download}</span>
                                <svg class="download-icon h-4 w-4 ml-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                                </svg>
                            </button>
                        </div>
                    </div>
                </div>
            `;
        });
        
        modal.innerHTML = `
            <div class="bg-white rounded-xl max-w-lg w-full max-h-[90vh] flex flex-col">
                <div class="flex justify-between items-center p-6 border-b sticky top-0 bg-white z-10">
                    <h3 class="text-lg font-semibold text-gray-900">${videoTranslations.availableFormats}</h3>
                    <button id="close-formats-modal" class="text-gray-500 hover:text-gray-800 focus:outline-none">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>
                <div class="formats-list p-6 overflow-y-auto space-y-3">
                    ${formatsContent}
                </div>
            </div>
        `;
        
        // Add event listener to close modal
        setTimeout(() => {
            document.getElementById('close-formats-modal')?.addEventListener('click', () => {
                document.getElementById('formats-modal').classList.add('hidden');
            });
            
            // Close modal when clicking outside
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.classList.add('hidden');
                }
            });
            
            // Set up download buttons for format options
            this.setupDownloadButtons(modal);
        }, 100);
        
        return modal;
    },
    
    /**
     * Format number with commas for thousands
     * @param {number} num - Number to format
     * @returns {string} - Formatted number
     */
    formatNumber(num) {
        return new Intl.NumberFormat().format(num);
    },
    
    /**
     * Format duration in seconds to MM:SS format
     * @param {number} seconds - Duration in seconds
     * @returns {string} - Formatted duration
     */
    formatDuration(seconds) {
        if (!seconds) return '00:00';
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
}; 