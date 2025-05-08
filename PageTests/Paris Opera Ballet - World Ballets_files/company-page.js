/**
 * World Ballets - Company Page JavaScript
 * 
 * This script handles the functionality for the individual ballet company pages.
 * It loads company information and performances, and renders them on the page.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Initialize UI
    UIController.init();
    
    // Set company ID for Paris Opera Ballet
    const companyId = 'paris-opera-ballet';
    
    // Load company information
    DataService.getCompanyInfo(companyId)
        .then(company => {
            // Update page title
            document.title = `${company.name} - World Ballets`;
            
            // Handle logo loading with specific event handlers to prevent flickering
            const logoContainer = document.querySelector('.company-logo-container');
            const logoImg = document.querySelector('.company-logo-img');
            
            if (logoImg) {
                // Remove any loading class that might cause animation/flickering
                if (logoContainer) {
                    logoContainer.classList.remove('loading');
                }
                
                // Update the alt text
                logoImg.alt = `${company.name} Logo`;
                
                // Add specific load event handler for the logo
                logoImg.onload = function() {
                    console.log('Logo image loaded successfully');
                    // Ensure the container doesn't have loading class
                    if (logoContainer) {
                        logoContainer.classList.remove('loading');
                    }
                    // Make sure the image is visible with proper styling
                    logoImg.style.opacity = '1';
                    logoImg.style.visibility = 'visible';
                };
                
                // Add specific error handler for the logo
                logoImg.onerror = function() {
                    console.error('Logo image failed to load:', logoImg.src);
                    // Still remove loading class to prevent animation
                    if (logoContainer) {
                        logoContainer.classList.remove('loading');
                    }
                };
                
                // Force a reload of the image to ensure proper loading
                const currentSrc = logoImg.src;
                logoImg.src = '';
                setTimeout(() => {
                    logoImg.src = currentSrc;
                }, 50);
            }
            
            // Add global image error handler for debugging
            document.addEventListener('error', function(e) {
                if (e.target.tagName.toLowerCase() === 'img') {
                    console.error('Image loading error:', e.target.src);
                    // Don't log the element to avoid circular references
                    console.log('Image error event:', e.type);
                }
            }, true);
            
            // Update company name and description
            const companyNameElement = document.querySelector('.company-info h1');
            const companyDescriptionElement = document.querySelector('.company-description');
            
            if (companyNameElement) {
                companyNameElement.textContent = company.name.toUpperCase();
            }
            
            if (companyDescriptionElement) {
                companyDescriptionElement.textContent = company.description;
            }
        })
        .catch(error => {
            console.error('Error loading company information:', error);
        });
    
    // Load company performances
    DataService.getCompanyPerformances(companyId)
        .then(performances => {
            console.log(`Received ${performances.length} performances for ${companyId}`);
            
            // Process performances to identify current and next shows
            const currentDate = new Date();
            
            // Sort performances by date
            performances.sort((a, b) => new Date(a.startDate) - new Date(b.startDate));
            
            // Mark current and next performances, and explicitly check for past performances
            performances.forEach((performance, index) => {
                // Check if performance is in the past (end date before current date)
                const endDate = new Date(performance.endDate);
                performance.isPast = endDate < currentDate;
                
                // Check if performance is current (happening now or within 30 days)
                performance.isCurrent = DataService.isCurrentPerformance(performance);
                
                // Check if performance is the next upcoming one
                performance.isNext = DataService.isNextPerformance(performances, performance);
                
                console.log(`Performance: ${performance.title}, Start: ${performance.startDate}, End: ${performance.endDate}, isPast: ${performance.isPast}, isCurrent: ${performance.isCurrent}`);
            });
            
            // Render current and upcoming performances (not in the past)
            const currentPerformances = performances.filter(p => !p.isPast);
            console.log(`Found ${currentPerformances.length} current/upcoming performances`);
            UIController.renderCompanyPerformances(currentPerformances, 'currentPerformances');
            
            // For Boston Ballet, we don't want to show past performances
            if (companyId === 'boston') {
                // Hide the past performances section
                const pastPerformancesSection = document.querySelector('.past-performances');
                if (pastPerformancesSection) {
                    pastPerformancesSection.style.display = 'none';
                }
            } else {
                // Render past performances for other companies
                const pastPerformances = performances.filter(p => p.isPast);
                console.log(`Found ${pastPerformances.length} past performances`);
                UIController.renderCompanyPerformances(pastPerformances, 'pastPerformances', true);
                
                // Initialize past performances toggle
                UIController.initPastPerformancesToggle('togglePastBtn', 'pastPerformances');
            }
        })
        .catch(error => {
            console.error('Error loading company performances:', error);
            document.getElementById('currentPerformances').innerHTML = '<p>Error loading performances. Please try again later.</p>';
        });
});
