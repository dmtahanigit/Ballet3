/**
 * World Ballets - API Integration with Cache and Mock Data Fallback
 * 
 * This file replaces the original data-service.js to use the server API
 * with localStorage caching and fallback to mock data when the API is unavailable.
 * Data persists between visits until explicitly refreshed.
 */

const DataService = (() => {
    // API configuration
    const API_BASE_URL = 'http://localhost:8000/api'; // Updated port for the API
    
    // Cache configuration
    const CACHE_VERSION = '1.0'; // Increment this when data structure changes
    const CACHE_PREFIX = 'ballet_data_';
    const CACHE_EXPIRY = 30 * 24 * 60 * 60 * 1000; // 30 days in milliseconds
    
    /**
     * Clears all cached data
     */
    const clearCache = () => {
        // Clear all cached data
        Object.keys(localStorage).forEach(key => {
            if (key.startsWith(CACHE_PREFIX)) {
                localStorage.removeItem(key);
            }
        });
        console.log('Cache cleared');
    };
    
    /**
     * Gets data from cache
     * @param {string} key - Cache key
     * @returns {Object|null} - Cached data or null if not found
     */
    const getCachedData = (key) => {
        const cacheKey = `${CACHE_PREFIX}${key}_v${CACHE_VERSION}`;
        const cachedData = localStorage.getItem(cacheKey);
        
        if (cachedData) {
            try {
                const parsed = JSON.parse(cachedData);
                
                // Check if cache has expired
                if (parsed.timestamp && (new Date().getTime() - parsed.timestamp < CACHE_EXPIRY)) {
                    console.log(`Using cached data for ${key}`);
                    return parsed.data;
                } else {
                    console.log(`Cache expired for ${key}`);
                    localStorage.removeItem(cacheKey);
                }
            } catch (e) {
                console.error('Error parsing cached data:', e);
                localStorage.removeItem(cacheKey);
            }
        }
        return null;
    };
    
    /**
     * Sets data in cache with timestamp
     * @param {string} key - Cache key
     * @param {Object} data - Data to cache
     */
    const setCachedData = (key, data) => {
        const cacheKey = `${CACHE_PREFIX}${key}_v${CACHE_VERSION}`;
        const cacheData = {
            data: data,
            timestamp: new Date().getTime()
        };
        
        try {
            localStorage.setItem(cacheKey, JSON.stringify(cacheData));
            console.log(`Data cached for ${key}`);
        } catch (e) {
            console.error('Error caching data:', e);
            // If localStorage is full, clear it and try again
            if (e.name === 'QuotaExceededError') {
                clearCache();
                try {
                    localStorage.setItem(cacheKey, JSON.stringify(cacheData));
                } catch (e2) {
                    console.error('Still unable to cache data after clearing:', e2);
                }
            }
        }
    };
    
    /**
     * Fetches company information with caching
     * @param {string} companyId - The ID of the company
     * @param {boolean} forceRefresh - Whether to bypass cache and force a refresh
     * @returns {Promise} - Resolves with company data
     */
    const getCompanyInfo = async (companyId, forceRefresh = false) => {
        // Check cache first (unless force refresh is requested)
        if (!forceRefresh) {
            const cachedData = getCachedData(`company_${companyId}`);
            if (cachedData) {
                return cachedData;
            }
        }
        
        try {
            const response = await fetch(`${API_BASE_URL}/companies/${companyId}`);
            
            if (!response.ok) {
                throw new Error(`Failed to fetch company info: ${response.status} ${response.statusText}`);
            }
            
            const data = await response.json();
            
            // Cache the successful response
            setCachedData(`company_${companyId}`, data);
            
            return data;
        } catch (error) {
            console.error(`Error fetching company ${companyId}:`, error);
            console.warn('Falling back to mock data');
            
            // We still want to show company info even if the API fails
            // so we'll keep the mock data fallback for company info
            return MockData.getCompanyInfo(companyId);
        }
    };
    
    /**
     * Fetches performances for a specific company with caching
     * @param {string} companyId - The ID of the company
     * @param {boolean} forceRefresh - Whether to bypass cache and force a refresh
     * @returns {Promise} - Resolves with performances data
     */
    const getCompanyPerformances = async (companyId, forceRefresh = false) => {
        console.log(`Fetching performances for company ${companyId}...`);
        
        // Check cache first (unless force refresh is requested)
        if (!forceRefresh) {
            const cachedData = getCachedData(`performances_${companyId}`);
            if (cachedData) {
                return cachedData;
            }
        }
        
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
            
            // Cache the successful response
            setCachedData(`performances_${companyId}`, processedPerformances);
            
            return processedPerformances;
        } catch (error) {
            console.error(`Error fetching performances for company ${companyId}:`, error);
            console.warn('Falling back to mock data');
            
            // Fallback to mock data
            return getMockPerformances(companyId);
        }
    };
    
    /**
     * Fetches all current performances across all companies with caching
     * @param {boolean} forceRefresh - Whether to bypass cache and force a refresh
     * @returns {Promise} - Resolves with current performances data
     */
    const getAllCurrentPerformances = async (forceRefresh = false) => {
        // Check cache first (unless force refresh is requested)
        if (!forceRefresh) {
            const cachedData = getCachedData('all_current_performances');
            if (cachedData) {
                return cachedData;
            }
        }
        
        try {
            const response = await fetch(`${API_BASE_URL}/performances/current`);
            
            if (!response.ok) {
                throw new Error(`Failed to fetch current performances: ${response.status} ${response.statusText}`);
            }
            
            const data = await response.json();
            
            // Cache the successful response
            setCachedData('all_current_performances', data);
            
            return data;
        } catch (error) {
            console.error('Error fetching current performances:', error);
            console.warn('Falling back to mock data (excluding NBC)');
            
            // Get all mock performances except NBC
            const allPerformances = MockData.getAllCurrentPerformances();
            return allPerformances.filter(p => p.company !== 'nbc');
        }
    };
    
    /**
     * Fetches featured performances for the homepage with caching
     * @param {number} count - Number of featured performances to return
     * @param {boolean} forceRefresh - Whether to bypass cache and force a refresh
     * @returns {Promise} - Resolves with featured performances data
     */
    const getFeaturedPerformances = async (count = 3, forceRefresh = false) => {
        // Check cache first (unless force refresh is requested)
        if (!forceRefresh) {
            const cachedData = getCachedData(`featured_performances_${count}`);
            if (cachedData) {
                return cachedData;
            }
        }
        
        try {
            const response = await fetch(`${API_BASE_URL}/performances?current=true&limit=${count}`);
            
            if (!response.ok) {
                throw new Error(`Failed to fetch featured performances: ${response.status} ${response.statusText}`);
            }
            
            const data = await response.json();
            
            // Cache the successful response
            setCachedData(`featured_performances_${count}`, data);
            
            return data;
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
        
        // First check that the end date is not in the past
        if (endDate < currentDate) {
            return false;
        }
        
        // Then check if it's currently running or starting within 30 days
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
        
        // Find the first performance that hasn't started yet and hasn't ended
        const upcomingPerformances = performances.filter(p => {
            const startDate = new Date(p.startDate);
            const endDate = new Date(p.endDate);
            return startDate > currentDate && endDate >= currentDate;
        });
        
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
    
    /**
     * Refreshes all data for a company by clearing cache and forcing refresh
     * @param {string} companyId - The ID of the company
     * @returns {Promise<boolean>} - Resolves with true when complete
     */
    const refreshAllData = async (companyId) => {
        console.log(`Refreshing all data for company ${companyId}...`);
        clearCache();
        
        // Force refresh all data
        try {
            await getCompanyInfo(companyId, true);
            await getCompanyPerformances(companyId, true);
            await getAllCurrentPerformances(true);
            await getFeaturedPerformances(3, true);
            console.log('All data refreshed successfully');
            return true;
        } catch (error) {
            console.error('Error refreshing data:', error);
            throw error;
        }
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
        getMockPerformances,
        refreshAllData,  // New function
        clearCache       // Expose for debugging
    };
})();
