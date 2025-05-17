"""
Bolshoi Ballet Scraper

This module scrapes ballet performance data from the Bolshoi Theatre website
and stores it in a MongoDB database.
"""

import os
import re
import time
import logging
import random
import argparse
from datetime import datetime
from bs4 import BeautifulSoup
import schedule

# Import common utilities
from scrapers.common.db import get_collection, store_performances
from scrapers.common.utils import (
    setup_selenium_driver,
    fetch_with_requests,
    fetch_with_selenium,
    accept_cookies,
    save_debug_info,
    clean_html,
    parse_date_range
)

# Import Bolshoi Ballet specific configuration
from scrapers.bolshoi_ballet.config import (
    BASE_URL,
    LOCAL_HTML_PATH,
    COLLECTION_NAME,
    BALLET_TITLES,
    SELECTORS,
    DEFAULT_DESCRIPTIONS,
    COOKIE_SELECTORS,
    REGEX_PATTERNS,
    IMPLICIT_WAIT,
    PAGE_LOAD_TIMEOUT,
    REQUEST_DELAY,
    UPDATE_INTERVAL
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def read_in_chunks(file_object, chunk_size=8192):
    """Read a file in chunks to avoid memory issues with large files."""
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data

def extract_ballet_performances_from_html(html_content):
    """
    Extract ballet performance data from HTML content.
    
    Args:
        html_content (str): HTML content
        
    Returns:
        list: List of performance dictionaries
    """
    logger.info("Extracting ballet performances from HTML content")
    
    try:
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        logger.info("HTML parsed with BeautifulSoup")
        
        # Extract performances
        performances = []
        
        # Find all text that matches ballet performance patterns
        ballet_pattern = re.compile(REGEX_PATTERNS['ballet_section'], re.DOTALL)
        ballet_sections = ballet_pattern.findall(html_content)
        
        # Extract sections around ballet titles
        for title in BALLET_TITLES:
            title_pattern = re.compile(f"{title}.*?(?:\d+\+|$)", re.DOTALL)
            title_sections = title_pattern.findall(html_content)
            if title_sections:
                logger.info(f"Found section for ballet: {title}")
                ballet_sections.extend(title_sections)
        
        logger.info(f"Found {len(ballet_sections)} potential ballet sections")
        
        # Process each ballet section
        for idx, section in enumerate(ballet_sections):
            try:
                # First check if this is a section from the ballet titles list
                title = "Unknown Ballet"
                for ballet_title in BALLET_TITLES:
                    if ballet_title in section:
                        title = ballet_title
                        break
                
                # If not found, try to extract from the pattern
                if title == "Unknown Ballet":
                    title_match = re.search(REGEX_PATTERNS['title'], section)
                    if title_match:
                        title = title_match.group(1).strip()
                
                # Extract composer/music
                composer_match = re.search(REGEX_PATTERNS['composer'], section)
                composer = composer_match.group(1).strip() if composer_match else ""
                
                # Extract date if present
                date_match = re.search(REGEX_PATTERNS['date'], section)
                date = date_match.group(1).strip() if date_match else ""
                
                # Extract age restriction
                age_match = re.search(REGEX_PATTERNS['age_restriction'], section)
                age_restriction = age_match.group(1) if age_match else ""
                
                # Extract ballet type
                type_match = re.search(REGEX_PATTERNS['ballet_type'], section)
                ballet_type = type_match.group(1).strip() if type_match else ""
                
                # Clean up HTML from extracted fields
                for field in ['title', 'composer', 'date', 'age_restriction', 'ballet_type']:
                    if locals()[field] and isinstance(locals()[field], str):
                        locals()[field] = clean_html(locals()[field])
                
                # Create performance object
                performance = {
                    'title': title,
                    'composer': composer,
                    'date': date,
                    'age_restriction': age_restriction,
                    'ballet_type': ballet_type,
                    'venue': 'Bolshoi Theatre',
                    'source': 'Bolshoi Theatre Website',
                    'url': f"{BASE_URL}/performances/{title.lower().replace(' ', '-')}",
                    'details_scraped': False,
                    'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'company': 'Bolshoi Ballet'
                }
                
                # Parse date range
                start_date, end_date = parse_date_range(date)
                if start_date and end_date:
                    performance['startDate'] = start_date.strftime('%Y-%m-%d')
                    performance['endDate'] = end_date.strftime('%Y-%m-%d')
                
                performances.append(performance)
                logger.info(f"Extracted performance {idx+1}: {title}")
                
            except Exception as e:
                logger.error(f"Error processing ballet section {idx+1}: {str(e)}")
                continue
        
        # If we couldn't extract performances using the pattern approach,
        # try to extract from the structured HTML
        if not performances:
            logger.info("Attempting to extract performances from structured HTML")
            
            # Look for elements that might contain performance information
            performance_elements = []
            for selector in SELECTORS['performance']:
                if selector.startswith("//"):
                    performance_elements = soup.find_all(selector, recursive=True)
                else:
                    performance_elements = soup.select(selector)
                if performance_elements:
                    logger.info(f"Found {len(performance_elements)} performance elements using selector: {selector}")
                    break
            
            for idx, element in enumerate(performance_elements):
                try:
                    # Extract title
                    title = "Unknown Ballet"
                    for selector in SELECTORS['title']:
                        title_elem = element.select_one(selector)
                        if title_elem:
                            title = title_elem.text.strip()
                            break
                    
                    # Extract date
                    date = ""
                    for selector in SELECTORS['date']:
                        date_elem = element.select_one(selector)
                        if date_elem:
                            date = date_elem.text.strip()
                            break
                    
                    # Extract composer
                    composer = ""
                    for selector in SELECTORS['composer']:
                        composer_elem = element.select_one(selector)
                        if composer_elem:
                            composer = composer_elem.text.strip()
                            break
                    
                    # Extract venue
                    venue = "Bolshoi Theatre"
                    for selector in SELECTORS['venue']:
                        venue_elem = element.select_one(selector)
                        if venue_elem:
                            venue = venue_elem.text.strip()
                            break
                    
                    # Extract URL if available
                    url = ""
                    link_elem = element.find('a')
                    if link_elem and 'href' in link_elem.attrs:
                        url = link_elem['href']
                        if not url.startswith('http'):
                            url = f"https://www.bolshoi.ru{url}"
                    else:
                        url = f"{BASE_URL}/performances/{title.lower().replace(' ', '-')}"
                    
                    # Create performance object
                    performance = {
                        'title': title,
                        'composer': composer,
                        'date': date,
                        'venue': venue,
                        'source': 'Bolshoi Theatre Website',
                        'url': url,
                        'details_scraped': False,
                        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'company': 'Bolshoi Ballet'
                    }
                    
                    # Parse date range
                    start_date, end_date = parse_date_range(date)
                    if start_date and end_date:
                        performance['startDate'] = start_date.strftime('%Y-%m-%d')
                        performance['endDate'] = end_date.strftime('%Y-%m-%d')
                    
                    performances.append(performance)
                    logger.info(f"Extracted performance {idx+1}: {title}")
                    
                except Exception as e:
                    logger.error(f"Error processing performance element {idx+1}: {str(e)}")
                    continue
        
        logger.info(f"Extracted {len(performances)} performances")
        return performances
        
    except Exception as e:
        logger.error(f"Error extracting ballet performances: {str(e)}")
        return []

def extract_ballet_performances_from_file(html_file):
    """
    Extract ballet performance data from a local HTML file.
    
    Args:
        html_file (str): Path to the HTML file
        
    Returns:
        list: List of performance dictionaries
    """
    logger.info(f"Processing HTML file: {html_file}")
    
    # Check if file exists
    if not os.path.exists(html_file):
        logger.error(f"File not found: {html_file}")
        return []
    
    try:
        # Read the file in chunks to avoid memory issues
        html_content = ""
        with open(html_file, 'r', encoding='utf-8') as f:
            for chunk in read_in_chunks(f):
                html_content += chunk
        
        logger.info(f"HTML content loaded, length: {len(html_content)} characters")
        
        return extract_ballet_performances_from_html(html_content)
        
    except Exception as e:
        logger.error(f"Error processing HTML file: {str(e)}")
        return []

def extract_ballet_performances_from_url(url=BASE_URL, use_selenium=False):
    """
    Extract ballet performance data directly from the Bolshoi Theatre website.
    
    Args:
        url (str): URL to scrape
        use_selenium (bool): Whether to use Selenium for JavaScript-heavy pages
        
    Returns:
        list: List of performance dictionaries
    """
    logger.info(f"Processing URL: {url}")
    
    try:
        # Fetch HTML content
        if use_selenium:
            driver = setup_selenium_driver()
            try:
                driver.get(url)
                driver.implicitly_wait(IMPLICIT_WAIT)
                
                # Handle cookie consent
                accept_cookies(driver, COOKIE_SELECTORS)
                
                # Wait for page to load
                time.sleep(2)
                
                html_content = driver.page_source
            finally:
                driver.quit()
        else:
            html_content = fetch_with_requests(url)
        
        if not html_content:
            logger.error("Failed to fetch HTML content")
            return []
        
        logger.info(f"HTML content fetched, length: {len(html_content)} characters")
        
        return extract_ballet_performances_from_html(html_content)
        
    except Exception as e:
        logger.error(f"Error processing URL: {str(e)}")
        return []

def scrape_performance_details(performance, use_selenium=False):
    """
    Scrape detailed information for a performance.
    
    Args:
        performance (dict): Performance dictionary
        use_selenium (bool): Whether to use Selenium for JavaScript-heavy pages
        
    Returns:
        dict: Updated performance dictionary
    """
    if not performance.get('url'):
        logger.warning(f"No URL for performance: {performance.get('title', 'Unknown')}")
        return performance
    
    url = performance['url']
    logger.info(f"Scraping details for: {performance.get('title', 'Unknown')} from {url}")
    
    try:
        # Fetch HTML content
        if use_selenium:
            driver = setup_selenium_driver()
            try:
                driver.get(url)
                driver.implicitly_wait(IMPLICIT_WAIT)
                
                # Handle cookie consent
                accept_cookies(driver, COOKIE_SELECTORS)
                
                # Wait for page to load
                time.sleep(2)
                
                html_content = driver.page_source
            finally:
                driver.quit()
        else:
            html_content = fetch_with_requests(url)
        
        if not html_content:
            logger.error(f"Failed to fetch HTML content for {url}")
            return performance
        
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract description
        description = None
        for selector in SELECTORS['description']:
            if selector.startswith('meta'):
                desc_elem = soup.select_one(selector)
                if desc_elem and 'content' in desc_elem.attrs:
                    description = desc_elem['content'].strip()
                    break
            else:
                desc_elem = soup.select_one(selector)
                if desc_elem:
                    description = desc_elem.text.strip()
                    break
        
        # Clean the description
        if description:
            description = clean_html(description)
            performance['description'] = description
            logger.info(f"Found description for {performance.get('title', 'Unknown')}")
        else:
            # Use default description if available
            title = performance.get('title', '')
            if title in DEFAULT_DESCRIPTIONS:
                performance['description'] = DEFAULT_DESCRIPTIONS[title]
                logger.info(f"Using default description for {title}")
            else:
                performance['description'] = f"This performance of {title} by the Bolshoi Ballet showcases the company's artistic excellence and technical precision."
                logger.info(f"Using generic description for {title}")
        
        # Add composer information to description if available
        if 'composer' in performance and performance['composer'] and 'description' in performance:
            composer_info = performance['composer']
            if not composer_info in performance['description']:
                performance['description'] = f"{performance['description']} Music by {composer_info}."
        
        # Mark as scraped
        performance['details_scraped'] = True
        performance['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return performance
    except Exception as e:
        logger.error(f"Error scraping details for {performance.get('title', 'Unknown')}: {str(e)}")
        return performance

def scrape_all_performances(use_web=False, use_selenium=False, html_file=LOCAL_HTML_PATH, scrape_details=True):
    """
    Scrape all performances, either from a local file or from the web.
    
    Args:
        use_web (bool): Whether to scrape from the web
        use_selenium (bool): Whether to use Selenium for web scraping
        html_file (str): Path to the local HTML file
        scrape_details (bool): Whether to scrape detailed information for each performance
        
    Returns:
        list: List of performance dictionaries
    """
    performances = []
    
    if use_web:
        logger.info("Scraping performances from the web")
        performances = extract_ballet_performances_from_url(BASE_URL, use_selenium)
    else:
        logger.info("Scraping performances from local file")
        performances = extract_ballet_performances_from_file(html_file)
    
    if scrape_details and performances:
        logger.info(f"Scraping details for {len(performances)} performances")
        for i, performance in enumerate(performances):
            logger.info(f"Scraping details for performance {i+1}/{len(performances)}: {performance.get('title', 'Unknown')}")
            
            # Add a random delay between requests (2-5 seconds)
            time.sleep(REQUEST_DELAY + random.random() * 3)
            
            # Scrape details
            performances[i] = scrape_performance_details(performance, use_selenium)
    
    return performances

def main_scrape(use_web=False, use_selenium=False, html_file=LOCAL_HTML_PATH, scrape_details=True):
    """
    Main scraping function.
    
    Args:
        use_web (bool): Whether to scrape from the web
        use_selenium (bool): Whether to use Selenium for web scraping
        html_file (str): Path to the local HTML file
        scrape_details (bool): Whether to scrape detailed information for each performance
        
    Returns:
        bool: True if successful, False otherwise
    """
    collection = get_collection(COLLECTION_NAME)
    
    try:
        logger.info("Starting Bolshoi Ballet scrape")
        performances = scrape_all_performances(use_web, use_selenium, html_file, scrape_details)
        
        if not performances:
            logger.error("No performances found")
            return False
        
        # Store performances in MongoDB
        success = store_performances(collection, performances)
        
        return success
    except Exception as e:
        logger.error(f"An error occurred during main scrape: {str(e)}")
        return False

def scheduled_scrape():
    """
    Function to be called by the scheduler.
    """
    logger.info("Starting scheduled Bolshoi Ballet scrape")
    success = main_scrape(use_web=True, use_selenium=True)
    logger.info(f"Scheduled scrape completed with success: {success}")

def print_stored_data():
    """
    Print stored data for debugging.
    """
    collection = get_collection(COLLECTION_NAME)
    
    performances = list(collection.find())
    logger.info(f"Total performances stored: {len(performances)}")
    
    for performance in performances[:3]:  # Print details of first 3 performances
        logger.info(f"\nPerformance: {performance['title']}")
        logger.info(f"URL: {performance['url']}")
        logger.info(f"Venue: {performance['venue']}")
        logger.info(f"Date: {performance['date']}")
        if 'description' in performance:
            logger.info(f"Description: {performance['description'][:100]}...")  # First 100 characters
        logger.info(f"Details Scraped: {performance['details_scraped']}")
        logger.info(f"Last Updated: {performance['last_updated']}")

def main():
    """
    Main function with command-line interface.
    """
    parser = argparse.ArgumentParser(description='Bolshoi Ballet Scraper')
    parser.add_argument('--web', action='store_true', help='Scrape from the web instead of local file')
    parser.add_argument('--selenium', action='store_true', help='Use Selenium for web scraping')
    parser.add_argument('--file', type=str, default=LOCAL_HTML_PATH, help='Path to local HTML file')
    parser.add_argument('--no-details', action='store_true', help='Skip scraping individual performance details')
    parser.add_argument('--print-data', action='store_true', help='Print stored data after scraping')
    parser.add_argument('--schedule', action='store_true', help='Run as a scheduled task')
    parser.add_argument('--interval', type=int, default=UPDATE_INTERVAL, help=f'Update interval in days (default: {UPDATE_INTERVAL})')
    
    args = parser.parse_args()
    
    if args.schedule:
        logger.info(f"Setting up scheduled scraping every {args.interval} days")
        main_scrape(args.web, args.selenium, args.file, not args.no_details)  # Run once immediately
        
        if args.print_data:
            print_stored_data()
        
        schedule.every(args.interval).days.do(scheduled_scrape)
        
        logger.info(f"Scheduled to run every {args.interval} days")
        while True:
            schedule.run_pending()
            time.sleep(1)
    else:
        success = main_scrape(args.web, args.selenium, args.file, not args.no_details)
        
        if args.print_data:
            print_stored_data()
        
        return 0 if success else 1

if __name__ == "__main__":
    main()
