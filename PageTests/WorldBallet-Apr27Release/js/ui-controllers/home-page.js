/**
 * Ballet World - Home Page UI Controller
 * 
 * This module handles the UI interactions for the home page.
 * It uses the BalletDataService to fetch data and updates the DOM accordingly.
 */

const HomePageController = (() => {
    // DOM element selectors
    const selectors = {
        featuredPerformancesList: '#featured-performances-list',
        featuredCompaniesList: '#featured-companies-list',
        loadingIndicators: '.loading-indicator'
    };
    
    /**
     * Shows loading indicators
     */
    const showLoading = () => {
        document.querySelectorAll(selectors.loadingIndicators).forEach(el => {
            el.style.display = 'block';
        });
    };
    
    /**
     * Hides loading indicators
     */
    const hideLoading = () => {
        document.querySelectorAll(selectors.loadingIndicators).forEach(el => {
            el.style.display = 'none';
        });
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
                <p class="performance-company">${performance.companyName || ''}</p>
                <p class="performance-date">${dateRange}</p>
                <p class="performance-venue">${performance.venue || ''}</p>
                <a href="performance.html?company=${performance.company}&id=${performance.id}" class="btn btn-primary">View Details</a>
            </div>
        `;
        
        // Add current badge if applicable
        if (performance.isCurrent) {
            const badge = document.createElement('div');
            badge.className = 'badge badge-current';
            badge.textContent = 'Current';
            card.appendChild(badge);
        }
        
        return card;
    };
    
    /**
     * Creates a company card element
     * @param {Object} company - Company data
     * @returns {HTMLElement} - Company card element
     */
    const createCompanyCard = (company) => {
        const card = document.createElement('div');
        card.className = 'company-card';
        card.dataset.id = company.id;
        
        // Create card content
        card.innerHTML = `
            <div class="company-logo">
                <img src="${company.logo || 'https://placehold.co/150x150?text=Logo'}" alt="${company.name} Logo">
            </div>
            <div class="company-info">
                <h3 class="company-name">${company.name}</h3>
                <p class="company-location">${company.location || ''}</p>
                <p class="company-description">${company.description.substring(0, 150)}${company.description.length > 150 ? '...' : ''}</p>
                <a href="company.html?id=${company.id}" class="btn btn-primary">View Performances</a>
            </div>
        `;
        
        return card;
    };
    
    /**
     * Renders featured performances
     * @param {Array} performances - Array of performance objects
     */
    const renderFeaturedPerformances = (performances) => {
        const container = document.querySelector(selectors.featuredPerformancesList);
        
        if (!container) return;
        
        // Clear loading indicator
        container.innerHTML = '';
        
        if (performances.length === 0) {
            container.innerHTML = '<p class="no-performances">No featured performances available</p>';
            return;
        }
        
        // Create and append performance cards
        performances.forEach(performance => {
            const card = createPerformanceCard(performance);
            container.appendChild(card);
        });
    };
    
    /**
     * Renders featured companies
     * @param {Array} companies - Array of company objects
     */
    const renderFeaturedCompanies = (companies) => {
        const container = document.querySelector(selectors.featuredCompaniesList);
        
        if (!container) return;
        
        // Clear loading indicator
        container.innerHTML = '';
        
        if (companies.length === 0) {
            container.innerHTML = '<p class="no-companies">No featured companies available</p>';
            return;
        }
        
        // Create and append company cards
        companies.forEach(company => {
            const card = createCompanyCard(company);
            container.appendChild(card);
        });
    };
    
    /**
     * Loads featured performances and companies
     */
    const loadFeaturedContent = async () => {
        showLoading();
        
        try {
            // Load featured performances (current performances)
            const featuredPerformances = await BalletDataService.getCurrentPerformances(3);
            renderFeaturedPerformances(featuredPerformances);
            
            // Load featured companies
            const allCompanies = await BalletDataService.getAllCompanies();
            // For now, just show all companies as featured
            renderFeaturedCompanies(allCompanies);
            
        } catch (error) {
            console.error('Error loading featured content:', error);
            
            // Show error message
            const performancesContainer = document.querySelector(selectors.featuredPerformancesList);
            if (performancesContainer) {
                performancesContainer.innerHTML = '<p class="error-message">Failed to load featured performances</p>';
            }
            
            const companiesContainer = document.querySelector(selectors.featuredCompaniesList);
            if (companiesContainer) {
                companiesContainer.innerHTML = '<p class="error-message">Failed to load featured companies</p>';
            }
        } finally {
            hideLoading();
        }
    };
    
    /**
     * Initializes the home page
     */
    const initPage = () => {
        // Load featured content
        loadFeaturedContent();
    };
    
    // Public API
    return {
        init: initPage
    };
})();

// Initialize the page when DOM is loaded
document.addEventListener('DOMContentLoaded', HomePageController.init);
