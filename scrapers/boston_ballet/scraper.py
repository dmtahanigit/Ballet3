"""
Boston Ballet Scraper

This module scrapes ballet performance data from the Boston Ballet website
and stores it in a MongoDB database.
"""

import time
import logging
import random
import argparse
import re
from bs4 import BeautifulSoup
import schedule

# Import common utilities
from scrapers.common.db import get_collection, store_performances
from scrapers.common.utils import (
    setup_selenium_driver, 
    accept_cookies, 
    save_debug_info, 
    clean_html,
    parse_date_range,
    fetch_with_selenium
)

# Import Boston Ballet specific configuration
from scrapers.boston_ballet.config import (
    BASE_URL, 
    COLLECTION_NAME, 
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

def scrape_main_page(driver):
    """
    Scrape the main page of the Boston Ballet website.
    
    Args:
        driver: Selenium WebDriver instance
        
    Returns:
        list: List of performance dictionaries
    """
    try:
        logger.info(f"Navigating to {BASE_URL}")
        driver.get(BASE_URL)
        
        logger.info("Handling cookie consent")
        accept_cookies(driver, COOKIE_SELECTORS)
        
        logger.info("Waiting for page to load")
        driver.implicitly_wait(IMPLICIT_WAIT)
        
        logger.info("Checking if page loaded correctly")
        if "Page not found" in driver.title or "Error" in driver.title:
            logger.error("Page not found or error encountered")
            save_debug_info(driver, "boston_main_page")
            raise Exception("Page not found or error")
        
        logger.info("Waiting for performance cards to load")
        performance_elements = None
        
        for selector in SELECTORS['performance']:
            try:
                logger.info(f"Trying selector: {selector}")
                if selector.startswith("//"):
                    from selenium.webdriver.common.by import By
                    performance_elements = driver.find_elements(By.XPATH, selector)
                else:
                    from selenium.webdriver.common.by import By
                    performance_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if performance_elements:
                    logger.info(f"Found {len(performance_elements)} performance elements using selector: {selector}")
                    break
            except Exception as e:
                logger.warning(f"Selector {selector} failed: {str(e)}")
                continue
        
        if not performance_elements:
            logger.error("Could not find performance elements with any selector")
            save_debug_info(driver, "boston_no_performances")
            raise Exception("No performance elements found")
        
        # Let the page settle after loading
        time.sleep(2)
        
        logger.info("Parsing page content")
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        performances = []
        
        # Find all performance elements
        performance_cards = []
        for selector in SELECTORS['performance']:
            if not selector.startswith("//"):  # Skip XPath selectors for BeautifulSoup
                performance_cards = soup.select(selector)
                if performance_cards:
                    logger.info(f"Found {len(performance_cards)} performance cards using selector: {selector}")
                    break
        
        if not performance_cards:
            logger.error("Could not find performance cards with BeautifulSoup")
            save_debug_info(driver, "boston_no_cards_bs4")
            raise Exception("No performance cards found with BeautifulSoup")

        for card in performance_cards:
            try:
                # Extract title
                title_elem = None
                for selector in SELECTORS['title']:
                    title_elem = card.select_one(selector)
                    if title_elem:
                        break
                
                # Extract link
                link_elem = None
                for selector in SELECTORS['link']:
                    link_elem = card.select_one(selector)
                    if link_elem:
                        break
                
                # Extract thumbnail
                img_elem = None
                for selector in SELECTORS['image']:
                    img_elem = card.select_one(selector)
                    if img_elem:
                        break
                
                if title_elem and link_elem:
                    title = title_elem.text.strip()
                    link = link_elem['href']
                    thumbnail = img_elem['src'] if img_elem and 'src' in img_elem.attrs else ''
                    
                    # Make sure link is absolute
                    if not link.startswith('http'):
                        if link.startswith('/'):
                            link = f"https://www.bostonballet.org{link}"
                        else:
                            link = f"https://www.bostonballet.org/{link}"
                    
                    # Make sure thumbnail is absolute
                    if thumbnail and not thumbnail.startswith('http'):
                        if thumbnail.startswith('/'):
                            thumbnail = f"https://www.bostonballet.org{thumbnail}"
                        else:
                            thumbnail = f"https://www.bostonballet.org/{thumbnail}"
                    
                    # Extract venue
                    venue_elem = None
                    for selector in SELECTORS['venue']:
                        venue_elem = card.select_one(selector)
                        if venue_elem:
                            break
                    venue = venue_elem.text.strip() if venue_elem else 'Boston Opera House'  # Default venue
                    
                    # Extract date
                    date_elem = None
                    for selector in SELECTORS['date']:
                        date_elem = card.select_one(selector)
                        if date_elem:
                            break
                    date = date_elem.text.strip() if date_elem else ''
                    
                    # If no date element found, try to extract from text
                    if not date:
                        card_text = card.get_text()
                        date_match = re.search(REGEX_PATTERNS['date'], card_text)
                        if date_match:
                            date = date_match.group(0)
                    
                    performance = {
                        'title': title,
                        'url': link,
                        'thumbnail': thumbnail,
                        'venue': venue,
                        'date': date,
                        'company': 'Boston Ballet',
                        'source': 'Boston Ballet Website'
                    }
                    performances.append(performance)
                    logger.info(f"Found performance: {title}")
                else:
                    logger.warning(f"Incomplete card element found - Title: {bool(title_elem)}, Link: {bool(link_elem)}")
            except Exception as e:
                logger.error(f"Error processing card element: {str(e)}", exc_info=True)
                continue

        # Log the first few performances for debugging
        for i, perf in enumerate(performances[:3]):
            logger.info(f"\nPerformance {i+1}:")
            logger.info(f"Title: {perf['title']}")
            logger.info(f"URL: {perf['url']}")
            logger.info(f"Thumbnail: {perf['thumbnail']}")
            logger.info(f"Venue: {perf['venue']}")
            logger.info(f"Date: {perf['date']}")
        
        logger.info(f"Successfully scraped {len(performances)} performances")
        return performances
    except Exception as e:
        logger.error(f"Error in scrape_main_page: {str(e)}", exc_info=True)
        raise

def scrape_individual_page(driver, url):
    """
    Scrape an individual performance page.
    
    Args:
        driver: Selenium WebDriver instance
        url (str): URL of the performance page
        
    Returns:
        dict: Performance details
    """
    try:
        logger.info(f"Navigating to individual page: {url}")
        driver.get(url)
        
        # Basic wait for page load
        driver.implicitly_wait(IMPLICIT_WAIT)
        time.sleep(2)  # Short settle time
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Enhanced selectors for description
        description = "Description not found"
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
        description = clean_html(description)
        
        # Save debug info if description not found
        if description == "Description not found":
            logger.warning("Description not found with any selector")
            save_debug_info(driver, f"boston_no_desc_{url.split('/')[-1]}")
        
        # Extract additional details
        details = {}
        
        # Look for price information
        price_match = re.search(REGEX_PATTERNS['price'], driver.page_source)
        if price_match:
            details['price_range'] = price_match.group(0)
        
        # Look for time information
        time_match = re.search(REGEX_PATTERNS['time'], driver.page_source)
        if time_match:
            details['time'] = time_match.group(0)
        
        # Look for video links (YouTube, Vimeo, etc.)
        video_links = []
        iframe_elements = soup.find_all('iframe')
        for iframe in iframe_elements:
            src = iframe.get('src', '')
            if 'youtube.com' in src or 'vimeo.com' in src:
                video_links.append(src)
        
        # Also look for YouTube links in anchor tags
        a_elements = soup.find_all('a')
        for a in a_elements:
            href = a.get('href', '')
            if 'youtube.com' in href or 'youtu.be' in href or 'vimeo.com' in href:
                video_links.append(href)
        
        logger.info(f"Found {len(video_links)} video links")
        
        return {
            'description': description,
            'video_links': video_links,
            'details': details,
            'details_scraped': True,
            'last_updated': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        logger.error(f"Error scraping individual page {url}: {str(e)}", exc_info=True)
        return {
            'description': "Failed to scrape",
            'video_links': [],
            'details': {},
            'details_scraped': False,
            'last_updated': time.strftime('%Y-%m-%d %H:%M:%S')
        }

def add_default_descriptions(performances):
    """
    Add default descriptions for well-known ballets if missing.
    
    Args:
        performances (list): List of performance dictionaries
        
    Returns:
        list: Updated performance dictionaries
    """
    for performance in performances:
        if ('description' not in performance or 
            not performance['description'] or 
            performance['description'] == "Description not found" or
            performance['description'] == "Failed to scrape"):
            
            title = performance.get('title', '')
            
            # Try to match with default descriptions
            matched = False
            for default_title, default_desc in DEFAULT_DESCRIPTIONS.items():
                if default_title.lower() in title.lower():
                    performance['description'] = default_desc
                    logger.info(f"Added default description for: {title} (matched with {default_title})")
                    matched = True
                    break
            
            if not matched and title in DEFAULT_DESCRIPTIONS:
                performance['description'] = DEFAULT_DESCRIPTIONS[title]
                logger.info(f"Added default description for: {title}")
    
    return performances

def main_scrape(use_selenium=True, scrape_details=True):
    """
    Main scraping function.
    
    Args:
        use_selenium (bool): Whether to use Selenium for scraping
        scrape_details (bool): Whether to scrape individual performance details
        
    Returns:
        bool: True if successful, False otherwise
    """
    driver = setup_selenium_driver()
    collection = get_collection(COLLECTION_NAME)
    
    try:
        logger.info("Starting Boston Ballet scrape")
        performances = scrape_main_page(driver)
        
        if scrape_details:
            for performance in performances:
                try:
                    # Add a random delay between requests (2-5 seconds)
                    time.sleep(REQUEST_DELAY + random.random() * 3)
                    
                    # Try to get additional details
                    details = scrape_individual_page(driver, performance['url'])
                    performance.update(details)
                    
                except Exception as e:
                    logger.error(f"Error scraping {performance['url']}: {str(e)}", exc_info=True)
                    # Set default values for failed scrapes
                    performance.update({
                        'description': "Failed to scrape",
                        'video_links': [],
                        'details': {},
                        'details_scraped': False,
                        'last_updated': time.strftime('%Y-%m-%d %H:%M:%S')
                    })
        else:
            logger.info("Skipping individual performance details")
            for performance in performances:
                performance.update({
                    'description': "Details not scraped",
                    'video_links': [],
                    'details': {},
                    'details_scraped': False,
                    'last_updated': time.strftime('%Y-%m-%d %H:%M:%S')
                })
        
        # Add default descriptions for well-known ballets
        performances = add_default_descriptions(performances)
        
        # Store performances in MongoDB
        success = store_performances(collection, performances)
        
        return success
    except Exception as e:
        logger.error(f"An error occurred during main scrape: {str(e)}", exc_info=True)
        return False
    finally:
        driver.quit()
        logger.info("Boston Ballet scrape completed")

def scheduled_scrape():
    """
    Function to be called by the scheduler.
    """
    logger.info("Starting scheduled Boston Ballet scrape")
    success = main_scrape()
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
        logger.info(f"Description: {performance['description'][:100]}...")  # First 100 characters
        logger.info(f"Video Links: {performance['video_links']}")
        logger.info(f"Details Scraped: {performance['details_scraped']}")
        logger.info(f"Last Updated: {performance['last_updated']}")

def main():
    """
    Main function with command-line interface.
    """
    parser = argparse.ArgumentParser(description='Boston Ballet Scraper')
    parser.add_argument('--no-details', action='store_true', help='Skip scraping individual performance details')
    parser.add_argument('--print-data', action='store_true', help='Print stored data after scraping')
    parser.add_argument('--schedule', action='store_true', help='Run as a scheduled task')
    parser.add_argument('--interval', type=int, default=UPDATE_INTERVAL, help=f'Update interval in days (default: {UPDATE_INTERVAL})')
    
    args = parser.parse_args()
    
    if args.schedule:
        logger.info(f"Setting up scheduled scraping every {args.interval} days")
        main_scrape(scrape_details=not args.no_details)  # Run once immediately
        
        if args.print_data:
            print_stored_data()
        
        schedule.every(args.interval).days.do(scheduled_scrape)
        
        logger.info(f"Scheduled to run every {args.interval} days")
        while True:
            schedule.run_pending()
            time.sleep(1)
    else:
        success = main_scrape(scrape_details=not args.no_details)
        
        if args.print_data:
            print_stored_data()
        
        return 0 if success else 1

if __name__ == "__main__":
    main()
