/**
 * World Ballets - Web Scraper
 * 
 * This module handles scraping ballet performance data from official ballet company websites.
 * It uses the browser's fetch API and DOMParser to extract performance information.
 * 
 * IMPORTANT: Browser-based scraping has significant limitations due to CORS policies and website security measures.
 * Most ballet company websites will block direct scraping attempts from browsers.
 * 
 * In a production environment, this would be implemented as:
 * 1. A server-side Node.js application that scrapes websites on a schedule
 * 2. A database to store the scraped data
 * 3. An API to serve the data to the frontend
 * 
 * For demonstration purposes, this implementation attempts to scrape but falls back to mock data when scraping fails.
 * The console will show 403 Forbidden errors, which is expected behavior when websites block scraping.
 */

const Scraper = (() => {
    // Cache for storing scraped data to avoid repeated requests
    const cache = {
        companies: {},
        performances: {}
    };

    // Cache expiration time in milliseconds (1 hour)
    const CACHE_EXPIRATION = 60 * 60 * 1000;

    /**
     * Fetches HTML content from a URL
     * @param {string} url - The URL to fetch
     * @returns {Promise<string>} - The HTML content
     */
    const fetchHTML = async (url) => {
        try {
            // In a real implementation, we would use a proper backend proxy or server-side scraping
            // The following proxy is for demonstration only and will likely be blocked
            console.log(`Attempting to fetch data from ${url} (Note: This will likely be blocked by CORS policies)`);
            
            // Try with CORS proxy (will likely fail with 403 Forbidden)
            const proxyUrl = `https://cors-anywhere.herokuapp.com/${url}`;
            
            const response = await fetch(proxyUrl, {
                headers: {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
            });
            
            if (!response.ok) {
                throw new Error(`Failed to fetch ${url}: ${response.status} ${response.statusText}`);
            }
            
            return await response.text();
        } catch (error) {
            console.error(`Error fetching ${url}:`, error);
            
            // Provide more informative error message
            if (error.message.includes('403')) {
                throw new Error(`Access forbidden to ${url}. The website is blocking scraping attempts. This is expected behavior in a browser environment.`);
            } else if (error.message.includes('CORS')) {
                throw new Error(`CORS policy preventing access to ${url}. This is a common limitation of browser-based scraping.`);
            } else {
                throw error;
            }
        }
    };

    /**
     * Parses HTML content into a DOM document
     * @param {string} html - The HTML content
     * @returns {Document} - The parsed DOM document
     */
    const parseHTML = (html) => {
        const parser = new DOMParser();
        return parser.parseFromString(html, 'text/html');
    };

    /**
     * Scrapes National Ballet of Canada performances
     * @returns {Promise<Array>} - Array of performance objects
     */
    const scrapeNBC = async () => {
        // Check cache first
        if (cache.performances.nbc && (Date.now() - cache.performances.nbc.timestamp) < CACHE_EXPIRATION) {
            return cache.performances.nbc.data;
        }
        
        try {
            const html = await fetchHTML('https://national.ballet.ca/Tickets/Season-Performances');
            const doc = parseHTML(html);
            
            const performances = [];
            
            // Select performance containers
            const performanceElements = doc.querySelectorAll('.performance-item');
            
            performanceElements.forEach((element, index) => {
                // Extract performance details
                const title = element.querySelector('h2')?.textContent.trim() || 'Unknown Title';
                const dateText = element.querySelector('.dates')?.textContent.trim() || '';
                
                // Parse date range
                let startDate = null;
                let endDate = null;
                
                const dateMatch = dateText.match(/(\w+\s+\d+,\s+\d{4})\s*-\s*(\w+\s+\d+,\s+\d{4})/);
                if (dateMatch) {
                    startDate = new Date(dateMatch[1]);
                    endDate = new Date(dateMatch[2]);
                }
                
                // Format dates as YYYY-MM-DD
                const formatDate = (date) => {
                    if (!date) return null;
                    return date.toISOString().split('T')[0];
                };
                
                const description = element.querySelector('.description')?.textContent.trim() || '';
                const imageUrl = element.querySelector('img')?.src || '';
                
                // Check if there's a video
                const videoUrl = element.querySelector('a[href*="youtube"]')?.href || '';
                
                // Create performance object
                const performance = {
                    id: `nbc-${index + 1}`,
                    title,
                    company: 'nbc',
                    startDate: formatDate(startDate),
                    endDate: formatDate(endDate),
                    description,
                    image: imageUrl,
                    videoUrl: videoUrl ? `https://www.youtube.com/embed/${videoUrl.split('v=')[1]}` : '',
                    isPast: startDate && startDate < new Date()
                };
                
                performances.push(performance);
            });
            
            // Update cache
            cache.performances.nbc = {
                timestamp: Date.now(),
                data: performances
            };
            
            return performances;
        } catch (error) {
            console.error('Error scraping NBC performances:', error);
            // Fallback to mock data if scraping fails
            console.info('Scraping failed for NBC. Using mock data instead. In a production environment, this would be handled by a server-side scraper.');
            return DataService.getMockPerformances('nbc');
        }
    };

    /**
     * Scrapes American Ballet Theatre performances
     * @returns {Promise<Array>} - Array of performance objects
     */
    const scrapeABT = async () => {
        // Check cache first
        if (cache.performances.abt && (Date.now() - cache.performances.abt.timestamp) < CACHE_EXPIRATION) {
            return cache.performances.abt.data;
        }
        
        try {
            const html = await fetchHTML('https://www.abt.org/performances/');
            const doc = parseHTML(html);
            
            const performances = [];
            
            // Select performance containers
            const performanceElements = doc.querySelectorAll('.performance-item');
            
            performanceElements.forEach((element, index) => {
                // Extract performance details
                const title = element.querySelector('h3')?.textContent.trim() || 'Unknown Title';
                const dateText = element.querySelector('.dates')?.textContent.trim() || '';
                
                // Parse date range
                let startDate = null;
                let endDate = null;
                
                const dateMatch = dateText.match(/(\w+\s+\d+,\s+\d{4})\s*-\s*(\w+\s+\d+,\s+\d{4})/);
                if (dateMatch) {
                    startDate = new Date(dateMatch[1]);
                    endDate = new Date(dateMatch[2]);
                }
                
                // Format dates as YYYY-MM-DD
                const formatDate = (date) => {
                    if (!date) return null;
                    return date.toISOString().split('T')[0];
                };
                
                const description = element.querySelector('.description')?.textContent.trim() || '';
                const imageUrl = element.querySelector('img')?.src || '';
                
                // Check if there's a video
                const videoUrl = element.querySelector('a[href*="youtube"]')?.href || '';
                
                // Create performance object
                const performance = {
                    id: `abt-${index + 1}`,
                    title,
                    company: 'abt',
                    startDate: formatDate(startDate),
                    endDate: formatDate(endDate),
                    description,
                    image: imageUrl,
                    videoUrl: videoUrl ? `https://www.youtube.com/embed/${videoUrl.split('v=')[1]}` : '',
                    isPast: startDate && startDate < new Date()
                };
                
                performances.push(performance);
            });
            
            // Update cache
            cache.performances.abt = {
                timestamp: Date.now(),
                data: performances
            };
            
            return performances;
        } catch (error) {
            console.error('Error scraping ABT performances:', error);
            // Fallback to mock data if scraping fails
            console.info('Scraping failed for ABT. Using mock data instead. In a production environment, this would be handled by a server-side scraper.');
            return DataService.getMockPerformances('abt');
        }
    };

    /**
     * Scrapes company information
     * @param {string} companyId - The ID of the company
     * @returns {Promise<Object>} - Company information object
     */
    const scrapeCompanyInfo = async (companyId) => {
        // Check cache first
        if (cache.companies[companyId] && (Date.now() - cache.companies[companyId].timestamp) < CACHE_EXPIRATION) {
            return cache.companies[companyId].data;
        }
        
        try {
            let url = '';
            let logoSelector = '';
            let descriptionSelector = '';
            
            // Set scraping parameters based on company
            switch (companyId) {
                case 'nbc':
                    url = 'https://national.ballet.ca/About';
                    logoSelector = '.logo img';
                    descriptionSelector = '.about-content p';
                    break;
                case 'abt':
                    url = 'https://www.abt.org/about/';
                    logoSelector = '.logo img';
                    descriptionSelector = '.about-content p';
                    break;
                // Add cases for other companies
                default:
                    throw new Error(`Scraping not implemented for company: ${companyId}`);
            }
            
            const html = await fetchHTML(url);
            const doc = parseHTML(html);
            
            // Extract company information
            const logoUrl = doc.querySelector(logoSelector)?.src || '';
            
            // Get all description paragraphs and join them
            const descriptionElements = doc.querySelectorAll(descriptionSelector);
            let description = '';
            
            descriptionElements.forEach(element => {
                description += element.textContent.trim() + ' ';
            });
            
            description = description.trim();
            
            // Create company info object
            const companyInfo = {
                name: getCompanyName(companyId),
                shortName: getCompanyShortName(companyId),
                logo: logoUrl || getPlaceholderLogo(companyId),
                description: description || getDefaultDescription(companyId),
                website: getCompanyWebsite(companyId)
            };
            
            // Update cache
            cache.companies[companyId] = {
                timestamp: Date.now(),
                data: companyInfo
            };
            
            return companyInfo;
        } catch (error) {
            console.error(`Error scraping ${companyId} info:`, error);
            // Fallback to mock data if scraping fails
            console.info(`Scraping failed for ${companyId} info. Using mock data instead. In a production environment, this would be handled by a server-side scraper.`);
            return DataService.getMockCompanyInfo(companyId);
        }
    };

    /**
     * Gets the full name of a company based on its ID
     * @param {string} companyId - The ID of the company
     * @returns {string} - The full company name
     */
    const getCompanyName = (companyId) => {
        const names = {
            abt: 'American Ballet Theatre',
            pob: 'Paris Opera Ballet',
            bolshoi: 'Bolshoi Ballet',
            royal: 'The Royal Ballet',
            rb: 'The Royal Ballet',
            stuttgart: 'Stuttgart Ballet',
            boston: 'Boston Ballet',
            nbc: 'National Ballet of Canada'
        };
        
        return names[companyId] || 'Unknown Ballet Company';
    };

    /**
     * Gets the short name of a company based on its ID
     * @param {string} companyId - The ID of the company
     * @returns {string} - The short company name
     */
    const getCompanyShortName = (companyId) => {
        const shortNames = {
            abt: 'ABT',
            pob: 'POB',
            bolshoi: 'BOLSHOI',
            royal: 'ROYAL',
            rb: 'RB',
            stuttgart: 'STUTTGART',
            boston: 'BOSTON',
            nbc: 'NBC'
        };
        
        return shortNames[companyId] || companyId.toUpperCase();
    };

    /**
     * Gets the website URL of a company based on its ID
     * @param {string} companyId - The ID of the company
     * @returns {string} - The company website URL
     */
    const getCompanyWebsite = (companyId) => {
        const websites = {
            abt: 'https://www.abt.org',
            pob: 'https://www.operadeparis.fr/en/artists/ballet',
            bolshoi: 'https://www.bolshoi.ru/en/',
            royal: 'https://www.roh.org.uk/about/the-royal-ballet',
            rb: 'https://www.roh.org.uk/about/the-royal-ballet',
            stuttgart: 'https://www.stuttgart-ballet.de/en/',
            boston: 'https://www.bostonballet.org',
            nbc: 'https://national.ballet.ca'
        };
        
        return websites[companyId] || '';
    };

    /**
     * Gets a placeholder logo URL for a company
     * @param {string} companyId - The ID of the company
     * @returns {string} - The placeholder logo URL
     */
    const getPlaceholderLogo = (companyId) => {
        return `https://via.placeholder.com/150x150.png?text=${getCompanyShortName(companyId)}+Logo`;
    };

    /**
     * Gets a default description for a company
     * @param {string} companyId - The ID of the company
     * @returns {string} - The default description
     */
    const getDefaultDescription = (companyId) => {
        const descriptions = {
            abt: 'Founded in 1940, American Ballet Theatre is recognized as one of the world\'s leading classical ballet companies. Based in New York City, ABT annually tours the United States and around the world.',
            pob: 'The Paris Opera Ballet is the oldest national ballet company in the world, founded in 1669. It is the ballet company of the Paris Opera and is one of the most prestigious ballet companies in the world.',
            bolshoi: 'The Bolshoi Ballet is an internationally renowned classical ballet company, based at the Bolshoi Theatre in Moscow, Russia. Founded in 1776, the Bolshoi is among the world\'s oldest and most prestigious ballet companies.',
            royal: 'The Royal Ballet is an internationally renowned classical ballet company, based at the Royal Opera House in Covent Garden, London, England. Founded in 1931, it is one of the world\'s greatest ballet companies.',
            rb: 'The Royal Ballet is one of the world\'s greatest ballet companies. Based at the Royal Opera House in London\'s Covent Garden, it brings together today\'s most dynamic and versatile dancers with a world-class orchestra and leading choreographers, composers, conductors, directors and creative teams to share awe-inspiring theatrical experiences with diverse audiences worldwide.',
            stuttgart: 'The Stuttgart Ballet is a leading German ballet company based in Stuttgart, Germany. Known for its innovative choreography and technical excellence, it has been a major influence in the ballet world since the 1960s.',
            boston: 'Founded in 1963, Boston Ballet is one of the leading dance companies in North America. The company maintains an internationally acclaimed repertoire and the largest ballet school in North America.',
            nbc: 'Founded in 1951, the National Ballet of Canada is one of the premier dance companies in North America. Based in Toronto, the company performs a traditional and contemporary repertoire of the highest caliber.'
        };
        
        return descriptions[companyId] || `A world-renowned ballet company.`;
    };

    // Public API
    return {
        scrapeNBC,
        scrapeABT,
        scrapeCompanyInfo
    };
})();
