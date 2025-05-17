"""
Paris Opera Ballet Scraper

This module scrapes ballet performance data from the Paris Opera Ballet website
and stores it in a MongoDB database.
"""

import time
import logging
import random
import argparse
from bs4 import BeautifulSoup
import schedule

# Import common utilities
from scrapers.common.db import get_collection, store_performances
from scrapers.common.utils import (
    setup_selenium_driver, 
    accept_cookies, 
    save_debug_info, 
    clean_html
)

# Import Paris Opera Ballet specific configuration
from scrapers.paris_opera_ballet.config import (
    BASE_URL, 
    COLLECTION_NAME, 
    SELECTORS, 
    DEFAULT_DESCRIPTIONS,
    COOKIE_SELECTORS,
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
    Scrape the main page of the Paris Opera Ballet website.
    
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
        if "Page not found" in driver.title:
            logger.error("Page not found error encountered")
            save_debug_info(driver, "pob_main_page")
            raise Exception("Page not found")
        
        logger.info("Waiting for show cards to load")
        show_cards = None
        
        for selector in SELECTORS['show_card']:
            try:
                logger.info(f"Trying selector: {selector}")
                if selector.startswith("//"):
                    from selenium.webdriver.common.by import By
                    show_cards = driver.find_elements(By.XPATH, selector)
                else:
                    from selenium.webdriver.common.by import By
                    show_cards = driver.find_elements(By.CSS_SELECTOR, selector)
                if show_cards:
                    logger.info(f"Found {len(show_cards)} show cards using selector: {selector}")
                    break
            except Exception as e:
                logger.warning(f"Selector {selector} failed: {str(e)}")
                continue
        
        if not show_cards:
            logger.error("Could not find show cards with any selector")
            save_debug_info(driver, "pob_no_cards")
            raise Exception("No show cards found")
        
        # Let the page settle after loading
        time.sleep(2)
        
        logger.info("Parsing page content")
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        performances = []
        
        # Find all FeaturedList__card elements
        card_elements = soup.find_all('div', class_='FeaturedList__card')
        logger.info(f"Found {len(card_elements)} FeaturedList__card elements")

        for card in card_elements:
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
                    
                    # Extract venue
                    venue_elem = None
                    for selector in SELECTORS['venue']:
                        venue_elem = card.select_one(selector)
                        if venue_elem:
                            break
                    venue = venue_elem.text.strip() if venue_elem else ''

                    # Extract date
                    date_elem = None
                    for selector in SELECTORS['date']:
                        date_elem = card.select_one(selector)
                        if date_elem:
                            break
                    date = date_elem.text.strip() if date_elem else ''

                    performance = {
                        'title': title,
                        'url': f"https://www.operadeparis.fr{link}" if not link.startswith('http') else link,
                        'thumbnail': thumbnail,
                        'venue': venue,
                        'date': date,
                        'company': 'Paris Opera Ballet',
                        'source': 'Paris Opera Ballet Website'
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
            save_debug_info(driver, f"pob_no_desc_{url.split('/')[-1]}")
        
        # Simple selector for video links
        video_links = []
        for selector in SELECTORS['video']:
            video_elements = soup.select(selector)
            for video in video_elements:
                if 'data-video-id' in video.attrs:
                    video_id = video['data-video-id']
                    video_links.append(f"https://www.youtube.com/watch?v={video_id}")
                elif 'src' in video.attrs and 'youtube.com' in video['src']:
                    video_id = video['src'].split('/')[-1].split('?')[0]
                    video_links.append(f"https://www.youtube.com/watch?v={video_id}")
        
        logger.info(f"Found {len(video_links)} video links")
        
        return {
            'description': description,
            'video_links': video_links,
            'details_scraped': True,
            'last_updated': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        logger.error(f"Error scraping individual page {url}: {str(e)}", exc_info=True)
        return {
            'description': "Failed to scrape",
            'video_links': [],
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
            if title in DEFAULT_DESCRIPTIONS:
                performance['description'] = DEFAULT_DESCRIPTIONS[title]
                logger.info(f"Added default description for: {title}")
    
    return performances

def main_scrape():
    """
    Main scraping function.
    
    Returns:
        bool: True if successful, False otherwise
    """
    driver = setup_selenium_driver()
    collection = get_collection(COLLECTION_NAME)
    
    try:
        logger.info("Starting Paris Opera Ballet scrape")
        performances = scrape_main_page(driver)
        
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
        logger.info("Paris Opera Ballet scrape completed")

def scheduled_scrape():
    """
    Function to be called by the scheduler.
    """
    logger.info("Starting scheduled Paris Opera Ballet scrape")
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
    parser = argparse.ArgumentParser(description='Paris Opera Ballet Scraper')
    parser.add_argument('--no-details', action='store_true', help='Skip scraping individual performance details')
    parser.add_argument('--print-data', action='store_true', help='Print stored data after scraping')
    parser.add_argument('--schedule', action='store_true', help='Run as a scheduled task')
    parser.add_argument('--interval', type=int, default=UPDATE_INTERVAL, help=f'Update interval in days (default: {UPDATE_INTERVAL})')
    
    args = parser.parse_args()
    
    if args.schedule:
        logger.info(f"Setting up scheduled scraping every {args.interval} days")
        main_scrape()  # Run once immediately
        
        if args.print_data:
            print_stored_data()
        
        schedule.every(args.interval).days.do(scheduled_scrape)
        
        logger.info(f"Scheduled to run every {args.interval} days")
        while True:
            schedule.run_pending()
            time.sleep(1)
    else:
        success = main_scrape()
        
        if args.print_data:
            print_stored_data()
        
        return 0 if success else 1

if __name__ == "__main__":
    main()
