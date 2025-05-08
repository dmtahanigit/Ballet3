/**
 * World Ballets - UI Controller
 * 
 * This module handles UI interactions, animations, and DOM manipulations for the World Ballets website.
 */

const UIController = (() => {
    // Cache DOM elements
    const DOM = {};
    
    /**
     * Validates an image URL and returns either the valid URL or a fallback
     * @param {string} url - The image URL to validate
     * @returns {string} - A valid image URL or fallback path
     */
    const validateImageUrl = (url) => {
        // Check if URL is undefined, null, or empty
        if (!url) {
            console.warn('Image URL is missing, using placeholder');
            return '../images/placeholder-performance.jpg';
        }
        
        // Check if URL is a valid format
        try {
            // Check if it's a relative path starting with ../
            if (url.startsWith('../') || url.startsWith('./')) {
                return url;
            }
            
            // Check if it's a data URL
            if (url.startsWith('data:')) {
                return url;
            }
            
            // For absolute URLs, validate format
            new URL(url);
            
            // Log successful validation
            console.log('Image URL validated:', url);
            return url;
        } catch (e) {
            // If URL is invalid, log error and return fallback
            console.error('Invalid image URL:', url, e.message);
            return '../images/placeholder-performance.jpg';
        }
    };
    
/**
 * Initializes the UI controller
 */
const init = () => {
    // Initialize any UI components that need setup
    initObservers();
    
    // Add mobile refresh button
    addMobileRefreshButton();
};

/**
 * Adds a refresh button for mobile users
 */
const addMobileRefreshButton = () => {
    // Create refresh button element
    const refreshBtn = document.createElement('button');
    refreshBtn.className = 'mobile-refresh-btn';
    refreshBtn.innerHTML = '↻';
    refreshBtn.setAttribute('aria-label', 'Refresh data');
    
    // Add click event to refresh data
    refreshBtn.addEventListener('click', () => {
        // Show loading indicator
        const loadingToast = document.createElement('div');
        loadingToast.style.position = 'fixed';
        loadingToast.style.top = '20px';
        loadingToast.style.left = '50%';
        loadingToast.style.transform = 'translateX(-50%)';
        loadingToast.style.backgroundColor = 'rgba(0,0,0,0.8)';
        loadingToast.style.color = 'white';
        loadingToast.style.padding = '10px 20px';
        loadingToast.style.borderRadius = '5px';
        loadingToast.style.zIndex = '1000';
        loadingToast.textContent = 'Refreshing data...';
        document.body.appendChild(loadingToast);
        
        // Clear localStorage cache
        localStorage.removeItem('ballet_data_cache');
        localStorage.removeItem('ballet_cache_timestamp');
        
        // Reload the page after a short delay
        setTimeout(() => {
            window.location.reload();
        }, 500);
    });
    
    // Add to document
    document.body.appendChild(refreshBtn);
};
    
    /**
     * Initializes intersection observers for scroll animations
     */
    const initObservers = () => {
        // Create observer for fade-in animations
        const fadeObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    fadeObserver.unobserve(entry.target);
                }
            });
        }, {
            root: null,
            threshold: 0.1,
            rootMargin: '0px 0px -100px 0px'
        });
        
        // Observe elements with fade-in class
        document.querySelectorAll('.performance-item, .performance-card').forEach(item => {
            fadeObserver.observe(item);
        });
    };
    
    /**
     * Creates and initializes the banner slider
     * @param {Array} slides - Array of slide objects with image and content
     * @param {string} containerId - ID of the container element
     */
    const initBannerSlider = (slides, containerId) => {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        // Clear existing content
        container.innerHTML = '';
        
        // Create slides
        slides.forEach((slide, index) => {
            const slideElement = document.createElement('div');
            slideElement.className = 'banner-slide';
            slideElement.innerHTML = `
                <img src="${validateImageUrl(slide.image)}" alt="${slide.title}" onerror="console.error('Failed to load banner image:', this.src); this.onerror=null; this.src='../images/placeholder-performance.jpg';">
                <div class="banner-slide-content">
                    <h3>${slide.title}</h3>
                    <p>${slide.companyName}</p>
                    <p>${DataService.formatDateRange(slide.startDate, slide.endDate)}</p>
                </div>
            `;
            container.appendChild(slideElement);
            
            // Make the slide clickable
            slideElement.addEventListener('click', () => {
                window.location.href = `companies/${slide.company}.html`;
            });
        });
        
        // Set up slider functionality
        let currentSlide = 0;
        const slideCount = slides.length;
        
        // Get control buttons
        const prevBtn = document.querySelector('.prev-btn');
        const nextBtn = document.querySelector('.next-btn');
        
        if (prevBtn && nextBtn) {
            // Add event listeners to control buttons
            prevBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                currentSlide = (currentSlide - 1 + slideCount) % slideCount;
                updateSliderPosition();
            });
            
            nextBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                currentSlide = (currentSlide + 1) % slideCount;
                updateSliderPosition();
            });
        }
        
        // Function to update slider position
        const updateSliderPosition = () => {
            container.style.transform = `translateX(-${currentSlide * 100}%)`;
        };
        
        // Auto-advance slider
        let sliderInterval = setInterval(() => {
            currentSlide = (currentSlide + 1) % slideCount;
            updateSliderPosition();
        }, 5000);
        
        // Pause auto-advance on hover
        const bannerContainer = document.querySelector('.banner-container');
        if (bannerContainer) {
            bannerContainer.addEventListener('mouseenter', () => {
                clearInterval(sliderInterval);
            });
            
            bannerContainer.addEventListener('mouseleave', () => {
                sliderInterval = setInterval(() => {
                    currentSlide = (currentSlide + 1) % slideCount;
                    updateSliderPosition();
                }, 5000);
            });
        }
    };
    
    /**
     * Renders performance cards for the featured performances section
     * @param {Array} performances - Array of performance objects
     * @param {string} containerId - ID of the container element
     */
    const renderPerformanceCards = (performances, containerId) => {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        // Clear existing content
        container.innerHTML = '';
        
        // Create performance cards
        performances.forEach(performance => {
            const card = document.createElement('div');
            card.className = 'performance-card';
            card.innerHTML = `
                <div class="performance-card-image">
                    <img src="${validateImageUrl(performance.image)}" alt="${performance.title}" onerror="console.error('Failed to load card image:', this.src); this.onerror=null; this.src='../images/placeholder-performance.jpg';">
                </div>
                <div class="performance-card-content">
                    <h3>${performance.title}</h3>
                    <p class="company">${performance.companyName}</p>
                    <p class="dates">${DataService.formatDateRange(performance.startDate, performance.endDate)}</p>
                    <p class="description">${performance.description.substring(0, 100)}...</p>
                    <a href="companies/${performance.company}.html" class="view-details-btn">View Details</a>
                </div>
            `;
            container.appendChild(card);
        });
    };
    
    /**
     * Renders the performance timeline for the upcoming performances section
     * @param {Array} performances - Array of performance objects
     * @param {string} containerId - ID of the container element
     */
    const renderPerformanceTimeline = (performances, containerId) => {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        // Clear existing content
        container.innerHTML = '';
        
        // Create timeline items
        performances.forEach((performance, index) => {
            const timelineItem = document.createElement('div');
            timelineItem.className = 'timeline-item';
            
            const timelineContent = document.createElement('div');
            timelineContent.className = 'timeline-content';
            
            timelineContent.innerHTML = `
                <span class="timeline-date">${DataService.formatDateRange(performance.startDate, performance.endDate)}</span>
                <h3>${performance.title}</h3>
                <p class="company">${performance.companyName}</p>
                <p class="description">${performance.description.substring(0, 150)}...</p>
                <a href="companies/${performance.company}.html" class="view-details-btn">View Details</a>
            `;
            
            timelineItem.appendChild(timelineContent);
            container.appendChild(timelineItem);
        });
    };
    
    /**
     * Renders company performances for a company page
     * @param {Array} performances - Array of performance objects
     * @param {string} containerId - ID of the container element
     * @param {boolean} isPast - Whether these are past performances
     */
    const renderCompanyPerformances = (performances, containerId, isPast = false) => {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        // Clear existing content except loading indicator
        const loadingIndicator = container.querySelector('.loading-indicator');
        container.innerHTML = '';
        
        if (performances.length === 0) {
            container.innerHTML = '<p class="no-performances">No performances found.</p>';
            return;
        }
        
        // Filter performances based on past/current status
        const filteredPerformances = isPast 
            ? performances.filter(p => p.isPast) 
            : performances.filter(p => !p.isPast);
        
        if (filteredPerformances.length === 0) {
            container.innerHTML = `<p class="no-performances">No ${isPast ? 'past' : 'upcoming'} performances found.</p>`;
            return;
        }
        
        // Create performance items for all performances
        filteredPerformances.forEach((performance, index) => {
            const performanceItem = document.createElement('div');
            performanceItem.className = 'performance-item';
            
            // Add special classes for current and next shows
            if (performance.isCurrent) {
                performanceItem.classList.add('current-show');
            } else if (performance.isNext) {
                performanceItem.classList.add('next-show');
            }
            
            // Enhanced logging to diagnose description issue
            console.log('Performance data for ' + performance.title + ':', {
                title: performance.title,
                description: performance.description,
                descriptionLength: performance.description ? performance.description.length : 0,
                hasDescription: !!performance.description,
                startDate: performance.startDate,
                endDate: performance.endDate,
                formattedDateRange: DataService.formatDateRange(performance.startDate, performance.endDate)
            });
            
            // Log the raw performance object
            console.log('Raw performance object:', JSON.stringify(performance, null, 2));
            
            performanceItem.innerHTML = `
                <div class="performance-header">
                    <div>
                        <h3 class="performance-title">${performance.title}</h3>
                        <p class="performance-dates">${DataService.formatDateRange(performance.startDate, performance.endDate)}</p>
                    </div>
                    ${performance.isCurrent ? '<span class="performance-tag current-tag">Current Performance</span>' : ''}
                    ${performance.isNext ? '<span class="performance-tag next-tag">Next Performance</span>' : ''}
                </div>
                <div class="performance-content">
                    <div class="performance-media">
                        <img 
                            src="${validateImageUrl(performance.image)}" 
                            alt="${performance.title}" 
                            class="performance-image" 
                            loading="lazy" 
                            onerror="console.error('Failed to load image:', this.src); this.onerror=null; this.src='../images/placeholder-performance.jpg';">
                        ${performance.videoUrl ? '<button class="performance-video-btn" aria-label="Play video">▶</button>' : ''}
                    </div>
                    <div class="performance-details">
                        <div class="performance-description">
                            ${performance.description || 'No description available'}
                        </div>
                    </div>
                </div>
            `;
            
            // Add video modal functionality if video exists
            if (performance.videoUrl) {
                const videoBtn = performanceItem.querySelector('.performance-video-btn');
                videoBtn.addEventListener('click', () => {
                    openVideoModal(performance.videoUrl, performance.title);
                });
            }
            
            
            container.appendChild(performanceItem);
        });

        // No "Load More" button - all performances are displayed at once

        // Initialize observers for initial elements
        initObservers();
    };
    
    /**
     * Opens a video modal with the provided video URL
     * @param {string} videoUrl - URL of the video to display
     * @param {string} title - Title of the video
     */
    const openVideoModal = (videoUrl, title) => {
        // Check if modal already exists
        let modal = document.querySelector('.video-modal');
        
        // Create modal if it doesn't exist
        if (!modal) {
            modal = document.createElement('div');
            modal.className = 'video-modal';
            modal.innerHTML = `
                <div class="video-container">
                    <button class="close-video-btn" aria-label="Close video">&times;</button>
                    <iframe title="${title}" frameborder="0" allowfullscreen></iframe>
                </div>
            `;
            document.body.appendChild(modal);
            
            // Add event listener to close button
            const closeBtn = modal.querySelector('.close-video-btn');
            closeBtn.addEventListener('click', () => {
                closeVideoModal();
            });
            
            // Close modal when clicking outside the video
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    closeVideoModal();
                }
            });
            
            // Close modal with escape key
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    closeVideoModal();
                }
            });
        }
        
        // Set video source
        const iframe = modal.querySelector('iframe');
        iframe.src = videoUrl;
        
        // Show modal
        setTimeout(() => {
            modal.classList.add('active');
        }, 10);
    };
    
    /**
     * Closes the video modal
     */
    const closeVideoModal = () => {
        const modal = document.querySelector('.video-modal');
        if (modal) {
            modal.classList.remove('active');
            
            // Remove iframe source to stop video
            setTimeout(() => {
                const iframe = modal.querySelector('iframe');
                iframe.src = '';
            }, 300);
        }
    };
    
    /**
     * Initializes the toggle functionality for past performances
     * @param {string} btnId - ID of the toggle button
     * @param {string} containerId - ID of the container to toggle
     */
    const initPastPerformancesToggle = (btnId, containerId) => {
        const btn = document.getElementById(btnId);
        const container = document.getElementById(containerId);
        
        if (btn && container) {
            btn.addEventListener('click', () => {
                container.classList.toggle('hidden');
                btn.textContent = container.classList.contains('hidden') 
                    ? 'Show Past Performances' 
                    : 'Hide Past Performances';
            });
        }
    };
    
    // Public API
    return {
        init,
        initBannerSlider,
        renderPerformanceCards,
        renderPerformanceTimeline,
        renderCompanyPerformances,
        initPastPerformancesToggle
    };
})();
