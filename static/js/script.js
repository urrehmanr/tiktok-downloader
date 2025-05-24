$(document).ready(function() {
    // Set current year in footer
    $('#current-year').text(new Date().getFullYear());
    
    // Mobile menu toggle
    $('#mobile-menu-button').click(function() {
        $('#mobile-menu').addClass('active');
    });
    
    $('#close-menu').click(function() {
        $('#mobile-menu').removeClass('active');
    });
    
    // Close mobile menu when clicking on a link
    $('#mobile-menu a').click(function() {
        $('#mobile-menu').removeClass('active');
    });
    
    // Smooth scroll for anchor links
    $('a[href^="#"]').click(function(e) {
        e.preventDefault();
        
        var target = $(this.hash);
        if (target.length) {
            $('html, body').animate({
                scrollTop: target.offset().top - 80
            }, 800);
        }
    });
    
    // FAQ accordion
    $('.faq-question').click(function() {
        var parent = $(this).parent();
        
        if (parent.hasClass('active')) {
            parent.removeClass('active');
        } else {
            $('.faq-item').removeClass('active');
            parent.addClass('active');
        }
    });
    
    // Paste button functionality - Desktop
    $('#paste-button-desktop').click(function() {
        if (navigator.clipboard) {
            navigator.clipboard.readText()
                .then(function(text) {
                    $('#tiktok-url-desktop').val(text);
                    $('#paste-button-desktop').hide();
                    $('#clear-button-desktop').show();
                })
                .catch(function(err) {
                    console.error('Failed to read clipboard: ', err);
                });
        } else {
            alert('Clipboard access is not available in your browser.');
        }
    });
    
    // Clear button functionality - Desktop
    $('#clear-button-desktop').click(function() {
        $('#tiktok-url-desktop').val('');
        $('#clear-button-desktop').hide();
        $('#paste-button-desktop').show();
    });
    
    // Input change event - Desktop
    $('#tiktok-url-desktop').on('input', function() {
        if ($(this).val().length > 0) {
            $('#paste-button-desktop').hide();
            $('#clear-button-desktop').show();
        } else {
            $('#clear-button-desktop').hide();
            $('#paste-button-desktop').show();
        }
    });
    
    // Paste button functionality - Mobile
    $('#paste-button-mobile').click(function() {
        if (navigator.clipboard) {
            navigator.clipboard.readText()
                .then(function(text) {
                    $('#tiktok-url-mobile').val(text);
                    $('#paste-button-mobile').hide();
                    $('#clear-button-mobile').show();
                })
                .catch(function(err) {
                    console.error('Failed to read clipboard: ', err);
                });
        } else {
            alert('Clipboard access is not available in your browser.');
        }
    });
    
    // Clear button functionality - Mobile
    $('#clear-button-mobile').click(function() {
        $('#tiktok-url-mobile').val('');
        $('#clear-button-mobile').hide();
        $('#paste-button-mobile').show();
    });
    
    // Input change event - Mobile
    $('#tiktok-url-mobile').on('input', function() {
        if ($(this).val().length > 0) {
            $('#paste-button-mobile').hide();
            $('#clear-button-mobile').show();
        } else {
            $('#clear-button-mobile').hide();
            $('#paste-button-mobile').show();
        }
    });
    
    // Process video info and update the UI
    function processVideoInfo(videoInfo, isMP3Page) {
        // Show download result section
        $('#download-form').hide();
        $('#download-result').show();
        
        // Update video details
        $('#result-author').text('@' + videoInfo.author);
        $('#result-title').text(videoInfo.title);
        
        // Format duration to minutes:seconds
        let duration = videoInfo.duration || 0;
        let durationStr = formatDuration(duration);
        
        // Create additional stats HTML
        let statsHtml = '';
        if (videoInfo.view_count) statsHtml += `<span class="mr-3"><i class="fas fa-eye mr-1"></i> ${formatNumber(videoInfo.view_count)}</span>`;
        if (videoInfo.like_count) statsHtml += `<span class="mr-3"><i class="fas fa-heart mr-1"></i> ${formatNumber(videoInfo.like_count)}</span>`;
        if (videoInfo.comment_count) statsHtml += `<span><i class="fas fa-comment mr-1"></i> ${formatNumber(videoInfo.comment_count)}</span>`;
        if (duration) statsHtml += `<span class="ml-3"><i class="fas fa-clock mr-1"></i> ${durationStr}</span>`;
        
        // Append stats if any
        if (statsHtml) {
            $('#result-stats').html(statsHtml);
            $('#result-stats').show();
        } else {
            $('#result-stats').hide();
        }
        
        // Set author image if available
        if (videoInfo.thumbnail) {
            $('#result-thumbnail-bg').css('background-image', `url('${videoInfo.thumbnail}')`);
        } else {
            // Default gradient if no thumbnail
            $('#result-thumbnail-bg').css('background-image', 'none');
        }
        
        // Clear previous formats
        $('#formats-container').empty();
        
        // For MP3 page, we'll create a simplified view with just one best audio option
        if (isMP3Page) {
            // Find the best audio format or use the first video format for conversion
            if (videoInfo.formats && videoInfo.formats.length > 0) {
                let bestFormat = videoInfo.formats[0]; // We'll use the single format returned by the server for MP3 page
                
                // Get the download URL
                let downloadUrl = bestFormat.download_url || '';
                if (!downloadUrl) {
                    // Construct it if not provided
                    downloadUrl = `/api/cached-download?url=${encodeURIComponent(videoInfo.source_url)}&type=mp3&convert_to_mp3=true`;
                    if (videoInfo.video_id) {
                        downloadUrl += `&video_id=${videoInfo.video_id}`;
                    }
                    if (videoInfo.tt_chain_token) {
                        downloadUrl += `&token=${videoInfo.tt_chain_token}`;
                    }
                }
                
                // Prepare quality and size info
                let qualityInfo = bestFormat.quality || 'High Quality';
                let sizeInfo = bestFormat.filesize ? ` (${bestFormat.filesize})` : '';
                
                // Add ffmpeg_required flag and check if it's needed
                let audioFormat = bestFormat.ext || 'mp3';
                let formatLabel = audioFormat.toUpperCase();
                let audioIcon = 'fas fa-music';
                
                // Create the download button with proper styling
                let mainFormatsHtml = `
                <a href="${downloadUrl}" 
                   class="bg-blue-600 hover:bg-blue-700 
                          text-white py-4 px-4 rounded-lg text-center transition-colors flex items-center justify-center mb-3">
                    <i class="${audioIcon} mr-2"></i> Download ${formatLabel} Audio ${qualityInfo}${sizeInfo}
                </a>`;
                
                $('#formats-container').append(mainFormatsHtml);
                
                // Add a note about quality and format
                let audioNote = '';
                if (audioFormat === 'mp3') {
                    audioNote = `
                    <div class="text-sm text-gray-600 text-center mt-2 mb-4">
                        <i class="fas fa-info-circle mr-1"></i> High quality MP3 extracted from the TikTok video.
                    </div>`;
                } else {
                    audioNote = `
                    <div class="text-sm text-gray-600 text-center mt-2 mb-4">
                        <i class="fas fa-info-circle mr-1"></i> Original audio format (M4A) from TikTok. To convert to MP3, install FFmpeg on the server.
                    </div>`;
                }
                $('#formats-container').append(audioNote);
            } else {
                $('#formats-container').append('<p class="text-red-600 text-center py-3">No audio format available for this video.</p>');
            }
            
            // Don't show the "all formats" section on MP3 page
            if ($('#all-formats-container').length) {
                $('#all-formats-container').remove();
            }
            if ($('#toggle-all-formats').length) {
                $('#toggle-all-formats').remove();
            }
        } else {
            // Setup download links for main formats for regular video page
            let mainFormatsHtml = '';
            
            // First add the best video and audio formats
            videoInfo.formats.forEach(function(format) {
                let icon = format.type === 'video' ? 'fas fa-video' : 'fas fa-music';
                let formatLabel = isMP3Page ? 'MP3 Audio' : (format.type === 'video' ? 'MP4 Video' : 'MP3 Audio');
                
                // Format quality info - use "Original" for audio resolution or if N/A
                let qualityInfo = format.type === 'video' ? 
                    (format.resolution && format.resolution !== 'N/A' ? `${format.resolution} - ` : '') + format.quality : 
                    format.quality || 'Original';
                
                // Format size info - use "Original" for audio with unknown size
                let sizeInfo = format.filesize ? 
                    ` - ${format.filesize}` : 
                    (format.type === 'audio' ? ' - Original' : '');
                
                // Get the download URL - use the download_url property if available,
                // otherwise construct it from the URL and other properties
                let downloadUrl;
                if (format.download_url) {
                    // Use the server-provided download URL (this should be a server-side cached download)
                    downloadUrl = format.download_url;
                    
                    // Add convert_to_mp3 parameter for MP3 page if not already present
                    if (isMP3Page && !downloadUrl.includes('convert_to_mp3=true')) {
                        downloadUrl += (downloadUrl.includes('?') ? '&' : '?') + 'convert_to_mp3=true';
                    }
                } else {
                    // Fallback to constructing a URL (should be rare)
                    downloadUrl = `/api/cached-download?url=${encodeURIComponent(format.url)}&type=${format.ext}`;
                    
                    // Add video_id if available
                    if (videoInfo.video_id) {
                        downloadUrl += `&video_id=${videoInfo.video_id}`;
                    }
                    
                    // Add format_id if available
                    if (format.format_id) {
                        downloadUrl += `&format_id=${format.format_id}`;
                    }
                    
                    // Add token if available
                    if (videoInfo.tt_chain_token) {
                        downloadUrl += `&token=${videoInfo.tt_chain_token}`;
                    }
                    
                    // Add force_url_hash if using a URL hash ID
                    if (videoInfo.video_id && videoInfo.video_id.startsWith('url_')) {
                        downloadUrl += '&force_url_hash=true';
                    }
                    
                    // Add convert_to_mp3 parameter for MP3 page
                    if (isMP3Page) {
                        downloadUrl += '&convert_to_mp3=true';
                    }
                }
                
                // Check if the format is cached (show a different color if it is)
                let isCached = format.is_cached === true;
                
                // For MP3 page, focus on audio formats
                if (isMP3Page && format.type !== 'audio') {
                    // For MP3 page, convert video formats to audio
                    formatLabel = 'MP3 from Video';
                    icon = 'fas fa-music';
                }
                
                let bgColorClass = isMP3Page ? 
                    'blue' : // All blue for MP3 page
                    (isCached ? 
                        (format.type === 'video' ? 'green' : 'blue') : 
                        (format.type === 'video' ? 'yellow' : 'purple'));
                
                mainFormatsHtml += `
                <a href="${downloadUrl}" 
                   class="bg-${bgColorClass}-600 hover:bg-${bgColorClass}-700 
                          text-white py-3 px-4 rounded-lg text-center transition-colors flex items-center justify-center mb-3">
                    <i class="${icon} mr-2"></i> Download ${formatLabel} (${qualityInfo}${sizeInfo})
                </a>`;
            });
            
            $('#formats-container').append(mainFormatsHtml);
        }
        
        // Add more formats section if available and not on MP3 page
        if (!isMP3Page && videoInfo.all_formats && videoInfo.all_formats.length > 0) {
            // Create a toggle for all formats
            let toggleHtml = `
            <div class="mt-3 mb-2">
                <button id="toggle-all-formats" class="text-primary-600 hover:text-primary-800 transition-colors flex items-center">
                    <i class="fas fa-chevron-down mr-1" id="toggle-formats-icon"></i> 
                    <span>Show all available formats</span>
                </button>
            </div>
            <div id="all-formats-container" class="hidden mt-3 border border-gray-200 rounded-lg p-3 bg-gray-50">
                <h4 class="font-bold mb-3">All Available Formats</h4>
                <div class="overflow-x-auto">
                    <table class="w-full text-sm">
                        <thead class="bg-gray-100">
                            <tr>
                                <th class="px-2 py-2 text-left">Format</th>
                                <th class="px-2 py-2 text-left">Quality</th>
                                <th class="px-2 py-2 text-left">Resolution</th>
                                <th class="px-2 py-2 text-left">Size</th>
                                <th class="px-2 py-2 text-left">Action</th>
                            </tr>
                        </thead>
                        <tbody>`;
            
            // Add rows for each format
            videoInfo.all_formats.forEach(function(format) {
                let ext = format.ext || 'unknown';
                let formatNote = format.format_note || '';
                let type = format.type || 'unknown';
                
                // Update resolution text - change "Audio Only" or "N/A" to "Original"
                let resolution = format.resolution && format.resolution !== 'N/A' ? 
                    format.resolution : 
                    (type === 'audio' || format.resolution === 'N/A' ? 'Original' : 'N/A');
                
                // Update size text - change "Unknown" to "Original" for audio formats
                let size = format.filesize || (type === 'audio' ? 'Original' : 'Unknown');
                
                // Get the download URL - prefer the server-generated one
                let downloadUrl;
                if (format.download_url) {
                    // Use the server-provided download URL
                    downloadUrl = format.download_url;
                } else {
                    // Fallback to constructing a URL
                    downloadUrl = `/api/cached-download?url=${encodeURIComponent(format.url)}&type=${format.ext}`;
                    
                    // Add video_id if available
                    if (videoInfo.video_id) {
                        downloadUrl += `&video_id=${videoInfo.video_id}`;
                    }
                    
                    // Add format_id if available
                    if (format.format_id) {
                        downloadUrl += `&format_id=${format.format_id}`;
                    }
                    
                    // Add token if available
                    if (videoInfo.tt_chain_token) {
                        downloadUrl += `&token=${videoInfo.tt_chain_token}`;
                    }
                    
                    // Add force_url_hash if using a URL hash ID
                    if (videoInfo.video_id && videoInfo.video_id.startsWith('url_')) {
                        downloadUrl += '&force_url_hash=true';
                    }
                }
                
                // Check if the format is cached and use a different button color
                let buttonClass = format.is_cached === true ? 
                    'bg-green-600 hover:bg-green-700' : 
                    'bg-gray-600 hover:bg-gray-700';
                
                toggleHtml += `
                    <tr class="border-b border-gray-200">
                        <td class="px-2 py-2">${ext.toUpperCase()} ${formatNote}</td>
                        <td class="px-2 py-2">${type === 'audio' ? 'Audio' : formatNote}</td>
                        <td class="px-2 py-2">${resolution}</td>
                        <td class="px-2 py-2">${size}</td>
                        <td class="px-2 py-2">
                            <a href="${downloadUrl}" 
                               class="${buttonClass} text-white text-xs py-1 px-2 rounded">
                                Download
                            </a>
                        </td>
                    </tr>`;
            });
            
            toggleHtml += `
                        </tbody>
                    </table>
                </div>
            </div>`;
            
            $('#formats-container').append(toggleHtml);
            
            // Add event listener for toggle
            $('#toggle-all-formats').click(function() {
                $('#all-formats-container').toggleClass('hidden');
                $('#toggle-formats-icon').toggleClass('fa-chevron-down fa-chevron-up');
                
                // Update text
                let buttonText = $('#all-formats-container').hasClass('hidden') ? 
                    'Show all available formats' : 'Hide all formats';
                $(this).find('span').text(buttonText);
            });
        }
        
        // Ensure the download another button is visible
        $('#download-another').removeClass('hidden');
        
        // Add this code after line 400, right after the formats-container section
        $('#formats-container').on('click', 'a', function(e) {
            // Prevent default action to handle the download programmatically
            e.preventDefault();
            
            // Get the download URL from the link
            var downloadUrl = $(this).attr('href');
            
            // Get button text to restore later
            var originalText = $(this).html();
            
            // Update button to show it's processing
            $(this).html('<i class="fas fa-spinner fa-spin mr-2"></i> Processing...');
            $(this).addClass('opacity-75 cursor-not-allowed');
            
            // Create a unique request ID for this download
            var requestId = 'download_' + Math.random().toString(36).substr(2, 9);
            
            // Create an iframe for download (better than window.location for downloads)
            var downloadFrame = $('<iframe>', {
                src: downloadUrl + '&requestId=' + requestId,
                id: 'download-frame-' + requestId,
                style: 'display:none;'
            }).appendTo('body');
            
            // After a short delay, restore the button (even if download is still ongoing)
            setTimeout(function() {
                // Check the download status
                var checkDownloadStatus = function() {
                    $.ajax({
                        url: '/api/check-download?requestId=' + requestId,
                        type: 'GET',
                        success: function(response) {
                            if (response.status === 'completed') {
                                // Download is done, update the button
                                $(e.target).closest('a').html('<i class="fas fa-check mr-2"></i> Downloaded!');
                                setTimeout(function() {
                                    $(e.target).closest('a').html(originalText);
                                    $(e.target).closest('a').removeClass('opacity-75 cursor-not-allowed');
                                }, 3000);
                            } else if (response.status === 'failed') {
                                // Download failed
                                $(e.target).closest('a').html('<i class="fas fa-exclamation-triangle mr-2"></i> Download Failed');
                                setTimeout(function() {
                                    $(e.target).closest('a').html(originalText);
                                    $(e.target).closest('a').removeClass('opacity-75 cursor-not-allowed');
                                }, 3000);
                            } else {
                                // Download still in progress
                                setTimeout(checkDownloadStatus, 1000);
                            }
                        },
                        error: function() {
                            // Just restore the button on error
                            $(e.target).closest('a').html(originalText);
                            $(e.target).closest('a').removeClass('opacity-75 cursor-not-allowed');
                        }
                    });
                };
                
                // For now, just restore the button after 5 seconds
                // The download will continue in the background
                setTimeout(function() {
                    $(e.target).closest('a').html('<i class="fas fa-check mr-2"></i> Download Started');
                    setTimeout(function() {
                        $(e.target).closest('a').html(originalText);
                        $(e.target).closest('a').removeClass('opacity-75 cursor-not-allowed');
                    }, 3000);
                }, 5000);
            }, 2000);
        });
    }
    
    // Format large numbers with commas
    function formatNumber(num) {
        if (!num) return '0';
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    }
    
    // Format duration from seconds to MM:SS
    function formatDuration(seconds) {
        if (!seconds) return '0:00';
        
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = Math.floor(seconds % 60);
        
        return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    }
    
    // Download another button
    $('#download-another').click(function() {
        $('#download-result').hide();
        $('#download-form').show();
        
        if ($(window).width() < 768) {
            $('#tiktok-url-mobile').val('');
            $('#clear-button-mobile').hide();
            $('#paste-button-mobile').show();
        } else {
            $('#tiktok-url-desktop').val('');
            $('#clear-button-desktop').hide();
            $('#paste-button-desktop').show();
        }
    });
    
    // Function to show error message
    function showError(message) {
        $('#error-alert').text(message).show();
    }
}); 