/**
 * TikTok Downloader - App Core
 * Main application logic and initialization
 */
const App = {
    /**
     * Initialize the application
     */
    init() {
        // Make sure DOM is ready before initializing
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                // Slight delay to ensure all elements are properly initialized
                setTimeout(() => {
                    this.initializeApp();
                }, 100);
            });
        } else {
            // Slight delay to ensure all elements are properly initialized
            setTimeout(() => {
                this.initializeApp();
            }, 100);
        }
    },
    
    /**
     * Initialize app components after DOM is ready
     */
    initializeApp() {
        this.setupEventListeners();
        this.setupUI();
        
        // Initialize FAQ accordions right away
        this.initializeFaqAccordions();
        
        // Set current year in footer if jQuery isn't handling it
        const currentYearElement = document.getElementById('current-year');
        if (currentYearElement && !currentYearElement.textContent) {
            currentYearElement.textContent = new Date().getFullYear();
        }
        
        // Scroll to top when page is refreshed
        window.onbeforeunload = function() {
            window.scrollTo(0, 0);
        };
        
        // Also scroll to top on page load
        window.scrollTo(0, 0);
    },

    /**
     * Set up event listeners for UI elements
     */
    setupEventListeners() {
        // Mobile menu toggle
        const mobileMenuButton = document.getElementById('mobile-menu-button');
        const mobileMenu = document.getElementById('mobile-menu');
        const closeMenu = document.getElementById('close-menu');

        if (mobileMenuButton && mobileMenu && closeMenu) {
            // Mobile menu button click - opens the menu
            mobileMenuButton.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                mobileMenu.classList.add('active');
                document.body.style.overflow = 'hidden'; // Prevent scrolling when menu is open
            });

            // Close button click - closes the menu
            closeMenu.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                mobileMenu.classList.remove('active');
                document.body.style.overflow = ''; // Re-enable scrolling
            });

            // Close menu when clicking outside (but not on the menu button)
            document.addEventListener('click', (e) => {
                if (mobileMenu.classList.contains('active') && 
                    mobileMenu.querySelector('.absolute') &&
                    !mobileMenu.querySelector('.absolute').contains(e.target) && 
                    e.target !== mobileMenuButton) {
                    mobileMenu.classList.remove('active');
                    document.body.style.overflow = ''; // Re-enable scrolling
                }
            });

            // Prevent clicks inside the menu from closing it
            const menuContainer = mobileMenu.querySelector('.absolute');
            if (menuContainer) {
                menuContainer.addEventListener('click', (e) => {
                e.stopPropagation();
            });
            }

            // Close mobile menu when clicking on links
            document.querySelectorAll('#mobile-menu a').forEach(link => {
                link.addEventListener('click', () => {
                    mobileMenu.classList.remove('active');
                    document.body.style.overflow = ''; // Re-enable scrolling
                });
            });
        }

        // Form submission
        const form = document.getElementById('tiktok-form');
        if (form && !form.getAttribute('data-listeners-added')) {
            form.setAttribute('data-listeners-added', 'true');
            form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleFormSubmit();
        });
        }

        // FAQ accordion - Fixed implementation
        const faqQuestions = document.querySelectorAll('.faq-question');
        if (faqQuestions.length > 0) {
            faqQuestions.forEach(question => {
                // Check if event listener is already added
                if (!question.getAttribute('data-listeners-added')) {
                    question.setAttribute('data-listeners-added', 'true');
                    
                    // Get the toggle element if exists
                    const parent = question.closest('.faq-item');
                    const toggle = parent ? parent.querySelector('.faq-toggle') : null;
                    
                    // Set the initial state - first item can be open by default
                    if (toggle && parent.classList.contains('active')) {
                        this.updateToggleIcon(toggle, true);
                    }
                    
                    question.addEventListener('click', () => {
                        const parent = question.closest('.faq-item');
                        if (!parent) return;
                        
                        const toggle = parent.querySelector('.faq-toggle');
                        const isActive = parent.classList.contains('active');
                        
                        if (isActive) {
                            // Close this FAQ item
                            parent.classList.remove('active');
                            if (toggle) {
                                this.updateToggleIcon(toggle, false);
                            }
                        } else {
                            // Close all FAQ items first
                            document.querySelectorAll('.faq-item').forEach(item => {
                                const itemToggle = item.querySelector('.faq-toggle');
                                item.classList.remove('active');
                                if (itemToggle) {
                                    this.updateToggleIcon(itemToggle, false);
                                }
                            });
                            
                            // Open this FAQ item
                            parent.classList.add('active');
                            if (toggle) {
                                this.updateToggleIcon(toggle, true);
                            }
                        }
                    });
                }
            });
        }

        // Smooth scroll for anchor links
        const anchorLinks = document.querySelectorAll('a[href^="#"]');
        if (anchorLinks.length > 0) {
            anchorLinks.forEach(anchor => {
                // Check if event listener is already added
                if (!anchor.getAttribute('data-listeners-added')) {
                    anchor.setAttribute('data-listeners-added', 'true');
            anchor.addEventListener('click', (e) => {
                e.preventDefault();
                const targetId = anchor.getAttribute('href');
                const targetElement = document.querySelector(targetId);

                if (targetElement) {
                    const offsetTop = targetElement.getBoundingClientRect().top + window.pageYOffset - 80;
                    window.scrollTo({
                        top: offsetTop,
                        behavior: 'smooth'
                    });
                }
            });
                }
        });
        }
    },

    /**
     * Set up UI elements and state
     */
    setupUI() {
        this.setupInputFields();
    },

    /**
     * Set up input fields with paste/clear functionality
     */
    setupInputFields() {
        const setupInputField = (inputId, pasteId, clearId) => {
            const input = document.getElementById(inputId);
            const pasteBtn = document.getElementById(pasteId);
            const clearBtn = document.getElementById(clearId);

            if (!input || !pasteBtn || !clearBtn) return;
            
            // Check if event listeners are already added
            if (input.getAttribute('data-listeners-added')) return;
            input.setAttribute('data-listeners-added', 'true');

            // Initial state
            if (input.value.length > 0) {
                pasteBtn.style.display = 'none';
                clearBtn.style.display = 'flex';
            } else {
                clearBtn.style.display = 'none';
                pasteBtn.style.display = 'flex';
            }

            // Input change event
            input.addEventListener('input', () => {
                if (input.value.length > 0) {
                    pasteBtn.style.display = 'none';
                    clearBtn.style.display = 'flex';
                } else {
                    clearBtn.style.display = 'none';
                    pasteBtn.style.display = 'flex';
                }
            });

            // Paste button
            pasteBtn.addEventListener('click', () => {
                if (navigator.clipboard) {
                    navigator.clipboard.readText()
                        .then(text => {
                            input.value = text;
                            pasteBtn.style.display = 'none';
                            clearBtn.style.display = 'flex';
                        })
                        .catch(err => {
                            // Failed clipboard operation - silently continue
                        });
                } else {
                    alert('Clipboard access is not available in your browser.');
                }
            });

            // Clear button
            clearBtn.addEventListener('click', () => {
                input.value = '';
                clearBtn.style.display = 'none';
                pasteBtn.style.display = 'flex';
            });
        };

        // Setup desktop and mobile input fields
        setupInputField('tiktok-url-desktop', 'paste-button-desktop', 'clear-button-desktop');
        setupInputField('tiktok-url-mobile', 'paste-button-mobile', 'clear-button-mobile');
    },
    
    /**
     * Handle form submission
     */
    handleFormSubmit() {
        // Get URL from either mobile or desktop input
        let url = '';
        if (window.innerWidth < 768) {
            url = document.getElementById('tiktok-url-mobile')?.value.trim() || '';
        } else {
            url = document.getElementById('tiktok-url-desktop')?.value.trim() || '';
        }

        // Determine if we're on the MP3 page for error messages
        const isMP3Page = window.location.pathname.includes('/mp3');
        
        // Get error message elements
        const errorMsgElem = document.getElementById('error-message');
        const errorAlert = document.getElementById('error-alert');
        
        // Default error message if element doesn't exist
        const defaultError = "Please enter a valid TikTok URL";
        
        // Validate URL
        if (!url) {
            this.showError(errorMsgElem?.textContent || defaultError);
            return;
        }

        if (!url.includes('tiktok.com')) {
            this.showError(errorMsgElem?.textContent || defaultError);
            return;
        }

        // Show loading state
        this.setLoadingState(true);

        // Clear any previous errors
        if (errorAlert) {
            errorAlert.classList.add('hidden');
        }

        // Call API
        fetch('/api/extract', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                url: url,
                is_mp3_page: isMP3Page
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Hide loading state
            this.setLoadingState(false);
            
            // Process the video info
            VideoProcessor.processVideoInfo(data, isMP3Page);
        })
        .catch(error => {
            // Hide loading state
            this.setLoadingState(false);
            
            // Show error message
            this.showError(errorMsgElem?.textContent || "Error processing video. Please try again.");
        });
    },

    /**
     * Toggle loading state
     */
    setLoadingState(isLoading) {
        const isMobile = window.innerWidth < 768;
        const loadingElem = isMobile ? 
            document.getElementById('loading-text-mobile') : 
            document.getElementById('loading-text-desktop');
        
        const downloadElem = isMobile ? 
            document.getElementById('download-text-mobile') : 
            document.getElementById('download-text-desktop');
            
        const downloadBtn = isMobile ?
            document.getElementById('download-button-mobile') :
            document.getElementById('download-button-desktop');
            
        if (!loadingElem || !downloadElem || !downloadBtn) return;
        
        if (isLoading) {
            downloadElem.style.display = 'none';
            loadingElem.style.display = 'inline-flex';
            downloadBtn.disabled = true;
        } else {
            downloadElem.style.display = 'inline-flex';
            loadingElem.style.display = 'none';
            downloadBtn.disabled = false;
        }
    },

    /**
     * Show error message
     * @param {string} message - The error message to display
     */
    showError(message) {
        const errorAlert = document.getElementById('error-alert');
        const errorMessage = document.getElementById('error-message');
        
        if (errorAlert) {
            // Only update the error message if a custom one is provided and element exists
            if (message && errorMessage) {
                errorMessage.textContent = message;
            }
            errorAlert.classList.remove('hidden');
        }
    },

    /**
     * Update toggle icon
     * @param {Element} toggle - The toggle element
     * @param {boolean} isActive - Whether the item is active
     */
    updateToggleIcon(toggle, isActive) {
        if (!toggle) return;
        
        toggle.innerHTML = isActive 
            ? '<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M3 10a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd" /></svg>'
            : '<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" clip-rule="evenodd" /></svg>';
    },

    /**
     * Initialize FAQ accordions
     */
    initializeFaqAccordions() {
        const faqItems = document.querySelectorAll('.faq-item');
        if (faqItems.length === 0) return;
        
        // Set the first item as active if no items are active
        if (document.querySelectorAll('.faq-item.active').length === 0 && faqItems.length > 0) {
            const firstItem = faqItems[0];
            const toggle = firstItem.querySelector('.faq-toggle');
            
            firstItem.classList.add('active');
            if (toggle) {
                this.updateToggleIcon(toggle, true);
            }
        }
    }
};

// Initialize the application when script loads
    App.init();