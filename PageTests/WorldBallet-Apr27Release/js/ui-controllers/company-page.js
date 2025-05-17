/**
 * Ballet World - Company Page UI Controller
 * 
 * This module handles the UI interactions for the company page.
 * It uses the BalletDataService to fetch data and updates the DOM accordingly.
 */

const CompanyPageController = (() => {
    // Private variables
    let companyId = null;
    let companyData = null;
    let performances = [];
    
    // DOM element selectors
    const selectors = {
        companyInfo: '#company-info',
        companyName: '#company-name',
        companyLogo: '#company-logo',
        companyDescription: '#company-description',
        companyWebsite: '#company-website',
        performancesList: '#performances-list',
        currentPerformances: '#current-performances',
        upcomingPerformances: '#upcoming-performances',
        loadingIndicator: '.loading-indicator',
        errorMessage: '#error-message',
        refreshButton: '#refresh-data'
    };
    
    /**
     * Extracts company ID from URL
     * @returns {string} - Company ID
     */
    const getCompanyIdFromUrl = () => {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('id');
    };
    
    /**
     * Shows loading indicator
     */
    const showLoading = () => {
        document.querySelectorAll(selectors.loadingIndicator).forEach(el => {
            el.style.display = 'block';
        });
    };
    
    /**
     * Hides loading indicator
     */
    const hideLoading = () => {
        document.querySelectorAll(selectors.loadingIndicator).forEach(el => {
            el.style.display = 'none';
        });
    };
    
    /**
     * Shows error message
     * @param {string} message - Error message to display
     */
    const showError = (message) => {
        const errorEl = document.querySelector(selectors.errorMessage);
        if (errorEl) {
            errorEl.textContent = message;
            errorEl.style.display = 'block';
        }
    };
    
    /**
     * Hides error message
     */
    const hideError = () => {
        const errorEl = document.querySelector(selectors.errorMessage);
        if (errorEl) {
            errorEl.style.display = 'none';
        }
    };
    
    /**
     * Renders company information
     * @param {Object} company - Company data
     */
    const renderCompanyInfo = (company) => {
        // Update company name
        const nameEl = document.querySelector(selectors.companyName);
        if (nameEl) {
            nameEl.textContent = company.name;
            document.title = `${company.name} - World Ballets`;
        }
        
        // Update company logo
        const logoEl = document.querySelector(selectors.companyLogo);
        if (logoEl) {
            logoEl.src = company.logo || '../images/placeholder-logo.svg';
            logoEl.alt = `${company.name} Logo`;
        }
        
        // Update company description
        const descEl = document.querySelector(selectors.companyDescription);
        if (descEl) {
            descEl.textContent = company.description;
        }
        
        // Update company website link
        const websiteEl = document.querySelector(selectors.companyWebsite);
        if (websiteEl && company.website) {
            websiteEl.href = company.website;
            websiteEl.textContent = company.website;
        }
    };
    
    /**
     * Creates a performance card element
     * @param {Object} performance - Performance data
     * @returns {HTMLElement} - Performance card element
     */
    const createPerformanceCard = (performance) => {
        const card = document.createElement('div');
        card.className = 'performance-card';
        card.dataset.id = performance.id;
        
        // Format date range
        const dateRange = BalletDataService.formatDateRange(performance.startDate, performance.endDate);
        
        // Create card content
        card.innerHTML = `
            <div class="performance-image">
                <img src="${performance.thumbnail || performance.image}" alt="${performance.title}">
            </div>
            <div class="performance-details">
                <h3 class="performance-title">${performance.title}</h3>
                <p class="performance-date">${dateRange}</p>
                <p class="performance-venue">${performance.venue || ''}</p>
                <p class="performance-description">${performance.description.substring(0, 150)}${performance.description.length > 150 ? '...' : ''}</p>
                <a href="performance.html?company=${performance.company}&id=${performance.id}" class="btn btn-primary">View Details</a>
            </div>
        `;
        
        // Add current or upcoming badge if applicable
        if (performance.isCurrent) {
            const badge = document.createElement('div');
            badge.className = 'badge badge-current';
            badge.textContent = 'Current';
            card.appendChild(badge);
        } else if (performance.isNext) {
            const badge = document.createElement('div');
            badge.className = 'badge badge-next';
            badge.textContent = 'Coming Soon';
            card.appendChild(badge);
        }
        
        return card;
    };
    
    /**
     * Renders performances list
     * @param {Array} performances - Array of performance objects
     */
    const renderPerformances = (performances) => {
        // Get current and upcoming performances
        const currentPerformances = performances.filter(p => p.isCurrent);
        const upcomingPerformances = performances.filter(p => !p.isCurrent && !p.isPast);
        
        // Render current performances
        const currentEl = document.querySelector(selectors.currentPerformances);
        if (currentEl) {
            currentEl.innerHTML = '';
            
            if (currentPerformances.length > 0) {
                currentPerformances.forEach(performance => {
                    const card = createPerformanceCard(performance);
                    currentEl.appendChild(card);
                });
            } else {
                currentEl.innerHTML = '<p class="no-performances">No current performances</p>';
            }
        }
        
        // Render upcoming performances
        const upcomingEl = document.querySelector(selectors.upcomingPerformances);
        if (upcomingEl) {
            upcomingEl.innerHTML = '';
            
            if (upcomingPerformances.length > 0) {
                upcomingPerformances.forEach(performance => {
                    const card = createPerformanceCard(performance);
                    upcomingEl.appendChild(card);
                });
            } else {
                upcomingEl.innerHTML = '<p class="no-performances">No upcoming performances</p>';
            }
        }
    };
    
    /**
     * Loads company data and performances
     * @param {boolean} forceRefresh - Whether to force refresh from API
     */
    const loadCompanyData = async (forceRefresh = false) => {
        if (!companyId) {
            showError('Company ID is missing');
            return;
        }
        
        showLoading();
        hideError();
        
        try {
            // Load company info
            companyData = await BalletDataService.getCompanyInfo(companyId, forceRefresh);
            
            if (!companyData) {
                throw new Error('Company not found');
            }
            
            renderCompanyInfo(companyData);
            
            // Load performances
            performances = await BalletDataService.getCompanyPerformances(companyId, forceRefresh);
            renderPerformances(performances);
            
        } catch (error) {
            console.error('Error loading company data:', error);
            showError(`Failed to load company data: ${error.message}`);
        } finally {
            hideLoading();
        }
    };
    
    /**
     * Initializes the company page
     */
    const initPage = () => {
        // Get company ID from URL
        companyId = getCompanyIdFromUrl();
        
        if (!companyId) {
            showError('Company ID is missing');
            return;
        }
        
        // Set up refresh button
        const refreshBtn = document.querySelector(selectors.refreshButton);
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                loadCompanyData(true);
            });
        }
        
        // Load company data
        loadCompanyData();
    };
    
    // Public API
    return {
        init: initPage
    };
})();

// Initialize the page when DOM is loaded
document.addEventListener('DOMContentLoaded', CompanyPageController.init);
