/**
 * Ballet World - Data Service
 * 
 * This module provides a unified interface for accessing ballet performance data
 * from the API with caching and fallback to mock data when the API is unavailable.
 */

const BalletDataService = (() => {
    // API configuration
    const API_BASE_URL = 'http://localhost:8000/api';
    
    // Cache configuration
    const CACHE_VERSION = '1.0';
    const CACHE_PREFIX = 'ballet_data_';
    const CACHE_EXPIRY = 30 * 24 * 60 * 60 * 1000; // 30 days in milliseconds
    
    // Private methods
    const clearCache = () => {
        Object.keys(localStorage).forEach(key => {
            if (key.startsWith(CACHE_PREFIX)) {
                localStorage.removeItem(key);
            }
        });
        console.log('Cache cleared');
    };
    
    const getCachedData = (key) => {
        const cacheKey = `${CACHE_PREFIX}${key}_v${CACHE_VERSION}`;
        const cachedData = localStorage.getItem(cacheKey);
        
        if (cachedData) {
            try {
                const parsed = JSON.parse(cachedData);
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
    
    const formatDateRange = (startDate, endDate) => {
        if (!startDate || !endDate) return '';
        
        const start = new Date(startDate);
        const end = new Date(endDate);
        
        const options = { month: 'long', day: 'numeric', year: 'numeric' };
        const startFormatted = start.toLocaleDateString('en-US', options);
        const endFormatted = end.toLocaleDateString('en-US', options);
        
        return `${startFormatted} - ${endFormatted}`;
    };
    
    const isCurrentPerformance = (performance) => {
        if (!performance.startDate || !performance.endDate) return false;
        
        const currentDate = new Date();
        const startDate = new Date(performance.startDate);
        const endDate = new Date(performance.endDate);
        
        if (endDate < currentDate) {
            return false;
        }
        
        return (currentDate >= startDate && currentDate <= endDate) || 
               (startDate > currentDate && startDate <= new Date(currentDate.getTime() + 30 * 24 * 60 * 60 * 1000));
    };
    
    // Public API
    return {
        // Company data
        getCompanyInfo: async (companyId, forceRefresh = false) => {
            if (!companyId) {
                console.error('Company ID is required');
                return null;
            }
            
            if (!forceRefresh) {
                const cachedData = getCachedData(`company_${companyId}`);
                if (cachedData) return cachedData;
            }
            
            try {
                const response = await fetch(`${API_BASE_URL}/companies/${companyId}`);
                
                if (!response.ok) {
                    throw new Error(`Failed to fetch company info: ${response.status} ${response.statusText}`);
                }
                
                const data = await response.json();
                setCachedData(`company_${companyId}`, data);
                return data;
            } catch (error) {
                console.error(`Error fetching company ${companyId}:`, error);
                console.warn('Falling back to mock data');
                return MockData.getCompanyInfo(companyId);
            }
        },
        
        getAllCompanies: async (forceRefresh = false) => {
            if (!forceRefresh) {
                const cachedData = getCachedData('all_companies');
                if (cachedData) return cachedData;
            }
            
            try {
                const response = await fetch(`${API_BASE_URL}/companies`);
                
                if (!response.ok) {
                    throw new Error(`Failed to fetch companies: ${response.status} ${response.statusText}`);
                }
                
                const data = await response.json();
                setCachedData('all_companies', data);
                return data;
            } catch (error) {
                console.error('Error fetching companies:', error);
                console.warn('Falling back to mock data');
                return MockData.getAllCompanies();
            }
        },
        
        // Performance data
        getCompanyPerformances: async (companyId, forceRefresh = false) => {
            if (!companyId) {
                console.error('Company ID is required');
                return [];
            }
            
            if (!forceRefresh) {
                const cachedData = getCachedData(`performances_${companyId}`);
                if (cachedData) return cachedData;
            }
            
            try {
                const response = await fetch(`${API_BASE_URL}/performances/${companyId}`);
                
                if (!response.ok) {
                    throw new Error(`Failed to fetch performances: ${response.status} ${response.statusText}`);
                }
                
                const result = await response.json();
                const performances = result.data || [];
                
                const processedPerformances = performances.map(performance => ({
                    id: performance.id || performance._id || performance.url,
                    title: performance.title || 'Untitled Performance',
                    description: performance.description || 'No description available',
                    image: performance.image || 'https://placehold.co/800x400?text=No+Image',
                    thumbnail: performance.thumbnail || performance.image || 'https://placehold.co/400x200?text=No+Image',
                    startDate: performance.startDate || '',
                    endDate: performance.endDate || '',
                    venue: performance.venue || '',
                    videoUrl: performance.videoUrl || '',
                    company: companyId,
                    isCurrent: isCurrentPerformance(performance)
                }));
                
                setCachedData(`performances_${companyId}`, processedPerformances);
                return processedPerformances;
            } catch (error) {
                console.error(`Error fetching performances for company ${companyId}:`, error);
                console.warn('Falling back to mock data');
                return MockData.getCompanyPerformances(companyId);
            }
        },
        
        getPerformanceDetails: async (companyId, performanceId, forceRefresh = false) => {
            if (!companyId || !performanceId) {
                console.error('Company ID and Performance ID are required');
                return null;
            }
            
            if (!forceRefresh) {
                const cachedData = getCachedData(`performance_${companyId}_${performanceId}`);
                if (cachedData) return cachedData;
            }
            
            try {
                const response = await fetch(`${API_BASE_URL}/performances/${companyId}/${performanceId}`);
                
                if (!response.ok) {
                    throw new Error(`Failed to fetch performance details: ${response.status} ${response.statusText}`);
                }
                
                const data = await response.json();
                
                const processedPerformance = {
                    id: data.id || data._id || data.url,
                    title: data.title || 'Untitled Performance',
                    description: data.description || 'No description available',
                    image: data.image || 'https://placehold.co/800x400?text=No+Image',
                    thumbnail: data.thumbnail || data.image || 'https://placehold.co/400x200?text=No+Image',
                    startDate: data.startDate || '',
                    endDate: data.endDate || '',
                    venue: data.venue || '',
                    videoUrl: data.videoUrl || '',
                    company: companyId,
                    isCurrent: isCurrentPerformance(data)
                };
                
                setCachedData(`performance_${companyId}_${performanceId}`, processedPerformance);
                return processedPerformance;
            } catch (error) {
                console.error(`Error fetching performance details for ${performanceId}:`, error);
                console.warn('Falling back to mock data');
                return MockData.getPerformanceDetails(companyId, performanceId);
            }
        },
        
        getCurrentPerformances: async (limit = 10, forceRefresh = false) => {
            if (!forceRefresh) {
                const cachedData = getCachedData(`current_performances_${limit}`);
                if (cachedData) return cachedData;
            }
            
            try {
                const response = await fetch(`${API_BASE_URL}/performances?current=true&limit=${limit}`);
                
                if (!response.ok) {
                    throw new Error(`Failed to fetch current performances: ${response.status} ${response.statusText}`);
                }
                
                const result = await response.json();
                const performances = result.data || [];
                
                const processedPerformances = performances.map(performance => ({
                    id: performance.id || performance._id || performance.url,
                    title: performance.title || 'Untitled Performance',
                    description: performance.description || 'No description available',
                    image: performance.image || 'https://placehold.co/800x400?text=No+Image',
                    thumbnail: performance.thumbnail || performance.image || 'https://placehold.co/400x200?text=No+Image',
                    startDate: performance.startDate || '',
                    endDate: performance.endDate || '',
                    venue: performance.venue || '',
                    videoUrl: performance.videoUrl || '',
                    company: performance.company,
                    companyName: performance.companyName,
                    companyShortName: performance.companyShortName,
                    isCurrent: true
                }));
                
                setCachedData(`current_performances_${limit}`, processedPerformances);
                return processedPerformances;
            } catch (error) {
                console.error('Error fetching current performances:', error);
                console.warn('Falling back to mock data');
                return MockData.getAllCurrentPerformances().slice(0, limit);
            }
        },
        
        getFeaturedPerformances: async (count = 3, forceRefresh = false) => {
            const currentPerformances = await this.getCurrentPerformances(count, forceRefresh);
            return currentPerformances.slice(0, count);
        },
        
        // Search functionality
        searchPerformances: async (query, options = {}) => {
            if (!query) return [];
            
            const cacheKey = `search_${query}_${JSON.stringify(options)}`;
            
            if (!options.forceRefresh) {
                const cachedData = getCachedData(cacheKey);
                if (cachedData) return cachedData;
            }
            
            try {
                const url = new URL(`${API_BASE_URL}/search`);
                url.searchParams.append('q', query);
                
                if (options.company) {
                    url.searchParams.append('company', options.company);
                }
                
                if (options.limit) {
                    url.searchParams.append('limit', options.limit);
                }
                
                if (options.skip) {
                    url.searchParams.append('skip', options.skip);
                }
                
                const response = await fetch(url.toString());
                
                if (!response.ok) {
                    throw new Error(`Failed to search performances: ${response.status} ${response.statusText}`);
                }
                
                const result = await response.json();
                const performances = result.data || [];
                
                setCachedData(cacheKey, performances);
                return performances;
            } catch (error) {
                console.error('Error searching performances:', error);
                console.warn('Falling back to mock data');
                return MockData.searchPerformances(query);
            }
        },
        
        // Utility methods
        formatDateRange,
        isCurrentPerformance,
        clearCache
    };
})();
