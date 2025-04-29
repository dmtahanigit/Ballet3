/**
 * World Ballets - Company Page JavaScript
 * 
 * This script handles the functionality for the individual ballet company pages.
 * It loads company information and performances, and renders them on the page.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Initialize UI
    UIController.init();
    
    // Get company ID from the current URL
    // Example: /companies/nbc.html -> nbc
    const path = window.location.pathname;
    const filename = path.substring(path.lastIndexOf('/') + 1);
    const companyId = filename.replace('.html', '');
    
    if (!companyId) {
        console.error('Company ID not found in URL');
        return;
    }
    
    // Load company information
    DataService.getCompanyInfo(companyId)
        .then(company => {
            // Update page title
            document.title = `${company.name} - World Ballets`;
            
            // Update company logo
            const logoImg = document.querySelector('.company-logo-img');
            if (logoImg) {
                // Set up error handler before setting src
                logoImg.onerror = () => {
                    console.warn(`Failed to load logo for ${company.name}, using fallback`);
                    logoImg.src = '../images/placeholder-logo.svg';
                };
                logoImg.src = company.logo;
                logoImg.alt = `${company.name} Logo`;
            }
            
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
            
            // Mark current and next performances
            performances.forEach((performance, index) => {
                // Check if performance is current (happening now or within 30 days)
                performance.isCurrent = DataService.isCurrentPerformance(performance);
                
                // Check if performance is the next upcoming one
                performance.isNext = DataService.isNextPerformance(performances, performance);
                
                console.log(`Performance: ${performance.title}, Start: ${performance.startDate}, End: ${performance.endDate}, isPast: ${performance.isPast}, isCurrent: ${performance.isCurrent}`);
            });
            
            // Render current and upcoming performances
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
