import time
import logging
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from pymongo import MongoClient
import requests
import schedule
from config import *

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Add more realistic headers
    chrome_options.add_argument('--accept-language=en-US,en;q=0.9')
    chrome_options.add_argument('--accept=text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(IMPLICIT_WAIT)
    driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
    
    # Add webdriver stealth
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        '''
    })
    
    return driver

def accept_cookies(driver):
    try:
        # Wait for cookie dialog to be present and visible
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "axeptio_overlay"))
        )
        
        # Try different selectors for accept button
        cookie_button_selectors = [
            (By.ID, "axeptio_btn_acceptAll"),
            (By.CSS_SELECTOR, "[data-test='cookie-accept-all']"),
            (By.CSS_SELECTOR, "button[aria-label*='accept']"),
            (By.XPATH, "//button[contains(text(), 'Accept')]")
        ]
        
        for selector_type, selector in cookie_button_selectors:
            try:
                button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((selector_type, selector))
                )
                # Add a small delay before clicking
                time.sleep(1)
                button.click()
                logger.info(f"Cookies accepted successfully using selector: {selector}")
                time.sleep(2)  # Wait for cookie dialog to disappear
                return
            except Exception:
                continue
        
        logger.warning("Could not find cookie accept button with any selector")
    except Exception as e:
        logger.warning(f"Failed to accept cookies: {str(e)}")

def get_mongodb_collection():
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    return db[COLLECTION_NAME]

def save_debug_info(driver, page_num=1):
    """Save debug information when scraping fails"""
    try:
        # Save page source
        with open(f'debug_page_{page_num}.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        logger.info(f"Saved page source to debug_page_{page_num}.html")
        
        # Save screenshot
        driver.save_screenshot(f'debug_screenshot_{page_num}.png')
        logger.info(f"Saved screenshot to debug_screenshot_{page_num}.png")
        
        # Log page title and URL
        logger.info(f"Page Title: {driver.title}")
        logger.info(f"Current URL: {driver.current_url}")
    except Exception as e:
        logger.error(f"Failed to save debug info: {str(e)}", exc_info=True)

def scrape_main_page(driver):
    try:
        logger.info(f"Navigating to {BASE_URL}")
        driver.get(BASE_URL)
        
        logger.info("Handling cookie consent")
        accept_cookies(driver)
        
        logger.info("Waiting for page to load")
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        logger.info("Checking if page loaded correctly")
        if "Page not found" in driver.title:
            logger.error("Page not found error encountered")
            save_debug_info(driver)
            raise Exception("Page not found")
        
        logger.info("Waiting for show cards to load")
        show_cards = None
        selectors = [
            ".show-card",
            "div.show-card",
            "[class*='show-card']",
            "//div[contains(@class, 'show-card')]",
            "//div[contains(@class, 'show')]"
        ]
        
        for selector in selectors:
            try:
                logger.info(f"Trying selector: {selector}")
                if selector.startswith("//"):
                    show_cards = WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.XPATH, selector))
                    )
                else:
                    show_cards = WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
                    )
                if show_cards:
                    logger.info(f"Found {len(show_cards)} show cards using selector: {selector}")
                    break
            except Exception as e:
                logger.warning(f"Selector {selector} failed: {str(e)}")
                continue
        
        if not show_cards:
            logger.error("Could not find show cards with any selector")
            save_debug_info(driver)
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
                title_elem = card.find('p', class_='show__title')
                # Extract link
                link_elem = card.find('a', class_='FeaturedList__reserve-img')
                # Extract thumbnail
                img_elem = card.find('img')
                
                if title_elem and link_elem:
                    title = title_elem.text.strip()
                    link = link_elem['href']
                    thumbnail = img_elem['src'] if img_elem else ''
                    
                    # Extract venue
                    venue_elem = card.find('p', class_='show__place')
                    venue = venue_elem.find('span').text.strip() if venue_elem else ''

                    # Extract date
                    date_elem = card.find('p', class_='show__date')
                    date = date_elem.find('span').text.strip() if date_elem else ''

                    performance = {
                        'title': title,
                        'url': f"https://www.operadeparis.fr{link}" if not link.startswith('http') else link,
                        'thumbnail': thumbnail,
                        'venue': venue,
                        'date': date
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
    try:
        logger.info(f"Navigating to individual page: {url}")
        driver.get(url)
        
        # Basic wait for page load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(2)  # Short settle time
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Simple selector for description
        description = "Description not found"
        desc_elem = soup.find('div', class_='show__description') or soup.find('div', class_='description')
        if desc_elem:
            description = desc_elem.text.strip()
            logger.info("Found performance description")
        
        # Simple selector for video links
        video_links = []
        video_elements = soup.find_all('div', class_='video-player') or soup.find_all('iframe', class_='video-iframe')
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

def store_performance(collection, performance_data):
    collection.update_one(
        {'url': performance_data['url']},
        {'$set': performance_data},
        upsert=True
    )

def main_scrape():
    driver = setup_driver()
    collection = get_mongodb_collection()
    
    try:
        logger.info("Starting main scrape")
        performances = scrape_main_page(driver)
        
        for performance in performances:
            try:
                # Add a random delay between requests (2-5 seconds)
                time.sleep(2 + random.random() * 3)
                
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
            
            try:
                # Store the performance regardless of whether details were scraped
                store_performance(collection, performance)
                status = "with" if performance.get('details_scraped', False) else "without"
                logger.info(f"Stored {performance['title']} {status} additional details")
            except Exception as e:
                logger.error(f"Error storing {performance['title']}: {str(e)}", exc_info=True)
                
    except Exception as e:
        logger.error(f"An error occurred during main scrape: {str(e)}", exc_info=True)
    finally:
        driver.quit()
        logger.info("Main scrape completed")

def scheduled_scrape():
    logger.info("Starting scheduled scrape")
    main_scrape()
    logger.info("Scheduled scrape completed")

def print_stored_data():
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]
    
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

if __name__ == "__main__":
    logger.info("Ballet scraper started")
    main_scrape()  # Run once immediately
    print_stored_data()  # Print stored data after scraping
    schedule.every(UPDATE_INTERVAL).days.do(scheduled_scrape)
    
    logger.info(f"Scheduled to run every {UPDATE_INTERVAL} days")
    while True:
        schedule.run_pending()
        time.sleep(1)
