/**
 * World Ballets - API Integration with Mock Data Fallback
 * 
 * This file replaces the original data-service.js to use the server API
 * instead of the browser-based scraper, with fallback to mock data when the API is unavailable.
 */

const DataService = (() => {
    // API configuration
    const API_BASE_URL = 'http://localhost:8000/api'; // Updated port for the API
    
    /**
     * Fetches company information
     * @param {string} companyId - The ID of the company
     * @returns {Promise} - Resolves with company data
     */
    const getCompanyInfo = async (companyId) => {
        try {
            const response = await fetch(`${API_BASE_URL}/companies/paris-opera-ballet`);
            
            if (!response.ok) {
                throw new Error(`Failed to fetch company info: ${response.status} ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`Error fetching company ${companyId}:`, error);
            console.warn('Falling back to mock data');
            
            // We still want to show company info for NBC even if the API fails
            // so we'll keep the mock data fallback for company info
            return MockData.getCompanyInfo(companyId);
        }
    };
    
    /**
     * Fetches performances for a specific company
     * @param {string} companyId - The ID of the company
     * @returns {Promise} - Resolves with performances data
     */
    const getCompanyPerformances = async (companyId) => {
        console.log(`Fetching performances for company ${companyId}...`);
        
        try {
            const response = await fetch(`${API_BASE_URL}/companies/${companyId}/performances`);
            
            if (!response.ok) {
                throw new Error(`Failed to fetch performances: ${response.status} ${response.statusText}`);
            }
            
            const performances = await response.json();
            
            console.log('API Response:', performances);
            
            // Process the performances to ensure all required fields are present
            const processedPerformances = performances.map(performance => ({
                id: performance.id || performance.url,
                title: performance.title || 'Untitled Performance',
                description: performance.description || 'No description available',
                image: performance.thumbnail || performance.image || 'placeholder.jpg',
                startDate: performance.startDate || '',
                endDate: performance.endDate || '',
                venue: performance.venue || '',
                videoUrl: performance.videoUrl || '',
                isCurrent: performance.isCurrent || false,
                isNext: performance.isNext || false
            }));
            
            console.log('Processed Performances:', processedPerformances);
            return processedPerformances;
        } catch (error) {
            console.error(`Error fetching performances for company ${companyId}:`, error);
            console.warn('Falling back to mock data');
            
            // Fallback to mock data
            return getMockPerformances(companyId);
        }
    };
    
    /**
     * Fetches all current performances across all companies
     * @returns {Promise} - Resolves with current performances data
     */
    const getAllCurrentPerformances = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/performances/current`);
            
            if (!response.ok) {
                throw new Error(`Failed to fetch current performances: ${response.status} ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error fetching current performances:', error);
            console.warn('Falling back to mock data (excluding NBC)');
            
            // Get all mock performances except NBC
            const allPerformances = MockData.getAllCurrentPerformances();
            return allPerformances.filter(p => p.company !== 'nbc');
        }
    };
    
    /**
     * Fetches featured performances for the homepage
     * @param {number} count - Number of featured performances to return
     * @returns {Promise} - Resolves with featured performances data
     */
    const getFeaturedPerformances = async (count = 3) => {
        try {
            const response = await fetch(`${API_BASE_URL}/performances?current=true&limit=${count}`);
            
            if (!response.ok) {
                throw new Error(`Failed to fetch featured performances: ${response.status} ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error fetching featured performances:', error);
            console.warn('Falling back to mock data (excluding NBC)');
            
            // Get featured performances from mock data, excluding NBC
            const mockPerformances = MockData.getFeaturedPerformances(count);
            return mockPerformances.filter(p => p.company !== 'nbc');
        }
    };
    
    /**
     * Formats a date range for display
     * @param {string} startDate - Start date in YYYY-MM-DD format
     * @param {string} endDate - End date in YYYY-MM-DD format
     * @returns {string} - Formatted date range
     */
    const formatDateRange = (startDate, endDate) => {
        const start = new Date(startDate);
        const end = new Date(endDate);
        
        const options = { month: 'long', day: 'numeric', year: 'numeric' };
        const startFormatted = start.toLocaleDateString('en-US', options);
        const endFormatted = end.toLocaleDateString('en-US', options);
        
        return `${startFormatted} - ${endFormatted}`;
    };
    
    /**
     * Checks if a performance is current (happening now or within 30 days)
     * @param {Object} performance - Performance object with startDate and endDate
     * @returns {boolean} - True if performance is current
     */
    const isCurrentPerformance = (performance) => {
        const currentDate = new Date();
        const startDate = new Date(performance.startDate);
        const endDate = new Date(performance.endDate);
        
        return (currentDate >= startDate && currentDate <= endDate) || 
               (startDate > currentDate && startDate <= new Date(currentDate.getTime() + 30 * 24 * 60 * 60 * 1000));
    };
    
    /**
     * Checks if a performance is the next upcoming one
     * @param {Array} performances - Sorted array of performance objects
     * @param {Object} performance - Performance to check
     * @returns {boolean} - True if performance is the next upcoming one
     */
    const isNextPerformance = (performances, performance) => {
        const currentDate = new Date();
        
        // Find the first performance that hasn't started yet
        const upcomingPerformances = performances.filter(p => new Date(p.startDate) > currentDate);
        
        if (upcomingPerformances.length > 0) {
            return performance.id === upcomingPerformances[0].id;
        }
        
        return false;
    };
    
    /**
     * Gets mock company information for a specific company
     * @param {string} companyId - The ID of the company
     * @returns {Object} - Company information object
     */
    const getMockCompanyInfo = (companyId) => {
        return MockData.getCompanyInfo(companyId);
    };
    
    /**
     * Gets mock performances for a specific company
     * @param {string} companyId - The ID of the company
     * @returns {Array} - Array of performance objects
     */
    const getMockPerformances = (companyId) => {
        return MockData.getCompanyPerformances(companyId);
    };
    
    // Public API
    return {
        getCompanyInfo,
        getCompanyPerformances,
        getAllCurrentPerformances,
        getFeaturedPerformances,
        formatDateRange,
        isCurrentPerformance,
        isNextPerformance,
        getMockCompanyInfo,
        getMockPerformances
    };
})();
